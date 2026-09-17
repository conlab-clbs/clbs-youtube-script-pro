# 他のAIを参加させる（Gemini 3.8 Flash・GPT・Grok）

Claude Code / Codex を「ディレクター」にして、工程ごとに得意なAIへ作業を振る考え方と手順。
セットアップの手順書は https://claude.ai/artifact/91fDN2Wz7GRTk2r6XdVy7W （同じものを `docs/multi_ai_manual.html` に同梱）。ここでは要点だけ書く。

## 役割分担（台本制作の実運用で固まった形）

| 工程 | 担当 | 理由 |
|---|---|---|
| 企画の採否・言い切りの強さ・タイトル・最終レビュー | ディレクター（Claude Code / Codex 上のメインモデル） | 判断の塊。他AIに丸投げしない |
| 日本語本文の執筆・言い換え・校正修正 | Gemini 3.8 Flash | 同一ブリーフ比較で「Geminiの素の出力が自然」と本人判断。安価で速い |
| 企画の反論・論理の穴・一次資料の確認 | GPT（Codex CLI 経由） | 留保が正確で言い過ぎを検出する。着地は弱めるのでタイトルは任せない |
| 市場の飽和度・X/Web のリアルタイム実測 | Grok（xAI API） | 外部の目として既出との衝突を暴く。社内実測を持たないので「勝ち型」の判断はさせない |

## 3つの接続経路

| 経路 | 例 | 向いている相手 |
|---|---|---|
| API を Python で直に叩く（標準ライブラリだけ） | `scripts/gemini_chat.py`, `scripts/grok_consult.py` | Gemini・Grok。キーがあれば10行で繋がる |
| CLI をサブプロセスで呼ぶ | `codex exec --model … -` に stdin でプロンプト（`scripts/gpt_consult.py`） | GPT。ChatGPT サブスク枠で動き API 課金がない |
| MCP サーバーとして登録 | `claude mcp add -s user codex -- codex mcp-server` | Claude Code からツールとして自然に呼びたいとき |

ディレクター側は「スクリプトを叩いて結果ファイルを読む」だけなので、どの経路でも Claude Code / Codex の挙動は同じ。

## 相談の回し方（企画段階）

1. ディレクターが共通ブリーフを1本書く（企画案・チャンネル前提・聞きたいこと）。数値の転記ミスは相手の分析を丸ごとズラすので必ず見直す
2. **R1: 同じブリーフを GPT と Grok に並列投入**（片方の結論を見せると引きずられる）
3. ディレクターが突合して決定メモ v1（採用／部分採用／不採用）
4. **R2: 決定メモ v1 を両者に返して叩かせる**（「決まった案を壊させる」ラウンドが一番効く。Grok は `reply` で同じセッションを継続）
5. ディレクターが決定メモを確定 → 本人へ

Grok へのブリーフには「褒めなくていい／反対と穴の指摘に字数を使え」と入れる。Grok が出す再生数・市場データは自分の実測と突合してから使う。

## 執筆・校正の回し方（台本段階）

1. ディレクターが章ごとにブリーフを書く（企画・語り手・章の位置・使う素材と順序・断定ライン・タグ形式・1行1文）。文長や語尾の数値縛りは入れない（数値制約付きは不自然になる）
2. `scripts/gemini_chat.py -f briefs/ch3.md --system references/japanese_style.md -o draft/ch3.txt`
3. `scripts/qa_script.py draft/ch3.txt` → FAIL があれば `scripts/ja_style_fix.py draft/ch3.txt` で該当文だけ Gemini に直させる
4. ディレクターが最終レビュー（企画とのズレ・フックの強さ・機械が消した対比の復元）→ script.txt / heygen_script.txt / media_list.yaml を出力 → `qa_script.py <project> --strict` PASS

## キー

- `GEMINI_API_KEY`: https://aistudio.google.com/ の Get API key（前払い課金。残高0だと 429）
- `XAI_API_KEY`: https://console.x.ai/ の API Keys（クレジット購入）
- GPT: キー不要。`brew install --cask codex` → `codex login`（ChatGPT でログイン）

環境変数か `~/.config/clbs/config.toml`（`[gemini] api_key` / `[xai] api_key`）に置く。スクリプトはこの順で読む。
