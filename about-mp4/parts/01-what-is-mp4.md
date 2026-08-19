{#part1-title}
# 1. MP4 とは何か

{.definition title="コーデック" pause scroll}
映像や音声そのものをどう圧縮するかを決めた規格。H.264 / H.265 / AAC など。

{.definition title="コンテナ" pause scroll}
圧縮済みのデータと再生に必要な情報を、どう 1 つのファイルにまとめるかを決めた規格。MP4 はこちら。

{.remark pause scroll}
今日扱うのは全部コンテナ側の話です。H.264 の中身には一切触れません。
逆に言うと、**コーデックを知らなくても MP4 は読めます**。

{pause up}

## 系譜

```text
QuickTime File Format  (Apple, 1991)
        │
        ▼
ISO Base Media File Format  (ISO/IEC 14496-12)
        │
        ├── MP4          (ISO/IEC 14496-14)
        ├── 3GP          (3GPP TS 26.244)
        ├── HEIF         (静止画)
        └── fragmented MP4 → DASH / HLS
```

{.remark pause scroll}
箱の構造は 30 年以上ほぼ変わっていません。
今日見る `moov` や `tkhd` は、1991 年の QuickTime にもう存在していました。

{pause up}

## この資料の出典

一次規格の **ISO/IEC 14496-12 は有償**です（2026 年版で国内価格は税込 5 万円程度）。

{.block title="根拠にしたもの" pause scroll}
> - Apple QuickTime File Format Specification（無償公開）
> - MP4RA：box type の公式登録簿（無償）
> - mp4box.js / Bento4 / FFmpeg の実装
> - **実ファイルでの検証**

{.remark pause scroll}
今日の話は、全部その場で確かめられます。
手元の mp4 と `xxd` があれば、同じことを追体験できます。
