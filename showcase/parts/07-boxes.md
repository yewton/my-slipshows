{pause up=part7-title}

{#part7-title}
# 7. 箱（block 系）

テーマ（default）が用意している注釈ボックス。クラスを付けるだけで使える。
ラベルは組み込みテーマでは英語だが、`_shared/ja.css` が和訳している
（`.definition:before` などの `content` を上書き。詳しくは `_shared/ja.css` 自身のコメント参照）。

{pause up}

## 一覧

{pause scroll}
```markdown
{.block title="任意のタイトル"}
規則性のない、汎用の箱。

{.definition title="コーデック"}
用語の定義。

{.theorem title="Fundamental theorem of definition"}
主張。

{.lemma}
補助的な主張。

{.corollary}
定理から直ちに従うもの。

{.example}
具体例。

{.remark}
補足。

{.proof}
> 証明の中身。
```

{pause scroll}
{.block title="任意のタイトル"}
規則性のない、汎用の箱。

{.definition title="コーデック"}
映像や音声そのものをどう圧縮するかを決めた規格。

{.theorem title="Fundamental theorem of definition"}
定義は面白い。

{.lemma}
補助的な主張。

{.corollary}
定理から直ちに従うもの。

{.example}
具体例。

{.remark}
補足。

{.proof}
> 仮に面白くないとする。
>
> すると証明を持たないことになる。

{.remark pause scroll}
`title` の有無でラベルの組み立て方が変わる（`title` 付きは「ラベル（タイトル）」の形）。
`_shared/ja.css` は両方のセレクタを上書きしている。
