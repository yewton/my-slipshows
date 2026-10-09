{pause up}

## Appendix

配信と DRM も、結局は箱の話です。

{slip .aside pause}
----
{.aside-label}
Appendix A

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
順番をプレイリスト（`.m3u8`）に書きます。初期の HLS は MPEG-2 TS だけでしたが、
2016 年の WWDC で fragmented MP4 の対応が発表され、DASH と同じ容れ物を使えるようになりました。

{.block title="一次資料" pause up}
> - Apple, *What's New in HTTP Live Streaming*（WWDC 2016, Session 504）
>   fMP4 対応が発表された回 — <https://developer.apple.com/videos/play/wwdc2016/504/>
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
5 回試したところ、変わったのは 14,736〜14,758 バイト。
初期化ベクタが毎回変わるので、平文とたまたま一致するバイト数が揺れます。

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
`avc1` が `encv` に変わり、元の type は `frma` に退避されます。
type を書き換えて無効化するのは、`udta` → `free` でメタデータを消したのと似た発想ですね。

{.remark pause up}
増えた箱の役割は、`sinf` が保護スキーム情報のまとめ役、`schm` がどの方式か（cenc / cbcs）、
`tenc` が既定の鍵 ID、`saiz` / `saio` / `senc` がサンプルごとの初期化ベクタとその位置です。

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
実際の DRM では、さらに `pssh` という箱に「どのライセンスサーバに、どの鍵 ID を訊けばよいか」を入れます
（`mp4encrypt` なら `--pssh` オプション。上のコマンドでは付けていないので `pssh` はありません）。

{.block title="一次資料" pause up}
> - Common Encryption は **ISO/IEC 23001-7（有償）**。本資料は引用せず、実ファイルの box 構造のみに基づく
> - W3C, *Encrypted Media Extensions*（無償、ブラウザ側の API）
>   <https://www.w3.org/TR/encrypted-media/>
> - DASH-IF, *Content Protection Implementation Guidelines*（無償）
>   <https://dashif.org/guidelines/>

----

{step}

{pause up}

## おわり

{.block}
ありがとうございました。
