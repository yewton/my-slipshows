{#part1-title}
# 1. 記法の基本

slipshow の記法は Markdown に近いが、いくつか重要な差がある。まずは素の記法から。

{pause up}

## 見出し・強調・リンク・thematic break

{pause scroll}
```markdown
# Title 1
## Subtitle
**bold**、*italic*、***both***
[text](link target)

___
```

{pause scroll}
# Title 1
## Subtitle

**bold**、*italic*、***both***

[slipshow のドキュメント](https://slipshow.readthedocs.io)

___

{.remark pause scroll}
`#` が多いほど小さくなる。thematic break（区切り線）は `___` `***` `<hr>` のいずれか。

{pause up}

## リスト（tight と loose）

{pause scroll}
```markdown
- 詰まったリスト
- 項目間に空行なし

- 間延びしたリスト

- 項目間に空行あり
```

{pause scroll}
- 詰まったリスト
- 項目間に空行なし

{pause scroll}
- 間延びしたリスト

- 項目間に空行あり

{.remark pause scroll}
項目間が近すぎると感じたら空行を入れる。「loose」になり、段落として広がる。

{pause up}

## 表とコード

{pause scroll}
```markdown
| foo | bar |
| --- | --- |
| baz | bim |

`inline code` と、言語付きコードブロック：

```ocaml
let salut = "hello"
```
```

{pause scroll}
| foo | bar |
| --- | --- |
| baz | bim |

`inline code` の例。以下はハイライトされる OCaml コード：

```ocaml
let salut = "hello"
```

{pause up}

## メディアは拡張子で振り分けられる

`![alt](path)` は拡張子から画像・SVG・動画・音声・PDF・HTML・`.draw`（描画リプレイ）を
自動判別する。`{video}` `{audio}` `{image}` `{svg}` を付けると判別を上書きできる。

{pause scroll}
```markdown
![](assets/sample.mp4){video muted controls width=40%}
```

{pause scroll}
![](../assets/sample.mp4){video muted controls width=40%}

{pause up}

## Markdown との差

{.block title="引用 (>) の意味が違う" pause scroll}
slipshow では `>` は引用ではなく「グルーピング」（3 章）に使う。引用が欲しいときは
`{blockquote}` 属性を使う。

{pause scroll}
```markdown
> これは引用にならない

{blockquote}
> Cogito Ergo Sum
```

{pause scroll}
> これは引用にならない

{blockquote}
> Cogito Ergo Sum

{.block title="Setext 見出し不可" pause scroll}
```
Title
=====
```
という書き方（アンダーラインで見出しを作る記法）は使えない。`#` の ATX 見出しのみ。

{pause up}
