#!/usr/bin/env python3
"""Grok（xAI API）を企画相談・X/Webリアルタイムリサーチの相談相手として呼ぶ。標準ライブラリのみ。

キーの読み込み順: 環境変数 XAI_API_KEY → ~/.config/clbs/config.toml の [xai] api_key
（キーは https://console.x.ai/ の API Keys で発行。クレジット購入が必要）

  ask      : 新規セッション。prompt(file/stdin) → 応答md。response_id を記録して続きの相談に使う
  reply    : 直前のセッションを継続（多ターン相談）
  research : X検索/Web検索を有効にした単発リサーチ（引用URL付き）

使い方:
  python3 scripts/grok_consult.py ask      --out _gen/grok --name plan -f brief.md
  python3 scripts/grok_consult.py reply    --out _gen/grok --name plan -f followup.md
  python3 scripts/grok_consult.py research --out _gen/grok --name market -f query.md [--from-date 2026-08-01]
  python3 scripts/grok_consult.py --list
出力: <dir>/<name>_rN.md（応答＋引用）, <dir>/<name>_prompt_rN.md, <dir>/<name>.session
"""
import argparse, json, os, pathlib, sys, time, urllib.error, urllib.request

BASE = "https://api.x.ai/v1"
CONFIG = os.path.expanduser("~/.config/clbs/config.toml")
DEFAULT_MODEL = "grok-4.6"
RESEARCH_INSTRUCTIONS = """あなたはリサーチャーです。検索で得た投稿を必ず本文に落とし込んでください。
- 「以下に整理します」のような予告で終わらせない。予告した内容はその場で書き切る
- 見出しごとに実際の投稿の要旨を1〜3行で示し、直後に投稿URLを添える
- 語彙・言い回しは原文の表現をそのまま拾う
- 賛同側と批判側を必ず両方扱う
- 全体で3,000字以上。検索件数が少なければ「少なかった」と明記する"""
WRITEUP_PROMPT = "調べ物は十分です。いま本文を書いてください。取得済みの検索結果を根拠に、最初の依頼に最後まで答えること。予告・前置きは書かず、本文の見出しから始めて書き切ってください。"


def load_key():
    k = os.environ.get("XAI_API_KEY")
    if k:
        return k
    if os.path.exists(CONFIG):
        try:
            import tomllib
            with open(CONFIG, "rb") as f:
                k = tomllib.load(f).get("xai", {}).get("api_key")
            if k:
                return k
        except Exception:
            pass
    sys.exit(f"XAI_API_KEY が未設定です。環境変数か {CONFIG} の [xai] api_key に設定してください（https://console.x.ai/ で発行）。")


def call(path, key, payload=None, timeout=900):
    req = urllib.request.Request(f"{BASE}/{path}", headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                                 data=json.dumps(payload).encode() if payload else None, method="POST" if payload else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode(errors='replace')[:1000]}")
    except urllib.error.URLError as e:
        sys.exit(f"接続失敗: {e.reason}")


def extract(res):
    parts, cites = [], []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") in ("output_text", "text") and isinstance(node.get("text"), str):
                parts.append(node["text"])
            u = node.get("url")
            if isinstance(u, str) and u.startswith("http"):
                cites.append(u)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(res.get("output", []))
    for c in res.get("citations", []) or []:
        cites.append(c if isinstance(c, str) else c.get("url", ""))
    return "\n".join(parts).strip(), list(dict.fromkeys(c for c in cites if c))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", choices=["ask", "reply", "research"])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--out"); ap.add_argument("--name")
    ap.add_argument("-f", "--file"); ap.add_argument("-p", "--prompt")
    ap.add_argument("--system", help="システム指示ファイル")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--search", choices=["none", "x", "web", "both"], help="既定: ask/reply=none, research=both")
    ap.add_argument("--from-date"); ap.add_argument("--to-date")
    ap.add_argument("--reasoning", choices=["low", "medium", "high"], default="medium",
                    help="既定 medium（high だと推論が出力予算を食い、本文が出ないことがある）")
    ap.add_argument("--max-searches", type=int, default=10)
    a = ap.parse_args()
    key = load_key()
    if a.list:
        for m in call("models", key).get("data", []):
            print(m.get("id"))
        return
    if not a.mode or not (a.out and a.name):
        ap.error("mode（ask/reply/research）と --out --name を指定してください")
    if a.search is None:
        a.search = "both" if a.mode == "research" else "none"

    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    prompt = a.prompt or (open(a.file, encoding="utf-8").read() if a.file else sys.stdin.read())
    n = len(list(out.glob(f"{a.name}_r*.md"))) + 1
    sess = out / f"{a.name}.session"
    prev = None
    if a.mode == "reply":
        if not sess.exists():
            sys.exit("session file がありません。先に ask を実行してください")
        prev = sess.read_text().strip()

    tools = []
    if a.search in ("x", "both"):
        t = {"type": "x_search"}
        if a.from_date: t["from_date"] = a.from_date
        if a.to_date: t["to_date"] = a.to_date
        tools.append(t)
    if a.search in ("web", "both"):
        tools.append({"type": "web_search"})
    instr = open(a.system, encoding="utf-8").read() if a.system else (RESEARCH_INSTRUCTIONS if a.mode == "research" else "")
    if tools and a.max_searches:
        instr += f"\n\n検索は最大{a.max_searches}回まで。超えたら集まった分で書き切ること。"
    instr = instr.strip()

    payload = {"model": a.model, "reasoning": {"effort": a.reasoning}}
    if prev:
        payload["previous_response_id"] = prev
        if instr:  # 継続ターンでは instructions を送れないため本文先頭に畳む
            prompt = f"{instr}\n\n---\n\n{prompt}"; instr = ""
    if instr:
        payload["instructions"] = instr
    payload["input"] = [{"role": "user", "content": prompt}]
    if tools:
        payload["tools"] = tools
    (out / f"{a.name}_prompt_r{n}.md").write_text(prompt, encoding="utf-8")

    t0 = time.time()
    res = call("responses", key, payload)
    text, cites = extract(res)
    usd = (res.get("usage", {}) or {}).get("cost_in_usd_ticks", 0) / 1e10
    if tools and len(text) < 500 and res.get("id"):  # 検索ターンは予告だけで終わることがある→続きを書かせる
        print(f"… 本文が{len(text)}字のため、同じセッションで続きを書かせます", file=sys.stderr)
        res2 = call("responses", key, {"model": a.model, "previous_response_id": res["id"], "reasoning": {"effort": a.reasoning},
                                       "input": [{"role": "user", "content": WRITEUP_PROMPT}]})
        text2, cites2 = extract(res2)
        usd += (res2.get("usage", {}) or {}).get("cost_in_usd_ticks", 0) / 1e10
        if len(text2) > len(text):
            text, cites = text2, cites + [c for c in cites2 if c not in cites]
        res = res2
    if not text:
        (out / f"{a.name}_raw_r{n}.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        sys.exit(f"応答の解析に失敗。生レスポンス: {out / f'{a.name}_raw_r{n}.json'}")
    body = text + ("\n\n---\n## 引用\n" + "\n".join(f"- {c}" for c in cites) if cites else "")
    resp = out / f"{a.name}_r{n}.md"
    resp.write_text(body, encoding="utf-8")
    if res.get("id"):
        sess.write_text(res["id"])
    print(f"round {n} -> {resp} ({len(body)} chars, {int(time.time() - t0)}s, 引用{len(cites)}件, 実費 ${usd:.4f})")


if __name__ == "__main__":
    main()
