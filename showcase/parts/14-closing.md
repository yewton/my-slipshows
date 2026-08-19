{pause up}

## このリポジトリで新しいデッキを作るには

{pause scroll}
```text
<デッキ名>/
  main.md          入口。frontmatter はここだけに書く
  style.css        デッキ固有の CSS（無ければ省略可）
  parts/NN-<slug>.md   2 桁ゼロ埋め + ハイフン区切りの章ファイル
  <素材ディレクトリ>/   画像・動画など
```

{pause scroll}
```markdown
---
dimension: 16:9
theme: default
css: ../_shared/ja.css ../_shared/layout.css style.css
highlightjs-theme: github-dark
---
```

{.remark pause scroll}
`_shared/` の 2 本を先に、デッキ固有の `style.css` を後に置く。列挙の順序がそのまま
上書きの優先順位になるので、共通スタイルをデッキ側で部分的に上書きしたいときに効いてくる。

{pause up}

## 参考文献

{.block title="上流ドキュメント（v0.11.0 固定）"}
> - 構文の基本 — <https://github.com/panglesd/slipshow/blob/v0.11.0/docs/slipshow-syntax.rst>
> - 属性 — <https://github.com/panglesd/slipshow/blob/v0.11.0/docs/attributes-ref.rst>
> - アクション一覧 — <https://github.com/panglesd/slipshow/blob/v0.11.0/docs/actions-api.rst>
> - 特殊要素（箱・slip・carousel・include） — <https://github.com/panglesd/slipshow/blob/v0.11.0/docs/special-elements.rst>
> - グルーピング — <https://github.com/panglesd/slipshow/blob/v0.11.0/docs/grouping.rst>
> - frontmatter — <https://github.com/panglesd/slipshow/blob/v0.11.0/docs/frontmatter.rst>
> - テーマ — <https://github.com/panglesd/slipshow/blob/v0.11.0/docs/themes.rst>
> - 発表機能（スピーカービュー・録画・ショートカット） — <https://github.com/panglesd/slipshow/tree/v0.11.0/docs>

{pause up}

{.deck-title}
# おわり
