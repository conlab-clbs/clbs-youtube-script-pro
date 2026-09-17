# clbs-youtube-script-pro

顔出しAIアバター動画（HeyGen等／VSL・ウェビナー・YouTube本編）の**企画考案から台本執筆、日本語校正まで**を一気通貫で行う [Claude Code](https://claude.com/claude-code) / [OpenAI Codex](https://openai.com/codex) 用スキルです。

YouTubeアルゴリズム（検索型/ブラウジング型・CTR・視聴維持率）に沿って企画を考え抜き、会話調・yesセット・AI構文禁止のCLBS文体で台本化。書き上げた台本は同梱の**日本語校正ゲート**（`scripts/qa_script.py`）を通してから納品します。そのまま編集スキル **[clbs-youtube-edit](https://github.com/conlab-clbs/clbs-youtube-edit)** に渡せる `script.txt` / `heygen_script.txt` / `media_list.yaml` を出力します。

---

## 特徴

- **YouTubeアルゴリズムに沿った企画考案** — 常識破壊8フレーム＋バズ10軸・心理トリガーで「精鋭3案」を考え抜き、企画審査5項目でセルフ採点（5中4未満は作り直し）。台本の上手さより**企画の強さ**を最優先。
- **冒頭30秒＝4点セット** — ①名乗り＋テーマ ②衝撃的な結論 ③天国と地獄 ④希少性・権威性＋「最後までご覧ください」を毎回この順で構成し、視聴維持率の急落を防ぐ。
- **日本語校正ゲート（v2 で追加）** — 文頭メタコメント（「結論から言うと」等）・許可取り（「〜させてください」）・AI記号（`**`／`——`）・**英文和訳調**（受け身で行為者を隠す／名詞化／冗長な強調／「〜ですね」で言い切りを弱める／「〜のほう」）・演出比喩・AI造語・タグ規約違反を機械検査。FAIL があるうちは納品しない。
- **Gemini 3.8 Flash による修正パス（任意）** — 指摘された文だけを Gemini が直して元の位置に戻す（`scripts/ja_style_fix.py`）。タグ・沈黙マーカーは触らない。
- **他AIとの協業（任意）** — GPT（Codex CLI 経由・API課金なし）と Grok（xAI API・X/Web実測）を企画の相談相手として呼ぶスクリプトを同梱。
- **そのまま編集に流せる** — 出力した台本＋素材台帳は `clbs-youtube-edit` が無改変で読み込み、Premiere XML と完成MP4を生成。
- **無発音の演出タグ** — `[見出し：◯◯] / [スライドN] / [ピクチャーN] / [BロールN] / [カムリターン]` をアバターに読ませない前提で配置。
- **HeyGen沈黙マーカー** — 文末・タグ直後に `<break time="0.8s" />` を付与。編集側がこの沈黙を切ってテンポを生む。
- **Bロール尺の安全設計** — 「1文＝1Bロール／セリフ尺 < 生成動画尺」を徹底し、尺不足で静止画化する事故を防ぐ。

## 出力ファイル

| ファイル | 内容 |
|---|---|
| `script.txt` | 演出タグ＋`<break>` を全て含む完成台本（編集スキルの正データ） |
| `heygen_script.txt` | `[…]`タグを除去し `<break>` のみ残した版（HeyGen貼り付け用） |
| `media_list.yaml` | 素材台帳（headings / brolls / pictures / slides / thumbnail） |
| `qa_script_report.md` | 日本語校正ゲートの結果（PASS/FAIL・指摘一覧） |

## 台本タグ仕様

| タグ | 用途 | 発音 |
|---|---|---|
| `[見出し：◯◯]` | 左上見出しバー（次の見出しまで継続・スライド/Bロール中は非表示） | しない |
| `[スライドN]` | スライド全画面＋右上ワイプ | しない |
| `[ピクチャーN]` | 左に画像ポップアップ | しない |
| `[BロールN]` | Bロール全画面（声のみ継続） | しない |
| `[カムリターン]` | 素材を終了しアバターに戻す | しない |
| `<break time="0.8s" />` | 沈黙ポーズ（編集のジェットカット点） | 沈黙 |

## 動作環境

| 環境 | 対応 | 配置先 |
|---|---|---|
| Claude Code（macOS） | ✅ | `~/.claude/skills/clbs-youtube-script-pro/` |
| Claude Code（Windows） | ✅ | `%USERPROFILE%\.claude\skills\clbs-youtube-script-pro\` |
| OpenAI Codex CLI（Agent Skills対応版） | ✅ | `~/.codex/skills/clbs-youtube-script-pro/` |

いずれもフォルダ直下に `SKILL.md` が来るように配置してください。同梱スクリプトは Python 3.11 以上の標準ライブラリだけで動きます（pip 不要）。Gemini / Grok を使う経路だけ API キーが要ります（後述）。

### インストール（受講生向け・AIに代行させる）

Claude Code か Codex のチャットに次を貼るだけです。AIが環境を調べて配置と接続確認を自分で行い、あなたにしかできない操作（ブラウザでのキー発行・ログイン・アプリ再起動）だけを1つずつ案内します。

```
次のAIエージェント向けガイドを読み、そこに書かれた「進め方の原則」に従って、私の環境のセットアップを代行してください。
https://raw.githubusercontent.com/conlab-clbs/clbs-youtube-script-pro/main/docs/AI_SETUP_GUIDE.md

URLを開けない場合は、先に
  git clone https://github.com/conlab-clbs/clbs-youtube-script-pro.git ~/.claude/skills/clbs-youtube-script-pro
を実行し（Codex の場合は配置先を ~/.codex/skills/clbs-youtube-script-pro にする）、
その中の docs/AI_SETUP_GUIDE.md を読んで進めてください。

私はターミナル操作に慣れていません。あなたが実行できることは全部あなたが実行し、
私にしかできない操作（ブラウザでのキー発行・ログイン・アプリの再起動）だけを、
1回に1つずつ、何をどこでやればいいか具体的に教えてください。
私が「終わった」と言ったら確認してから次に進んでください。キーの値はチャットに貼らせないでください。
```

AIが従う手順書は [`docs/AI_SETUP_GUIDE.md`](docs/AI_SETUP_GUIDE.md) です。

### インストール（自分で行う場合）

```bash
git clone https://github.com/conlab-clbs/clbs-youtube-script-pro.git ~/.claude/skills/clbs-youtube-script-pro
```

Codex の場合は配置先を `~/.codex/skills/clbs-youtube-script-pro` に読み替えてください。既に入っている場合は同じフォルダで `git pull`。

## 使い方

Claude Code でこのスキルを入れた状態で「YouTube企画考えて」「企画から台本作って」「YouTube台本書いて」などと話しかけると起動します。止まるのは企画の選択と構成の承認の2箇所だけです。

```
0 ヒアリング（業種・ターゲットの悩み・伝えたいノウハウ・CTA・戦略タイプ）
1 軽量リサーチ（任意・WebSearchで競合の勝ち型と空き枠を抽出）
2 ジャンル適性チェック（視聴者パイは十分広いか）
3 企画考案：精鋭3案＋企画審査5項目セルフ採点   ← 本丸（ここで1案を選ぶ）
4 構成案＋冒頭30秒フック設計（ここで承認）
5 台本執筆（全パートを書き切ってから提示）
6 素材台帳出力（script.txt / heygen_script.txt / media_list.yaml）
7 日本語校正ゲート（scripts/qa_script.py --strict が PASS になるまで直す）
```

`references/` に教材一式があります：
- `japanese_style.md` — **日本語表現ルール**（禁止フレーズ／和訳調7原則／演出比喩／直すときの原則）
- `multi_ai_collaboration.md` — Gemini・GPT・Grok を Claude Code / Codex に参加させる考え方と手順
- `docs/daily_research_prompt.md` — **毎日リサーチ＋ネタ出しタスクのテンプレート**（自分のジャンルに書き換えて Cowork / Claude Code の定期実行に貼る。台本の前段）
- `example_kikaku_quantum_antenna.md` — 企画書サンプル（どの常識破壊フレーム・審査項目で設計したかの解説）
- `example_script_quantum_antenna.txt` — 完成台本（編集スキルの練習素材と同じ）
- `example_heygen_script.txt` / `example_media_list.yaml`

## 日本語校正ゲート

```bash
# 台本フォルダごと検査（script.txt / heygen_script.txt / media_list.yaml）
python3 ~/.claude/skills/clbs-youtube-script-pro/scripts/qa_script.py videos/20260917_xxx/ --strict

# 指摘された文だけ Gemini 3.8 Flash に直させる（GEMINI_API_KEY が必要）
python3 ~/.claude/skills/clbs-youtube-script-pro/scripts/ja_style_fix.py videos/20260917_xxx/script.txt --strict
```

FAIL は禁止フレーズ・許可取り・AI記号・見出し行の残存・タグ番号不一致など「必ず直すもの」。WARN は和訳調の比率・演出比喩・AI造語など「目視で判断するもの」で、`--strict` を付けると和訳調 WARN も FAIL 扱いになります（納品前の基準）。詳しい引数は [`scripts/README.md`](scripts/README.md)。

## 他のAIを参加させる

| 工程 | 相手 | スクリプト | 必要なもの |
|---|---|---|---|
| 日本語本文の執筆・言い換え・校正修正 | Gemini 3.8 Flash | `scripts/gemini_chat.py` / `scripts/ja_style_fix.py` | `GEMINI_API_KEY`（[Google AI Studio](https://aistudio.google.com/)） |
| 企画の反論・論理の穴・一次資料の確認 | GPT（Codex CLI 経由） | `scripts/gpt_consult.py` | Codex CLI ＋ ChatGPT ログイン（API課金なし） |
| 市場の飽和度・X/Webのリアルタイム実測 | Grok（xAI API） | `scripts/grok_consult.py` | `XAI_API_KEY`（[console.x.ai](https://console.x.ai/)） |

セットアップ手順と役割分担の考え方は **[マルチAI台本制作ガイド（Web版）](https://claude.ai/artifact/91fDN2Wz7GRTk2r6XdVy7W)** にまとめています。同じ内容を [`docs/multi_ai_manual.html`](docs/multi_ai_manual.html)（ダウンロードしてブラウザで開く）と `references/multi_ai_collaboration.md`（要点版）にも同梱しています。

## パイプライン上の位置づけ

```
（任意）clbs-youtube-research（競合リサーチ）
   ↓ research_summary.yaml
clbs-youtube-script-pro（企画考案＋台本＋日本語校正）→ HeyGenで video.mp4 生成 → clbs-youtube-edit（編集）→ 完成動画
```

## 更新履歴

- **v2.0（2026-09-17）** 日本語校正ゲート（`scripts/qa_script.py`）・Gemini 修正パス（`scripts/ja_style_fix.py`）・日本語表現ルール（`references/japanese_style.md`）・GPT/Grok 相談スクリプト・他AI連携マニュアルを追加。承認ゲートを企画選択と構成承認の2箇所に整理。冒頭30秒を4点セットに更新。
- **v1.0（2026-06）** 初版（企画考案〜台本〜素材台帳）。

## ライセンス

[MIT](LICENSE)

## 関連

- 競合リサーチ（前段・任意）: [clbs-youtube-research](https://github.com/conlab-clbs/clbs-youtube-research)
- 編集（後段）: [clbs-youtube-edit](https://github.com/conlab-clbs/clbs-youtube-edit)
- 英語版台本: clbs-video-script-en
- ショート動画台本: clbs-video-script-short
