# my-slipshows

[slipshow](https://github.com/panglesd/slipshow) で作ったプレゼン資料を格納するリポジトリです。

## 公開ページ

`main` ブランチへの push をトリガーに GitHub Actions がビルド・デプロイします。

- https://yewton.github.io/my-slipshows/ — デッキ一覧
- https://yewton.github.io/my-slipshows/about-mp4/ — バイナリを触って学ぶ MP4
- https://yewton.github.io/my-slipshows/showcase/ — slipshow ショーケース

## 構成

1 デッキ = 1 ディレクトリで、入口は各ディレクトリの `main.md` です。デッキ間で使い回す CSS は
`_shared/` に、ランディングページのソースは `site/index.html` に置いています。

## ローカルでのプレビュー

[slipshow CLI](https://github.com/panglesd/slipshow/releases) が必要です。

```bash
slipshow serve about-mp4/main.md   # ホットリロード付きプレビュー（既定 http://localhost:8080）
slipshow serve showcase/main.md

slipshow compile about-mp4/main.md # 単体 HTML を生成（CSS・動画などをすべてインライン展開）
```

## 素材のクレジット

`about-mp4/demo/intro-*.mp4` は *Big Buck Bunny*（© 2008 Blender Foundation, CC BY 3.0,
https://peach.blender.org）を素材に、バイナリ書き換えのみで加工したものです。生成手順は
`about-mp4/demo/make_demos.py` の docstring に記載しています。
