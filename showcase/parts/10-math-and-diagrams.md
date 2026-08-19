{pause up=part10-title}

{#part10-title}
# 10. 数式と図

{pause up}

## 数式

インラインは `$...$`、ブロックは `$$...$$` か ```` ```math ```` フェンス。LaTeX の数式構文と同じ。
レンダラーは既定で MathJax 3.2.2（HTML に丸ごと同梱される）。

{pause scroll}
```markdown
円周率の定義の 1 つ： $$\pi = \frac{C}{d}$$

インラインなら $e^{i\pi} = -1$ のように書く。
```

{pause scroll}
円周率の定義の 1 つ： $$\pi = \frac{C}{d}$$

インラインなら $e^{i\pi} = -1$ のように書く。

{pause up}

## 数式の一部を pause の的にする

MathJax の HTML 出力拡張（既定で有効）で `\cssId{id}{式}` を使うと、式の一部に id を振れる。
コンパイラは数式の中身までは見ないので、`external-ids` frontmatter で「このファイルには
この ID がある」と申告しておく（さもないと warning が出る）。

{pause scroll}
```markdown
---
external-ids: eq-pause1 eq-pause2
---

$$ S = \cssId{eq-pause1}{1 + 2} + \cdots + \cssId{eq-pause2}{100} $$

{pause=eq-pause1 unreveal=eq-pause1}
{reveal=eq-pause1}
{pause=eq-pause2}
```

{pause scroll}
$$ S = \cssId{eq-pause1}{1 + 2} + \cdots + \cssId{eq-pause2}{100} $$

{pause=eq-pause1 unreveal=eq-pause1}

{reveal=eq-pause1}

{pause=eq-pause2}

{.remark pause scroll}
`unreveal` してすぐ `reveal` するのは、初期状態でも見えているが「ここで登場した」感じを
出すための定番テクニック（一瞬隠して出し直す）。代替レンダラーとして KaTeX も選べる
（frontmatter の `math-mode: katex`）。`pause` の粒度が MathJax よりやや粗くなる。

{pause up}

## Mermaid.js の図

```` ```=mermaid ```` フェンスで書く。

{pause scroll}
```markdown
``` =mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```
```

{pause scroll}
``` =mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```

{pause up}

## TikZ と Manim（このデッキには未収録）

どちらも外部ツールでのビルドを前提とする。

{.block title="TikZ" pause scroll}
`\documentclass[tikz]{standalone}` で単体コンパイルし、`.pdf` を `![](file.pdf)` で
取り込む。図の一部を id で狙いたいときは `.svg` へ出力する。

{.block title="Manim" pause scroll}
`manim` コマンドで書き出した `.mp4` をそのまま動画として取り込む（9 章の動画埋め込みと同じ）。

{pause up}
