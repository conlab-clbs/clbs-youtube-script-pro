#!/usr/bin/env python3
"""Gemini API 最小クライアント（標準ライブラリのみ・追加インストール不要）。

Claude Code / Codex から「日本語の本文執筆・校正」を Gemini に任せるための橋渡し。

キーの読み込み順:
  1. 環境変数 GEMINI_API_KEY
  2. ~/.config/clbs/config.toml の [gemini] api_key
  （キーは https://aistudio.google.com/ の「Get API key」で発行）

使い方:
  python3 scripts/gemini_chat.py --list                       # 利用可能モデル一覧
  python3 scripts/gemini_chat.py -p "質問"                    # 単発プロンプト（既定 gemini-3.8-flash）
  python3 scripts/gemini_chat.py -f prompt.txt -o out.txt     # ファイルを送って結果を保存
  python3 scripts/gemini_chat.py -f brief.md --system references/japanese_style.md
                                                              # システム指示に文体ルールを渡す
  python3 scripts/gemini_chat.py -f prompt.txt --json         # JSONだけを返させる（機械処理向け）
"""
import argparse, json, os, sys, urllib.request, urllib.error

BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-3.8-flash"
CONFIG = os.path.expanduser("~/.config/clbs/config.toml")


def load_key():
    k = os.environ.get("GEMINI_API_KEY")
    if k:
        return k
    if os.path.exists(CONFIG):
        try:
            import tomllib
            with open(CONFIG, "rb") as f:
                k = tomllib.load(f).get("gemini", {}).get("api_key")
            if k:
                return k
        except Exception:
            pass
    sys.exit("GEMINI_API_KEY が未設定です。\n"
             "  export GEMINI_API_KEY=\"AIza...\"  か、\n"
             f"  {CONFIG} に\n  [gemini]\n  api_key = \"AIza...\"\n  を書いてください（キーは https://aistudio.google.com/ で発行）。")


def call(path, key, payload=None, timeout=300):
    req = urllib.request.Request(f"{BASE}/{path}",
                                 headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                                 data=json.dumps(payload).encode() if payload else None,
                                 method="POST" if payload else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:800]
        hint = ""
        if e.code == 429 and "prepay" in body.lower():
            hint = "\n→ 前払いクレジットが尽きています。https://aistudio.google.com/ の Billing でチャージしてください。"
        if e.code in (400, 404) and "model" in body.lower():
            hint = "\n→ モデル名が違う可能性。--list で利用可能なモデルを確認してください。"
        sys.exit(f"HTTP {e.code}: {body}{hint}")
    except urllib.error.URLError as e:
        sys.exit(f"接続失敗: {e.reason}")


def generate(model, key, prompt, system=None, temperature=1.0, json_mode=False):
    """テキスト生成。戻り値 (text, usage)。"""
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
               "generationConfig": {"temperature": temperature}}
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}
    if json_mode:
        payload["generationConfig"]["responseMimeType"] = "application/json"
    res = call(f"models/{model}:generateContent", key, payload)
    try:
        text = "".join(p.get("text", "") for p in res["candidates"][0]["content"]["parts"])
    except (KeyError, IndexError):
        sys.exit("応答の解析に失敗:\n" + json.dumps(res, ensure_ascii=False, indent=2)[:1500])
    return text, res.get("usageMetadata", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("-m", "--model", default=DEFAULT_MODEL)
    ap.add_argument("-p", "--prompt")
    ap.add_argument("-f", "--file")
    ap.add_argument("--system", help="システム指示ファイル（文体ルール等）")
    ap.add_argument("-o", "--out")
    ap.add_argument("--json", action="store_true", help="JSON応答モード")
    ap.add_argument("--temperature", type=float, default=1.0)
    a = ap.parse_args()
    key = load_key()

    if a.list:
        data = call("models?pageSize=200", key)
        for m in data.get("models", []):
            if "generateContent" in m.get("supportedGenerationMethods", []):
                print(f"{m['name'].removeprefix('models/'):40s} {m.get('displayName', '')}")
        return

    prompt = a.prompt or (open(a.file, encoding="utf-8").read() if a.file else None)
    if not prompt:
        sys.exit("-p か -f でプロンプトを指定してください")
    system = open(a.system, encoding="utf-8").read() if a.system else None
    text, u = generate(a.model, key, prompt, system, a.temperature, a.json)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"saved: {a.out}")
    else:
        print(text)
    print(f"\n[tokens] in={u.get('promptTokenCount')} out={u.get('candidatesTokenCount')} model={a.model}", file=sys.stderr)


if __name__ == "__main__":
    main()
