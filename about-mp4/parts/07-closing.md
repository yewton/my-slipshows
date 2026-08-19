{pause up}

## まとめ

- MP4 は `[size][type][payload]` の入れ子。ルールはこれだけ
- `mdat` が本体、`moov` が索引
- 索引を書き換えれば、映像データを触らずに再生を変えられる
- ただし `stco` が絶対オフセットを持つので、**サイズを変えた瞬間に壊れる**
- faststart も fragmented MP4 も、この制約から出てきた設計
- 仕様にあっても、実装が見なければ効かない（変換行列の平行移動、`tkhd` の track enabled）

{.block pause scroll}
手元の mp4 を `xxd` で開いてみてください。10 分で `ftyp` と `moov` は見つかります。

{pause up}

## 参考文献

{.block title="仕様"}
> - Apple, *QuickTime File Format Specification* — <https://developer.apple.com/documentation/quicktime-file-format>
>   引用は 2001-03-01 版 PDF <https://developer.apple.com/standards/qtff-2001.pdf> の
>   Matrices / Track header atom / Sprite properties / Modifier tracks から
> - MP4RA（box type とブランドの登録簿）— <https://mp4ra.org>
> - W3C, *ISO BMFF Byte Stream Format* — <https://www.w3.org/TR/mse-byte-stream-format-isobmff/>
> - RFC 8216（HTTP Live Streaming）— <https://www.rfc-editor.org/rfc/rfc8216>
> - 一次規格は ISO/IEC 14496-12（有償）。本資料は引用しておらず、上記と実ファイル検証に基づく

{pause up}

{.block title="実装 / ツール"}
> - mp4box.js — <https://github.com/gpac/mp4box.js> (BSD-3-Clause)
> - Bento4（`mp4dump` / `mp4fragment` / `mp4encrypt`）— <https://github.com/axiomatic-systems/Bento4>
> - FFmpeg `libavformat/mov.c`, `libavutil/display.c`
>   `-movflags` の説明は <https://ffmpeg.org/ffmpeg-formats.html> の mov / mp4 / ismv の項
> - ImHex + `mp4.hexpat` — <https://github.com/WerWolv/ImHex-Patterns>
> - MP4Box.js Box Viewer — <https://gpac.github.io/mp4box.js/test/filereader.html>

{pause up}

{.block title="デモ素材"}
> - 冒頭：*Big Buck Bunny* © 2008 Blender Foundation, CC BY 3.0
>   <https://peach.blender.org> の 320x180 版から 5 秒を切り出して使用
> - 2 章以降：`ffmpeg -f lavfi -i testsrc` で生成

{.remark pause scroll}
向きの反転も、速度の変更も、破壊も、切り出したファイルを直接書き換えたもので、
再エンコードは行っていません。
