{pause up=part4-title}

{#part4-title}
# 4. tkhd と変換行列

## tkhd

`trak` > `tkhd`。トラック 1 本の「外側」を決める box です。
FullBox なので、payload は `version(1) + flags(3)` から始まります。

{pause scroll}
```text
$ xxd -s 24111 -l 96 00-original.mp4
00005e2f: 0000 005c 746b 6864 0000 0003 0000 0000  ...\tkhd........
00005e3f: 0000 0000 0000 0001 0000 0000 0000 1388  ................
00005e4f: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00005e5f: 0001 0000 0000 0000 0000 0000 0000 0000  ................
00005e6f: 0001 0000 0000 0000 0000 0000 0000 0000  ................
00005e7f: 4000 0000 0140 0000 00f0 0000 0000 0024  @....@.........$
```

{pause up}

## tkhd の中身

```text
+0   version(1) + flags(3)   00 00 00 03   ← enabled + in_movie
+4   creation_time     (4)
+8   modification_time (4)
+12  track_ID          (4)   00 00 00 01
+16  reserved          (4)
+20  duration          (4)   00 00 13 88   = 5000
+24  reserved          (8)
+32  layer             (2)   重ね順
+34  alternate_group   (2)
+36  volume            (2)
+38  reserved          (2)
+40  matrix           (36)   ★ ここ
+76  width             (4)   01 40 00 00   = 320.0
+80  height            (4)   00 f0 00 00   = 240.0
```

{.remark pause scroll}
> `width` の生の値は `0x01400000` = 20,971,520。でも表示は 320 です。
>
> **65536 で割ると 320.0** になります。固定小数点で入っているんですね。

{pause up}

## 固定小数点

{.definition title="16.16 形式"}
32 ビットのうち上位 16 ビットが整数部、下位 16 ビットが小数部。
値 = 生の整数 ÷ 65536。

{pause scroll}
```text
16.16 の 1.0  =  65536       =  0x00010000
16.16 の -1.0 =  -65536      =  0xFFFF0000   (2 の補数)
2.30  の 1.0  =  1073741824  =  0x40000000
```

{.remark pause scroll}
`0x40000000` は `0b01.000...0`。小数点の位置が違うだけです。
行列の中には、この 2 つの形式が混ざっています。

{pause up}

## matrix

`+40` から 36 バイト。4 バイト × 9 個です。
xxd の 1 行がちょうど 4 個ぶんなので、3 行に収まります。

{pause scroll}
```text
00005e5f: 0001 0000  0000 0000  0000 0000  0000 0000
          a = 1.0    b = 0      u = 0      c = 0
00005e6f: 0001 0000  0000 0000  0000 0000  0000 0000
          d = 1.0    v = 0      tx = 0     ty = 0
00005e7f: 4000 0000  0140 0000  00f0 0000
          w = 1.0    width      height
```

{pause scroll}
```math
\begin{bmatrix} a & b & u \\ c & d & v \\ t_x & t_y & w \end{bmatrix}
=
\begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{bmatrix}
```

{.block pause scroll}
**単位行列**、つまり「何もしない」が入っています。
では **180 度回転**させるには、どこをいくつにすればよいでしょう？

{pause up}

## 何を計算しているのか

この 9 個は、表示するときに座標をどう変換するかの指定です。

{pause scroll}
```math
\begin{bmatrix} x & y & 1 \end{bmatrix}
\times
\begin{bmatrix} a & b & u \\ c & d & v \\ t_x & t_y & w \end{bmatrix}
=
\begin{bmatrix} x' & y' & z' \end{bmatrix}
```

{pause scroll}
展開するとこうなります。

- $x' = a x + c y + t_x$
- $y' = b x + d y + t_y$
- $z' = u x + v y + w$

{pause scroll}
最終的な表示位置は $x'/z'$, $y'/z'$。普段は $u=v=0, w=1$ なので割り算は無視できます。

{pause up}

## 各要素の担当

{.definition}
> - $a\ b\ c\ d$ … 拡大縮小と回転
> - $t_x\ t_y$ … 平行移動
> - $u\ v\ w$ … 遠近法。動画では使わず $0, 0, 1$ 固定

{.remark pause scroll}
> 2 行 2 列だと拡大と回転しかできません。平行移動は掛け算では作れないからです。
>
> そこで座標に常に `1` をくっつけておくと、$t_x \times 1 = t_x$ として足し込めます（同次座標）。

{pause up}

## 回転行列

$\theta$ 回転は $a = \cos\theta,\ b = \sin\theta,\ c = -\sin\theta,\ d = \cos\theta$。

| 角度 | a | b | c | d |
| --- | --- | --- | --- | --- |
| 0° | 1 | 0 | 0 | 1 |
| 90° | 0 | 1 | -1 | 0 |
| 180° | -1 | 0 | 0 | -1 |

{pause scroll}
180° で計算すると $x' = -x$, $y' = -y$。原点を中心に点対称、つまり半回転です。

{.block pause scroll}
というわけで、さっきの問いの答えは **$a$ と $d$ を $-1.0$ にする**。
16.16 の $-1.0$ は `0xFFFF0000` なので、`0001 0000` が並んだ 2 箇所を書き換えます。

{pause up}

## 回転させる

```text
単位行列 (無変換):
00010000 00000000 00000000
00000000 00010000 00000000
00000000 00000000 40000000

180 度回転:
FFFF0000 00000000 00000000     ← a: +1.0 → -1.0
00000000 FFFF0000 00000000     ← d: +1.0 → -1.0
00000000 00000000 40000000
```

{pause scroll=demo2 play-media=demo2}

![](../demo/02-rotate.mp4){video #demo2 width=40%}

{pause scroll}
```text
$ cmp --verbose 00-original.mp4 02-rotate.mp4 | wc -l
4
```

{.remark pause scroll}
> `0001 0000` → `FFFF 0000` なので、変わるのは `a` と `d` で 2 バイトずつ、計 4 バイトです。
>
> `a` と `d` は 16 バイト離れているので、xxd では別々の行に出ます。冒頭の diff が 2 行だったのはこのためです。

{.remark pause scroll}
90 度ではなく 180 度にしたのは、90 度だと縦横の入れ替えが絡んでプレイヤーによって挙動が割れるからです。
180 度なら寸法が変わらないので、どのプレイヤーでも同じ結果になります。

{pause up}

## ffprobe で確認

```text
$ ffprobe -hide_banner 02-rotate.mp4 2>&1 | grep 'Display Matrix'
      Display Matrix: rotation of -180.00 degrees
```

{.remark pause scroll}
書き換えた行列が、ちゃんと回転として解釈されています。

{pause up}

## FFmpeg で答え合わせ

`-display_rotation` を付けて `-c copy` で通すと、映像には触れずに行列だけが書き直されます。
これを正解として、手で書き換えたものと突き合わせてみます。

{pause scroll}
```diff
$ ffmpeg -display_rotation 180 -i 00-original.mp4 -c copy ref.mp4
$ diff --unified=1 --label 02-rotate.mp4 --label ref.mp4 <(xxd 02-rotate.mp4) <(xxd ref.mp4)
--- 02-rotate.mp4
+++ ref.mp4
@@ -1536,3 +1536,3 @@
 00005ff0: 0000 0001 0000 0001 0000 0014 6274 7274  ............btrt
-00006000: 0000 0000 0000 959e 0000 0000 0000 0018  ................
+00006000: 0000 0000 0000 959e 0000 959e 0000 0018  ................
 00006010: 7374 7473 0000 0000 0000 0001 0000 0096  stts............
```

{.remark pause scroll}
> 違うのは `btrt`（bit rate。ビットレートの箱）の avgBitrate だけ。
> 再多重化のときに FFmpeg が埋めた値で、回転とは関係ありません。
>
> **回転については、手で書き換えたものと完全に一致しました。**

{pause up}

## ところで

さっき出てきた平行移動の $t_x$ と $t_y$ ですが、実際には**手元のどのプレイヤーでも効果がありませんでした**。

{slip .aside pause}
----
{.aside-label}
余談

## 平行移動はどこへ行った

$t_x$ と $t_y$ を書き換えても、画は 1 ピクセルも動きません。
ffmpeg もブラウザも、値を読んだうえで捨てています。

{pause scroll}
じゃあなぜ仕様にあるのか。祖先の QuickTime の仕様書に、用途が書いてありました。

{.definition title="QuickTime File Format Specification, Matrices" pause scroll}
"QuickTime files use matrices to describe spatial information about **many objects**,
such as tracks within a movie."

{pause scroll}
`tkhd` の他のフィールドにも、同じような意図が見えます:

- **layer** … "this track's **spatial priority** in its movie"。重ね順
- **alternate group** … 互いに代替となるトラックの組
- `matt`（matte）… トラックの画像をブレンドする box
- `clip` … クリッピング領域を指定する box

{.remark pause scroll}
字幕を右下に置く、小窓を重ねる、といった 2D 合成をやるつもりだったようです。
そうなると、各トラックを「どこに」置くかを決める必要があります。

{pause up}

## QuickTime では使われていた

同じ仕様書に、平行移動を使う機能が 2 つ載っています。

{.definition title="スプライト" pause scroll}
"By modifying a sprite's matrix, you can modify the sprite's location so that it
appears to **move in a smooth path on the screen**." そして
"**Translation-only matrices provide the best performance.**"

{.definition title="モディファイア トラック" pause scroll}
行列をサンプルとして持つトラックが、別のトラックへ毎フレーム行列を送る仕組み。
"This data can be sent to a video track to cause it to **move and resize as it plays**."

{.remark pause up}
画面の中を動き回る映像、という使い方が実際にあったわけです。

{pause up}

## なぜ回転だけ残ったのか

いま流通している MP4 は、だいたい映像 1 本と音声 1 本。
映像は画面いっぱいに表示されるので、どこに置くかを決める必要がありません。

{pause scroll}
一方でスマートフォンが縦でも横でも撮れるようになり、**回転だけ**は必要になりました。
センサーの向きは固定なので、撮影時の向きを行列で伝えるわけです。

{.block title="FFmpeg の実装" pause scroll}
`av_display_rotation_get` が読むのは配列の 0, 1, 3, 4 番目、つまり $a\ b\ c\ d$ だけ。
対になる `av_display_rotation_set` は、残る $u\ v\ t_x\ t_y$ を 0 で潰し、$w$ にだけ 1.0 を書きます。
そもそも平行移動を書く手段がありません。

{.block title="出典" pause up}
> - Apple, *QuickTime File Format Specification*（2001-03-01 版, 無償）
>   Matrices / Track header atom / Sprite properties / Modifier tracks の各項
> - FFmpeg `libavutil/display.c` の `av_display_rotation_get` / `av_display_rotation_set`
>   <https://ffmpeg.org/doxygen/trunk/display_8c_source.html>
> - 「動かない」のは実装上の都合。仕様側に「無視してよい」とは書かれていない

----

{step}

{pause up}

## もう一つ、効かないもの

`tkhd` の flags を書き換えて、トラックを無効にしてみます。

```text
tkhd は FullBox。その先頭 flags(3) の下位ビット:
0x0001  track enabled      このトラックを再生するか
0x0002  track in movie     本編で使うか
0x0004  track in preview   プレビューで使うか
0x0008  track in poster    ポスターで使うか
```

{.remark pause scroll}
preview は「3〜5 秒の短い紹介」、poster は「代表の 1 コマ」。今はまず使われません。

{pause scroll}
```text
変更前:  00 00 00 03      ← enabled + in movie
変更後:  00 00 00 02      ← enabled を落とす
```

{.remark pause scroll}
`mp4dump` は `enabled = 0` と読みますが、**ffmpeg も Chrome も無視して再生しました**。
さっきの平行移動と同じで、仕様にあっても実装が見ていなければ効きません。
