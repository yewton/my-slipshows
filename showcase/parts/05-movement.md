{pause up=part5-title}

{#part5-title}
# 5. 画面移動

いずれも「対象の要素が画面のどこに来るように動かすか」を指定するアクション。
`~duration:FLOAT`（秒）と `~margin:INT`（px）を引数に取れる。

{pause up}

## up / down / center / scroll

{pause scroll}
```markdown
{#target}
この段落を動かす。

{up=target}       目標を画面の最上部へ
{down=target}     目標を画面の最下部へ
{center=target}   目標を画面の中央へ
{scroll=target}   目標が画面に収まるように（up/down/center と違い「今すでに全部見えていれば動かさない」）
```

{.remark pause scroll}
`about-mp4/` の実測では、**`up` は対象を最上部へ送るので、その上にあった要素を押し出す**。
動画を見せたまま次を出すなら `scroll`、動画の下に本文を置きたいなら先に `up` で動画自体を
上げておく、という使い分けが要る（`CLAUDE.md` の「slipshow のハマりどころ」参照）。

{pause up}

## focus / unfocus — ズーム

`focus` は要素にズームインする。`center` 等と違い、拡大率も変わる。`unfocus` で直前の
focus 前の位置へ戻る。

{pause scroll}
```markdown
{#zoom-target style="display:inline-block; padding:0.6em 1em; border:2px solid #5b8def"}
ここへズームする

{focus=zoom-target}

{unfocus}
```

{pause scroll}
{#zoom-target style="display:inline-block; padding:0.6em 1em; border:2px solid #5b8def"}
ここへズームする

{pause focus=zoom-target}

{pause unfocus}

{.remark pause scroll}
`~duration:0` を指定すると瞬間移動になる。`frontmatter` の `toplevel-attributes` の既定値
（`slip enter="~duration:0"`）はこれを使って、最初の enter を一瞬で終わらせている。

{pause up}
