{pause up=part6-title}

{#part6-title}
# 6. stco と絶対オフセット

{.definition title="stco（Chunk Offset Box）" pause scroll}
各チャンクが**ファイル先頭から何バイト目にあるか**を、絶対値で並べた表。
「何バイト後ろ」ではなく「何バイト目」であることが、この章の全部です。

{pause scroll}
```text
$ mp4dump --verbosity 2 sample.mp4
          [stco] size=12+8
            entry_count = 1
            entries:
              (       0) 48        ← ファイル先頭から 48 バイト目
```

{.remark pause scroll}
実物では 1 エントリしかありません。長い動画ならチャンクの数だけ並びます。
どれもファイル先頭を基準にした絶対値です。

{pause up}

## 絶対値だから、前を動かせない

さきほど壊したファイルがこれでした。`free` box を 8 バイト挿しただけで、
`stco` は 48 のまま、実際のデータは 56 バイト目へ動きました。

{.block pause scroll}
表を書き換えていないのに、表の指す先が嘘になる。
**前に何かを足すと、後ろの全エントリを書き直さなければならない。**

{.remark pause scroll}
5 章の書き換えを 4 つとも「同じサイズのまま」で通したのは、このためです。
1 バイトでも増えれば、索引の作り直しが要ります。

{pause up}

## 48 バイト目には、何があったのか

デコーダは `stco` を信じて 48 バイト目を読みました。そこにあったものを見ます。

{pause scroll}
```diff
$ diff -U1 <(xxd -l 64 sample.mp4) <(xxd -l 64 broken.mp4)
--- sample.mp4
+++ broken.mp4
@@ -2,3 +2,3 @@
 00000010: 6973 6f6d 6973 6f32 6176 6331 6d70 3431  isomiso2avc1mp41
-00000020: 0000 0008 6672 6565 0000 5d8b 6d64 6174  ....free..].mdat
-00000030: 0000 02ae 0605 ffff aadc 45e9 bde6 d948  ..........E....H
+00000020: 0000 0008 6672 6565 0000 0008 6672 6565  ....free....free
+00000030: 0000 5d8b 6d64 6174 0000 02ae 0605 ffff  ..].mdat........
```

{.remark pause scroll}
48 バイト目（`0x30`）にあるのは `0000 5d8b`。**`mdat` の size フィールド**です。
本来そこにあるはずだった `0000 02ae` は、8 バイト後ろへ逃げました。

{pause up}

## 長さだと思って読まれる

2 章で見たとおり、`mdat` は「長さ + データ」の繰り返しです。

{.definition title="NAL unit — Network Abstraction Layer unit" pause scroll}
H.264 は、圧縮そのものを受け持つ層（**VCL**）と、それを器に載せるための包み（**NAL**）に
分けて設計されています。同じ映像データが MP4 でも RTP でも運べるのは、この分離があるからです。
1 章で「触らない」と言った中身は VCL の側で、NAL は器との境目にあります。

{.remark pause scroll}
器が違えば区切り方も違います。生の H.264 は `00 00 01` というスタートコードを探して切れ目を見つけますが、
**MP4 は長さを前に置きます**。`stsz` が「1 個目のサンプルは 3,902 バイト」と言い、
その中を長さで辿ると 690 + 3,212 の NAL 2 つに割れる。**階層ごとに位置が分かる形**です。

{.remark pause scroll}
長さフィールドの幅は `avcC`（`stsd` の中にある、H.264 の設定を書いた箱）の
`lengthSizeMinusOne` が決めます。このファイルでは 4 バイトです。

{pause scroll}
```text
正しい先頭:  0000 02ae | 06 05 ff ff ...
             ↑ 686     ↑ 1 個目の NAL（686 バイト）

壊れた先頭:  0000 5d8b | 6d 64 61 74 ...
             ↑ 23947   ↑ "mdat" の 4 文字を中身だと思って読む
```

{.block pause scroll}
```text
$ ffmpeg -i broken.mp4 -f null -
[h264] Invalid NAL unit size (23947 > 3898).
```
エラーの **23947 は `mdat` の size** そのものです。

{.remark pause scroll}
索引が 8 バイトずれただけで、デコーダは箱のヘッダをフレームの長さとして読みました。
`free` は「読み飛ばしてよい箱」なのに、**読み飛ばす主体が箱の外にいた**わけです。

{pause up}

## だから faststart がある

エンコードが終わるまで索引は確定しないので、`moov` はファイル末尾に置かれることがよくあります。
ところがストリーミングでは、**再生を始める前に索引が要ります**。
末尾にあると、全部落とすまで再生が始まりません。

{pause scroll}
そこで `moov` を先頭へ移す操作が用意されています。

{.definition title="-movflags" pause scroll}
ffmpeg の MP4 出力（mov / mp4 / ismv マルチプレクサ）に渡す、書き出し方の指定です。
`+faststart` はその 1 つ。公式ドキュメントの説明は
"Run a second pass **moving the index (moov atom) to the beginning of the file**"。

{pause up}

## 実際に動かしてみる

```text
$ ffmpeg -i sample.mp4 -c copy plain.mp4
$ ffmpeg -i sample.mp4 -c copy -movflags +faststart fast.mp4
$ boxes() { mp4dump "$1" | grep -o '^\[....\]'; }   # 最上位の箱だけ並べる
```

{pause scroll}
```diff
$ diff -U2 <(boxes plain.mp4) <(boxes fast.mp4)
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
**箱の順番が入れ替わっただけ**に見えます。

{pause up}

## ただでは済んでいない

```text
             stco の 1 つ目のエントリ
plain.mp4              48
fast.mp4             2667      ← 2,619 バイトぶん後ろへ
```

{pause scroll}
2,619 は `moov` の大きさ（8 + 2,611）そのものです。
前に割り込んだ分だけ、`mdat` の中身が丸ごと後ろへ動きました。

{.remark pause scroll}
だから `stco` の全エントリが書き直されます。ドキュメントに "**second pass**" と書いてあるのはこのため。
**ファイルを丸ごと読み直す処理**です。

{.block pause scroll}
長い動画ならエントリは何千と並びます。
「箱を前に持ってくる」だけの操作が重いのは、絶対オフセットの表があるからです。

{pause up}

## だから fragmented MP4 がある

{.block title="索引を分割する"}
1 つの大きな `moov` を持つ代わりに、`moof`（movie fragment）+ `mdat` のペアを並べる形式です。
各フラグメントが自分の索引を持ち、位置は `moof` からの**相対**で書かれます。

{.remark pause scroll}
絶対オフセットの表がなくなるので、後ろに足せます。
ライブ配信も DASH も HLS も、この構造があって成り立っています。

{.block pause scroll}
普段使っている配信技術は、**「絶対オフセットの表を持ってしまった」という制約への回答**です。
実際の box 構造は Appendix A で見ます。

{.block title="fragmented MP4 を無償で読むには" pause up}
> 定義そのものは ISO/IEC 14496-12（有償）にありますが、構造の要件は
> 配信側の規格が無償で書いています。
>
> - W3C, *ISO BMFF Byte Stream Format*（Group Note, 2024）— <https://www.w3.org/TR/mse-byte-stream-format-isobmff/>
>   初期化セグメントは `ftyp` + `moov`（`mvex` 必須）、メディアセグメントは `moof` + `mdat`
> - RFC 8216 §3.3 *Fragmented MPEG-4* — <https://www.rfc-editor.org/rfc/rfc8216#section-3.3>
> - MP4RA — `moof` = "movie fragment", `traf` = "track fragment", `trun` = "track fragment run"
