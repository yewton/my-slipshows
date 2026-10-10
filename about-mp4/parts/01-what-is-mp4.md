{#part1-title}
# 1. MP4 とは何か

{.definition title="コーデック" pause scroll}
映像や音声そのものをどう圧縮するかを決めた規格。H.264 / H.265 / AAC（Advanced Audio Coding）など。

{.definition title="コンテナ" pause scroll}
圧縮済みのデータと再生に必要な情報を、どう 1 つのファイルにまとめるかを決めた規格。MP4（MPEG-4 Part 14。MPEG は標準化団体 Moving Picture Experts Group の略）はこちら。

{.remark pause scroll}
本編で扱うのは全部コンテナ側の話です。H.264 の中身には触れません（Appendix A で少しだけ補足します）。
逆に言うと、**コーデックを知らなくても MP4 は読めます**。

{pause up}

## 系譜

```text
QuickTime File Format  (Apple, 1991)
        │
        ▼
ISO Base Media File Format, ISO BMFF  (ISO/IEC 14496-12)
        │
        ├── MP4          (ISO/IEC 14496-14)
        ├── 3GP          (3GPP TS 26.244)
        ├── HEIF         (静止画)
        └── fragmented MP4 → DASH / HLS
```

- 3GP … 3GPP（携帯電話の標準化団体 3rd Generation Partnership Project）が定めた携帯向けの形式
- HEIF … High Efficiency Image File Format
- DASH … Dynamic Adaptive Streaming over HTTP
- HLS … HTTP Live Streaming

{.remark pause scroll}
箱の構造は 30 年以上ほぼ変わっていません。
今日見る `moov`（movie）や `tkhd` は、1991 年の QuickTime にもう存在していました。

{pause up}

## この資料の出典

一次規格の **ISO/IEC 14496-12 は有償**です（2026 年版で国内価格は税込 5 万円程度 💸）

流石に買うのは厳しかったので…

{.block title="根拠にしたもの" pause scroll}
> - Apple QuickTime File Format Specification（無償公開）
> - MP4RA（MP4 Registration Authority）：box type の公式登録簿（無償）
> - mp4box.js / Bento4 / FFmpeg の実装
> - **実ファイルでの検証**
