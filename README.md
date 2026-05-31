# clbs-video-script-pro

顔出しAIアバター動画（HeyGen等／VSL・ウェビナー・YouTube本編）の**企画考案から台本執筆まで**を一気通貫で行う [Claude Code](https://claude.com/claude-code) スキルです。

YouTubeアルゴリズム（検索型/ブラウジング型・CTR・視聴維持率）に沿って企画を考え抜き、会話調・yesセット・AI構文禁止のCLBS文体で台本化。そのまま編集スキル **[clbs-youtube-edit](https://github.com/conlab-clbs/clbs-youtube-edit)** に渡せる `script.txt` / `heygen_script.txt` / `media_list.yaml` を出力します。

---

## 特徴

- **YouTubeアルゴリズムに沿った企画考案** — 常識破壊8フレーム＋バズ10軸・心理トリガーで「精鋭3案」を考え抜き、企画審査5項目でセルフ採点（5中4未満は作り直し）。台本の上手さより**企画の強さ**を最優先。
- **冒頭30秒フック設計** — 衝撃結論／天国と地獄／希少性・権威性を明示的に構成し、視聴維持率の急落を防ぐ。
- **そのまま編集に流せる** — 出力した台本＋素材台帳は `clbs-youtube-edit` が無改変で読み込み、Premiere XML と完成MP4を生成。
- **無発音の演出タグ** — `[見出し：◯◯] / [スライドN] / [ピクチャーN] / [BロールN] / [カムリターン]` をアバターに読ませない前提で配置。
- **HeyGen沈黙マーカー** — 文末・タグ直後に `<break time="0.8s" />` を付与。編集側がこの沈黙を切ってテンポを生む。
- **CLBS文体の徹底** — yesセット・話し言葉・AI構文禁止（「結論から言います」等を排除）。
- **Bロール尺の安全設計** — 「1文＝1Bロール／セリフ尺 < 生成動画尺」を徹底し、尺不足で静止画化する事故を防ぐ。

## 出力ファイル

| ファイル | 内容 |
|---|---|
| `script.txt` | 演出タグ＋`<break>` を全て含む完成台本（編集スキルの正データ） |
| `heygen_script.txt` | `[…]`タグを除去し `<break>` のみ残した版（HeyGen貼り付け用） |
| `media_list.yaml` | 素材台帳（headings / brolls / pictures / slides / thumbnail） |

## 台本タグ仕様

| タグ | 用途 | 発音 |
|---|---|---|
| `[見出し：◯◯]` | 左上見出しバー（次の見出しまで継続・スライド/Bロール中は非表示） | しない |
| `[スライドN]` | スライド全画面＋右上ワイプ | しない |
| `[ピクチャーN]` | 左に画像ポップアップ | しない |
| `[BロールN]` | Bロール全画面（声のみ継続） | しない |
| `[カムリターン]` | 素材を終了しアバターに戻す | しない |
| `<break time="0.8s" />` | 沈黙ポーズ（編集のジェットカット点） | 沈黙 |

## 使い方

Claude Code でこのスキルを入れた状態で「YouTube企画考えて」「企画から台本作って」「YouTube台本書いて」などと話しかけると起動します。7フェーズを承認ゲート付きで進めます。

```
0 ヒアリング（業種・ターゲットの悩み・伝えたいノウハウ・CTA・戦略タイプ）
1 軽量リサーチ（任意・WebSearchで競合の勝ち型と空き枠を抽出）
2 ジャンル適性チェック（視聴者パイは十分広いか）
3 企画考案：精鋭3案＋企画審査5項目セルフ採点   ← 本丸
4 構成案＋冒頭30秒フック設計
5 台本執筆（パートごと承認）
6 素材台帳出力（script.txt / heygen_script.txt / media_list.yaml）
```

`references/` に教材一式があります：
- `example_kikaku_quantum_antenna.md` — **企画書サンプル**（どの常識破壊フレーム・審査項目で設計したかの解説）
- `example_script_quantum_antenna.txt` — 完成台本（編集スキルの練習素材と同じ）
- `example_heygen_script.txt` / `example_media_list.yaml`

## 企画考案の中身（自己完結・外部資料不要）

SKILL.md に次のリファレンスを内蔵しているので、このスキル単体で企画を考え抜けます：
常識破壊8フレーム／バズ10軸・心理トリガー早見表／企画審査5項目／ジャンル適性3チェック／冒頭30秒フック構成／専門用語→日常語の変換／検索型・ブラウジング型の戦略早見表。

本格的な競合リサーチ（異常値分析・バズ方程式モデリング）が必要なときは、前段スキル `clbs-yt-research` の `04_research_summary.yaml` を渡せます。

## パイプライン上の位置づけ

```
（任意）clbs-yt-research（競合リサーチ）
   ↓ research_summary.yaml
clbs-video-script-pro（企画考案＋台本）→ HeyGenで video.mp4 生成 → clbs-youtube-edit（編集）→ 完成動画
```

## ライセンス

[MIT](LICENSE)

## 関連

- 競合リサーチ（前段・任意）: [clbs-youtube-research](https://github.com/conlab-clbs/clbs-youtube-research)
- 編集（後段）: [clbs-youtube-edit](https://github.com/conlab-clbs/clbs-youtube-edit)
- 英語版台本: clbs-video-script-en
- ショート動画台本: clbs-video-script-short
