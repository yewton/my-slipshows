---
dimension: 16:9
theme: default
css: ../_shared/ja.css ../_shared/layout.css
highlightjs-theme: github-dark
---

![](demo/intro-upside-slow.mp4){video autoplay muted loop #video-before width=35%}

{.credit}
*Big Buck Bunny* © 2008 Blender Foundation, CC BY 3.0（[peach.blender.org](https://peach.blender.org)）

{pause scroll}
## 突然ですが

この動画、上下が反転していて、しかも間延びしています。
向きを直して、再生速度を倍にしたい。どうしますか。

{pause up}

## 素直にやるなら、再エンコード

```text
$ ffmpeg -i in.mp4 -vf "hflip,vflip,setpts=0.5*PTS" -r 24 out.mp4
```

{.compare pause scroll}
> ![](demo/intro-upside-slow.mp4){video autoplay muted loop #cmp-before width=100%}
>
> ![](demo/intro-reencoded.mp4){video autoplay muted loop #cmp-reenc width=100%}

{.compare .caps}
> 変換前　**50,911** バイト
>
> 変換後　**68,163** バイト

{pause scroll}
```text
$ cmp -l before.mp4 after.mp4 | wc -l
49965
```

{.remark pause scroll}
確かに直りました。ただし映像を全部デコードして、H.264 で圧縮し直しています。
50,911 バイト中 **49,965 バイト**が変わりました。**中身は別のファイルです。**

{pause up}

## 実は、バイナリエディタで直せます

{.compare pause scroll}
> ![](demo/intro-upside-slow.mp4){video autoplay muted loop #cmp-fixed-before width=100%}
>
> ![](demo/intro-original.mp4){video autoplay muted loop #cmp-fixed-after width=100%}

{.compare .caps}
> 修正前　**50,911** バイト
>
> 修正後　**50,911** バイト

{pause scroll}
```text
$ cmp -l before.mp4 after.mp4 | wc -l
5
```

{#intro-diff pause scroll}
```diff
$ diff -U1 --label before.mp4 --label after.mp4 <(xxd before.mp4) <(xxd after.mp4)
--- before.mp4
+++ after.mp4
@@ -3053,4 +3053,4 @@
 0000bec0: 0000 0000 0000 1388 0000 0000 0000 0000  ................
-0000bed0: 0000 0000 0000 0000 ffff 0000 0000 0000  ................
-0000bee0: 0000 0000 0000 0000 ffff 0000 0000 0000  ................
+0000bed0: 0000 0000 0000 0000 0001 0000 0000 0000  ................
+0000bee0: 0000 0000 0000 0000 0001 0000 0000 0000  ................
 0000bef0: 0000 0000 0000 0000 4000 0000 0140 0000  ........@....@..
@@ -3060,3 +3060,3 @@
 0000bf30: 0000 0020 6d64 6864 0000 0000 0000 0000  ... mdhd........
-0000bf40: 0000 0000 0000 1800 0000 f200 55c4 0000  ............U...
+0000bf40: 0000 0000 0000 3000 0000 f200 55c4 0000  ......0.....U...
 0000bf50: 0000 002e 6864 6c72 0000 0000 0000 0000  ....hdlr........
```

{.remark pause scroll}
上の 2 箇所が向き、下の 1 箇所が速さです。
どちらも、変更行のすぐ上にある白い行が居場所を教えてくれます。
下の変更は `mdhd` という箱の中で起きています。

{.remark pause scroll}
映像データ（`mdat`）は 48,636 バイトまるごと、**1 バイトも変わっていません**。
今日の話は、この 3 箇所が何なのかの説明でしかありません。

{pause center}

{.deck-title}
# バイナリを触って学ぶ MP4

{pause up}

## 今日の道筋

- MP4 は「箱」の入れ子にすぎない
- 箱のルールは 3 行で説明できる
- だから手で書き換えられる（デモ 5 本）
- でもサイズを変えた瞬間に壊れる。**その理由が MP4 の設計そのもの**

{pause up=part1-title}

{#part-container}
--------

{include src=parts/01-what-is-mp4.md}

{include src=parts/02-box-rules.md}

{include src=parts/03-moov.md}

{include src=parts/04-tkhd-matrix.md}

{include src=parts/05-demos.md}

{include src=parts/06-stco.md}

{include src=parts/07-closing.md}

{include src=parts/08-appendix.md}

--------
