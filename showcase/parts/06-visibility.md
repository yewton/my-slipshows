{pause up=part6-title}

{#part6-title}
# 6. 可視性

`pause` は「隠して、後で出す」の定型だが、可視性そのものを直接操作するアクションもある。

{pause up}

## reveal / unreveal

`.unrevealed` クラスを付けた要素は `opacity: 0` から始まる。`reveal` / `unreveal` で
直接切り替えられる。`pause` はこの仕組みの上に構築された糖衣構文にすぎない。

{pause scroll}
```markdown
{#hidden .unrevealed}
最初は透明。

{reveal=hidden}

{unreveal=hidden}
```

{pause scroll}
{#hidden .unrevealed}
最初は透明。

{pause reveal=hidden}

{pause unreveal=hidden}

{pause up}

## static / unstatic

`position` と `visibility` を切り替える。`unstatic` は `position:absolute; visibility:hidden`
になり、レイアウトから外れる（場所を空けたまま消える `unreveal` と違い、詰める）。

{pause scroll}
```markdown
{static}   position:static; visibility:visible に戻す
{unstatic} position:absolute; visibility:hidden にする
```

{pause up}

## emph / unemph

上流の `actions-api.rst` には載っていないが、`src/actions-arguments/actions_arguments.ml` と
`slip` API（カスタムスクリプト用、11 章）に実在する。要素を強調する（既定テーマでは背景色）。

{pause scroll}
```markdown
{#target}
強調前。

{emph=target}

{unemph=target}
```

{pause scroll}
{#target}
強調前。

{pause emph=target}

{pause unemph=target}

{pause up}
