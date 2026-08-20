{pause up=part4-title}

{#part4-title}
# 4. ステップ

**1 ステップ = DOM 上で次に見つかるアクション属性 1 つ**。これが slipshow のステップ機構の
全部（エンジン本体 `src/engine/runtime/step/action_scheduler.ml` の `next` で確認済み）。

{pause up}

## pause

初期状態で「その先」を隠し、実行されると表示する。属性の乗った要素自身から後が対象になる。

{pause scroll}
```markdown
A

{pause}

B
```

{pause scroll}
A

{pause}

B

{.remark pause scroll}
`{pause up=x}` のように書くと、内部では `pause` と `up-at-unpause`（unpause の瞬間に発火する
`up`）という 2 つの属性に分解される（`src/actions-arguments/actions_arguments.ml` 参照）。
1 つのステップで両方が起きるように見えるのはこのため。

{pause up}

## pause-block

`pause` は既定でブロックの外まで巻き込んで隠す。`pause-block` を付けた祖先の内側だけに
影響を閉じ込められる。

{pause scroll}
```markdown
A

{pause-block}
> B
>
> {pause}
>
> C
>
> {pause}
>
> D

E
```

{pause scroll}
> A
>
> {pause-block}
> > B
> >
> > {pause}
> >
> > C
> >
> > {pause}
> >
> > D
>
> E

{.remark pause scroll}
E は `pause-block` の外なので、B・C・D の pause に関係なく最初から見えている。

{pause up}

## step — 何もしないアクション

`step` は画面を変えずに 1 ステップだけ消費する「空アクション」。8 章で見る通り、
subslip から抜ける（`exit`）タイミングを独立させたいときに使う。

{pause scroll}
```markdown
{step}
```

{pause up}

## 1 つの属性に複数アクション

同じ属性の中に複数のアクションを書くと、同じステップで一斉に実行される。

{pause scroll}
```markdown
{#one}
段落 1。

{#two .unrevealed}
段落 2（最初は隠れている）。

{center=one reveal=two}
```

{pause scroll}
{#one}
段落 1。

{#two .unrevealed}
段落 2（最初は隠れている）。

{center=one reveal=two}

{.remark pause scroll}
`center` と `reveal` が同時に発火した。ステップ数を節約したいときに使う。
