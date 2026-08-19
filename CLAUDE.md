# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## このリポジトリについて

[slipshow](https://github.com/panglesd/slipshow)（v0.11.0 "Brazlip"）で作るプレゼン資料を格納する。

1 デッキ = 1 ディレクトリ。入口は `main.md` で、frontmatter はここにだけ書く。章ごとの本文は `parts/` に分け、`main.md` から `{include src=parts/....md}` で並べる。ほかにデッキ固有の `style.css`（無いデッキもある）、素材ディレクトリ、生成された `main.html`。`about-mp4/` が最初の実例、`showcase/` は slipshow の機能を実物で引くためのリファレンスデッキ。

デッキ間で使い回す CSS はリポジトリ直下の `_shared/` に置く（`ja.css` が日本語デッキ共通の調整、`layout.css` が言語非依存のレイアウトユーティリティ）。デッキ側は frontmatter の `css:` から相対パスで列挙する：

```
css: ../_shared/ja.css ../_shared/layout.css style.css
```

列挙順がそのまま CSS の優先順位になるので、デッキ固有の `style.css` は最後に置く。`@import` は使わない。slipshow は `css:` に列挙した各ファイルを HTML へ `<style>` としてインライン展開するため、`@import` の相対パスは単体 HTML の中では解決できず壊れる。

章をファイルに分けるのは、全章を 1 つの slip に収める都合で `>` の入れ子が深くなり、編集が困難になるため。`main.md` 側では `{#part-container}` + `----` のグループで全 include を括り、1 つの slip に閉じ込めている。

ビルド設定ファイル（Makefile / package.json / dune など）は持たない。slipshow CLI を直接実行する。

## slipshow CLI

パッケージマネージャ管理ではなく、単体バイナリを PATH に置いている：
`~/bin/slipshow` → `~/opt/slipshow-linux-x86_64/bin/slipshow`

`slipshow --version` は `%%VERSION%%: Brazlip` を返す（バージョン文字列が展開されていないリリースビルド）。数値バージョンを取る手段がないので、コードネーム `Brazlip` = v0.11.0 が唯一の手掛かり。

```bash
slipshow serve about-mp4/main.md      # ホットリロード付きプレビュー（既定 :8080、-p で変更）
slipshow compile about-mp4/main.md    # HTML を生成
slipshow compile about-mp4/main.md --watch
slipshow themes list                  # 組み込みテーマ（default / vanier / none）
slipshow markdown about-mp4/main.md   # 属性を除去した素の Markdown を出力
slipshow lsp --stdio                  # エディタから呼ばれる LSP サーバ
```

- `-o` を省略すると **ソースと同じディレクトリ**に `<名前>.html` を生成する（カレントディレクトリではない）。
- Markdown 内の相対パス（画像・動画・frontmatter の `css:` / `js:`）は、**その記述がある .md ファイルからの相対**で解決される。そのためリポジトリルートを起点に実行してよい。
- **`{include}` した部分ファイルの中も、その部分ファイルからの相対になる。** `parts/` から素材を指すには `../demo/...` と書く。`main.md` からの相対ではない。間違えても warning が出るだけで終了コードは 0（次節）。

## ビルドの落とし穴：参照先が無くてもビルドは成功する

画像や動画のパスが存在しない場合、slipshow は warning を出すだけで **終了コード 0 で完了する**。生成された HTML には `src` を持たない `<video>` / `<img>` が残り、デッキは黙って壊れる。

終了コードでは検知できないので、compile の出力に warning が無いことを毎回確認する。`-q` を付けてもこの warning は抑制されない。

## 生成される HTML の性質

CSS・画像・動画（base64 data URI）・MathJax・highlight.js・slipshow 本体の JS が、すべて 1 ファイルにインライン展開される。単体で開けば動作する代わりに、内容が少なくても 3〜4 MB になる。

`.md` から常に再生成できるビルド成果物。このリポジトリは空の initial commit が 1 つあるだけで、`.gitignore` も無く、CLAUDE.md も `about-mp4/` もまだ追跡されていない。最初の `git add` の際に、HTML を含めるかどうかをユーザーに確認する。

## 日本語デッキのフォント指定と箱ラベルの和訳

組み込みテーマの font-family は和文グリフを持たない。そのため日本語のデッキは frontmatter で `_shared/ja.css` を読み込み、body と等幅要素の font-family を上書きする（実装は `_shared/ja.css` 自身のコメント参照）。

`.definition` `.theorem` などの箱ラベル（7 章「箱」相当）も組み込みテーマが `:before` の `content` プロパティで英語を埋め込んでいる。`content` は通常の上書きでは効かず、セレクタごと書き直す必要があるため、`_shared/ja.css` がそれも兼ねている。テーマのバージョンが上がってラベルの文言や `title` 付きの組み立て方（`"Definition (" attr(title) ") "` の形）が変わったら、ここも追随が要る。

## diff を色付きで見せる

同梱の highlight.js は `diff` 文法を持っているので、フェンスを ` ```diff ` にすれば削除行が赤地、追加行が緑地、`@@` が青で描かれる。追加の仕込みは要らない。

条件は **unified 形式であること**。`diff` の既定出力（`<` と `>` の形式）には色が付かないので、`diff -U1` のように明示して出力を取る。

## slipshow のハマりどころ

原因特定に時間がかかったもの。いずれもコンパイルは成功するので気付きにくい。

- **`{pause}` はスクロールしない。** 積み上がった要素は画面外に出たままになる。要素の直前行（空行なし）に `{.remark pause scroll}` のように書くと `scroll-at-unpause` が付き、収まらないときだけスクロールする。
- **`up` は対象を画面最上部へ送る。** その上にある動画は必ず押し出される。動画を見せたまま次を出すなら `scroll`、動画の下に本文を置くなら先に `up=<video-id>` で動画を上げる。
- **章ごとに `{slip}` を分けない。** 分けると境界に空ステップが生じ、入る前後で 1.13 倍の中途半端なズームも挟まる（テーマの `.slip-body` が持つ左右 110px の余白が原因）。上流サンプルも 1 つの slip に章を並べている。`{slip}` は寄り道や 3 カラムなど、ズームして潜りたい箇所にだけ使う。
- **pause の後ろにある要素は、画面内に入っていても opacity 0 で見えない。** 次章の見出しが覗くのを防ぐための余白は不要。
- **subslip のズーム倍率は親に対する幅で決まる。** 親と同じ幅だと 1 倍でズームせず、脇道に見えない。`width: 40%` 程度で約 2.5 倍。
- **`vh` は slip の中では位置決めに使わない。** `vh` はブラウザの実ビューポート基準、slip の中身は `dimension:` 由来の論理座標系で動く。ブラウザの縦横比が `dimension:` より縦長だと、レターボックス（上下の余白）の分だけ `vh` 由来の高さが実際より膨張する。縦位置は `center` / `up` / `down` / `scroll` アクションで合わせること。`center` は要素の中心を画面中心に置くので、要素の高さがどうであれウィンドウ形状に関わらず安定する。
- **`play-media` は 2 度目が発火しない。** 複数箇所で自動再生するなら `autoplay muted loop` を使う。
- **再生できない動画に `play-media` を付けるとステップ送りが完全に止まる。** 前にも後ろにも進めず、コンソールにエラーも出ない。
- **`serve` は静的ファイルを配信しない。** `demo/x.mp4` は 404。素の `<video src="...">` は base64 埋め込みを避けられるが serve では見えない（compile 後に直接開けば見える）。
- **`serve` のルートは殻ページで、デッキ本文は別経路（polling）で届く。** `curl http://127.0.0.1:8080/` の中身に本文は無いため、反映の確認を curl で行うと「変わっていない」と誤判定する。ブラウザで見ること。`{include}` 先の部分ファイルを編集してもホットリロードは効く。
- **テーマの UI は body のスタイルを継承する。** `body { line-height }` が `#slipshow-counter` の枠を縦に伸ばすので line-height を個別に戻す。`#slipshow-toc` は本文と同じ見出しサイズのままだと日本語の項目が折り返して読めないので、font-size を個別に縮める。

## ステップの機構（ソースで確認済み）

`src/engine/runtime/step/action_scheduler.ml` の `next` が本体。読めば挙動はすべて説明できる。

- **1 ステップ = DOM 上で次に見つかるアクション属性 1 つ。**
- **slip の出入りはステップを消費しない。** `exit` は次のアクションを見つけた時点で、そのアクションと同じステップ内で呼ばれる。脱出のために区切りを置く必要はない。ただし subslip の末尾に `{step}` を置くと、その 1 ステップが `exit` の受け皿になり、ズームアウトだけを独立して見せられる（公式 `actions-api.rst` が `step` を "Useful to exit entered slips" と書くのはこの用途）。
- **`{step}` は「何もしないアクション」で、それ自体が 1 ステップを食う。** 画面が変わらないステップの正体はたいていこれ。上流サンプルの章ファイルには `slip` も `step` も書かれていない。
- **`auto-continue` で空ステップは消せない。** `activate` が実行時にその属性を DOM から削除するため、エンジンが確認する時点で対象の `pause` が既に剥がれている。同じ理由で `play-media` の 2 度目も発火しない。
- 上流のソースとサンプルは `git clone --depth 1 https://github.com/panglesd/slipshow.git`、サンプルは `example/undo-monad-short/`。

## 表示崩れの検証

ステップを送りながら要素の座標を実測すると、画面外へ出る箇所を機械的に洗い出せる。スクロールはアニメーションするので、`.slip-body` の位置が安定するまで待ってから測らないと誤検出する（待たずに測って 18 件中 17 件が誤検出だった）。

「何も起きないステップ」を探すときは、可視状態の差分ではなく次の 2 つを使う。可視判定は opacity の遷移とタイミングがずれ、誤検出が出る。

- **実行ログ**: slipshow は `Activating <action> by <element>` を console に出す。`console.log` をフックすれば各ステップの実行内容が分かる。
- **画面の写し**: 可視要素の位置を全部集めて文字列化し、前後で比較する。`#slipshow-counter` は毎回変わるので除外する。

ヘッドレスブラウザ（puppeteer 等）で自動検証する場合、**プレゼン本体は `about:srcdoc` の内部 iframe（`#slipshow__internal_iframe`）の中にある**。トップページの `document` には iframe とスクリプトしかなく、`page.evaluate` をトップフレームに対して行うと要素が 1 つも見つからず誤って「異常なし」と判定する。`page.frames()` から `about:srcdoc` の URL を持つフレームを取り、そちらに対して DOM 検査・キー入力後の状態確認を行うこと。ステップ送り（ArrowRight）の成否は可視状態の差分ではなく、`#slipshow-counter` の表示テキストが変わったかで判定する方が確実（`up` 等のアニメーション中は次の入力を engine 側が無視するため、固定 wait だけだと偽陽性の「空ステップ」を検出する）。

## ツールと公開

- Bento4 1.6.0-641 を `~/.local/share/bento4/` に置き、`~/.local/bin` から `mp4dump` `mp4info` `mp4edit` `mp4extract` を symlink している。`mp4dump --verbosity 2` で stco のエントリ値まで出る。
- `slipshow serve` は 127.0.0.1 固定で bind オプションがない。tailnet に見せるには `tailscale serve --bg --http=8080 http://127.0.0.1:8080`（解除は `tailscale serve --http=8080 off`）。
- developer.apple.com の仕様書は JS 描画なので WebFetch では空が返る。ブラウザで開けば読める。

## GitHub Pages への公開

`main` への push で `.github/workflows/deploy.yml` が自動デプロイする。公開先は
https://yewton.github.io/my-slipshows/ 、デッキごとの URL は `<公開先>/<デッキ名>/`。

- デッキを追加したら `site/index.html` の一覧にリンクを足すこと。デッキの検出自体は
  `*/main.md` のグロブなので CI 側の変更は不要。
- CI は compile の出力が 1 バイトでもあれば失敗させる。「ビルドの落とし穴」節の通り
  参照先の欠落は warning のみで終了コード 0 になるため、`-q` でも消えないこの warning を
  出力の有無で検知している（成功時の compile は完全に無出力なことを確認済み）。
- リリース tar（`slipshow-linux-x86_64.tar`）の中身はトップレベルの `bin/slipshow` のみ。
  ローカルの `~/opt/slipshow-linux-x86_64/bin/slipshow` のような中間ディレクトリは無い。

## 構文リファレンス

Markdown 拡張構文（`{pause}` `{step}` `{slip}` `{.block}` や属性記法）は上流ドキュメントを参照する。CLAUDE.md には転記しない。v0.11.0 に固定した URL：

https://github.com/panglesd/slipshow/tree/v0.11.0/docs

| ファイル | 内容 |
| --- | --- |
| `slipshow-syntax.rst` | 拡張構文の基本 |
| `frontmatter.rst` | `dimension` / `theme` / `css` / `js` / `highlightjs-theme` / `attributes` / `external-ids` |
| `attributes-ref.rst`, `actions-api.rst` | 属性とアクションの一覧 |
| `groups-and-layouts.rst`, `visual-structure.rst`, `grouping.rst` | slip の分割とレイアウト |
| `math.rst`, `mermaid.rst`, `tikz.rst`, `manim.rst` | 数式・図 |
| `split-in-multiple-files.rst` | 複数ファイルへの分割 |
| `themes.rst`, `write-your-own-theme.rst` | テーマの選択と自作 |
| `record-and-replay.rst`, `use-speaker-view.rst`, `shortcuts.rst` | 発表時の機能 |
