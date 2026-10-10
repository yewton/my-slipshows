{pause up}

## Appendix

本編で省いた `mdat` の中身と、配信・DRM（Digital Rights Management）の話を補足します。

{slip .aside pause}
----
{.aside-label}
Appendix A

## mdat の中身

本編では「映像データ」とひとまとめにした `mdat` の中身を、もう一段だけ覗きます。

```text
0000 02ae | 06 05 ff ff aa dc ...   (686 バイト)
0000 0c88 | 65 88 84 00 ...         (3,208 バイト)
...
```

`mdat` は「長さ（4 バイト） + データ」の繰り返しでできています。この「データ」が NAL unit です。

{pause up}

## NAL unit

{.definition title="NAL unit — Network Abstraction Layer unit" pause scroll}
H.264 は、圧縮そのものを受け持つ層（**VCL**）と、それを運ぶための包み（**NAL**）に
分けて設計されています。同じ映像データを MP4 でも RTP（Real-time Transport Protocol）でも運べるのは、この分離のおかげです。

{.definition title="VCL — Video Coding Layer" pause scroll}
画を圧縮したデータそのもの。1 フレーム（またはその一部 = スライス）を、予測と差分で表します。
H.264 の圧縮技術の本体はこちらですが、今日は中身には立ち入りません。

{pause up}

## NAL の種類

{.remark}
---
NAL unit の中身は、VCL のデータ（スライス）か、それ以外の付随情報のどちらかです。
先頭 1 バイトの下位 5 ビットが種類を表します。このファイルの 1 個目のサンプルだと：

```text
1 個目の NAL  06 05 ff ff ...   type 6  SEI（エンコーダの設定などの付随情報）
2 個目の NAL  65 88 84 00 ...   type 5  IDR スライス（VCL。キーフレームの画そのもの）
```

- SEI … Supplemental Enhancement Information
- IDR … Instantaneous Decoder Refresh。ここから単独でデコードを始められるフレーム

---

{.remark pause scroll}
冒頭の `xxd` で `mdat` の直後に見えていた `x264 -` という文字列は、この SEI の中身です。

{.remark pause up}
---
生の H.264 は `00 00 01` というスタートコードを探して切れ目を見つけますが、
**MP4 では長さを前に置きます**。

たとえば `stsz` が「1 個目のサンプルは 3,902 バイト」と言い、
その中を長さで辿ると (4 + 686) + (4 + 3,208) = 3,902 で、NAL 2 つに分かれる、という具合です。

---

{.remark pause scroll}
長さフィールドの幅は `avcC`（AVC configuration。`stsd` の中にある、H.264 の設定を書いた箱）の
`lengthSizeMinusOne` が決めます。このファイルでは 4 バイトです。

{pause up}

## 壊れたファイルのエラーの意味

6 章で壊したファイルは、`stco` が指す 48 バイト目に `mdat` のヘッダが来ていました。

```text
正しい先頭:  0000 02ae | 06 05 ff ff ...
             ↑ 686     ↑ 1 個目の NAL（686 バイト）

壊れた先頭:  0000 5d8b | 6d 64 61 74 ...
             ↑ 23947   ↑ "mdat" の 4 文字を中身だと思って読む
```

{.block pause scroll}
```text
$ ffmpeg -i 05-broken.mp4 -f null -
[h264 @ 0x...] Invalid NAL unit size (23947 > 3898).
```
デコーダは `mdat` の size 23,947 を NAL の長さだと思って読みました。
ところがこのサンプルの残りは 3,898 バイト（3,902 − 長さフィールド 4）しかないので、「長さがおかしい」と止まったわけです。

----

{step}

{slip .aside pause}
----
{.aside-label}
Appendix B

## HLS と fragmented MP4

`stco` は絶対オフセットの表なので、後ろに足していくのが苦手です。
配信では**追記できる形**が要るので、索引を分割した fragmented MP4 を使います。

{pause scroll}
```text
$ ffmpeg -i 00-original.mp4 -c copy -movflags frag_keyframe+empty_moov out.mp4
$ mp4dump out.mp4
[ftyp] size=8+28
[moov] size=8+763        ← 2611 から縮んだ。索引の「型」だけが残る
  [mvex] size=8+32       ← この先はフラグメントで来る、という宣言
[moof] size=8+1304       ← 1 個目の索引
  [traf]
    [trun]               ← サンプルの位置。moof からの相対
[mdat] size=8+23939      ← 1 個目のデータ
```

{.block pause scroll}
元ファイルの `moov` は 2,611 バイト。fragmented にすると **763 バイト**まで縮み、
残りは `moof` へ移ります。`stco` は残りますが `entry_count = 0`、つまり**空っぽ**です。

{.remark pause up}
箱のサイズは ffmpeg のバージョンによって多少変わります（上は 8.1.2 での実測）。

{.remark pause up}
HLS はこの `moof` + `mdat` のペアを 1 セグメントとして並べ、
順番をプレイリスト（`.m3u8`）に書きます。初期の HLS は MPEG-2 TS（Transport Stream）だけでしたが、
2016 年の WWDC（Apple の開発者会議 Worldwide Developers Conference）で fragmented MP4 の対応が発表され、DASH と同じ容れ物を使えるようになりました。

{.block title="一次資料" pause up}
> - Apple, *What's New in HTTP Live Streaming*（WWDC 2016, Session 504）
>   fMP4 対応が発表された回。スライド PDF — <https://devstreaming-cdn.apple.com/videos/wwdc/2016/504m956dgg4hlw2uez9/504/504_whats_new_in_http_live_streaming.pdf>
> - RFC 8216 §3.3 *Fragmented MPEG-4*（無償）— <https://www.rfc-editor.org/rfc/rfc8216#section-3.3>
>   「MPEG-4 フラグメントは、サンプルテーブルの一部を持つ `moof` と、そのサンプルを収めた `mdat` から成る」と規定
> - Apple, HTTP Live Streaming の資料一覧 — <https://developer.apple.com/streaming/>

{pause up}

## DRM

暗号化しても、**箱の形は変わりません**。`mdat` のサイズも 1 バイトも動きません。

{.remark pause scroll}
CENC（Common Encryption）は fragmented MP4 が前提の方式です。素の MP4 に掛けると警告が出ます。

{pause scroll}
```text
$ mp4encrypt --method MPEG-CENC \
    --key 1:000102030405060708090a0b0c0d0e0f:random \
    --property 1:KID:101112131415161718191a1b1c1d1e1f \
    00-original.mp4 raw-encrypted.mp4
WARNING: this encryption method only applies to fragmented files
```

{.remark pause scroll}
箱は暗号化用のものに書き換わるのに、`mdat` の中身は平文のまま残ります。
なので先に `mp4fragment` を通しておきます。

{pause up}

```text
$ mp4fragment 00-original.mp4 plain.mp4
unable to autodetect fragment duration, using default
$ mp4encrypt --method MPEG-CENC \
    --key 1:000102030405060708090a0b0c0d0e0f:random \
    --property 1:KID:101112131415161718191a1b1c1d1e1f \
    plain.mp4 encrypted.mp4
$ mp4dump plain.mp4 | grep '^\[mdat\]'
[mdat] size=8+23939
$ mp4dump encrypted.mp4 | grep '^\[mdat\]'
[mdat] size=8+23939
```

{pause scroll}
サイズはそのままで、23,939 バイトのうち**およそ 6 割**が変わりました。

{.remark pause up}
暗号化されるのは 14,800 バイトで、残り 9,139 バイトは平文のままです（`senc` の集計）。
暗号化した部分も 1/256 の確率で元と同じ値になるので、`cmp` で数えると 14,740 前後になります。

{pause up}

## 平文で残す部分

残りが平文なのは、NAL のヘッダなど、復号する前に読む必要のある部分を
**わざと平文で残している**からです（subsample encryption）。

{pause scroll}
```text
$ mp4dump --verbosity 3 encrypted.mp4
    [senc] size=12+3604, flags=2
      sample info count = 150
      ...
        (       0)
          info = [0b ce e5 cb 11 9a e5 02 00 00 00 00 00 00 00 00]
          sub entries:
            (       0) bytes_of_clear_data = 798, bytes_of_encrypted_data = 3104
```

{.remark pause scroll}
1 個目のサンプルは、平文 798 + 暗号 3,104 = 3,902 バイト。
`stsz` の言う 1 個目のサンプルの大きさと一致しますね。

{.block pause up}
ここでも**サイズを変えない**のは、本編と同じ理由です。
変えてしまうと、索引を全部書き直す羽目になります。

{pause up}

## 増える箱

暗号化で足されるのは、鍵の在り処と暗号化方式を書いた箱です。
箱の名前だけを取り出して比べてみます。

{pause scroll}
```text
$ boxes() { mp4dump "$1" | grep -o '^ *\[....\]'; }
$ diff --unified=1 --label plain.mp4 --label encrypted.mp4 <(boxes plain.mp4) <(boxes encrypted.mp4)
```

{#cenc-diff pause up}
```diff
--- plain.mp4
+++ encrypted.mp4
@@ -15,3 +15,3 @@
           [stsd]
-            [avc1]
+            [encv]
               [avcC]
@@ -19,2 +19,7 @@
               [btrt]
+              [sinf]
+                [frma]
+                [schm]
+                [schi]
+                  [tenc]
           [stts]
@@ -32,2 +37,5 @@
     [trun]
+    [saiz]
+    [saio]
+    [senc]
 [mdat]
```

{.remark pause up}
`avc1` が `encv`（encrypted video）に変わり、元の type は `frma`（original format）に退避されます。
type を書き換えて無効化するのは、`udta` → `free` でメタデータを消したのと似た発想ですね。

{.remark pause up}
増えた箱の役割は、`sinf`（protection scheme information）が保護スキーム情報のまとめ役、`schm`（scheme type）がどの方式か（cenc / cbcs）、
`schi`（scheme information）が方式ごとの詳細の入れ物、`tenc`（track encryption）が既定の鍵 ID、
`saiz` / `saio`（sample auxiliary information sizes / offsets）と `senc`（sample encryption）がサンプルごとの初期化ベクタとその位置です。

{pause up}

## 鍵はどこに？

```text
$ mp4dump --verbosity 2 encrypted.mp4 | grep --after-context=3 '\[tenc\]'
                  [tenc] size=12+20
                    default_isProtected = 1
                    default_Per_Sample_IV_Size = 16
                    default_KID = [10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f]
```

{.remark pause scroll}
ファイルに入っているのは鍵 ID（KID）だけで、鍵そのものは入っていません。

{.remark pause scroll}
実際の DRM では、さらに `pssh`（protection system specific header）という箱に「どのライセンスサーバに、どの鍵 ID を訊けばよいか」を入れます
（`mp4encrypt` なら `--pssh` オプション。上のコマンドでは付けていないので `pssh` はありません）。

{.block title="一次資料" pause up}
> - Common Encryption は **ISO/IEC 23001-7（有償）**。本資料は引用せず、実ファイルの box 構造のみに基づく
> - W3C, *Encrypted Media Extensions*（無償、ブラウザ側の API）
>   <https://www.w3.org/TR/encrypted-media/>
> - DASH-IF（DASH Industry Forum）, *DASH-IF implementation guidelines: content protection and security*（無償）
>   <https://dashif.org/Guidelines-Security/>

----

{step}

{pause up}

## おわり

{.block}
ありがとうございました。
