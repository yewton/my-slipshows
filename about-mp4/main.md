---
dimension: 16:9
theme: default
css: ../_shared/ja.css ../_shared/layout.css
highlightjs-theme: github-dark
---

# 突然ですが

![](demo/intro-upside-slow.mp4){video autoplay muted loop #video-before width=50%}

{.credit}
*Big Buck Bunny* © 2008 Blender Foundation, CC BY 3.0（[peach.blender.org](https://peach.blender.org)）

この動画、上下が反転していて、しかもなんだかスローモーションになってますね。

{pause scroll}
向きを直して、再生速度も直したい。

こんなこと、よくありますよね。 **皆さんなら、どう直しますか？**

{pause up}

# 再エンコードしてみる

```text
$ ffmpeg -i in.mp4 -vf "hflip,vflip,setpts=0.5*PTS" -r 24 out.mp4
```

{.compare pause scroll}
> ![](demo/intro-upside-slow.mp4){video autoplay muted loop #cmp-before width=100%}
>
> ![](demo/intro-reencoded.mp4){video autoplay muted loop #cmp-reenc width=100%}

{.remark pause scroll}
確かに直りました。ただしこれは **映像を全部デコードして、H.264 で圧縮し直しています。**

{.compare .caps pause scroll}
> 変換前　**50,911** バイト
>
> 変換後　**68,163** バイト

{pause scroll}
```text
$ cmp --verbose intro-upside-slow.mp4 intro-reencoded.mp4 | wc -l
cmp: EOF on ‘intro-upside-slow.mp4’ after byte 50911
49965
```

{pause scroll}
> 50,911 バイトのうち **49,965 バイト** が変わってます。つまり、 **中身は完全に別のファイルです。**
>
> …なんだか、もったいない感じがしますね？

{pause up}
# バイナリエディタを使おう

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
$ cmp --verbose intro-upside-slow.mp4 intro-original.mp4 | wc -l
5
```

{#intro-diff pause up}
```diff
$ diff --unified=3 --label before.mp4 --label after.mp4 <(xxd intro-upside-slow.mp4) <(xxd intro-original.mp4)
--- before.mp4
+++ after.mp4
@@ -3051,14 +3051,14 @@
 0000bea0: 0000 0747 7472 616b 0000 005c 746b 6864  ...Gtrak...\tkhd
 0000beb0: 0000 0003 0000 0000 0000 0000 0000 0001  ................
 0000bec0: 0000 0000 0000 1388 0000 0000 0000 0000  ................
-0000bed0: 0000 0000 0000 0000 ffff 0000 0000 0000  ................
-0000bee0: 0000 0000 0000 0000 ffff 0000 0000 0000  ................
+0000bed0: 0000 0000 0000 0000 0001 0000 0000 0000  ................
+0000bee0: 0000 0000 0000 0000 0001 0000 0000 0000  ................
 0000bef0: 0000 0000 0000 0000 4000 0000 0140 0000  ........@....@..
 0000bf00: 00b4 0000 0000 0024 6672 6565 0000 001c  .......$free....
 0000bf10: 656c 7374 0000 0000 0000 0001 0000 1388  elst............
 0000bf20: 0000 0400 0001 0000 0000 06bf 6d64 6961  ............mdia
 0000bf30: 0000 0020 6d64 6864 0000 0000 0000 0000  ... mdhd........
-0000bf40: 0000 0000 0000 1800 0000 f200 55c4 0000  ............U...
+0000bf40: 0000 0000 0000 3000 0000 f200 55c4 0000  ......0.....U...
 0000bf50: 0000 002e 6864 6c72 0000 0000 0000 0000  ....hdlr........
 0000bf60: 7669 6465 0000 0000 0000 0000 0000 0000  vide............
 0000bf70: 0c56 6964 656f 4861 6e64 6c65 7200 0000  .VideoHandler...
```

{.remark pause scroll}
> 上の hunk が向き、下の hunk が速さの差分です。
>
> 右側に見えている `tkhd`（track header）, `mdhd`（media header）というのが、構造を表すキーワードです。

{pause scroll}
---

```
$ xxd intro-upside-slow.mp4 | head --lines 5
00000000: 0000 0020 6674 7970 6973 6f6d 0000 0200  ... ftypisom....
00000010: 6973 6f6d 6973 6f32 6176 6331 6d70 3431  isomiso2avc1mp41
00000020: 0000 0008 6672 6565 0000 be04 6d64 6174  ....free....mdat
00000030: 0000 02ae 0605 ffff aadc 45e9 bde6 d948  ..........E....H
00000040: b796 2cd8 20d9 23ee ef78 3236 3420 2d20  ..,. .#..x264 -
```

先頭の方には `mdat`（media data）と呼ばれている部分があり、これが実際の映像データです。

ここは **1 バイトも変わっていません**。

今日は、これら 3 つのキーワードを説明していきます。

{pause center .deck-title}
---
# バイナリを<br />触って学ぶ MP4
---

{pause up}

## 三行サマリ

- MP4 は「箱」の入れ子にすぎない
- だからバイナリエディタで修正したっていい
- でも一歩間違えば…もちろん壊れる。**その理由が MP4 の設計そのもの**

{pause up=part1-title}

{#part-container}
--------

{include src=parts/01-what-is-mp4.md}

{include src=parts/02-box-rules.md}

{include src=parts/03-moov.md}

{include src=parts/04-tkhd-matrix.md}

{include src=parts/05-mdhd.md}

{include src=parts/06-stco.md}

{include src=parts/07-closing.md}

{include src=parts/08-appendix.md}

--------
