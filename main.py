#!/usr/bin/env python3
"""The World Today - Friday 27 November 2026.

Draws a 1024x1024 newspaper front page summing up the real world news of
Friday 27 November 2026 and writes it to /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png).

Pure standard library only: a hand-rolled rasterizer, a 5x7 bitmap font and
a PNG encoder built on zlib. No network, no randomness, no clock reads, so
every run writes byte-identical output.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font -----
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, written as strings of
# '#' (ink) and '.' (blank). Only the characters the page needs are defined;
# everything is rendered in capitals.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}

CHAR_W, CHAR_H = 5, 7


def text_width(text, scale):
    """Pixel width of text at the given scale (6 px advance per glyph)."""
    return len(text) * 6 * scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines fitting max_width pixels."""
    words = text.split(' ')
    lines, cur = [], ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas -----
class Canvas:
    """An RGB raster with filled shapes, lines, circles and bitmap text."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def _put(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = color

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            row = color * (x1 - x0)
            self.px[base:base + (x1 - x0) * 3] = row

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def frame(self, x, y, w, h, color, t=1):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self._put(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            self.rect(cx - dx, yy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, t=2):
        for k in range(t):
            rr = r - k
            for a in range(360):
                import math
                x = cx + int(rr * math.cos(math.radians(a)))
                y = cy + int(rr * math.sin(math.radians(a)))
                self._put(x, y, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2),
                                     (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.rect(xa, yy, xb - xa + 1, 1, color)

    def text(self, x, y, s, scale, color):
        """Draw upper-cased text; unknown glyphs become a blank."""
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[' '])
            for row in range(CHAR_H):
                bits = glyph[row]
                for col in range(CHAR_W):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_centred(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)


# ----------------------------------------------------------------- png ------
def write_png(path, canvas):
    """Encode the canvas as a deterministic 8-bit RGB PNG."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack('>I', len(data)) + kind + data
        out += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack('>IIBBBBB', canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)

# -------------------------------------------------------------- palette ----
INK = bytes((18, 18, 20))          # near-black text
PAPER = bytes((250, 247, 238))     # newsprint cream
NAVY = bytes((14, 30, 58))         # masthead
NAVY_LT = bytes((28, 52, 92))
RED = bytes((178, 34, 34))         # lead accent / rules
GOLD = bytes((198, 148, 44))
GREY = bytes((105, 105, 110))
LIGHT = bytes((232, 228, 216))     # panel separators
WHITE = bytes((255, 255, 255))
BLUE = bytes((31, 84, 160))
ORANGE = bytes((224, 110, 30))
TEAL = bytes((18, 128, 122))
GREEN = bytes((46, 125, 50))
PURPLE = bytes((102, 60, 145))
BROWN = bytes((122, 74, 34))

# -------------------------------------------------------------- stories ----
# Every story below happened, or was first reported, on Friday 27 Nov 2026,
# as carried by the wire services that day. Headline + short factual summary.
STORIES = [
    dict(kicker="MIDDLE EAST", accent=RED, icon="flame",
         headline="HOUTHI STRIKE HITS SAUDI ARAMCO REFINERY",
         body="A Houthi attack on the Jazan refinery kills one worker and "
              "halts some operations. The Saudi-led coalition answers with "
              "strikes on Sanaa, Hodeidah and Saada, and two missiles aimed "
              "at Riyadh are intercepted overnight."),
    dict(kicker="UKRAINE", accent=BLUE, icon="drone",
         headline="RUSSIA LAUNCHES 155 DRONES OVERNIGHT",
         body="Air defences down 110 of the drones, 83 of them jet-powered "
              "Shaheds, but strikes hit 27 sites and one man is killed in "
              "Zaporizhzhia. Estonia warns of an air threat and scrambles "
              "NATO jets over possible drone activity."),
    dict(kicker="EUROPE", accent=NAVY_LT, icon="stars",
         headline="EU LEADERS FAIL TO AGREE THE BUDGET",
         body="After more than 12 hours of talks in Brussels, leaders leave "
              "the 2028-2034 budget unsettled. Twenty-four states back a "
              "45-billion-euro loan for Ukraine in 2027, with a final "
              "decision put off until December."),
    dict(kicker="GAZA", accent=BROWN, icon="ruins",
         headline="TEN KILLED IN GAZA AS STRIKES GO ON",
         body="Israeli strikes kill ten Palestinians across Gaza, hospital "
              "officials say, including senior Hamas official Khaled Abu "
              "Nada in Deir al-Balah - the third senior Hamas figure killed "
              "since Tuesday."),
    dict(kicker="NEW ZEALAND", accent=TEAL, icon="ballot",
         headline="DEADLOCKED PARLIAMENT AFTER FINAL COUNT",
         body="The final election count leaves the ruling coalition with 65 "
              "of 130 seats, one short of a majority. The centrist "
              "Opportunity Party, new to parliament with seven seats, now "
              "decides the next government."),
    dict(kicker="MARKETS", accent=GREEN, icon="barrel",
         headline="BRENT NEARS $98 AS TANKER ATTACKS LIFT OIL",
         body="Brent crude climbs to about $97.71 a barrel, on track for its "
              "first weekly gain in four weeks after attacks on tankers in "
              "the Strait of Hormuz and on Saudi energy sites. Gold steadies "
              "near $3,565 an ounce."),
    dict(kicker="HEALTH", accent=PURPLE, icon="virus",
         headline="CONGO EBOLA OUTBREAK PASSES 12,000 CASES",
         body="Confirmed infections reach 12,021 with 5,904 deaths, health "
              "ministry data shows, as fighting in Ituri forces responders "
              "to pull out of affected areas."),
]

# ----------------------------------------------------------------- icons ---
def draw_icon(cv, kind, x, y, s, accent):
    """A small pictogram inside a s x s box at (x, y)."""
    cx, cy = x + s // 2, y + s // 2
    if kind == "flame":
        hw, hh = int(s * 0.34), int(s * 0.42)
        cv.triangle(cx - hw, cy + hh, cx, cy - hh, cx + hw, cy + hh, ORANGE)
        cv.triangle(cx - hw // 2, cy + hh, cx, cy - hh // 3, cx + hw // 2,
                    cy + hh, GOLD)
        cv.rect(x + 6, cy + hh, s - 12, 6, INK)
    elif kind == "drone":
        cv.rect(cx - 22, cy - 3, 44, 6, INK)
        cv.rect(cx - 3, cy - 22, 6, 44, INK)
        for dx, dy in ((-22, -22), (22, -22), (-22, 22), (22, 22)):
            cv.disc(cx + dx, cy + dy, 9, accent)
            cv.disc(cx + dx, cy + dy, 4, WHITE)
    elif kind == "stars":
        cv.disc(cx, cy, 28, BLUE)
        import math
        for k in range(12):
            a = math.radians(k * 30 - 90)
            cv.disc(cx + int(19 * math.cos(a)), cy + int(19 * math.sin(a)),
                    3, GOLD)
    elif kind == "ruins":
        cv.rect(x + 8, cy - 4, 22, 34, INK)
        cv.rect(x + 38, cy + 8, 26, 22, BROWN)
        cv.triangle(x + 38, cy + 8, x + 51, cy - 8, x + 64, cy + 8, BROWN)
        cv.rect(x + 70, cy - 16, 16, 46, GREY)
        cv.line(x + 8, cy - 4, x + 30, cy - 4, RED)
    elif kind == "ballot":
        cv.rect(x + 14, cy - 6, 52, 36, accent)
        cv.rect(x + 14, cy - 6, 52, 8, NAVY)
        cv.line(cx - 12, cy + 8, cx - 2, cy + 18, WHITE)
        cv.line(cx - 2, cy + 18, cx + 16, cy - 6, WHITE)
        cv.rect(x + 22, cy + 30, 36, 6, INK)
    elif kind == "barrel":
        cv.rect(x + 18, cy - 26, 44, 52, accent)
        cv.rect(x + 18, cy - 14, 44, 4, INK)
        cv.rect(x + 18, cy + 10, 44, 4, INK)
        cv.text(x + 32, cy - 6, "$", 2, WHITE)
    elif kind == "virus":
        cv.disc(cx, cy, 18, accent)
        import math
        for k in range(8):
            a = math.radians(k * 45)
            cv.line(cx + int(16 * math.cos(a)), cy + int(16 * math.sin(a)),
                    cx + int(28 * math.cos(a)), cy + int(28 * math.sin(a)),
                    accent)
            cv.disc(cx + int(28 * math.cos(a)), cy + int(28 * math.sin(a)),
                    3, accent)
        cv.disc(cx - 6, cy - 5, 3, WHITE)
        cv.disc(cx + 6, cy + 4, 3, WHITE)


# -------------------------------------------------------------- layout -----
def draw_masthead(cv):
    cv.rect(0, 0, W, 132, NAVY)
    cv.rect(0, 132, W, 4, GOLD)
    cv.text_centred(W // 2, 18, "THE WORLD TODAY", 6, WHITE)
    cv.text_centred(W // 2, 84, "FRIDAY 27 NOVEMBER 2026", 3, GOLD)
    cv.text(24, 100, "ONE DAY - ONE PAGE - THE WORLD", 1, bytes((160, 175, 200)))
    cv.text(W - 24 - text_width("SEVEN STORIES THAT MATTERED", 1), 100,
            "SEVEN STORIES THAT MATTERED", 1, bytes((160, 175, 200)))


def draw_lead(cv, story, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.frame(x, y, w, h, INK, 2)
    cv.rect(x, y, w, 34, story["accent"])
    cv.text(x + 16, y + 9, story["kicker"] + "  -  LEAD STORY", 2, WHITE)
    tx = x + 20
    ty = y + 52
    lines = wrap_text(story["headline"], 4, w - 240)
    for ln in lines:
        cv.text(tx, ty, ln, 4, INK)
        ty += 34
    ty += 8
    for ln in wrap_text(story["body"], 2, w - 240):
        cv.text(tx, ty, ln, 2, INK)
        ty += 20
    draw_icon(cv, story["icon"], x + w - 200, y + 70, 170, story["accent"])
    cv.text(x + w - 200, y + h - 26, "JAZAN, SAUDI ARABIA", 1, GREY)


def draw_cell(cv, story, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.frame(x, y, w, h, LIGHT, 1)
    cv.rect(x, y, 6, h, story["accent"])
    cv.text(x + 18, y + 12, story["kicker"], 2, story["accent"])
    ty = y + 40
    for ln in wrap_text(story["headline"], 2, w - 150):
        cv.text(x + 18, ty, ln, 2, INK)
        ty += 19
    ty += 4
    for ln in wrap_text(story["body"], 1, w - 150)[:5]:
        cv.text(x + 18, ty, ln, 1, INK)
        ty += 11
    draw_icon(cv, story["icon"], x + w - 118, y + h - 108, 96,
              story["accent"])


def draw_footer(cv):
    y = 972
    cv.rect(0, y, W, 2, RED)
    cv.text_centred(W // 2, y + 12,
                    "COMPILED FROM WIRE REPORTS OF FRIDAY 27 NOVEMBER 2026",
                    1, GREY)
    cv.text_centred(W // 2, y + 28,
                    "THE WORLD TODAY - THE DAY IN ONE PAGE", 1, GREY)

# ----------------------------------------------------------------- main ----
def build_page():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    lead, rest = STORIES[0], STORIES[1:]
    draw_lead(cv, lead, 12, 148, W - 24, 250)
    cell_w, cell_h, gap = 496, 176, 8
    gx, gy = 12, 410
    for i, story in enumerate(rest):
        cx = gx + (i % 2) * (cell_w + gap)
        cy = gy + (i // 2) * (cell_h + gap)
        draw_cell(cv, story, cx, cy, cell_w, cell_h)
    draw_footer(cv)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, build_page())
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
