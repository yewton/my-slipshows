{pause up}

## Appendix

配信と DRM は、今日の話の続きにあります。どちらも箱の話に落ちます。

{slip .aside pause}
> {.aside-label}
> Appendix A
>
> ## HLS は MP4 をどう切るか
>
> 6 章で見たとおり、`stco` は絶対オフセットの表なので、後ろに足せません。
> 配信では**追記できる形**が要ります。そこで索引を分割したのが fragmented MP4 です。
>
> {pause scroll}
> ```text
> $ ffmpeg -i sample.mp4 -c copy -movflags frag_keyframe+empty_moov out.mp4
> $ mp4dump out.mp4
> [ftyp] size=8+28
> [moov] size=8+763        ← 2611 から縮んだ。索引の「型」だけが残る
>   [mvex] size=8+32       ← この先はフラグメントで来る、という宣言
> [moof] size=8+1304       ← 1 個目の索引
>   [traf]
>     [trun]               ← サンプルの位置。moof からの相対
> [mdat] size=8+23939      ← 1 個目のデータ
> ```
>
> {.block pause scroll}
> 元ファイルの `moov` は 2,611 バイト。fragmented にすると **763 バイト**まで縮み、
> 残りは `moof` へ移ります。`stco` は残りますが `entry_count = 0` です。
> **絶対オフセットの表が空になった**、それが追記できる理由です。
>
> {.remark pause up}
> ここだけは実行時に ffmpeg が組み立てる箱なので、版によって数バイト動きます
> （上は 8.1.2 での実測）。`moov` が縮むことと `entry_count = 0` は変わりません。
>
> {.remark pause up}
> HLS はこの `moof` + `mdat` のペアを 1 セグメントとして並べ、
> 順番をプレイリスト（`.m3u8`）に書きます。初期の HLS は MPEG-2 TS だけでしたが、
> **2016 年の WWDC で fragmented MP4 の対応が発表され**、DASH と同じ器を共有できるようになりました。
>
> {.block title="一次資料" pause up}
> > - Apple, *What's New in HTTP Live Streaming*（WWDC 2016, Session 504）
> >   fMP4 対応が発表された回 — <https://developer.apple.com/videos/play/wwdc2016/504/>
> > - RFC 8216 §3.3 *Fragmented MPEG-4*（無償）— <https://www.rfc-editor.org/rfc/rfc8216#section-3.3>
> >   「MPEG-4 フラグメントは、サンプルテーブルの一部を持つ `moof` と、そのサンプルを収めた `mdat` から成る」と規定
> > - Apple, HTTP Live Streaming の資料一覧 — <https://developer.apple.com/streaming/>
>
> {pause up}
>
> ## DRM は箱を壊さない
>
> 暗号化しても、**箱の形は変わりません**。実際に暗号化して並べると、
> `mdat` のサイズは 1 バイトも動きません。
>
> {.remark pause scroll}
> CENC は fragmented MP4 が前提の方式です。素の `sample.mp4` に掛けると
> `only applies to fragmented files` と警告が出て、**1 バイトも変わりません**。
> 先に `mp4fragment` を通しておきます。
>
> {pause scroll}
> ```text
> $ mp4fragment sample.mp4 plain.mp4
> $ mp4encrypt --method MPEG-CENC --key 1:000102...0f:random \
>              --property 1:KID:<鍵 ID> plain.mp4 encrypted.mp4
>
> 暗号化前:  [mdat] size=8+23939
> 暗号化後:  [mdat] size=8+23939
> ```
>
> {pause scroll}
> サイズは 1 バイトも動かないまま、中身は別物になります。
> 23,939 バイトのうち**およそ 6 割**が入れ替わりました。
>
> {.remark pause up}
> 実測では 14,735〜14,752 バイトの間で揺れます。初期化ベクタが毎回変わるので、
> 平文とたまたま一致するバイト数が動くためです。割合は 61.6% あたりに落ち着きます。
>
> {.remark pause up}
> 残りが平文なのは、暗号化し損ねているからではありません。NAL のヘッダなど、
> 復号する前に読む必要のある部分は**わざと平文で残します**（subsample encryption）。
> 索引から辿れる構造を保ったまま、絵の実体だけを潰す作りです。
>
> {.block pause up}
> 5 章の書き換えと同じで、**サイズを変えない**という制約はここでも守られています。
> 守らなければ、索引を全部書き直す羽目になるからです。
>
> {pause up}
>
> ## 増えるのは箱の方
>
> 暗号化で足されるのは、鍵の在り処と暗号化方式を書いた箱です。
> Bento4 で実際に暗号化して、箱の名前だけを取り出して比べます。
>
> {pause scroll}
> ```text
> $ mp4fragment sample.mp4 plain.mp4
> $ mp4encrypt --method MPEG-CENC --key 1:<鍵>:random \
>              --property 1:KID:<鍵 ID> plain.mp4 encrypted.mp4
> $ boxes() { mp4dump "$1" | grep -o '^ *\[....\]'; }
> $ diff -U1 <(boxes plain.mp4) <(boxes encrypted.mp4)
> ```
>
> {#cenc-diff pause up}
> ```diff
> @@ -15,3 +15,3 @@
>            [stsd]
> -            [avc1]
> +            [encv]
>                [avcC]
> @@ -19,2 +19,7 @@
>                [btrt]
> +              [sinf]
> +                [frma]
> +                [schm]
> +                [schi]
> +                  [tenc]
>            [stts]
> @@ -32,2 +37,5 @@
>      [trun]
> +    [saiz]
> +    [saio]
> +    [senc]
>  [mdat]
> ```
>
> {.remark pause up}
> `avc1` が `encv` に化け、元の型は `frma` に退避されます。
> 4 文字を差し替えて中身を退避する、**5 章で見た** `udta` → `free` と同じ手口です。
>
> {.remark pause up}
> 増えた箱の役割は、`sinf` が保護スキーム情報のまとめ役、`schm` がどの方式か（cenc / cbcs）、
> `tenc` が既定の鍵 ID、`saiz` / `saio` / `senc` がサンプルごとの初期化ベクタとその位置です。
>
> {.block title="一次資料" pause up}
> > - Common Encryption は **ISO/IEC 23001-7（有償）**。本資料は引用せず、実ファイルの box 構造のみに基づく
> > - W3C, *Encrypted Media Extensions*（無償、ブラウザ側の API）
> >   <https://www.w3.org/TR/encrypted-media/>
> > - DASH-IF, *Content Protection Implementation Guidelines*（無償）
> >   <https://dashif.org/guidelines/>
>
> {.remark pause up}
> 鍵そのものはファイルに入りません。`pssh` に入るのは「どのライセンスサーバに、
> どの鍵 ID を訊けばよいか」だけです。そこから先は箱の外の話になります。

{step}

{pause up}

## おわり

{.block}
箱の入れ子と、絶対オフセットの表。今日の話はこの 2 つに尽きます。
