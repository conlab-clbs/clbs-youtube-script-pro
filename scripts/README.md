# scripts/ — clbs-youtube-script-pro

全て Python 3.11 以上の標準ライブラリだけで動く（pip 不要）。`<スキルのルート>` は `~/.claude/skills/clbs-youtube-script-pro`（Codex は `~/.codex/skills/...`）。

| スクリプト | 役割 | 必要なもの |
|---|---|---|
| `qa_script.py <project または ファイル> [--strict] [--json] [--role auto\|script\|heygen\|draft]` | 台本リンター。禁止フレーズ／許可取り／`**`・`——`／見出し行残存／和訳調（比率WARN、`--strict`でFAIL）／演出比喩／AI造語／タグ番号・閉じ忘れ／Bロール区間の長さ／文末break／`media_list.yaml` との番号整合を検査し `qa_script_report.md` を出力。FAIL があれば exit 1 | なし |
| `ja_style_fix.py <script.txt> [--all] [--strict] [--dry-run]` | qa_script が拾った文だけを Gemini 3.8 Flash に直させ、元の位置に戻す（タグ・break不変、`.bak_日時` に退避、修正後に再検査） | `GEMINI_API_KEY` |
| `gemini_chat.py [-m gemini-3.8-flash] -p "…" \| -f prompt.md [--system rules.md] [-o out.txt] [--json] [--list]` | Gemini API 最小クライアント。本文執筆や言い換えを Gemini に振るときの土台 | `GEMINI_API_KEY` |
| `gpt_consult.py ask\|reply --out <dir> --name <topic> -f prompt.md [--model gpt-6-astra] [--effort medium\|high]` | GPT に企画相談（Codex CLI 経由・ChatGPTサブスク枠、API課金なし）。`reply` で同じセッションを継続 | `codex login` 済み |
| `make_research_skill.py --channel … --slug … --genre … --target … --style search\|browse\|both --themes … --kw-ja … --out-dir … [--codex] [--force]` | 受講生のジャンル専用「毎日リサーチ」スキル（SKILL.md ＋ Cowork 用 research_prompt.md）を `assets/daily_research_skill_template.md` から生成。AI が `docs/AI_RESEARCH_SETUP_GUIDE.md` の手順で呼ぶ | なし |
| `grok_consult.py ask\|reply\|research --out <dir> --name <topic> -f prompt.md [--search x\|web\|both] [--from-date …]` | Grok に企画相談・X/Web実測リサーチ（引用URL付き）。`--reasoning medium` 既定 | `XAI_API_KEY` |

## キーの置き場所

環境変数が最優先。無ければ `~/.config/clbs/config.toml` を読む。

```toml
[gemini]
api_key = "AIza..."     # https://aistudio.google.com/  → Get API key

[xai]
api_key = "xai-..."     # https://console.x.ai/ → API Keys
```

Claude Code で常時使うなら `~/.claude/settings.json` の `env` に入れておくとセッションごとに設定不要。

```json
{ "env": { "GEMINI_API_KEY": "AIza...", "XAI_API_KEY": "xai-..." } }
```

## 典型的な流れ

```bash
# 1. 台本を書いたら検査
python3 ~/.claude/skills/clbs-youtube-script-pro/scripts/qa_script.py videos/20260917_xxx/ --strict
# 2. 指摘された文だけ Gemini に直させる（任意）
python3 ~/.claude/skills/clbs-youtube-script-pro/scripts/ja_style_fix.py videos/20260917_xxx/script.txt --strict
# 3. heygen_script.txt を作り直し、もう一度検査 → PASS で納品
```
