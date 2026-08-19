{pause up=part8-title}

{#part8-title}
# 8. slip と subslip

`slip` 属性を付けた要素は、幅固定・高さ無制限のコンテナになる。プレゼン全体も実は
1 つの slip。slip の中にさらに slip を置くと「subslip」になり、そこへ潜っていける。

{pause up}

## slip と slide の違い

{pause scroll}
```markdown
{slip}
高さは無制限。up / down / scroll でスクロールする。

{slide}
高さも固定される。
```

`slide` は「slip の亜種で、高さも固定したもの」。一連のスライド構成にしたい場合は
13 章の `attributes: { children:slide ... }` を使う方法もある。

{pause up}

## `slip` は自動的に `enter` する

`slip` 属性を付けると、暗黙に `enter` アクションも付く（`no-enter` で止められる）。
**enter/exit はステップを消費しない** — 次に見つかったアクションと同じステップで実行される。

{pause scroll}
```markdown
{slip #demo-subslip}
> 潜った先の内容。
>
> {step}
```

末尾の `{step}` は「何もしないアクション」で、これがあることで、subslip から抜ける
`exit` だけを独立した 1 ステップとして見せられる（無いと、次の見出しへ進む pause と
同じステップで exit してしまい、ズームアウトが見えないまま次の内容が出る）。

{pause up}

## ズーム倍率は親に対する幅で決まる

subslip の拡大率は「本編の中でその subslip が占める幅」の逆数で決まる。親と同じ幅なら
1 倍（潜った感じがしない）。`_shared/layout.css` の `.aside` は幅 40% にしてあるので
約 2.5 倍になる。

{pause scroll}
```markdown
{slip .aside pause}
> {.aside-label}
> 寄り道
>
> 幅 40% の subslip。入ると約 2.5 倍にズームする。
>
> {step}
```

{slip .aside pause}
> {.aside-label}
> 寄り道
>
> 幅 40% の subslip。入ると約 2.5 倍にズームする。
>
> {step}

{pause up}

## 3 カラムに並べて 1 つずつ潜る

`.columns-3` + `.card`（`_shared/layout.css`、元は `about-mp4/` の `.op`）の組み合わせ。

{pause scroll}
```markdown
{.columns-3 pause scroll}
> {slip .card}
> ----
> ### 1 つ目
>
> 中身。
>
> {slip .card}
> ----
> ### 2 つ目
>
> 中身。
>
> {slip .card}
> ----
> ### 3 つ目
>
> 中身。
```

{.columns-3 pause scroll}
> {slip .card}
> ----
> ### 1 つ目
>
> 潜った先の内容 A。
>
> {step}
>
>
>
> {slip .card}
> ----
> ### 2 つ目
>
> 潜った先の内容 B。
>
> {step}
>
>
>
> {slip .card}
> ----
> ### 3 つ目
>
> 潜った先の内容 C。
>
> {step}
