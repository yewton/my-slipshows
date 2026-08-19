{pause up=part11-title}

{#part11-title}
# 11. カスタムスクリプト

`exec` アクションで任意の JavaScript を実行できる。

{pause up}

## 基本形

{pause scroll}
```markdown
{#script-target}
Hello World!

{exec}
```slip-script
document.querySelector("#script-target").style.background = "red"
```
```

{pause scroll}
{#script-target style="display:inline-block; padding:0.3em 0.6em"}
Hello World!

{pause exec}
```slip-script
document.querySelector("#script-target").style.background = "#ffd27a"
```

{.remark pause scroll}
このまま戻る方向にステップを送っても、背景色は元に戻らない。**undo を書いていないため**。

{pause up}

## `slip` API を使えば undo は自動で入る

自前の副作用ではなく `slip.setStyle` / `slip.setClass` / `slip.setProp` などの API 経由で
変更すると、slipshow が「戻すときの操作」を自動的に記録する。

{pause scroll}
```markdown
{exec}
```slip-script
slip.setStyle(document.querySelector("#script-target"), "background", "#a9e5a0")
```
```

{pause scroll}
{pause exec}
```slip-script
slip.setStyle(document.querySelector("#script-target"), "background", "#a9e5a0")
```

{.remark pause scroll}
この段の背景色は、戻る方向にステップを送ると元に戻る（試してみてほしい）。

{pause up}

## API で足りないときは `slip.onUndo`

API がカバーしない副作用（テキストの書き換えなど）は、`return {undo: () => {...}}` か
`slip.onUndo(callback)` で自分の undo 手続きを登録する。

{pause scroll}
```markdown
{exec}
```slip-script
let e = document.querySelector("#script-target");
let old = e.innerText;
e.innerText = "書き換えた";
slip.onUndo(() => { e.innerText = old });
```
```

{pause up}
