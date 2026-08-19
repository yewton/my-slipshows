{pause up=part2-title}

{#part2-title}
# 2. 属性

`{...}` で囲んだ部分が属性。すべての動的な振る舞い（ステップ・スタイル・ID）はここに書く。

{pause up}

## 4 種類

{pause scroll}
```markdown
{#example .definition title="Hello there" focus}
```

{pause scroll}
- `#example` — **識別子**。要素内で一意。
- `.definition` — **クラス**。複数付けられ、要素間で共有できる。
- `title="Hello there"` — **key=value 属性**。スペースを含めるには引用符が要る。
- `focus` — **フラグ属性**。値を持たない。

{pause up}

## ブロック属性とインライン属性

ブロック（段落・見出し・リストなど）とインライン（太字・リンクなど文の一部）で、
属性の付け方が違う。

{.block title="ブロックに付ける" pause scroll}
直前の（空行を挟まない）行に置く：

```markdown
{style="background:lightyellow"}
段落全体に属性が付く。
```

{style="background:lightyellow"}
段落全体に属性が付く。

{.block title="インラインに付ける" pause scroll}
触れている要素の直後に置く。`[...]` でまとめて囲むこともできる：

```markdown
一部の**単語**{style="color:red"}にだけ属性が付く。

[複数の**単語**をまとめる]{style="color:red"}こともできる。
```

一部の**単語**{style="color:red"}にだけ属性が付く。

[複数の**単語**をまとめる]{style="color:red"}こともできる。

{pause up}

## 参照属性

同じ属性を何度も書くのはつらいので、footnote 風に外出しできる。

{pause scroll}
```markdown
[text][A] [with][A] [many][A] [words][A].

[A]: {style="color:#5b8def; font-weight:bold"}
```

{pause scroll}
[text][A] [with][A] [many][A] [words][A].

[A]: {style="color:#5b8def; font-weight:bold"}

{pause up}

## 画像の落とし穴：ブロックかインラインか

画像は「インライン要素だが、段落の唯一の中身であることが多い」ため、属性をブロックに
付けるかインラインに付けるかで意味が変わる。中央寄せは**親ブロック**の性質、幅は
**画像自身**の性質。

{pause scroll}
```markdown
{style="text-align:center"}
![](assets/sample.mp4){video width=40%}
```

{pause scroll}
{style="text-align:center"}
![](../assets/sample.mp4){video width=40%}

{.remark pause scroll}
`text-align` を画像側に付けても効かない（画像はインラインなので、揃えるべき対象が無い）。
`width` を段落側に付けても効かない（段落は画像を包む箱でしかない）。

{pause up}

## 単独属性（standalone）

属性だけの行を、空行で前後から切り離すと「空の要素」に付く。特定の要素に紐付けずに
アクションだけを流し込むときに使う（4 章のステップで多用する）。

{pause scroll}
```markdown
Some text

{style="color:gray"}

Some other text
```
