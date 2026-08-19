{pause up=part3-title}

{#part3-title}
# 3. グルーピング

属性は 1 つのブロックにしか付けられない。複数ブロックをまとめて 1 つの要素にするには、
「グループ」を作る必要がある。方法は 2 つ。

{pause up}

## `>` によるグルーピング

Commonmark の引用と同じ記号だが、slipshow では意味が違う（1 章参照）。

{pause scroll}
```markdown
{.card style=padding:1em}
> 複数の段落を
>
> 1 つのグループにまとめる
```

{pause scroll}
{.card style=padding:1em}
> 複数の段落を
>
> 1 つのグループにまとめる

{pause up}

## `---` によるグルーピング

区切り線でグループを分ける方式。`---` の**ダッシュの本数が多い方が優先**される。

{pause scroll}
```markdown
A

---

B

----

C
```

上の例は `(A, B)` を 1 グループ、`C` をもう 1 グループにする。4 本ダッシュの `----` の方が
2 グループを分ける優先度が高いため。

{pause up}

## ダッシュに属性を付ける

区切り線自体に属性を付けると、直後にできるグループに付く。

{pause scroll}
```markdown
A

{#labelled style=color:teal}
---

B
```

{pause scroll}
A

{#labelled style=color:teal}
---

B

{pause up}

## 組み合わせ

`>` と `---` は混在できる。深いネストを `>` の入れ子にすると読みにくいので、
外側は `---`、内側だけ `>` にするなどの使い分けができる
（このリポジトリの `about-mp4/` は逆に、章ごとファイルを分けることで `>` の深いネストを避けている。
`CLAUDE.md` の「このリポジトリについて」参照）。
