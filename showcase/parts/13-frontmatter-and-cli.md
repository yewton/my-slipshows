{pause up=part13-title}

{#part13-title}
# 13. frontmatter と CLI

{pause up}

## frontmatter の全項目

このファイル自身のフロントマターは `main.md` にしか書けない（複数ファイルに分割した場合、
各ファイルのフロントマターは可能な範囲で結合される。詳細は上流の `frontmatter.rst`）。

{pause scroll}
```markdown
---
dimension: 16:9              4:3（既定） / 16:9 / "WIDTHxHEIGHT"
theme: default                default / vanier / CSS ファイルへのパス・URL
css: a.css b.css               追加 CSS（スペース区切り）
js: a.js                       追加 JS
highlightjs-theme: github-dark highlight.js のテーマ名
math-mode: mathjax             mathjax（既定） / katex
external-ids: id1 id2          コンパイラに存在を伝えたい ID（数式内など）
attributes: {...}              このファイルの要素すべてに付く既定属性
toplevel-attributes: {...}     プレゼン全体の既定属性（既定は slip enter="~duration:0"）
---
```

{pause up}

## スライド形式にする

`attributes` で「すべての子要素を slide にし、enter を瞬間移動にする」と指定し、
`toplevel-attributes` を空にすると、`---` 区切りだけの通常のスライドショーになる。

{pause scroll}
```markdown
---
attributes: { children:slide children:enter=~duration:0 }
toplevel-attributes: {}
---

# Slide 1

内容

---

# Slide 2

{pause}
続きの内容
```

`{pause}` などステップ機構はスライド形式でもそのまま使える。

{pause up}

## CLI

{pause scroll}
```bash
slipshow serve deck/main.md       # ホットリロード付きプレビュー（127.0.0.1:8080 固定）
slipshow compile deck/main.md     # HTML を生成（-o 省略時は main.md と同じディレクトリに main.html）
slipshow compile deck/main.md --watch
slipshow themes list              # 組み込みテーマ一覧
slipshow markdown deck/main.md    # 属性を除去した素の Markdown を出力
slipshow lsp --stdio              # エディタ用 LSP サーバ
```

{pause up}

## 気を付けること（このリポジトリの `CLAUDE.md` にも記載）

{.block title="参照切れは warning だけで exit 0" pause scroll}
画像や動画のパスが存在しなくても `compile` は成功したことになる。生成 HTML には
`src` の無い `<video>` / `<img>` が残る。**exit code では検知できない**ので、
compile の出力に warning が無いことを毎回目で確認する。

{.block title="相対パスは記述元のファイル基準" pause scroll}
`main.md` からの相対ではなく、**その記述がある `.md` ファイルからの相対**で解決される。
`{include}` した部分ファイルの中も、その部分ファイル自身からの相対になる。

{.block title="serve は静的ファイルを配信しない" pause scroll}
`slipshow serve` はホットリロード用の専用経路で本文を配る。素の `<video src="demo.mp4">` を
`serve` で開くと 404 になる（`compile` した HTML を直接開けば見える）。

{pause up}
