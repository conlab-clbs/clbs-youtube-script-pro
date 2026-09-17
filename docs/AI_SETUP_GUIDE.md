# AIエージェント向け セットアップ代行ガイド（clbs-youtube-script-pro v2）

この文書を読んでいるのは Claude Code / Codex などのAIエージェントである前提で書いている。
ユーザーは講座の受講生で、ターミナル操作に慣れていない。あなたの仕事は、ユーザーの環境に
このスキルと他AI連携（Gemini 3.8 Flash 必須、GPT / Grok 任意）をセットアップし、
ユーザーにしかできない操作だけを1回に1つずつ案内して完了させることである。

## 進め方の原則（必ず守る）

1. **自分でできることは全部自分で実行する。** git clone、ファイル作成、python の実行、`claude mcp add`、検証コマンドは自分で叩く。ユーザーに端末コマンドを打たせない。
2. **ユーザーにしかできない操作は3種類だけ。** (a) ブラウザでAPIキーを発行して設定ファイルに貼る (b) ブラウザでログインする（`codex login`）(c) アプリを完全再起動する。これ以外は自分でやる。
3. **1回に1つ。** ユーザーへの依頼は番号を付けて1つだけ出す。「何を・どこで・終わったら何と言うか」を必ず書く。ユーザーが「終わった」と言ったら、**自分の検証コマンドで確認してから**次の依頼を出す。確認できないうちは進まない。
4. **キーの値をチャットに貼らせない。** 自分がプレースホルダ入りの設定ファイルを作り、開き方を示し、ユーザーがそこにキーを貼って保存する。自分は `--list` で疎通だけ確認する。キーの値を読み上げたり表示したりしない。
5. **任意項目は先に「使うか」を1問で聞く。** GPT（ChatGPT有料プランが要る）と Grok（xAIのクレジット購入が要る）は任意。Gemini だけは必須。使わないと言われたら飛ばす。
6. **課金に関わる操作は自分でやらない。** クレジット購入・プラン契約はユーザーに委ねる。金額の目安は伝えてよい。
7. **エラーは自分で読んで直す。** ユーザーにログを読ませない。3回直して解決しなければ、症状と試したことを3行で報告して指示を仰ぐ。
8. **各ステップの終わりに進捗を1行で示す。** 形式:「✅ STEP n 完了 ／ 次: 〜」。全部終わったら最終表（下記）を出す。
9. **ユーザーへの文章は短く、専門語を避ける。** 「ターミナル」「環境変数」など言わないと進めない語は、初出でひと言説明する。

## STEP 0 環境判定（自分で）

次を自分で確認し、1行で報告する。ユーザーには何も頼まない。

- 自分は Claude Code か Codex か
- OS: macOS / Windows（WSL2 上か、ネイティブか）/ Linux
- `python3 --version`（3.11 以上が必要。Windows ネイティブは `python --version`）
- `git --version` の有無（無ければ ZIP 経路を使う）
- Claude Code なら `claude --version`、Codex なら `codex --version`

Python が 3.11 未満、または無い場合はここで止まり、ユーザーに python.org からのインストールを1つの依頼として案内する（macOS は `brew install python` を自分で実行してよい）。

## STEP 1 スキル配置（自分で）

```bash
# Claude Code
git clone https://github.com/conlab-clbs/clbs-youtube-script-pro.git ~/.claude/skills/clbs-youtube-script-pro
# Codex
git clone https://github.com/conlab-clbs/clbs-youtube-script-pro.git ~/.codex/skills/clbs-youtube-script-pro
```

- 既に同名フォルダがあれば `git pull`。git のクローンでなければ退避してから入れ直す。
- git が無い環境は `https://github.com/conlab-clbs/clbs-youtube-script-pro/archive/refs/heads/main.zip` を取得して展開し、`clbs-youtube-script-pro-main` の中身を配置先直下に移す。
- 検証: 配置先直下に `SKILL.md` と `scripts/qa_script.py` があること。`python3 <配置先>/scripts/qa_script.py <配置先>/references/example_script_quantum_antenna.txt` が `PASS` を返すこと。
- Claude Code は再起動しないとスキルが `/` 一覧に出ない。再起動の依頼は最後（STEP 5）にまとめて1回だけ出す。ここでは頼まない。

## STEP 2 Gemini 3.8 Flash（必須）

### 2-1 設定ファイルを自分で作る

```bash
mkdir -p ~/.config/clbs
cat > ~/.config/clbs/config.toml <<'EOF'
[gemini]
api_key = "ここにAIzaで始まるキーを貼る"

[xai]
api_key = ""
EOF
```

既にファイルがあれば上書きせず、`[gemini]` セクションが無いときだけ追記する。

### 2-2 ユーザーへの依頼（そのまま使ってよい）

> **お願い①（Geminiのキーを取る）**
> 1. ブラウザで https://aistudio.google.com/ を開き、Googleアカウントでログインします。
> 2. 左下の「Get API key」→「Create API key」を押します。`AIza` で始まる長い文字列が出るので、右側のコピーボタンでコピーします。
> 3. 私が用意した設定ファイルを開きます: （macOS）ターミナルに `open -e ~/.config/clbs/config.toml` と入力、（Windows）エクスプローラーのアドレス欄に `%USERPROFILE%\.config\clbs` と入力して `config.toml` をメモ帳で開く。
> 4. `ここにAIzaで始まるキーを貼る` の部分を、コピーしたキーに置き換えて保存します（両端の `"` は残す）。
> 5. 同じ画面の「Billing」（請求）で少額の前払いをしておくと、途中で止まりません。
> 終わったら「貼った」と言ってください。

macOS で `open -e` を使わせるとき、ターミナルの開き方（Spotlight で「ターミナル」）を添える。あるいは自分で `open -e ~/.config/clbs/config.toml` を実行してファイルを開いてあげてよい（そのほうが速い）。

### 2-3 検証（自分で）

```bash
python3 <配置先>/scripts/gemini_chat.py --list | grep -i "3.8"
python3 <配置先>/scripts/gemini_chat.py -p "「今日は天気がいいですね」を友達に話す口調で1文に。答えだけ"
python3 <配置先>/scripts/ja_style_fix.py <配置先>/references/example_script_quantum_antenna.txt --dry-run
```

- `gemini-3.8-flash` が一覧に出て、2つ目が日本語1文を返せば完了。
- `GEMINI_API_KEY が未設定` → ファイルの `"` の欠け、プレースホルダの消し忘れ、保存忘れを自分で確認する。ファイルの中身を表示するときはキーを `AIza****` に伏せる。
- `429 prepayment credits are depleted` → 前払い残高が0。Billing でのチャージを依頼②として出す。
- `403` / `API key not valid` → キーのコピー漏れ。貼り直しを依頼する。

## STEP 3 GPT（任意・ChatGPT 有料プランが必要）

まず1問:「ChatGPT の有料プラン（Plus / Pro など）を使っていますか？ 使っていれば GPT も相談相手に加えられます。使わない場合は飛ばします」。

使う場合:

1. `codex --version` を確認。無ければ macOS は `brew install --cask codex` を自分で実行（brew が無ければ npm: `npm install -g @openai/codex`）。Windows は WSL2 上で npm。
2. ユーザーへの依頼:
   > **お願い②（ChatGPTでログイン）**
   > 私がこれから `codex login` を実行するとブラウザが開きます。ChatGPT のアカウントでログインして、「許可」まで進めてください。終わったら「ログインした」と言ってください。
   `codex login` は自分で実行してよい（ブラウザが開く）。非対話環境で開かない場合は、表示されたURLをユーザーに渡す。
3. 検証: `codex login status` が `Logged in using ChatGPT`。
4. Claude Code の場合は MCP 登録を自分で実行: `claude mcp add -s user codex -- codex mcp-server` → `claude mcp list` に `codex … Connected`。
5. 疎通: `echo "1行で自己紹介して" | codex exec -s read-only --skip-git-repo-check -` が応答を返す。

## STEP 4 Grok（任意・xAI のクレジット購入が必要）

まず1問:「X（旧Twitter）の投稿をリアルタイムに調べる Grok も使いますか？ xAI のサイトで数ドルのクレジット購入が必要です。使わない場合は飛ばします」。

使う場合:

1. ユーザーへの依頼:
   > **お願い③（Grokのキーを取る）**
   > 1. https://console.x.ai/ を開き、X または Google でログインします。
   > 2. 「Billing」でクレジットを購入します（数ドルで十分です）。
   > 3. 「API Keys」→「Create API key」でキーを作り、コピーします。
   > 4. さっきの設定ファイル（`~/.config/clbs/config.toml`）の `[xai]` の下、`api_key = ""` の `""` の間に貼って保存します。
   > 終わったら「貼った」と言ってください。
2. 検証: `python3 <配置先>/scripts/grok_consult.py --list` がモデル名を返す。

## STEP 5 仕上げ

1. 役割分担をプロジェクトに書く（自分で）。ユーザーが台本を作るフォルダ（分からなければ `~/Desktop/youtube` を作って提案）に `CLAUDE.md`（Codex は `AGENTS.md`）を作り、次を書く:

   ```
   ## 台本制作の役割分担
   - 企画3案・構成・章ブリーフ・最終レビュー: このエージェント
   - 本文の執筆と校正修正: Gemini 3.8 Flash
     （<配置先>/scripts/gemini_chat.py, <配置先>/scripts/ja_style_fix.py）
   - 納品前に <配置先>/scripts/qa_script.py <project> --strict が PASS であること
   - （GPT/Grokを設定した場合）企画の反論は scripts/gpt_consult.py / scripts/grok_consult.py に振る。採否・タイトルはこのエージェントが決める
   ```
2. Claude Code の場合、最後の依頼:
   > **お願い④（アプリの再起動）**
   > Claude のアプリを Cmd+Q（Windows はタスクトレイのアイコンから終了）で完全に終了して、もう一度開いてください。開いたら、チャット欄に `/` と打って一覧に `clbs-youtube-script-pro` が出るか見てください。出たら「出た」と言ってください。
   Codex は再起動不要。新しいセッションで `/skills` に出ることを自分で案内する。
3. 最終表を出す:

   | 項目 | 状態 |
   |---|---|
   | スキル配置 | ✅ `~/.claude/skills/clbs-youtube-script-pro` |
   | Gemini 3.8 Flash | ✅ 接続OK |
   | GPT（Codex CLI） | ✅ 接続OK ／ ⏭ 未設定（理由） |
   | Grok（xAI） | ✅ 接続OK ／ ⏭ 未設定（理由） |
   | 役割分担ファイル | ✅ `<path>/CLAUDE.md` |

   最後に一言:「これで、『YouTube企画考えて』と話しかければスキルが動きます。本文は Gemini が書き、私が企画とレビューを持ちます」。

## よくあるエラーと自分で直す方法

| 症状 | 対処 |
|---|---|
| `python3: command not found`（Windows） | `python` / `py -3` で再試行。無ければ python.org のインストールを依頼 |
| `tomllib` が無い | Python 3.10 以下。3.11 以上を入れる |
| Gemini `404 model not found` | `--list` で名前を確認。`gemini-3.8-flash` が無ければ `gemini-flash-latest` を `-m` で指定 |
| Gemini `429 … depleted` | Billing でチャージを依頼 |
| `codex exec` が stdin 待ちで止まる | プロンプトを引数で渡している。末尾の `-` と標準入力で渡す |
| `claude mcp add` 後に一覧に出ない | セッション再起動（STEP 5 の依頼④にまとめる） |
| Grok `401` | キー貼り間違い。`[xai]` の下に貼ったか確認 |
| スキルが `/` に出ない | フォルダが入れ子（`…/clbs-youtube-script-pro/clbs-youtube-script-pro-main/SKILL.md`）になっていないか確認して自分で直す |

## 人間向けの全体像

役割分担の考え方、各AIの使いどころ、相談の回し方は `docs/multi_ai_manual.html`（同じ内容の Web 版: https://claude.ai/artifact/91fDN2Wz7GRTk2r6XdVy7W ）にある。セットアップが終わったら、ユーザーが読める場所としてこのリンクを1回だけ案内する。
