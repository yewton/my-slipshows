{pause up=part6-title}

{#part6-title}
# 6. stco と絶対オフセット

## サイズを変えて壊す

ここまでは全部**同じサイズ**のままの書き換えでした。ではサイズを変えるとどうなるか。

{pause scroll}
中身のない `free` box を 1 つ、`mdat` の直前に挿し込んでみます。
box のルールには何も違反していません。

```text
$ head --bytes=40 00-original.mp4           > 05-broken.mp4
$ printf '\x00\x00\x00\x08free'            >> 05-broken.mp4
$ tail --bytes=+41 00-original.mp4         >> 05-broken.mp4
```

{pause up}
box としては正しいので、パーサーは何も文句を言いません。

```text
$ mp4dump 05-broken.mp4
[ftyp] size=8+24
[free] size=8+0
[free] size=8+0        ← 挿し込んだ box
[mdat] size=8+23939
[moov] size=8+2611
```

{pause up=demo5}
![](../demo/05-broken.mp4){video controls #demo5 width=38%}

{pause scroll}
でも再生できません。読み飛ばされるはずの箱を足しただけなのに。

{pause scroll}
```text
$ ffmpeg -i 05-broken.mp4 -f null -
[h264 @ 0x...] Invalid NAL unit size (23947 > 3898).
```

{.remark pause scroll}
エラーに出ている `23947` という数字、どこかで見覚えがありませんか？
（NAL unit は H.264 のデータの単位です。中身は Appendix A で扱うので、ここでは数字の方に注目してください）

{pause up}

## stco

{.definition title="stco（Chunk Offset Box）" pause scroll}
各チャンクが**ファイル先頭から何バイト目にあるか**を、絶対値で並べた表。
「何バイト後ろ」ではなく「何バイト目」なのがポイントです。

{pause scroll}
```text
$ mp4dump --verbosity 2 00-original.mp4
          [stco] size=12+8
            entry_count = 1
            entries:
              (       0) 48        ← ファイル先頭から 48 バイト目
```

{.remark pause scroll}
このファイルでは 1 エントリだけですが、長い動画ならチャンクの数だけ並びます。

{pause up}

## 前に足すとずれる

壊したファイルでは、`free` box を 8 バイト追加しただけで、
`stco` は 48 のまま、実際のデータは 56 バイト目へ動いていました。

{.block pause scroll}
表を書き換えていないのに、表の指す先がずれてしまう。
**前に何かを足したら、後ろを指すエントリを全部書き直さないといけない。**

{.remark pause scroll}
ここまでの書き換えを全部「同じサイズのまま」にしていたのは、このためです。

{pause up}

## 48 バイト目には何があったか

デコーダは `stco` を信じて 48 バイト目を読みました。そこにあったものを見てみます。

{pause scroll}
```diff
$ diff --unified=1 --label 00-original.mp4 --label 05-broken.mp4 <(xxd -l 64 00-original.mp4) <(xxd -l 64 05-broken.mp4)
--- 00-original.mp4
+++ 05-broken.mp4
@@ -2,3 +2,3 @@
 00000010: 6973 6f6d 6973 6f32 6176 6331 6d70 3431  isomiso2avc1mp41
-00000020: 0000 0008 6672 6565 0000 5d8b 6d64 6174  ....free..].mdat
-00000030: 0000 02ae 0605 ffff aadc 45e9 bde6 d948  ..........E....H
+00000020: 0000 0008 6672 6565 0000 0008 6672 6565  ....free....free
+00000030: 0000 5d8b 6d64 6174 0000 02ae 0605 ffff  ..].mdat........
```

{.remark pause scroll}
> 48 バイト目（`0x30`）にあるのは `0000 5d8b`。**`mdat` の size フィールド**です。
>
> 本来の映像データの先頭（`0000 02ae 0605 ...`）は、8 バイト後ろへずれています。

{.block pause scroll}
エラーの **23947 は `mdat` の size** そのもの。
箱のヘッダを、映像データの一部だと思って読んでしまったわけです。

{.remark pause scroll}
`free` はパーサーにとっては読み飛ばせる箱ですが、
`stco` はそんなことお構いなしに、絶対位置でデータを指していたんですね。

{pause up}

## mdat の前に置きたいもの

壊れる理由は分かりました。では `mdat` より前には何も足さなければいいかというと、
実は**前に置きたいもの**がよくあります。代表が `moov` そのものです。

{pause scroll}
エンコードが終わるまで索引は確定しないので、`moov` はファイル末尾に置かれることがよくあります。
今日のファイルも `ftyp`, `free`, `mdat`, `moov` の順で、`moov` は最後でした。

{pause scroll}
ところがストリーミングでは、**再生を始める前に索引が要ります**。
末尾にあると、全部ダウンロードするまで再生が始まりません。

{.block pause scroll}
`moov` を `mdat` の前へ移したい。でも移せば `mdat` の位置がずれるので、`stco` の書き直しが要ります。
さっき壊したのと同じ状況です。

{pause up}

## faststart

`moov` の移動を、`stco` の書き直しまで込みでやってくれるのが ffmpeg の faststart です。

{.definition title="-movflags" pause scroll}
ffmpeg の MP4 出力（mov / mp4 / ismv マルチプレクサ）に渡す、書き出し方の指定です。
`+faststart` はその 1 つ。公式ドキュメントの説明は
"Run a second pass **moving the index (moov atom) to the beginning of the file**"。

{pause up}

## 試してみる

```text
$ ffmpeg -i 00-original.mp4 -c copy plain.mp4
$ ffmpeg -i 00-original.mp4 -c copy -movflags +faststart fast.mp4
$ boxes() { mp4dump "$1" | grep -o '^\[....\]'; }   # 最上位の箱だけ並べる
```

{pause scroll}
```diff
$ diff --unified=2 --label plain.mp4 --label fast.mp4 <(boxes plain.mp4) <(boxes fast.mp4)
--- plain.mp4
+++ fast.mp4
@@ -1,4 +1,4 @@
 [ftyp]
+[moov]
 [free]
 [mdat]
-[moov]
```

{.block pause scroll}
`moov` が末尾から `mdat` の前へ来ました。ファイルサイズは両方とも 26,606 バイトのまま。
箱の順番が入れ替わっただけ…に見えます。

{pause up}

## stco はどうなった？

```text
             stco の 1 つ目のエントリ
plain.mp4              48
fast.mp4             2667      ← 2,619 バイトぶん後ろへ
```

{pause scroll}
2,619 は `moov` の大きさ（8 + 2,611）そのものです。
前に割り込んだ分だけ、`mdat` の中身が丸ごと後ろへ動いています。

{.remark pause scroll}
> なので `stco` の全エントリを書き直す必要があります。
> ドキュメントに "**second pass**" と書いてあるのはこのためです。

{.block pause scroll}
長い動画ならエントリは何千と並びます。
「箱を前に持ってくる」だけなのに手間がかかるのは、絶対オフセットの表があるからなんですね。

{pause up}

## fragmented MP4

{.block title="索引を分割する"}
1 つの大きな `moov` を持つ代わりに、`moof`（movie fragment）+ `mdat` のペアを並べる形式です。
各フラグメントが自分の索引を持ち、位置は `moof` からの**相対**で書かれます。

{.remark pause scroll}
> 絶対オフセットの表がなくなるので、後ろにどんどん足していけます。
>
> ライブ配信や DASH、HLS で使われているのがこの形式です。

{.remark pause scroll}
実際の box 構造は Appendix B で見ます。

{.block title="fragmented MP4 を無償で読むには" pause up}
> 定義そのものは ISO/IEC 14496-12（有償）にありますが、構造の要件は
> 配信側の規格が無償で書いています。
>
> - W3C, *ISO BMFF Byte Stream Format*（Group Note, 2024）— <https://www.w3.org/TR/mse-byte-stream-format-isobmff/>
>   初期化セグメントは `ftyp` + `moov`（`mvex` = movie extends 必須）、メディアセグメントは `moof` + `mdat`
> - RFC 8216 §3.3 *Fragmented MPEG-4* — <https://www.rfc-editor.org/rfc/rfc8216#section-3.3>
> - MP4RA — `moof` = "movie fragment", `traf` = "Track fragment", `trun` = "track fragment run"
