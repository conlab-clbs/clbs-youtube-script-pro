#!/usr/bin/env python3
"""受講生専用の「毎日リサーチ」スキルを生成する（標準ライブラリのみ）。

AIエージェントがヒアリング結果を引数で渡すと、
  <配置先>/<slug>-daily-research/SKILL.md      … Claude Code / Codex 用スキル
  <配置先>/<slug>-daily-research/research_prompt.md … Cowork のスケジュールタスクに貼る単体プロンプト
の2つを assets/daily_research_skill_template.md から作る。

使い方（例）:
  python3 scripts/make_research_skill.py \
    --channel "50代の転職チャンネル" --slug tenshoku \
    --genre "50代の転職・副業・年金" \
    --target "50〜60代の会社員。定年後の収入と働き方に不安" \
    --style search \
    --themes "早期退職の落とし穴,50代からの副業,年金の繰り下げ,再雇用の実態,資格より人脈" \
    --kw-en "midlife career change 2026,retirement income Japan 2026" \
    --kw-ja "50代 転職 最新 2026,定年後 働き方 調査 2026,年金 改正 2026" \
    --sources "厚生労働省,日経,リクルートワークス研究所,東洋経済" \
    --cta "動画末尾 → LINE登録 → 個別相談" \
    --hashtags "#50代転職 #定年後 #副業" \
    --out-dir ~/Desktop/youtube/research \
    [--skills-dir ~/.claude/skills | --codex]
"""
import argparse, os, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "daily_research_skill_template.md"

STYLE_TEXT = {
    "search": ("検索型（悩み解決・資産型）", "検索されている悩みに正面から答える。タイトルに検索語を入れ、網羅性と回答精度で勝つ。"),
    "browse": ("ブラウジング型（おすすめ表示・常識破壊・驚き）", "タイトルだけで「え？」「なぜ？」と止まる力が必要。強いフック（「〜はウソだった」「〜の正体」「あなたの〜が変わる」）とコメント誘発を意識する。"),
    "both": ("検索型とブラウジング型の両方", "検索語を含みつつ、常識破壊のフックを1つ乗せる。"),
}


def csv(s):
    return [x.strip() for x in re.split(r"[,、，]", s or "") if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", required=True); ap.add_argument("--slug", required=True, help="英小文字とハイフン")
    ap.add_argument("--genre", required=True); ap.add_argument("--target", required=True)
    ap.add_argument("--style", choices=list(STYLE_TEXT), default="search")
    ap.add_argument("--themes", required=True, help="キーテーマ（カンマ区切り・3〜6個）")
    ap.add_argument("--kw-en", default="", help="英語検索語（カンマ区切り）"); ap.add_argument("--kw-ja", required=True, help="日本語検索語（カンマ区切り）")
    ap.add_argument("--sources", default="公的機関・学会・大手メディア・一次発表")
    ap.add_argument("--cta", default="動画末尾の案内 → LINE登録"); ap.add_argument("--hashtags", default="")
    ap.add_argument("--out-dir", required=True, help="レポートの保存先フォルダ")
    ap.add_argument("--skills-dir", default=None, help="スキルの配置先（既定 ~/.claude/skills）")
    ap.add_argument("--codex", action="store_true", help="~/.codex/skills に配置")
    ap.add_argument("--force", action="store_true", help="既存のスキルを上書き")
    a = ap.parse_args()

    slug = re.sub(r"[^a-z0-9-]", "-", a.slug.lower()).strip("-")
    if not slug:
        sys.exit("--slug は英小文字とハイフンで指定してください")
    slug_full = f"{slug}-daily-research"
    skills_dir = pathlib.Path(a.skills_dir or ("~/.codex/skills" if a.codex else "~/.claude/skills")).expanduser()
    dest = skills_dir / slug_full
    if dest.exists() and not a.force:
        sys.exit(f"既にあります: {dest}（上書きするなら --force）")
    themes = csv(a.themes); kw_en = csv(a.kw_en); kw_ja = csv(a.kw_ja)
    if not themes or not kw_ja:
        sys.exit("--themes と --kw-ja は1つ以上必要です")
    out_dir = str(pathlib.Path(a.out_dir).expanduser())
    style_label, style_note = STYLE_TEXT[a.style]

    tpl = TEMPLATE.read_text(encoding="utf-8")
    rep = {
        "{{SLUG}}": slug_full, "{{CHANNEL}}": a.channel, "{{GENRE}}": a.genre, "{{TARGET}}": a.target,
        "{{STYLE}}": style_label, "{{STYLE_NOTE}}": style_note, "{{OUT_DIR}}": out_dir,
        "{{THEMES_LIST}}": "\n".join(f"  {i+1}. {t}" for i, t in enumerate(themes)),
        "{{KW_EN_LIST}}": "\n".join(f"- `{k}`" for k in kw_en) if kw_en else "- （英語の一次情報が無いジャンルなら省略可）",
        "{{KW_JA_LIST}}": "\n".join(f"- `{k}`" for k in kw_ja),
        "{{KW_JA_MAIN}}": kw_ja[0].split()[0] if kw_ja else a.genre,
        "{{SOURCES}}": a.sources, "{{CTA}}": a.cta,
        "{{HASHTAGS}}": a.hashtags or "ジャンルの定番タグ",
    }
    body = tpl
    for k, v in rep.items():
        body = body.replace(k, v)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "SKILL.md").write_text(body, encoding="utf-8")

    # Cowork / claude -p 用の単体プロンプト（frontmatter を外し、パスをそのまま残す）
    prompt = re.sub(r"^---.*?---\n", "", body, count=1, flags=re.S)
    prompt = "以下の手順を最後まで実行し、指定の保存先にレポートを保存してください。\n\n" + prompt
    (dest / "research_prompt.md").write_text(prompt, encoding="utf-8")
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)

    print(f"作成: {dest / 'SKILL.md'}")
    print(f"作成: {dest / 'research_prompt.md'}（Cowork のスケジュールタスク用）")
    print(f"保存先フォルダ: {out_dir}")
    print(f"起動: チャットで「今日のリサーチ」または /{slug_full}")


if __name__ == "__main__":
    main()
