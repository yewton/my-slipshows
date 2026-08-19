#!/usr/bin/env python3
"""デッキ（../main.md と ../parts/）が使うデモ素材を、原本 2 本からのバイナリ書き換えだけで生成する。

デッキの主張が「映像データに触らずに再生を変える」なので、ここでも再エンコードはしない。
box のオフセットは決め打ちせず、毎回ファイルの構造を辿って求める。

原本（このスクリプトでは生成しない。消したら取り直しが必要）:
  intro-original.mp4  Big Buck Bunny (CC BY 3.0, (c) 2008 Blender Foundation) の
                      320x180 版 https://peach.blender.org から 1:44 以降を 5 秒切り出したもの。
                      slipshow は動画を base64 で HTML に埋め込むので、原本の時点で軽くしておく
                      （-c copy で切り出すと 432KB になり、3 箇所で使うため HTML が 2MB 太る）。
                        ffmpeg -i BigBuckBunny_320x180.mp4 -ss 104 -t 5 -an \
                               -c:v libx264 -crf 28 -preset slow intro-original.mp4
                      切り出した直後は edts/elst（編集リスト）が再生範囲を 5 秒に固定するため、
                      timescale を変えても尺が伸びない。type を free に潰して無効化してある。
                        off, _, _ = find_box(buf, [b"moov", b"trak", b"edts"]) の off+4 を b"free" に
  00-original.mp4     ffmpeg の testsrc で生成したもの
                        ffmpeg -f lavfi -i testsrc=size=320x240:rate=30:duration=5 \
                               -c:v libx264 -pix_fmt yuv420p 00-original.mp4

使い方:
  python3 make_demos.py        # 派生 4 本を再生成し、冒頭で見せる diff を表示する
"""
import struct
import subprocess
import tempfile
from pathlib import Path

DEMO = Path(__file__).resolve().parent
NEG_ONE = struct.pack(">i", -65536)  # 16.16 固定小数点の -1.0


def find_box(data, path, start=0, end=None):
    """path（例 [b"moov", b"trak", b"tkhd"]）を辿り (offset, size, payload_offset) を返す。"""
    end = len(data) if end is None else end
    want, rest = path[0], path[1:]
    off = start
    while off + 8 <= end:
        size = struct.unpack(">I", data[off : off + 4])[0]
        typ = data[off + 4 : off + 8]
        hdr = 8
        if size == 1:  # size == 1 なら type の直後の 8 バイトが実際の大きさ
            size = struct.unpack(">Q", data[off + 8 : off + 16])[0]
            hdr = 16
        elif size == 0:  # size == 0 はファイル末尾まで
            size = end - off
        if typ == want:
            if not rest:
                return off, size, off + hdr
            return find_box(data, rest, off + hdr, off + size)
        off += size
    raise KeyError(b"/".join(path).decode())


def double_timescale(buf):
    """mdhd の timescale を 2 倍にする。duration はそのままなので倍速で読まれる。"""
    _, _, mdhd = find_box(buf, [b"moov", b"trak", b"mdia", b"mdhd"])
    off = mdhd + 12  # version(1) + flags(3) + creation_time(4) + modification_time(4)
    old = struct.unpack(">I", buf[off : off + 4])[0]
    buf[off : off + 4] = struct.pack(">I", old * 2)
    return f"timescale {old} -> {old * 2} @{off}"


def halve_timescale(buf):
    """mdhd の timescale を半分にする。目盛りが粗くなるので、同じデータが倍の時間をかけて流れる。"""
    _, _, mdhd = find_box(buf, [b"moov", b"trak", b"mdia", b"mdhd"])
    off = mdhd + 12  # version(1) + flags(3) + creation_time(4) + modification_time(4)
    old = struct.unpack(">I", buf[off : off + 4])[0]
    buf[off : off + 4] = struct.pack(">I", old // 2)
    return f"timescale {old} -> {old // 2} @{off}"


def rotate_180(buf):
    """tkhd の変換行列の a と d を -1.0 にする。原点対称、つまり 180 度回転。"""
    _, _, tkhd = find_box(buf, [b"moov", b"trak", b"tkhd"])
    # version 1 では creation/modification/duration が 64bit になり、行列の位置が 12 バイト後ろへ動く
    m = tkhd + (52 if buf[tkhd] == 1 else 40)
    buf[m : m + 4] = NEG_ONE  # a
    buf[m + 16 : m + 20] = NEG_ONE  # d
    return f"matrix a,d -> -1.0 @{m},{m + 16}"


def build(src_name, dst_name, *ops):
    src = (DEMO / src_name).read_bytes()
    buf = bytearray(src)
    notes = [op(buf) for op in ops]
    (DEMO / dst_name).write_bytes(buf)
    changed = sum(1 for a, b in zip(src, buf) if a != b)
    print(f"{dst_name}: {'; '.join(notes)}  (実差分 {changed} バイト / 全体 {len(buf)} バイト)")


# 冒頭デモ: 聴衆に最初に見せる、上下が反転していて間延びした状態の動画。
# ここから intro-original.mp4（正しい向きと速さ）へ戻すのが冒頭の題材になる。
build("intro-original.mp4", "intro-upside-slow.mp4", rotate_180, halve_timescale)

# 冒頭で「素直にやるとこうなる」と対置するための再エンコード版。
# このスクリプトで唯一、映像を作り直しているファイル。サイズが激減することを見せるために置く。
# -r 24 は必須。setpts は PTS を詰めるだけで出力 fps は入力の 12 を引き継ぐため、
# 指定しないとフレームが半分に間引かれ、書き換え版との比較が不公平になる。
subprocess.run([
    "ffmpeg", "-hide_banner", "-loglevel", "error",
    "-i", str(DEMO / "intro-upside-slow.mp4"),
    "-vf", "hflip,vflip,setpts=0.5*PTS", "-r", "24", "-an",
    str(DEMO / "intro-reencoded.mp4"), "-y",
], check=True)
print(f"intro-reencoded.mp4: ffmpeg で再エンコード "
      f"({(DEMO / 'intro-upside-slow.mp4').stat().st_size:,} バイト -> "
      f"{(DEMO / 'intro-reencoded.mp4').stat().st_size:,} バイト)")

# 倍速だけ
build("00-original.mp4", "01-speed.mp4", double_timescale)

# 回転だけ
build("00-original.mp4", "02-rotate.mp4", rotate_180)

# mdat の直前に中身のない free box を挟む。box のルールには一切違反しないが、
# mdat 以降が 8 バイト後ろへ動くので、stco が持つ絶対オフセットが指す先が嘘になる。
# デッキ本文に載せた head/printf/tail の手順と同じ結果になる。
src = (DEMO / "00-original.mp4").read_bytes()
mdat_off, _, _ = find_box(src, [b"mdat"])
(DEMO / "05-broken.mp4").write_bytes(src[:mdat_off] + b"\x00\x00\x00\x08free" + src[mdat_off:])
print(f"05-broken.mp4: mdat (@{mdat_off}) の直前に free box 8 バイトを挿入")

def show_hex_diff(a, b, label_a, label_b, context=1):
    """デッキに貼る unified diff を、本文の ```diff ブロックと同じ形で出す。

    unified 形式なのは highlight.js に色を付けさせるため。`<` `>` の既定形式では
    変更行が色分けされない。前後 1 行の文脈も残す。ASCII 欄に箱の名前が出るので、
    変更がどの箱で起きたかが行を数えずに分かる。
    """
    cmd = (f"$ diff -U{context} --label {label_a} --label {label_b} "
           f"<(xxd {label_a}) <(xxd {label_b})")
    with tempfile.TemporaryDirectory() as tmp:
        dumps = []
        for src in (a, b):
            dst = Path(tmp) / f"{len(dumps)}.hex"
            dst.write_text(subprocess.run(["xxd", str(src)],
                                          capture_output=True, text=True).stdout)
            dumps.append(str(dst))
        out = subprocess.run(
            ["diff", f"-U{context}", "--label", label_a, "--label", label_b, *dumps],
            capture_output=True, text=True).stdout
    print(f"\n{cmd}")
    print(out, end="")


# 冒頭のスライドに載せている diff。数字がずれたら本文を直すこと。
# 向きは「聴衆に見せた壊れた状態 → 直した状態」。
show_hex_diff(DEMO / "intro-upside-slow.mp4", DEMO / "intro-original.mp4",
              "before.mp4", "after.mp4")

# 5 章「答え合わせ」の 2 本。FFmpeg に -display_rotation で正解を作らせ、
# 手で書き換えた 02-rotate.mp4 と突き合わせる。-c copy なので映像は触られない。
# 行列の 4 バイト以外に btrt の avgBitrate も動くが、これは再多重化のときに
# FFmpeg が 0 のままだった欄を埋めたもので、回転とは関係ない。
with tempfile.TemporaryDirectory() as tmp:
    ref = Path(tmp) / "ref.mp4"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-display_rotation", "180", "-i", str(DEMO / "00-original.mp4"),
        "-c", "copy", str(ref), "-y",
    ], check=True)
    print("\n$ ffmpeg -display_rotation 180 -i sample.mp4 -c copy ref.mp4")
    show_hex_diff(DEMO / "00-original.mp4", ref, "sample.mp4", "ref.mp4")
    show_hex_diff(DEMO / "02-rotate.mp4", ref, "sample-rotated.mp4", "ref.mp4")
