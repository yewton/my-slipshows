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

## はみ出しへの対応

要素が 1 画面に収まらないまま次のステップへ進むと、下が読めないまま置き去りになる。
コンパイルは通り warning も出ないので、気付きにくい。

{pause scroll}
```markdown
{.remark pause scroll}
長い補足。収まらないときだけスクロールする。

{up=video-id}       前の要素を押し出してから次へ進む
```

{.remark pause scroll}
原因は (a) 前の節の動画が押し出されずに残り、後続が積み上がって画面下へ追い出される (b) 長い表や
コードブロックがそもそも 1 画面に収まらない、の 2 つ。対処は、要素の直前行（空行なし）に
`{.remark pause scroll}` の形で `scroll` を付ける、先に `up=<id>` で前の要素を押し出す、長い表は
分割する。`{pause}` だけではスクロールしない。

{.remark pause scroll}
`scroll` で送る実演。この箱は、直前に見たソース例と注の下へそのまま積むと画面を越える高さにしてある。
直前行の `scroll` が、収まらないときだけスクロールして箱の下まで見せている。長い表、長いコードブロック、
丁寧に書いた注など、1 画面に収まらない要素の定番の対処。押し出したい要素（前の節の動画など）には
`up=<id>` を使う。`scroll` は「今すでに全部見えていれば動かさない」ので、動画を残したまま次を出す場合は
`up` と使い分ける。

{.remark pause scroll}
見つけ方：ステップを送りながら可視要素の座標を実測すると機械的に洗い出せる。スクロールは
アニメーションするので `.slip-body` の位置が安定するまで待つこと。`#slipshow-universe` や
`#slipshow-content` はスクロール用のコンテナで画面より大きいのが正常なので、判定から外す。
pause 中の要素は親要素に `opacity: 0` が付き、子要素自身の `opacity` は 1 のまま残る。要素自身の
opacity だけを見ると、隠れている要素を「画面外へはみ出した可視要素」と誤判定する（この原因で
4 件の誤検出を出した）。可視判定は祖先を辿って行う。
