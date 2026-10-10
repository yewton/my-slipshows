{pause up=part5-title}

{#part5-title}
# 5. mdhd と timescale

向きの謎は解けました。次は、冒頭の動画の**速さ**です。

## mdhd

`mdia` > `mdhd` の中の **timescale**。「1 秒を何目盛りに刻むか」の値です。

{pause scroll}
```text
mdhd の構造（version = 0 の場合）

+0   version(1) + flags(3)
+4   creation_time      (4)
+8   modification_time  (4)
+12  timescale          (4)   ★ ここ
+16  duration           (4)
```

{pause up}

## 倍速にする

```text
$ xxd -s 24247 -l 32 00-original.mp4
00005eb7: 0000 0020 6d64 6864 0000 0000 0000 0000  ... mdhd........
00005ec7: 0000 0000 0000 3c00 0001 2c00 55c4 0000  ......<...,.U...
                    ^^^^^^^^^ ^^^^^^^^^
                    timescale duration
```

{pause scroll}
```text
変更前:  00 00 3c 00     (15360)     1 秒 = 15360 目盛り
変更後:  00 00 78 00     (30720)     1 秒 = 30720 目盛り
```

{.remark pause scroll}
> `duration` は 76800 のまま。目盛りの刻みだけを倍にしたので、
> 76800 ÷ 15360 = **5 秒**だった動画が 76800 ÷ 30720 = **2.5 秒**になります。
>
> 同じデータを倍の速さで読んでいるだけですね。

{pause up=video-speed-demo play-media=video-speed-demo}

![](../demo/01-speed.mp4){video #video-speed-demo width=30%}

{pause scroll}
```text
$ cmp --verbose 00-original.mp4 01-speed.mp4 | wc -l
1
```

{.remark pause scroll}
フィールドは 4 バイトですが、実際に変わったのは 1 バイトだけ。

{pause up}

## 冒頭の 5 バイト

これで、冒頭の動画を直した 5 バイトの正体が全部わかりました。

```text
tkhd の matrix     a と d を -1.0 → +1.0  4 バイト   向きが直る
mdhd の timescale  0x1800 → 0x3000        1 バイト   速さが直る
                                     計 5 バイト
```

{.block pause scroll}
`mdat` の映像データには 1 バイトも触っていません。
**箱の中の「再生のしかた」を書き換えただけ**です。

{pause up}

## 補足：version と flags

---
`mdhd` も FullBox です。[mp4box.js の mdhd](https://github.com/gpac/mp4box.js/blob/v2.4.1/src/boxes/mdhd.ts) を見ると、`version` は duration などの bit 長に影響。

```ts
    if (this.version === 1) {
      this.creation_time = stream.readUint64();
      this.modification_time = stream.readUint64();
      this.timescale = stream.readUint32();
      this.duration = stream.readUint64();
    } else {
      this.creation_time = stream.readUint32();
      this.modification_time = stream.readUint32();
      this.timescale = stream.readUint32();
      this.duration = stream.readUint32();
    }
```

---

{pause scroll}
---
`flags` は未使用。

```ts
    this.flags = 0;
```
---

{pause up}

## もう一つ、同じサイズの書き換え

`udta`（user data。メタデータ置き場）の **type 4 文字だけ**を書き換えます。

```text
$ xxd -s 26508 -l 16 00-original.mp4
0000678c: 0000 0062 7564 7461 0000 005a 6d65 7461  ...budta...Zmeta

変更前:  00 00 00 62 75 64 74 61     size=98, type='udta'
変更後:  00 00 00 62 66 72 65 65     size=98, type='free'
```

{pause scroll}
`free` は読み飛ばされる箱なので、サイズを変えずにメタデータが消えます。
