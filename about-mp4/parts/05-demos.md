{pause up=part5-title}

{#part5-title}
# 5. 書き換えデモ

## 4 バイトで倍速にする

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
$ xxd -s 24247 -l 32 sample.mp4
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
`duration` は 76800 のまま動かしません。目盛りの刻みだけを倍にしたので、
76800 ÷ 15360 = **5 秒**だった動画が 76800 ÷ 30720 = **2.5 秒**になります。
同じデータを倍の速さで読んでいるだけです。

{pause up=video-speed-demo play-media=video-speed-demo}

![](../demo/01-speed.mp4){video #video-speed-demo width=30%}

{.remark pause scroll}
カウンタが倍速で回ります。これが冒頭のタネの片方です。

{pause up}

## 8 バイトで回転させる

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

{pause scroll}
書き換えるのは **2 箇所、計 8 バイト**だけです。

{pause scroll=demo2 play-media=demo2}

![](../demo/02-rotate.mp4){video #demo2 width=40%}

{.remark pause scroll}
フィールドとしては 8 バイトですが、`0001 0000` → `FFFF 0000` なので
実際に値が変わるのは 4 バイトです。`a` と `d` は 16 バイト離れているため、
xxd では別々の行に現れます。冒頭の diff が 2 行に分かれて見えたのはそのためです。

{.remark pause scroll}
180 度を選んだ理由：90 度は表示ボックスの縦横スワップが絡むのでプレイヤーによって
挙動が割れます。180 度は寸法が変わらないので、どのプレイヤーでも同じ結果になります。

{pause up}

## ffprobe で検算する

```text
$ ffprobe -hide_banner sample-rotated.mp4
  Stream #0:0: Video: h264 (High), yuv420p, 320x240, 30 fps
    Side data:
      Display Matrix: rotation of -180.00 degrees
```

{.block title="因果が一直線に見える" pause scroll}
バイトを書き換えた → ライブラリが行列を角度として解釈した → 画が回った

{pause up}

## 答え合わせ：FFmpeg に同じものを作らせる

`-display_rotation` を付けて `-c copy` で通すと、映像には触れずに行列だけが書き直されます。
これを正解として、手で書いた 4 バイトと突き合わせます。

{pause scroll}
```diff
$ ffmpeg -display_rotation 180 -i sample.mp4 -c copy ref.mp4
$ diff -U1 --label sample.mp4 --label ref.mp4 <(xxd sample.mp4) <(xxd ref.mp4)
--- sample.mp4
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
上の塊は 3 行に散らばって見えますが、変わったのは `0001` → `ffff` が 2 箇所、計 4 バイト。
`a` も `d` も 16 バイト区切りの行境界を跨いでいるので、3 行に見えているだけです。
位置も値も、手で書き換えたところと一致します。

{.remark pause scroll}
下の塊は `btrt`（ビットレートの箱）の avgBitrate です。
再多重化のときに FFmpeg が、0 のままだった欄を埋めました。回転とは関係ありません。

{pause scroll}
```diff
$ diff -U1 --label sample-rotated.mp4 --label ref.mp4 <(xxd sample-rotated.mp4) <(xxd ref.mp4)
--- sample-rotated.mp4
+++ ref.mp4
@@ -1536,3 +1536,3 @@
 00005ff0: 0000 0001 0000 0001 0000 0014 6274 7274  ............btrt
-00006000: 0000 0000 0000 959e 0000 0000 0000 0018  ................
+00006000: 0000 0000 0000 959e 0000 959e 0000 0018  ................
 00006010: 7374 7473 0000 0000 0000 0001 0000 0096  stts............
```

{.remark pause scroll}
手で書き換えたファイルと FFmpeg 版の差は、その avgBitrate の 2 バイトだけ。
**回転に関する限り、両者は 1 バイトも違いません。**

{pause up}

{#other-ops pause up=other-ops}
## 残り 3 つは、まとめて

書き換える場所と、その結果だけを並べます。ひとつずつ見ていきます。

{.columns-3 pause scroll}
> {slip .card #op-track}
> ----
> ### 1 ビットでトラックを無効にする
>
> ```text
> tkhd は FullBox。その先頭 flags(3) の下位ビット:
> 0x0001  track enabled      このトラックを再生するか
> 0x0002  track in movie     本編で使うか
> 0x0004  track in preview   プレビューで使うか
> 0x0008  track in poster    ポスターで使うか
> ```
>
> {.remark pause scroll}
> preview は「3〜5 秒の短い紹介」、poster は「代表の 1 コマ」。今はまず使われません。
>
> {pause scroll}
> ```text
> 変更前:  00 00 00 03      ← enabled + in movie
> 変更後:  00 00 00 02      ← enabled を落とす
> ```
>
> {.remark pause scroll}
> `mp4dump` は `enabled = 0` と読みますが、**ffmpeg も Chrome も無視して再生しました**。
> 4 章の平行移動と同じで、仕様にあっても実装が見なければ効きません。
>
>
>
> {slip .card #op-meta}
> ----
> ### 4 文字でメタデータを消す
>
> `udta`（メタデータ置き場）の **type 4 文字だけ**を書き換えます。
>
> ```text
> $ xxd -s 26508 -l 16 sample.mp4
> 0000678c: 0000 0062 7564 7461 0000 005a 6d65 7461  ...budta...Zmeta
>
> 変更前:  00 00 00 62 75 64 74 61     size=98, type='udta'
> 変更後:  00 00 00 62 66 72 65 65     size=98, type='free'
> ```
>
> {.definition title="free box" pause scroll}
> 「ここは読み飛ばしてよい」という意味の box。パディング用。
>
> {pause scroll}
> サイズは 1 バイトも変わっていないのに、メタデータが消えます。
>
> {.remark pause scroll}
> これが、**メタデータを安全に削除する定石**です。中身を詰め直す必要がありません。
>
>
>
> {slip .card #op-break}
> ----
> ### サイズを変えて壊す
>
> ここまでは全部**同じサイズ**の書き換えでした。ではサイズを変えるとどうなるか。
>
> {pause scroll}
> 今度は box のルールに**一切違反しません**。
> 中身のない `free` box を 1 つ、`mdat` の直前に挿し込むだけです。
>
> ```text
> $ head -c 40 sample.mp4          > broken.mp4
> $ printf '\x00\x00\x00\x08free' >> broken.mp4
> $ tail -c +41 sample.mp4        >> broken.mp4
> ```
>
> {pause scroll}
> box として完全に正しく、パーサーは何も文句を言いません。
>
> ```text
> $ mp4dump broken.mp4
> [ftyp] size=8+24
> [free] size=8+0
> [free] size=8+0        ← 挿し込んだ box
> [mdat] size=8+23939
> [moov] size=8+2611
> ```
>
> {pause up=demo5}
> ![](../demo/05-broken.mp4){video controls #demo5 width=38%}
>
> {pause scroll}
> それでも再生できません。「読み飛ばしてよい」箱を足しただけなのに。
>
> {pause scroll}
> ```text
> $ ffmpeg -i broken.mp4 -f null -
> [h264] Invalid NAL unit size (23947 > 3898).
> ```
>
> {.remark pause scroll}
> `23947` は `mdat` の size です。8 バイト手前を読んだデコーダが、
> `mdat` のヘッダを「次のフレームの長さ」として解釈しました。
> 犯人は次の章で挙げます。
>
>
