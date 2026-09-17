#!/usr/bin/env python3
"""日本語表現の修正パス（Gemini 3.8 Flash に「指摘された文だけ」を直させる）。

qa_script.py が拾った文（禁止フレーズ・和訳調・演出比喩など）を番号付きで Gemini に渡し、
直した文だけを JSON で受け取って元の位置に差し戻す。演出タグ・<break>・段落構造は一切触らない。
修正後に qa_script.py を再実行し、前後の件数を表示する。修正前のファイルは <file>.bak_<日時> に退避。

使い方:
  python3 scripts/ja_style_fix.py videos/20260917_xxx/script.txt            # 指摘された文だけ直す
  python3 scripts/ja_style_fix.py videos/20260917_xxx/script.txt --all      # 全文を和訳調の観点で通す
  python3 scripts/ja_style_fix.py <file> --dry-run                          # 何が送られるか見るだけ
  python3 scripts/ja_style_fix.py <file> --model gemini-3.8-flash --strict  # 納品前ゲート基準で判定

heygen_script.txt は script.txt を直したあと作り直す（タグ除去するだけ）。
"""
import argparse, datetime, importlib.util, io, json, pathlib, re, sys
from contextlib import redirect_stdout

HERE = pathlib.Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


qa = load("qa_script")
gc = load("gemini_chat")

RULES_PATH = HERE.parent / "references" / "japanese_style.md"
SENT_END = "。！？"
# 文の切れ目: 句点の直後（次が break/タグ/改行/文字のどれでも）
SPLIT_RE = re.compile(r"(?<=[。！？])")


def tokenize(raw: str):
    """タグ・break・改行を保護し、地の文だけを文単位に分ける。戻り値は [(kind, text)]"""
    toks = []
    pos = 0
    guard = re.compile(qa.TAG_RE.pattern + "|" + qa.BREAK_RE.pattern + r"|\n")
    for m in guard.finditer(raw):
        if m.start() > pos:
            _push_text(toks, raw[pos:m.start()])
        toks.append(("keep", m.group(0)))
        pos = m.end()
    if pos < len(raw):
        _push_text(toks, raw[pos:])
    return toks


def _push_text(toks, chunk):
    for piece in SPLIT_RE.split(chunk):
        if not piece:
            continue
        core = piece.strip()
        if not core:                      # 空白だけの断片はそのまま保持
            toks.append(("keep", piece))
            continue
        lead = len(piece) - len(piece.lstrip())
        trail = len(piece) - len(piece.rstrip())
        if lead:
            toks.append(("keep", piece[:lead]))
        toks.append(("sent", core))
        if trail:
            toks.append(("keep", piece[len(piece) - trail:]))


def run_qa(path: pathlib.Path, strict: bool):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = qa.main([str(path), "--json"] + (["--strict"] if strict else []))
    data = json.loads(buf.getvalue())
    return data


def build_prompt(items, rules):
    listing = "\n".join(f'{i}: {s}' for i, s in items)
    return f"""次は日本語のYouTube台本から抜き出した文です（話し手が視聴者ひとりに語りかける会話調）。
各文を、下の「日本語表現ルール」に沿って自然な話し言葉に直してください。

## 守ること
- 事実・数値・固有名詞・主張の強さ（断定は断定、留保は留保）・話の順序は変えない
- 会話調（〜なんです／〜ですよね／〜なんですよ）は保つ。敬語の丁寧さも元のまま
- 1文は1文のまま返す（分割・結合・削除をしない）。直す必要がない文はそのまま返す
- 文頭のメタコメント（結論から言うと 等）、許可取り（〜させてください）、反語（〜ではありませんか）は必ず消す
- 「衝撃的な結論を先に言いますけど」は冒頭の決まり文句なので残す
- 返答は JSON オブジェクトだけ。キーは文番号（文字列）、値は直した文。説明文は書かない

## 日本語表現ルール
{rules}

## 対象の文
{listing}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--all", action="store_true", help="指摘の有無に関わらず全文を通す")
    ap.add_argument("--strict", action="store_true", help="qa_script を --strict で判定")
    ap.add_argument("--model", default=gc.DEFAULT_MODEL)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--batch", type=int, default=60, help="1回のリクエストに載せる文数")
    a = ap.parse_args()
    path = pathlib.Path(a.file).expanduser().resolve()
    if not path.exists():
        sys.exit(f"ファイルがありません: {path}")

    before = run_qa(path, a.strict)
    raw = path.read_text(encoding="utf-8")
    toks = tokenize(raw)
    sent_idx = [i for i, (k, _) in enumerate(toks) if k == "sent"]
    flagged = set(before["flagged"])

    def is_target(s):
        if a.all:
            return True
        # qa は文末記号を残した文で返すので、記号有無の両方で照合
        return s in flagged or s.rstrip(SENT_END) in {f.rstrip(SENT_END) for f in flagged}

    targets = [(i, toks[i][1]) for i in sent_idx if is_target(toks[i][1])]
    print(f"修正前: {before['verdict']} FAIL {len(before['fails'])} / WARN {len(before['warns'])}  文数 {len(sent_idx)}  対象 {len(targets)}文")
    if not targets:
        print("直す対象がありません。")
        return 0
    rules = RULES_PATH.read_text(encoding="utf-8") if RULES_PATH.exists() else ""
    if a.dry_run:
        for i, s in targets[:80]:
            print(f"  - {s}")
        return 0

    key = gc.load_key()
    changed = 0
    for b in range(0, len(targets), a.batch):
        chunk = targets[b:b + a.batch]
        prompt = build_prompt(chunk, rules)
        text, usage = gc.generate(a.model, key, prompt, json_mode=True, temperature=0.4)
        try:
            fixed = json.loads(text)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", text, re.S)
            fixed = json.loads(m.group(0)) if m else {}
        for i, s in chunk:
            new = str(fixed.get(str(i), "")).strip()
            if not new or new == s:
                continue
            if len(re.findall(r"[。！？]", new)) > 1:  # 分割された→採用しない
                continue
            if new[-1] not in SENT_END and s[-1] in SENT_END:
                new += s[-1]
            toks[i] = ("sent", new)
            changed += 1
        print(f"  batch {b // a.batch + 1}: {len(chunk)}文送信 / tokens in={usage.get('promptTokenCount')} out={usage.get('candidatesTokenCount')}")

    if not changed:
        print("Gemini は変更を返しませんでした。")
        return 0
    bak = path.with_name(path.name + f".bak_{datetime.datetime.now():%Y%m%d_%H%M}")
    bak.write_text(raw, encoding="utf-8")
    out = "".join(t for _, t in toks)
    path.write_text(out, encoding="utf-8")
    after = run_qa(path, a.strict)
    # タグ列と break 数が保たれているか
    tags_ok = qa.TAG_RE.findall(raw) == qa.TAG_RE.findall(out) and len(qa.BREAK_RE.findall(raw)) == len(qa.BREAK_RE.findall(out))
    print(f"修正後: {after['verdict']} FAIL {len(after['fails'])} / WARN {len(after['warns'])}  差し替え {changed}文  タグ/break保持 {'OK' if tags_ok else 'NG（要確認）'}")
    print(f"退避: {bak}")
    if after["fails"]:
        print("残った FAIL:")
        for m in after["fails"]:
            print("  -", m)
    return 0 if not after["fails"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
