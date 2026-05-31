# clbs-video-script-pro

顔出しAIアバター動画（HeyGen等／VSL・ウェビナー・YouTube本編）用の**日本語台本を執筆する** [Claude Code](https://claude.com/claude-code) スキルです。

会話調・yesセット・AI構文禁止のCLBS文体で台本を書き、無発音の演出タグと HeyGen形式の沈黙マーカーを配置。そのまま編集スキル **[clbs-youtube-edit](https://github.com/conlab-clbs/clbs-youtube-edit)** に渡せる `script.txt` / `heygen_script.txt` / `media_list.yaml` を出力します。

---

## 特徴

- **そのまま編集に流せる** — 出力した台本＋素材台帳は `clbs-youtube-edit` が無改変で読み込み、Premiere XML と完成MP4を生成。
- **無発音の演出タグ** — `[見出し：◯◯] / [スライドN] / [ピクチャーN] / [BロールN] / [カムリターン]` をアバターに読ませない前提で配置。
- **HeyGen沈黙マーカー** — 文末・タグ直後に `<break time="0.8s" />` を付与。編集側がこの沈黙を切ってテンポを生む。
- **見出しタグ生成** — 各セクション冒頭に左上バー用の短い看板コピーを自動配置。
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

Claude Code でこのスキルを入れた状態で「YouTube台本書いて」「顔出し動画の台本作って」などと話しかけると起動します。

1. **ヒアリング** — テーマ／ターゲットの悩み／伝えたいノウハウ／CTA／トーン
2. **構成案** — OP→共感→解決策→本題（見出し3〜4）→まとめ（承認ゲート）
3. **本文執筆** — パートごとにタグ配置（承認ゲート）
4. **出力** — `script.txt` → `heygen_script.txt` → `media_list.yaml`

`references/` に完成サンプル一式があります（`example_script_quantum_antenna.txt` / `example_heygen_script.txt` / `example_media_list.yaml`）。これは編集スキル [clbs-youtube-edit](https://github.com/conlab-clbs/clbs-youtube-edit) の練習素材と同じ台本です。

## パイプライン上の位置づけ

```
clbs-video-script-pro（台本）→ HeyGenで video.mp4 生成 → clbs-youtube-edit（編集）→ 完成動画
```

## ライセンス

[MIT](LICENSE)

## 関連

- 編集（後段）: [clbs-youtube-edit](https://github.com/conlab-clbs/clbs-youtube-edit)
- 英語版台本: clbs-video-script-en
- ショート動画台本: clbs-video-script-short
