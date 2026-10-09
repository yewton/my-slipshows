{pause up=part2-title}

{#part2-title}
# 2. Box のルール

{.definition title="box（atom）" pause scroll}
```text
[ size : 4 bytes ][ type : 4 bytes ][ payload : size - 8 bytes ]
```

{pause scroll}
- `size` は **自分自身を含めた** 全体のバイト数（ビッグエンディアン）
- `type` は ASCII 4 文字。`ftyp`, `moov`, `mdat` など
- `payload` の中身は type ごとに違う。**box が入れ子になっていることも多い**

{.block pause scroll}
これだけです。あとは全部この繰り返し。

{pause up}

## ここから使うファイル

冒頭のデモでは、配布されている動画を使いました。
ここから先は、**中身が完全に分かっているファイル**を使います。

{pause scroll}
```text
$ ffmpeg -f lavfi -i testsrc=size=320x240:rate=30:duration=5 \
         -c:v libx264 -pix_fmt yuv420p sample.mp4
```

{.definition title="testsrc" pause scroll}
ffmpeg に内蔵されたテスト信号のジェネレータ。素材ファイルなしで、
カラーバーと経過時間カウンタの入った映像を作れます。

{pause up play-media=video-testsrc}
## こんなの

![](../demo/00-original.mp4){video #video-testsrc width=30%}

{pause up}

## 実物を見る

```text
$ xxd -R always -l 64 00-original.mp4 | ansi2html -n | pbcopy
```

<pre style="padding:30px;background-color:#000;color:#bbb;white-space:pre-wrap;word-wrap:break-word;overflow-wrap:break-word">00000000: <span style="color:#fff">0000</span> <span style="color:#fff">00</span><span style="color:#5f5">20</span> <span style="color:#5f5">6674</span> <span style="color:#5f5">7970</span> <span style="color:#5f5">6973</span> <span style="color:#5f5">6f6d</span> <span style="color:#fff">0000</span> <span style="color:#f55">02</span><span style="color:#fff">00</span>  <span style="color:#fff">...</span><span style="color:#5f5"> ftypisom</span><span style="color:#fff">..</span><span style="color:#f55">.</span><span style="color:#fff">.</span>
00000010: <span style="color:#5f5">6973</span> <span style="color:#5f5">6f6d</span> <span style="color:#5f5">6973</span> <span style="color:#5f5">6f32</span> <span style="color:#5f5">6176</span> <span style="color:#5f5">6331</span> <span style="color:#5f5">6d70</span> <span style="color:#5f5">3431</span>  <span style="color:#5f5">isomiso2avc1mp41</span>
00000020: <span style="color:#fff">0000</span> <span style="color:#fff">00</span><span style="color:#f55">08</span> <span style="color:#5f5">6672</span> <span style="color:#5f5">6565</span> <span style="color:#fff">0000</span> <span style="color:#5f5">5d</span><span style="color:#f55">8b</span> <span style="color:#5f5">6d64</span> <span style="color:#5f5">6174</span>  <span style="color:#fff">...</span><span style="color:#f55">.</span><span style="color:#5f5">free</span><span style="color:#fff">..</span><span style="color:#5f5">]</span><span style="color:#f55">.</span><span style="color:#5f5">mdat</span>
00000030: <span style="color:#fff">0000</span> <span style="color:#f55">02ae</span> <span style="color:#f55">0605</span> <span style="color:#55f">ffff</span> <span style="color:#f55">aadc</span> <span style="color:#5f5">45</span><span style="color:#f55">e9</span> <span style="color:#f55">bde6</span> <span style="color:#f55">d9</span><span style="color:#5f5">48</span>  <span style="color:#fff">..</span><span style="color:#f55">....</span><span style="color:#55f">..</span><span style="color:#f55">..</span><span style="color:#5f5">E</span><span style="color:#f55">....</span><span style="color:#5f5">H</span>
</pre>


{pause scroll}
この 64 バイトに box が 3 つ入っています。右の ASCII 欄に出ている
`ftyp`, `free`, `mdat` です。

{pause up}

## ftyp

左端は、その行が占めるバイト数です。

```text
   4  0000 0020            size = 32
   4  6674 7970            type = 'ftyp'
   4  6973 6f6d            major_brand   = 'isom'
   4  0000 0200            minor_version
  16  6973 6f6d 6973 6f32  compatible_brands
      6176 6331 6d70 3431    = 'isom' 'iso2' 'avc1' 'mp41'
  --
  32                       ← 先頭が宣言した size と一致
```

{pause scroll}
- **major_brand** … このファイルが第一に従う規格。`isom` は ISO base media file format
- **minor_version** … major_brand の版を示す情報用の値
- **compatible_brands** … 「これとしても読める」の列挙。ここでは 4 つ

{.remark pause scroll}
`iso2` は 2004 年版の ISO ファイル形式、`avc1` は H.264（AVC）の拡張、`mp41` は MP4 version 1。
つまり「容れ物は ISO で、中身は H.264」という自己申告です。ブランドの一覧は MP4RA が公開しています。

{.block pause scroll}
足し上げた数が `size` と一致したら、**その box を最後まで正しく読めた**ということです。

{pause up}

## free

```text
0000 0008 6672 6565           size = 8, type = 'free'
```

{pause scroll}
**何も入っていません。** `size` が 8 なので payload は 0 バイト。
`free` は「ここは読み飛ばしてよい」という意味の箱で、詰め物として置かれます。

{.remark pause scroll}
ffmpeg は `ftyp` の直後に空の `free` を 1 つ書きます。
パディング用に便利に使うためらしい。

{pause up}

## mdat

```text
0000 5d8b 6d64 6174           size = 23,947, type = 'mdat'
0000 02ae                     ← payload の先頭 4 バイト
0605 ffff aadc 45e9 ...
```

{pause scroll}
ファイル全体の **9 割**がこの箱で、中身は H.264 の生データです。
ただし先頭の `0000 02ae` は映像ではありません。**686 という長さ**です。

{.remark pause scroll}
`mdat` は「長さ + データ」の繰り返しでできています。
なぜそうなっているか、そしてこれが何を引き起こすかは、後ほど。

{pause up}

## 例外は 2 つだけ

{.block title="size == 1 のとき"}
type の直後に 8 バイトの `extended size` が続く。4GB を超える box 用。

{.block title="size == 0 のとき" pause scroll}
この box はファイル末尾まで続く。実質 `mdat` 専用。

{pause up}

## FullBox

{.definition}
一部の box は payload 先頭に `version` と `flags` を持ちます。FullBox と呼ばれます。

```text
[ size : 4 ][ type : 4 ][ version : 1 ][ flags : 3 ][ payload ... ]
```

{pause scroll}
[mp4box.js の boxes 配下](https://github.com/gpac/mp4box.js/tree/v2.4.1/src/boxes) を見ると、各 type で version や flags がどういう意味を持つか、確認し易いです。

{pause scroll}
---
### mdhd の例

`version` は、 duration などの bit 長に影響。

```ts
    if (this.version === 1) {
      this.creation_time = stream.readUint64();
      this.modification_time = stream.readUint64();
      this.timescale = stream.readUint32();
      this.duration = stream.readUint64();
    } else {
      this.creation_time = stream.readUint32();
      this.modification_time = stream.readUint32();
      this.timescale = stream.readUint32();
      this.duration = stream.readUint32();
    }
```

---

{pause scroll}
---
`flags` は未使用。

```ts
    this.flags = 0;
```
---
