{pause up=part3-title}

{#part3-title}
# 3. moov の構造

{.definition title="ftyp — file type" pause scroll}
このファイルがどの規格に従うかを宣言する box。必ず先頭付近にある。

{.definition title="mdat — media data" pause scroll}
映像と音声の生データ。ファイルサイズのほぼ全部がこれ。

{.definition title="moov — movie" pause scroll}
`mdat` の**どこに何があるか**を書いた索引。今日いじるのは全部この中。

{.block pause scroll}
`mdat` が本、`moov` が目次。これだけ押さえれば迷いません。

{.remark pause scroll}
4 文字の type は英語の短縮です。読み方は MP4RA の登録簿に載っていて、
たとえば `ftyp` は "file type and compatibility"、`mdat` は "media data container"。
以降も、初出のものは元の語を添えます。

{pause up}

## moov の中身

```text
moov  movie                 ムービー全体
├── mvhd  movie header      時間の単位、全体の長さ
└── trak  track             トラック 1 本（映像 or 音声）
    ├── tkhd  track header    ★ 表示サイズ、変換行列
    ├── edts  edit list container  再生範囲の編集
    └── mdia  media
        ├── mdhd  media header   ★ 時間の単位
        ├── hdlr  handler        このトラックの種類（vide / soun）
        └── minf  media information
            └── stbl  sample table    ← 索引の本体
                ├── stsd  sample description  コーデック情報
                ├── stts  time-to-sample      各サンプルの表示時間
                ├── stsc  sample-to-chunk     サンプルとチャンクの対応
                ├── stsz  sample size         各サンプルのバイト数
                └── stco  chunk offset        ★ 絶対ファイルオフセット
```

{.remark pause scroll}
`st` で始まる 5 つは、どれも `stbl`（sample table）の子です。
名前を眺めるだけで、どれが何の表なのかは大体わかります。

{.remark pause scroll}
`edts` は今日は触りませんが、手元で辿るときは注意してください。
`tkhd` の次は `mdia` ではなく `edts` です（このファイルでは 36 バイト）。
これを飛ばすと、以降のオフセットが全部ずれます。

{.remark pause scroll}
★ の 3 つだけ覚えてください。この後のデモで全部使います。

{pause up}

## サンプルとチャンク

`stbl` の 5 つの表が何を数えているのか、先に決めておきます。

{.definition title="サンプル" pause scroll}
トラックが**時間順に持つデータの 1 要素**。映像なら 1 フレーム、音声なら一定量の波形です。
`mdat` の中身は、このサンプルが並んだものです。
（コマンド例に出てくるファイル名の `sample.mp4` とは関係ありません）

{.definition title="チャンク" pause scroll}
連続するサンプルをまとめた置き場所の単位。1 つのチャンクに 1 個以上のサンプルが入ります。

{.remark pause scroll}
このファイルは 5 秒 30fps なのでサンプルは **150 個**。
それが全部 **1 つのチャンク**に入っているので、`stco` のエントリは 1 つだけです。

{.block pause scroll}
`stco` が持つのは**チャンクの位置**だけ。
その中の何番目がどのサンプルかは、`stsc` と `stsz` が引き受けます。

{pause up}

## ツールで同じものを見る

{#tool-dump}
```text
$ mp4dump sample.mp4
[ftyp] size=8+24
  major_brand = isom
  ...
[free] size=8+0
[mdat] size=8+23939
[moov] size=8+2611
  [mvhd] size=12+96
    timescale = 1000
    duration = 5000
  [trak] size=8+2397
    [tkhd] size=12+80, flags=3
      enabled = 1
      width = 320.000000
      height = 240.000000
```

{pause up=tool-dump}

{.remark}
`xxd` で数えた `mdat` の 23,939 バイトがそのまま出ています。
`tkhd` の `flags=3` も覚えておいてください。
トラックを消すデモで、この 3 を書き換えます。

{pause up}

## 今日使うツール

特別なものは要りません。この資料に出てくるコマンドは以下だけです。

{.definition title="バイト列を見る・比べる" pause scroll}
`xxd`（16 進ダンプ）、`cmp -l`（違うバイトを列挙）、`diff`。
どれも標準的な環境に入っています。

{.definition title="箱の構造を読む" pause scroll}
`mp4dump`（Bento4）。box を入れ子のまま表示します。
`--verbosity 2` を付けると、表の中身まで出ます。

{.definition title="再生して確かめる" pause scroll}
`ffprobe`（ファイルの解釈結果を表示）、`ffmpeg`（変換・再多重化）。
再多重化（remux）は、映像データに触らず箱の詰め方だけを変えること。`-c copy` がそれです。

{.remark pause scroll}
書き換え自体は、バイナリエディタでも `head` / `printf` / `tail` でもできます。
この資料の素材は Python で box を辿って書き換えました。

{.block title="手元で試すなら" pause scroll}
> - **ImHex** + `mp4.hexpat` … box 構造を色分けして見せるバイナリエディタ
> - **MP4Box.js Box Viewer** … ブラウザで完結。ファイルは端末から出ません
> - **MP4Box -info**（GPAC）… `mp4dump` と同じ用途の別実装
