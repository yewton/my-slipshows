---
dimension: 16:9
theme: default
css: ../_shared/ja.css ../_shared/layout.css
highlightjs-theme: github-dark
external-ids: eq-pause1 eq-pause2 svg-a svg-b svg-c
---

![](assets/sample.mp4){video autoplay muted loop #video-hook width=35%}

{.credit}
素材は ffmpeg の `testsrc` フィルタで生成した合成パターン映像（著作権表示不要）。

{pause scroll}
## これは何か

slipshow（v0.11.0 "Brazlip"）の構文とアクションを、実物を動かしながら引くための
自分用リファレンス。`about-mp4/` で実際に使った機能に加えて、上流ドキュメントを読んで
見つけた機能も収録する。

{pause center}

{.deck-title}
# slipshow ショーケース

{pause up}

## 目次

- 記法の基本 / 属性 / グルーピング
- ステップと画面移動 / 可視性
- 箱（block 系）/ slip と subslip
- メディア（動画・carousel・SVG）
- 数式と図 / カスタムスクリプト
- 発表時の機能 / frontmatter と CLI

{pause up=part1-title}

{#part-container}
--------

{include src=parts/01-syntax.md}

{include src=parts/02-attributes.md}

{include src=parts/03-grouping.md}

{include src=parts/04-steps.md}

{include src=parts/05-movement.md}

{include src=parts/06-visibility.md}

{include src=parts/07-boxes.md}

{include src=parts/08-slips.md}

{include src=parts/09-media.md}

{include src=parts/10-math-and-diagrams.md}

{include src=parts/11-custom-scripts.md}

{include src=parts/12-presenting.md}

{include src=parts/13-frontmatter-and-cli.md}

{include src=parts/14-closing.md}

--------
