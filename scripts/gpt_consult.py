#!/usr/bin/env python3
"""GPT（OpenAI Codex CLI 経由・ChatGPTサブスク認証）を企画・構成の相談相手として呼ぶ。API課金なし。

前提: `brew install --cask codex` → `codex login`（ChatGPTでログイン）。
  ask   : 新規セッション。prompt(file/stdin) → 応答md。セッションIDを記録して続きの相談に使う
  reply : 直前のセッションを resume して追加質問（Claude⇄GPT の多ターン相談）

使い方:
  python3 scripts/gpt_consult.py ask   --out _gen/gpt --name plan -f brief.md [--model gpt-6-astra] [--effort medium|high]
  python3 scripts/gpt_consult.py reply --out _gen/gpt --name plan -f followup.md
出力: <dir>/<name>_rN.md（応答）, <dir>/<name>_prompt_rN.md（送った質問）, <dir>/<name>.session
"""
import argparse, glob, os, pathlib, re, subprocess, sys, time


def newest_session_id(since):
    files = [f for f in glob.glob(os.path.expanduser("~/.codex/sessions/*/*/*/rollout-*.jsonl")) if os.path.getmtime(f) >= since - 2]
    if not files:
        return None
    f = max(files, key=os.path.getmtime)
    m = re.search(r"rollout-.*?-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.jsonl$", f)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["ask", "reply"])
    ap.add_argument("--out", required=True); ap.add_argument("--name", required=True)
    ap.add_argument("-f", "--file"); ap.add_argument("--effort", default="high")
    ap.add_argument("--model", default=None, help="未指定なら ~/.codex/config.toml の model。例: gpt-6-astra")
    a = ap.parse_args()
    if subprocess.run(["which", "codex"], capture_output=True).returncode != 0:
        sys.exit("codex コマンドがありません。brew install --cask codex → codex login を先に実行してください。")
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    prompt = open(a.file, encoding="utf-8").read() if a.file else sys.stdin.read()
    n = len(list(out.glob(f"{a.name}_r*.md"))) + 1
    (out / f"{a.name}_prompt_r{n}.md").write_text(prompt, encoding="utf-8")
    resp = out / f"{a.name}_r{n}.md"; sess = out / f"{a.name}.session"
    t0 = time.time()
    model_cfg = ["-c", f"model=\"{a.model}\""] if a.model else []
    if a.mode == "reply":
        if not sess.exists():
            sys.exit("session file がありません。先に ask を実行してください")
        cmd = ["codex", "exec", "resume", sess.read_text().strip(), *model_cfg,
               "-c", f"model_reasoning_effort=\"{a.effort}\"", "-c", "sandbox_mode=\"read-only\"",
               "--skip-git-repo-check", "--output-last-message", str(resp), "-"]
    else:
        cmd = ["codex", "exec", *(["--model", a.model] if a.model else []), "-c", f"model_reasoning_effort=\"{a.effort}\"",
               "-s", "read-only", "--skip-git-repo-check", "--output-last-message", str(resp), "-"]
    # プロンプトは必ず標準入力から渡す（引数渡しだと「Reading additional input from stdin」で止まる）
    r = subprocess.run(cmd, input=prompt, text=True, capture_output=True)
    if not resp.exists() and r.stdout.strip():
        resp.write_text(r.stdout.rsplit("tokens used", 1)[0].strip(), encoding="utf-8")
    (out / f"{a.name}_log_r{n}.txt").write_text(r.stdout[-4000:] + "\n--- stderr ---\n" + r.stderr[-3000:], encoding="utf-8")
    if not resp.exists() or not resp.read_text(encoding="utf-8").strip():
        sys.exit(f"応答なし (exit={r.returncode}). ログ: {out / f'{a.name}_log_r{n}.txt'}")
    if a.mode == "ask":
        sid = newest_session_id(t0)
        if sid:
            sess.write_text(sid)
    print(f"round {n} -> {resp} ({len(resp.read_text(encoding='utf-8'))} chars, {int(time.time() - t0)}s, session={'saved' if sess.exists() else 'NOT FOUND'})")


if __name__ == "__main__":
    main()
