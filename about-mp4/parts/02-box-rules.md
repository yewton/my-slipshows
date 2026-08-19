{pause up=part2-title}

{#part2-title}
# 2. Box のルールは 3 行

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

冒頭には、実際に配布されている動画を使いました。
ここから先は、**中身が完全に分かっているファイル**に持ち替えます。

{pause scroll}
```text
$ ffmpeg -f lavfi -i testsrc=size=320x240:rate=30:duration=5 \
         -c:v libx264 -pix_fmt yuv420p sample.mp4
```

{.definition title="testsrc" pause scroll}
ffmpeg に内蔵されたテスト信号のジェネレータ。素材ファイルなしで、
カラーバーと経過時間カウンタの入った映像をその場で作れます。

{pause up=video-testsrc play-media=video-testsrc}

![](../demo/00-original.mp4){video #video-testsrc width=30%}

{.remark pause scroll}
音声トラックなし、5 秒、**26,606 バイト**。box を数え上げられる大きさです。
カウンタが入っているので、倍速にしたときに何が起きたかも一目で分かります。

{pause up}

## 実物を見る

```text
$ xxd -l 64 sample.mp4
00000000: 0000 0020 6674 7970 6973 6f6d 0000 0200  ... ftypisom....
00000010: 6973 6f6d 6973 6f32 6176 6331 6d70 3431  isomiso2avc1mp41
00000020: 0000 0008 6672 6565 0000 5d8b 6d64 6174  ....free..].mdat
00000030: 0000 02ae 0605 ffff aadc 45e9 bde6 d948  ..........E....H
```

{pause scroll}
この 64 バイトに box が 3 つ入っています。右の ASCII 欄に出ている
`ftyp` `free` `mdat` が、その名前です。**1 つずつ全部読みます。**

{pause up}

## 1 つ目：ftyp を余さず読む

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
つまり「ISO の器で、中身は H.264」という自己申告です。ブランドの一覧は MP4RA が公開しています。

{.block pause scroll}
足し上げた数が `size` と一致したら、**その box を最後まで正しく読めた**ということです。
箱を辿るときの検算になります。

{pause up}

## 2 つ目：free には何が入っているか

```text
0000 0008 6672 6565           size = 8, type = 'free'
```

{pause scroll}
**何も入っていません。** `size` が 8 なので payload は 0 バイト。
`free` は「ここは読み飛ばしてよい」という意味の箱で、詰め物として置かれます。

{.remark pause scroll}
ffmpeg は `ftyp` の直後に空の `free` を 1 つ書きます。
この「読み飛ばしてよい箱」が、後で 2 回効いてきます。

{pause up}

## 3 つ目：mdat の入口

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
なぜそうなっているか、そしてこれが何を引き起こすかは **6 章**で見ます。

{pause up}

## 例外は 2 つだけ

{.block title="size == 1 のとき"}
type の直後に 8 バイトの `largesize` が続く。4GB を超える box 用。

{.block title="size == 0 のとき" pause scroll}
この box はファイル末尾まで続く。実質 `mdat` 専用。

{pause up}

## FullBox

{.definition}
一部の box は payload の先頭に固定 8 バイトを持ちます。

```text
[ size : 4 ][ type : 4 ][ version : 1 ][ flags : 3 ][ payload ... ]
```

{pause scroll}
`version` が 0 か 1 かで、後続フィールドのビット幅が変わります（32bit / 64bit）。
`tkhd` や `mdhd` がこれです。後で実際に効いてきます。
