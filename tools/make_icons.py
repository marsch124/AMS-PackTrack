#!/usr/bin/env python3
"""Generate the AMS PackTrack app icons (no third-party libraries).

House rule (see memory: icon style clean & handmade) — flat, calm background,
NO glow, NO neon. A cream ground, the app's kraft ring from the order cards,
and a hand-drawn parcel inside it: box, lid line, tape band. Strokes carry
only a whisper of wobble so it reads as drawn, not as a scrawl.
"""
import math, struct, zlib, os

OUT = os.path.join(os.path.dirname(__file__), "..", "icons")
os.makedirs(OUT, exist_ok=True)

# ---- colours (from the app's light theme) ----
TOP = (250, 244, 236)    # cream, slightly lighter up top
BOT = (240, 228, 213)    # warmer cream at the bottom
KRAFT = (176, 106, 53)   # #b06a35 — ring + parcel outline
CARD = (226, 190, 152)   # the parcel's soft cardboard fill


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def smoothstep(e0, e1, x):
    if e1 == e0:
        return 0.0 if x < e0 else 1.0
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def wobble(ax, ay, bx, by, S, seed, pieces=4, amp=0.0035):
    """Split a line into sub-segments with a tiny deterministic jitter."""
    def rnd(i):
        v = math.sin(seed * 127.1 + i * 311.7) * 43758.5453
        return (v - math.floor(v)) * 2 - 1
    nx, ny = -(by - ay), (bx - ax)
    L = math.hypot(nx, ny) or 1.0
    nx, ny = nx / L, ny / L
    pts = []
    for i in range(pieces + 1):
        t = i / pieces
        off = rnd(i) * amp * S if 0 < i < pieces else 0.0
        pts.append((ax + (bx - ax) * t + nx * off, ay + (by - ay) * t + ny * off))
    return [(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) for i in range(pieces)]


def dist_to_segment(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


CARD_TOP  = (236, 208, 176)   # lid, catching the light
CARD_LEFT = (223, 186, 146)   # left face
CARD_RIGHT= (206, 165, 124)   # right face, in shade


def in_poly(x, y, poly):
    """even-odd ray casting"""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            if x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                inside = not inside
        j = i
    return inside


def render(size, ss, rounded, scale):
    S = size * ss
    px = bytearray(S * S * 4)
    cx = cy = S / 2.0
    corner = S * 0.225 if rounded else 0.0

    # ---- the kraft ring ----
    ring_r = S * 0.355 * scale * 2
    ring_hw = S * 0.030
    ring_feather = S * 0.006

    # ---- an isometric shipping box, drawn by hand ----
    hw = S * 0.185 * scale * 2       # half-width
    dy = S * 0.080 * scale * 2       # how far the lid tilts away
    bh = S * 0.175 * scale * 2       # body height
    yT = cy - (2 * dy + bh) / 2.0    # very top of the lid

    T  = (cx,      yT)               # lid: back corner
    L  = (cx - hw, yT + dy)          # lid: left corner
    R  = (cx + hw, yT + dy)          # lid: right corner
    B  = (cx,      yT + 2 * dy)      # lid: front corner (top of the seam)
    BL = (cx - hw, yT + dy + bh)     # bottom-left
    BR = (cx + hw, yT + dy + bh)     # bottom-right
    BB = (cx,      yT + 2 * dy + bh) # bottom-front

    top_face   = [T, L, B, R]
    left_face  = [L, B, BB, BL]
    right_face = [R, B, BB, BR]

    stroke = S * 0.017
    feather = S * 0.006
    tape_hw = hw * 0.16              # the tape band running over the lid

    segs = []
    segs += wobble(*T, *L, S, 1)
    segs += wobble(*T, *R, S, 2)
    segs += wobble(*L, *B, S, 3)
    segs += wobble(*R, *B, S, 4)
    segs += wobble(*L, *BL, S, 5)
    segs += wobble(*R, *BR, S, 6)
    segs += wobble(*B, *BB, S, 7)     # the front seam
    segs += wobble(*BL, *BB, S, 8)
    segs += wobble(*BR, *BB, S, 9)
    segs += wobble(*L, *R, S, 10)     # tape across the lid

    for y in range(S):
        ty = y / (S - 1)
        base = lerp(TOP, BOT, ty)
        row = y * S * 4
        for x in range(S):
            col = list(base)

            # --- the three cardboard faces ---
            if in_poly(x, y, top_face):
                col = list(CARD_TOP)
            elif in_poly(x, y, left_face):
                col = list(CARD_LEFT)
            elif in_poly(x, y, right_face):
                col = list(CARD_RIGHT)

            # --- hand-drawn strokes ---
            dmin = 1e9
            for (ax, ay, bx, by) in segs:
                d = dist_to_segment(x, y, ax, ay, bx, by)
                if d < dmin:
                    dmin = d
                    if dmin < stroke * 0.4:
                        break
            a_core = 1.0 - smoothstep(stroke, stroke + feather, dmin)
            if a_core > 0:
                col = list(lerp(col, KRAFT, a_core))

            # --- the ring ---
            rd = abs(math.hypot(x - cx, y - cy) - ring_r)
            a_ring = 1.0 - smoothstep(ring_hw, ring_hw + ring_feather, rd)
            if a_ring > 0:
                col = list(lerp(col, KRAFT, a_ring))

            # rounded-corner alpha mask
            alpha = 255
            if rounded:
                ddx = max(0.0, abs(x - cx) - (S / 2 - corner))
                ddy = max(0.0, abs(y - cy) - (S / 2 - corner))
                cd = math.hypot(ddx, ddy)
                alpha = int(round(255 * (1.0 - smoothstep(corner - 1.0, corner + 0.5, cd))))

            o = row + x * 4
            px[o] = int(max(0, min(255, col[0])))
            px[o + 1] = int(max(0, min(255, col[1])))
            px[o + 2] = int(max(0, min(255, col[2])))
            px[o + 3] = alpha

    return downsample(px, S, ss), size


def downsample(px, S, ss):
    out_size = S // ss
    out = bytearray(out_size * out_size * 4)
    inv = 1.0 / (ss * ss)
    for y in range(out_size):
        for x in range(out_size):
            r = g = b = a = 0
            for dy in range(ss):
                sy = (y * ss + dy) * S * 4
                for dx in range(ss):
                    o = sy + (x * ss + dx) * 4
                    r += px[o]; g += px[o + 1]; b += px[o + 2]; a += px[o + 3]
            o = (y * out_size + x) * 4
            out[o] = int(r * inv); out[o + 1] = int(g * inv)
            out[o + 2] = int(b * inv); out[o + 3] = int(a * inv)
    return out


def write_png(path, rgba, size):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        raw += rgba[y * size * 4:(y + 1) * size * 4]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    for size, ss, rounded, scale, name in [
        (512, 3, True,  0.50, "icon-512.png"),
        (192, 3, True,  0.50, "icon-192.png"),
        (180, 3, True,  0.50, "icon-180.png"),
        (512, 3, False, 0.42, "icon-512-maskable.png"),
    ]:
        print(f"Rendering {name}…")
        rgba, _ = render(size, ss, rounded=rounded, scale=scale)
        write_png(os.path.join(OUT, name), rgba, size)
    print("Done →", os.path.abspath(OUT))
