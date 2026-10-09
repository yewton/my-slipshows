{pause up=part5-title}

{#part5-title}
# 5. 書き換えデモ

## 倍速にする

`mdia` > `mdhd` の中の **timescale**。「1 秒を何目盛りに刻むか」の値です。

{pause scroll}
```text
mdhd の構造（version = 0 の場合）

+0   version(1) + flags(3)
+4   creation_time      (4)
+8   modification_time  (4)
+12  timescale          (4)   ★ ここ
+16  duration           (4)
```

{pause scroll}
```text
$ xxd -s 24247 -l 32 00-original.mp4
00005eb7: 0000 0020 6d64 6864 0000 0000 0000 0000  ... mdhd........
00005ec7: 0000 0000 0000 3c00 0001 2c00 55c4 0000  ......<...,.U...
                    ^^^^^^^^^ ^^^^^^^^^
                    timescale duration
```

{pause scroll}
```text
変更前:  00 00 3c 00     (15360)     1 秒 = 15360 目盛り
変更後:  00 00 78 00     (30720)     1 秒 = 30720 目盛り
```

{.remark pause scroll}
> `duration` は 76800 のまま。目盛りの刻みだけを倍にしたので、
> 76800 ÷ 15360 = **5 秒**だった動画が 76800 ÷ 30720 = **2.5 秒**になります。
>
> 同じデータを倍の速さで読んでいるだけですね。

{pause up=video-speed-demo play-media=video-speed-demo}

![](../demo/01-speed.mp4){video #video-speed-demo width=30%}

{pause scroll}
```text
$ cmp --verbose 00-original.mp4 01-speed.mp4 | wc -l
1
```

{.remark pause scroll}
> フィールドは 4 バイトですが、実際に変わったのは 1 バイトだけ。
>
> 冒頭の動画の速さも、ここを書き換えて直していました。

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
$ diff --unified=1 --label 00-original.mp4 --label ref.mp4 <(xxd 00-original.mp4) <(xxd ref.mp4)
--- 00-original.mp4
+++ ref.mp4
@@ -1509,5 +1509,5 @@
 00005e40: 0000 0000 0000 0100 0000 0000 0013 8800  ................
-00005e50: 0000 0000 0000 0000 0000 0000 0000 0000  ................
-00005e60: 0100 0000 0000 0000 0000 0000 0000 0000  ................
-00005e70: 0100 0000 0000 0000 0000 0000 0000 0040  ...............@
+00005e50: 0000 0000 0000 0000 0000 0000 0000 00ff  ................
+00005e60: ff00 0000 0000 0000 0000 0000 0000 00ff  ................
+00005e70: ff00 0000 0000 0000 0000 0000 0000 0040  ...............@
 00005e80: 0000 0001 4000 0000 f000 0000 0000 2465  ....@.........$e
@@ -1536,3 +1536,3 @@
 00005ff0: 0000 0001 0000 0001 0000 0014 6274 7274  ............btrt
-00006000: 0000 0000 0000 959e 0000 0000 0000 0018  ................
+00006000: 0000 0000 0000 959e 0000 959e 0000 0018  ................
 00006010: 7374 7473 0000 0000 0000 0001 0000 0096  stts............
```

{.remark pause scroll}
> 上の hunk は 3 行にまたがっていますが、変わったのは `0001` → `ffff` が 2 箇所、計 4 バイト。
> ここでは `a` と `d` が行の境目をまたいでいるので、3 行に見えています。
>
> 下の hunk は `btrt`（ビットレートの箱）の avgBitrate です。
> 再多重化のときに FFmpeg が埋めたもので、回転とは関係ありません。

{pause scroll}
```diff
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
手で書き換えたものとの差は、この avgBitrate だけ。**回転については完全に一致しました。**

{pause up}

{#other-ops pause up=other-ops}
## 他にもできること

{.columns-3 pause scroll}
-----
{slip .card #op-track}
----
### トラックを無効にする

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
平行移動と同じで、仕様にあっても実装が見ていなければ効きません。



{slip .card #op-meta}
----
### メタデータを消す

`udta`（メタデータ置き場）の **type 4 文字だけ**を書き換えます。

```text
$ xxd -s 26508 -l 16 00-original.mp4
0000678c: 0000 0062 7564 7461 0000 005a 6d65 7461  ...budta...Zmeta

変更前:  00 00 00 62 75 64 74 61     size=98, type='udta'
変更後:  00 00 00 62 66 72 65 65     size=98, type='free'
```

{pause scroll}
`free` は読み飛ばされる箱なので、サイズを変えずにメタデータが消えます。



{slip .card #op-break}
----
### サイズを変えて壊す

ここまでは全部**同じサイズ**のままの書き換えでした。ではサイズを変えるとどうなるか。

{pause scroll}
中身のない `free` box を 1 つ、`mdat` の直前に挿し込んでみます。
box のルールには何も違反していません。

```text
$ head --bytes=40 00-original.mp4           > 05-broken.mp4
$ printf '\x00\x00\x00\x08free'            >> 05-broken.mp4
$ tail --bytes=+41 00-original.mp4         >> 05-broken.mp4
```

{pause scroll}
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
`23947` は `mdat` の size です。デコーダは 8 バイト手前を読んでしまい、
`mdat` のヘッダを「次のフレームの長さ」だと思い込みました。なぜでしょう？

-----
