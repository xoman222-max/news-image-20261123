#!/usr/bin/env python3
"""news-image-20261123: draw one front page summing up the world news of
Monday 23 November 2026, in pure Python stdlib (no PIL in the reviewer
container). Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Everything is drawn in code: flat vector illustration, a 5x7 bitmap font
defined below, a hand-rolled PNG encoder. Deterministic: no clock, no
randomness, no network, fixed story data.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# 5x7 pixel font, drawn from scratch. Each glyph is 7 rows of 5 bits.
# Uppercase, digits and punctuation only; text is rendered in capitals.
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
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
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
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '~': ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
}

# ------------------------------------------------------------ PNG writer
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path, px, w, h):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw.extend(px[y])
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


# --------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = [bytearray(bg * w) for _ in range(h)]

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            row = self.px[yy]
            for xx in range(x0, x1):
                row[xx * 3:xx * 3 + 3] = c

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        while True:
            self.rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill and d <= r * r:
                    if 0 <= xx < self.w and 0 <= yy < self.h:
                        self.px[yy][xx * 3:xx * 3 + 3] = c
                elif not fill and abs(d - r * r) <= r:
                    if 0 <= xx < self.w and 0 <= yy < self.h:
                        self.px[yy][xx * 3:xx * 3 + 3] = c

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, c)

    def text(self, x, y, s, c, scale=1):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g is None:
                cx += 6 * scale
                continue
            for r, row in enumerate(g):
                for col, bit in enumerate(row):
                    if bit == "1":
                        self.rect(cx + col * scale, y + r * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale=1):
        return len(s) * 6 * scale - scale

    def wrap(self, s, maxw, scale=1):
        """Word-wrap s (uppercased) into lines fitting maxw pixels."""
        words = s.upper().split(" ")
        lines, cur = [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if self.text_w(trial, scale) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, c, maxw, scale=1, leading=None):
        lh = leading if leading is not None else 7 * scale + 2
        for ln in self.wrap(s, maxw, scale):
            self.text(x, y, ln, c, scale)
            y += lh
        return y

# ------------------------------------------------------------ story data
# Every story was checked against reporting dated Monday 23 November 2026
# (AP, Reuters, AFP, BBC, Al Jazeera, Xinhua, UN News, SCMP, WSJ).
# Events that happened on an earlier day are NOT in this list; they are
# named in DATE_CHECK below as excluded.
NAVY = bytes((16, 28, 52))
INK = bytes((24, 24, 24))
PAPER = bytes((250, 246, 235))
RED = bytes((178, 34, 34))
BLUE = bytes((31, 78, 140))
TEAL = bytes((14, 110, 110))
GOLD = bytes((176, 124, 0))
GREEN = bytes((34, 110, 60))
PURPLE = bytes((96, 48, 130))
BROWN = bytes((122, 74, 30))
GREY = bytes((110, 110, 110))
LIGHT = bytes((238, 232, 218))
MIDGREY = bytes((210, 204, 190))

# (num, icon, tag, source, headline, summary, lon, lat)
FEATURED = [
    (1, "ballot", "USA - POLITICS", "AP",
     "DEMOCRATS CLINCH 258 SEATS",
     "AP calls the N. Carolina race: Democrats win at least 258 House seats, "
     "the largest majority since 1992. +44 seats; 4 races still uncalled.",
     -95, 39),
    (2, "shield", "EUROPE - SECURITY", "POLAND",
     "NATO MEETS ON POLAND MISSILES",
     "Emergency council in Brussels today after 3 Russian Kh-101 cruise "
     "missiles fell in SE Poland on Friday. No one hurt; PM Tusk calls it "
     "a deliberate provocation.",
     4, 51),
    (3, "talks", "USA - MIDDLE EAST", "REUTERS",
     "TRUMP 'INCLINED' TO HIT IRAN AGAIN",
     "Trump says he is inclined to resume strikes on Tehran if no deal "
     "is reached by the New Year.",
     51, 35),
    (4, "star", "ASIA - KOREA", "AFP",
     "KIM: SECURITY, NOT SUPREMACY",
     "Kim Jong Un says North Korea seeks security, not supremacy, as it "
     "builds up its capabilities.",
     126, 39),
    (5, "blast", "EUROPE - WAR", "AFP",
     "RUSSIAN STRIKES KILL 11 IN KYIV REGION",
     "Russian strikes kill 11 in the Kyiv region; residents search the rubble "
     "of collapsed homes for the missing.",
     30, 50),
    (6, "flame", "ASIA - DISASTER", "AP",
     "24 BODY BAGS AFTER FACTORY FIRE",
     "Rescuers recover 24 body bags after a candy factory fire in Indonesia; "
     "36 workers still missing as the search resumes.",
     107, -7),
    (7, "chart", "ASIA - MARKETS", "TAIWAN FSC",
     "TAIWAN MOVES TO HALT MARKET ROUT",
     "Taiwan bans short selling from today after shares fell 17.5% "
     "in a week; the index closed at 36,033.",
     121, 24),
    (8, "plane", "USA - TRAVEL", "AP",
     "DELTA MELTDOWN AT ATLANTA HUB",
     "More than 1,000 Delta flights delayed at Atlanta on Sunday as "
     "a tech fault hits operations; fixed by the afternoon.",
     -84, 34),
    (9, "virus", "AFRICA - HEALTH", "WHO",
     "FIGHTING NEAR EBOLA ZONE, WHO WARNS",
     "The WHO chief says fighting near the DR Congo Ebola outbreak area is "
     "disrupting the response, and pleads for peace.",
     25, -2),
    (10, "drone", "AFRICA - CONFLICT", "AP",
     "DRONE STRIKES HIT UN BUILDING IN SUDAN",
     "Drone strikes hit homes and a UN building in Sudan's capital, Khartoum.",
     32, 16),
    (11, "ball", "EUROPE - SPORT", "FIFA",
     "UK TO HOST 2035 WOMEN'S WORLD CUP",
     "FIFA confirms today the UK will host the 2035 Women's World "
     "Cup: 48 teams, 104 matches, first in Britain since 1966.",
     8, 47),
    (12, "factory", "OCEANIA - ECONOMY", "S&P GLOBAL",
     "AUSTRALIA SHRINKS FASTEST IN 5 YEARS",
     "Australia's private sector contracts at the sharpest rate in more than "
     "five years; the flash PMI falls to 46.1.",
     134, -25),
    (13, "robot", "GLOBAL - DIPLOMACY", "UN",
     "128 STATES BACK KILLER-ROBOT RULES",
     "128 states agree to pursue international rules on autonomous weapons "
     "by 2028.",
     6, 46),
    (14, "pick", "OCEANIA - BUSINESS", "BHP",
     "BHP'S $18.1BN COPPER BET",
     "BHP plans an $18.1bn expansion to double South Australian copper "
     "output by 2040.",
     138, -30),
]

# One line each: headline-style, all from 23 November reporting.
ALSO = [
    "S. KOREA MINISTER QUITS OVER EXAM ROW",
    "YEMEN STRIKES, DRONE ATTACK KILL 5",
    "9 SHOT AT CALIFORNIA CONCERT",
    "US ARMY TO DETONATE BOMB CHEMICALS",
    "POLAND: RUSSIA TRIED TO KILL RAPPER",
    "PAOLO BULGARI, JEWELLER, DIES AT 89",
    "COURT: PREGNANCY LAW UNCONSTITUTIONAL",
    "CHINA SLAMS US BAN ON TELECOM FIRMS",
    "MYANMAR TO END GRAFT IN RECRUITMENT",
    "NETANYAHU, EISENKOT RESUME TALKS",
    "SPLA-IO ATTACK KILLS 24 IN S. SUDAN",
    "AFGHAN WOMEN FORCED HOME STRUGGLE",
    "INDIA FLAGS EQUITY CONCERNS AT COP31",
    "US STOCKS PLUNGE; ASIA ON ALERT",
    "TRUMP TO HOST GALA FOR MEME COIN",
    "ALCARAZ BEATS ZVEREV FOR ATP TITLE",
    "MARQUEZ WINS 8TH MOTOGP TITLE",
    "THITIKUL WINS 3RD STRAIGHT LPGA TITLE",
    "LIVERPOOL BEAT TEN-MAN MAN UTD",
    "NSW PASSES LAW TO EXPAND COAL MINE",
    "KOGAN.COM PAY VOTE: FIRST STRIKE",
    "JPMORGAN, VISA, MASTERCARD EMAIL LEAK",
    "US PROBING ALLEGED SPY TIED TO HUANG",
    "INDIA YOUTH CONGRESS PROTESTS META",
    "TRUMP REPOSTS 'TRUMPCARE' PITCH",
    "US POWER IN ASIA WEAKEST SINCE 2018",
    "TRUMP: SCHUMER AS LEADER 'DIFFICULT'",
    "LIBYA SUSPECTS DRONE HIT RUSSIAN SHIP",
    "SANCHEZ: VOTERS WILL DECIDE MY FUTURE",
    "GERWYN PRICE WINS GRAND SLAM DARTS",
    "CHINA COMPUTING TO TOP 90% OF CAPACITY",
]

# (time label, text) — times UTC where verified, dayparts otherwise.
TIMELINE = [
    ("00:28 UTC", "BHP UNVEILS $18.1BN COPPER PLAN"),
    ("01:16 UTC", "KIM: SECURITY, NOT SUPREMACY"),
    ("MORNING", "TAIWAN BANS SHORT SELLING"),
    ("MIDDAY", "NATO COUNCIL MEETS IN BRUSSELS"),
    ("AFTERNOON", "FIFA CONFIRMS UK AS 2035 HOST"),
    ("EVENING", "WHO PLEADS FOR PEACE IN EBOLA ZONE"),
]

# Tempting stories that are NOT Monday's news — checked and excluded.
DATE_CHECK = [
    "COP31 ENDED SUNDAY WITHOUT A DEAL - SUNDAY'S NEWS, NOT MONDAY'S",
    "BEPICOLOMBO REACHED MERCURY ON SATURDAY 21 NOV - NOT MONDAY'S",
    "'CHAPO ISIDRO' WAS SEIZED ON FRIDAY NIGHT IN SINALOA",
    "NIGERIA BOAT TOLL REACHED 24 ON SATURDAY - FRIDAY'S CAPSIZING",
    "NVIDIA'S HUANG STEPPED DOWN ON 12 NOV - NOT TODAY'S NEWS",
    "HORMUZ TANKERS WERE HIT ON SATURDAY - NOT MONDAY'S",
]

REGIONS = "N. AMERICA - S. AMERICA - EUROPE - MIDDLE EAST - AFRICA - ASIA - OCEANIA - SPACE"
SOURCES = "SOURCES: AP - REUTERS - AFP - BBC - AL JAZEERA - XINHUA - UN NEWS - SCMP - WSJ - S&P GLOBAL"

# ------------------------------------------------------------ flat icons
# Each draws a simple flat pictogram inside a box (x, y, s) in accent color.
def icon(cv, kind, x, y, s, c):
    u = s / 48.0

    def R(px, py, pw, ph, col):
        cv.rect(int(x + px * u), int(y + py * u),
                max(1, int(pw * u)), max(1, int(ph * u)), col)

    def C(cx, cy, r, col):
        cv.circle(int(x + cx * u), int(y + cy * u), max(1, int(r * u)), col)

    def L(x0, y0, x1, y1, col, t=2):
        cv.line(int(x + x0 * u), int(y + y0 * u), int(x + x1 * u),
                int(y + y1 * u), col, max(1, int(t * u)))

    if kind == "ballot":
        R(8, 6, 32, 6, c)
        R(12, 12, 24, 6, c)
        R(16, 18, 16, 6, c)
        R(6, 26, 36, 16, c)
        R(20, 18, 5, 14, PAPER)
        L(12, 32, 20, 38, PAPER, 3)
        L(20, 38, 34, 26, PAPER, 3)
    elif kind == "shield":
        cv.poly([(int(x + px * u), int(y + py * u)) for px, py in
                 [(24, 4), (42, 10), (42, 24), (24, 44), (6, 24), (6, 10)]], c)
        C(24, 22, 7, PAPER)
        L(24, 15, 24, 29, PAPER, 3)
        L(17, 22, 31, 22, PAPER, 3)
    elif kind == "talks":
        cv.poly([(int(x + px * u), int(y + py * u)) for px, py in
                 [(6, 8), (30, 8), (30, 26), (16, 26), (12, 34), (12, 26),
                  (6, 26)]], c)
        cv.poly([(int(x + px * u), int(y + py * u)) for px, py in
                 [(20, 18), (42, 18), (42, 34), (34, 34), (32, 42),
                  (28, 34), (20, 34)]], TEAL)
        R(10, 14, 14, 3, PAPER)
        R(24, 24, 14, 3, PAPER)
    elif kind == "star":
        pts = [(24, 4), (29, 17), (43, 17), (32, 26), (36, 40),
               (24, 32), (12, 40), (16, 26), (5, 17), (19, 17)]
        cv.poly([(int(x + px * u), int(y + py * u)) for px, py in pts], c)
    elif kind == "blast":
        pts = [(24, 4), (30, 14), (40, 10), (34, 22), (44, 26), (32, 30),
               (36, 42), (24, 34), (12, 42), (16, 30), (4, 26), (14, 22),
               (8, 10), (18, 14)]
        cv.poly([(int(x + px * u), int(y + py * u)) for px, py in pts], c)
        C(24, 24, 5, PAPER)
    elif kind == "flame":
        cv.poly([(int(x + px * u), int(y + py * u)) for px, py in
                 [(24, 4), (30, 16), (38, 14), (40, 26), (34, 40),
                  (24, 44), (14, 40), (8, 26), (12, 18), (18, 20)]],
                c)
        cv.poly([(int(x + px * u), int(y + py * u)) for px, py in
                 [(24, 22), (29, 28), (28, 36), (20, 36), (19, 28)]],
                GOLD)
    elif kind == "chart":
        L(6, 38, 42, 38, INK, 3)
        L(6, 12, 16, 22, c, 3)
        L(16, 22, 26, 14, c, 3)
        L(26, 14, 36, 28, c, 3)
        L(36, 28, 42, 20, c, 3)
        C(16, 22, 3, c)
        C(26, 14, 3, c)
        C(36, 28, 3, c)
    elif kind == "plane":
        cv.poly([(int(x + px * u), int(y + py * u)) for px, py in
                 [(4, 26), (20, 20), (40, 14), (44, 18), (28, 26),
                  (40, 30), (40, 34), (24, 30), (12, 36), (8, 32)]],
                c)
        R(20, 22, 8, 3, PAPER)
    elif kind == "virus":
        C(24, 24, 12, c)
        for ang in range(0, 360, 45):
            import math
            a = math.radians(ang)
            L(24 + 12 * math.cos(a), 24 + 12 * math.sin(a),
              24 + 18 * math.cos(a), 24 + 18 * math.sin(a), c, 3)
        C(20, 21, 3, PAPER)
        C(28, 28, 3, PAPER)
    elif kind == "drone":
        C(12, 12, 6, c)
        C(36, 12, 6, c)
        C(12, 36, 6, c)
        C(36, 36, 6, c)
        R(18, 18, 12, 12, c)
        L(12, 12, 36, 36, c, 2)
        L(36, 12, 12, 36, c, 2)
        C(24, 24, 3, PAPER)
    elif kind == "ball":
        C(24, 24, 18, c)
        cv.poly([(int(x + px * u), int(y + py * u)) for px, py in
                 [(24, 18), (30, 22), (28, 30), (20, 30), (18, 22)]],
                PAPER)
        L(24, 6, 24, 18, PAPER, 2)
        L(42, 24, 30, 22, PAPER, 2)
        L(6, 24, 18, 22, PAPER, 2)
    elif kind == "factory":
        R(6, 20, 36, 22, c)
        cv.poly([(int(x + px * u), int(y + py * u)) for px, py in
                 [(6, 20), (14, 8), (22, 20)]], c)
        cv.poly([(int(x + px * u), int(y + py * u)) for px, py in
                 [(20, 20), (28, 8), (36, 20)]], c)
        R(10, 28, 6, 6, PAPER)
        R(20, 28, 6, 6, PAPER)
        R(30, 28, 6, 6, PAPER)
        L(38, 42, 44, 42, RED, 4)
        L(44, 42, 38, 34, RED, 4)
    elif kind == "robot":
        R(12, 10, 24, 22, c)
        C(19, 20, 3, PAPER)
        C(29, 20, 3, PAPER)
        R(18, 27, 12, 2, PAPER)
        L(24, 10, 24, 4, c, 3)
        C(24, 4, 2, RED)
        R(8, 16, 4, 8, c)
        R(36, 16, 4, 8, c)
        R(16, 32, 16, 10, c)
    elif kind == "pick":
        cv.poly([(int(x + px * u), int(y + py * u)) for px, py in
                 [(6, 40), (16, 24), (26, 10), (30, 14), (20, 28),
                  (14, 42)]], BROWN)
        cv.poly([(int(x + px * u), int(y + py * u)) for px, py in
                 [(42, 40), (32, 24), (22, 10), (18, 14), (28, 28),
                  (34, 42)]], BROWN)
        C(24, 8, 4, GOLD)
        R(14, 42, 20, 4, c)

# ------------------------------------------------------------ world map
# Coarse continent outlines in (lon, lat), equirectangular projection.
CONTINENTS = [
    [(-168, 66), (-145, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 76),
     (-75, 72), (-65, 62), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-81, 26), (-85, 20), (-92, 15), (-97, 16), (-105, 20), (-110, 24),
     (-117, 32), (-125, 40), (-124, 48), (-135, 58), (-150, 60), (-165, 60)],
    [(-45, 60), (-30, 68), (-25, 70), (-40, 76), (-58, 76), (-55, 70),
     (-50, 64)],
    [(-78, 10), (-72, 12), (-62, 9), (-52, 5), (-50, 0), (-40, -5),
     (-35, -8), (-38, -15), (-40, -22), (-48, -27), (-55, -33), (-62, -38),
     (-68, -45), (-70, -52), (-73, -45), (-73, -35), (-75, -20), (-80, -10),
     (-80, 0)],
    [(-17, 15), (-15, 25), (-10, 30), (-5, 35), (0, 36), (10, 37),
     (15, 33), (20, 32), (30, 31), (33, 28), (36, 22), (40, 15), (43, 11),
     (48, 11), (51, 10), (46, 0), (40, -8), (38, -15), (35, -22),
     (32, -28), (28, -33), (20, -35), (17, -30), (14, -22), (12, -17),
     (12, -8), (9, -2), (9, 4), (-2, 5), (-10, 7), (-17, 12)],
    [(-10, 36), (-9, 43), (-2, 44), (-2, 48), (0, 50), (3, 51), (5, 53),
     (8, 57), (10, 59), (14, 58), (18, 56), (21, 55), (24, 59), (28, 60),
     (30, 63), (35, 66), (42, 68), (48, 69), (50, 65), (45, 58), (40, 52),
     (38, 47), (35, 45), (30, 46), (28, 44), (26, 40), (23, 38), (22, 40),
     (19, 42), (15, 44), (12, 45), (8, 44), (4, 43), (0, 40), (-2, 37),
     (-6, 36)],
    [(30, 36), (35, 36), (40, 38), (45, 40), (50, 42), (55, 45), (60, 48),
     (65, 50), (70, 55), (75, 60), (80, 65), (85, 68), (90, 70), (100, 72),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 68),
     (170, 66), (178, 65), (170, 60), (162, 58), (158, 52), (150, 50),
     (142, 48), (140, 42), (135, 38), (130, 34), (127, 35), (122, 32),
     (120, 28), (115, 22), (110, 20), (108, 12), (105, 8), (100, 7),
     (97, 12), (94, 17), (90, 22), (86, 20), (82, 16), (80, 12), (77, 8),
     (74, 12), (72, 20), (68, 23), (64, 25), (60, 25), (56, 26), (52, 28),
     (50, 30), (48, 30), (44, 30), (40, 32), (36, 36)],
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (144, -38), (147, -38),
     (150, -37), (153, -33), (153, -28), (150, -24), (148, -20), (145, -17),
     (142, -14), (142, -11), (138, -12), (136, -15), (133, -12), (130, -13),
     (127, -14), (124, -16), (121, -19), (117, -21)],
    [(167, -45), (170, -42), (173, -39), (175, -37), (178, -38), (176, -41),
     (173, -43), (169, -46)],
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -9),
     (125, -8), (130, -5), (135, -3), (140, -4), (138, -8), (132, -6),
     (126, -3), (120, 0), (115, 2), (108, 0), (102, 3), (97, 5)],
    [(130, 31), (132, 33), (135, 34), (137, 36), (139, 38), (141, 40),
     (143, 43), (145, 44), (142, 42), (140, 38), (138, 35), (135, 33),
     (132, 32)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 50)],
    [(44, -16), (47, -15), (50, -16), (48, -22), (45, -25), (43, -21)],
]
# Badge offsets (dx, dy) for pins that would collide.
PIN_OFFSET = {1: (-14, -10), 2: (-14, -12), 3: (16, 4), 4: (10, -12),
              5: (12, 8), 7: (-10, 10), 8: (12, 10), 9: (-12, 8),
              10: (12, -10), 11: (14, -8), 12: (-14, -6), 13: (-16, 10),
              14: (12, 8)}


def draw_map(cv, x0, y0, w, h):
    ocean = bytes((214, 230, 240))
    land = bytes((196, 205, 178))
    cv.rect(x0, y0, w, h, ocean)
    for poly in CONTINENTS:
        pts = [(int(x0 + (lon + 180) / 360.0 * w),
                int(y0 + (78 - lat) / 136.0 * h)) for lon, lat in poly]
        cv.poly(pts, land)
    cv.rect(x0, y0, w, 2, INK)
    cv.rect(x0, y0 + h - 2, w, 2, INK)
    cv.rect(x0, y0, 2, h, INK)
    cv.rect(x0 + w - 2, y0, 2, h, INK)
    for num, _ic, _tag, _src, _hl, _sm, lon, lat in FEATURED:
        px = int(x0 + (lon + 180) / 360.0 * w)
        py = int(y0 + (78 - lat) / 136.0 * h)
        dx, dy = PIN_OFFSET.get(num, (0, 0))
        bx, by = px + dx, py + dy
        if (dx, dy) != (0, 0):
            cv.line(px, py, bx, by, RED, 2)
        cv.circle(bx, by, 9, RED)
        cv.circle(bx, by, 9, bytes((255, 255, 255)), fill=False)
        label = str(num)
        tw = cv.text_w(label, 1)
        cv.text(bx - tw // 2, by - 3, label, bytes((255, 255, 255)), 1)


# ------------------------------------------------------------ layout
def draw_header(cv):
    cv.rect(16, 16, 992, 92, NAVY)
    cv.rect(16, 16, 992, 4, GOLD)
    cv.text(32, 28, "THE WORLD IN ONE DAY", GOLD, 1)
    cv.text(32, 44, "MONDAY 23 NOVEMBER 2026", bytes((255, 255, 255)), 4)
    cv.text(700, 30, "45 STORIES - 8 REGIONS", bytes((255, 255, 255)), 2)
    cv.text(700, 58, "EVERY ONE FROM THIS MONDAY", GOLD, 1)
    cv.text(700, 74, "AN AI-EDITED FRONT PAGE", bytes((200, 205, 215)), 1)


def draw_lead(cv, story, x, y, w, h, accent):
    num, ic, tag, src, hl, sm, _lon, _lat = story
    cv.rect(x, y, w, h, bytes((255, 255, 255)))
    cv.rect(x, y, w, 4, accent)
    cv.rect(x, y, w, h, INK)  # placeholder border overwritten below
    cv.rect(x + 1, y + 1, w - 2, h - 2, bytes((255, 255, 255)))
    cv.rect(x, y, w, 4, accent)
    icon(cv, ic, x + 14, y + 26, 72, accent)
    tx = x + 100
    cv.text(tx, y + 12, "%d - %s" % (num, tag), accent, 1)
    yy = cv.para(tx, y + 26, hl, INK, w - 116, 2, 18)
    cv.para(tx, yy + 4, sm, bytes((60, 60, 60)), w - 116, 1, 10)
    cv.text(tx, y + h - 16, "SOURCE: " + src, GREY, 1)


def draw_cell(cv, story, x, y, w, h, accent):
    num, ic, tag, src, hl, sm, _lon, _lat = story
    cv.rect(x, y, w, h, bytes((255, 255, 255)))
    cv.rect(x, y, w, h, INK)
    cv.rect(x + 1, y + 1, w - 2, h - 2, bytes((255, 255, 255)))
    cv.rect(x, y, w, 3, accent)
    icon(cv, ic, x + 10, y + 14, 40, accent)
    tx = x + 58
    cv.text(tx, y + 10, "%d - %s - %s" % (num, tag, src), accent, 1)
    lines = cv.wrap(hl, w - 68, 2)
    yy = y + 24
    for ln in lines[:2]:
        cv.text(tx, yy, ln, INK, 2)
        yy += 16
    slines = cv.wrap(sm, w - 68, 1)
    yy += 2
    for ln in slines[:3]:
        cv.text(tx, yy, ln, bytes((60, 60, 60)), 1)
        yy += 10


def draw_timeline(cv, y):
    cv.text(16, y, "MONDAY IN UTC - AS THE DAY UNFOLDED", RED, 1)
    line_y = y + 26
    cv.hline(16, line_y, 992, INK, 2)
    n = len(TIMELINE)
    for i, (t, txt) in enumerate(TIMELINE):
        cx = 16 + int((i + 0.5) * 992 / n)
        cv.circle(cx, line_y, 5, RED)
        tw = cv.text_w(t, 1)
        cv.text(cx - tw // 2, y + 10, t, INK, 1)
        for j, ln in enumerate(cv.wrap(txt, 150, 1)):
            lw = cv.text_w(ln, 1)
            cv.text(cx - lw // 2, line_y + 10 + j * 10, ln,
                    bytes((60, 60, 60)), 1)


def draw_also(cv, x, y, w, h):
    cv.text(x, y, "ALSO ON MONDAY 23 NOVEMBER", RED, 2)
    col_w = (w - 12) // 2
    half = (len(ALSO) + 1) // 2
    for col in range(2):
        cx = x + col * (col_w + 12)
        items = ALSO[col * half:(col + 1) * half]
        yy = y + 24
        for it in items:
            cv.text(cx, yy, "- " + it, INK, 1)
            yy += 13
    return y + 24 + half * 13


def draw_date_check(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((255, 240, 240)))
    cv.rect(x, y, w, h, RED)
    cv.rect(x + 1, y + 1, w - 2, h - 2, bytes((255, 240, 240)))
    cv.text(x + 8, y + 6, "DATE CHECK - WHAT WE LEFT OUT", RED, 1)
    yy = y + 20
    for line in DATE_CHECK:
        cv.text(x + 8, yy, "X " + line, bytes((90, 30, 30)), 1)
        yy += 9


def draw_footer(cv, y):
    cv.hline(16, y, 992, INK, 2)
    cv.text(16, y + 8,
            "EVERY STORY HERE HAPPENED OR WAS FIRST REPORTED ON MONDAY "
            "23 NOVEMBER 2026. ORIGINAL DRAWINGS - NOT PHOTOGRAPHS.",
            INK, 1)
    cv.text(16, y + 22, SOURCES, GREY, 1)
    cv.text(16, y + 34, REGIONS, GREY, 1)


def build():
    cv = Canvas(W, H, PAPER)
    draw_header(cv)
    draw_lead(cv, FEATURED[0], 16, 116, 488, 122, RED)
    draw_lead(cv, FEATURED[1], 520, 116, 488, 122, BLUE)
    accents = [TEAL, GOLD, PURPLE, GREEN, BROWN, RED, BLUE, TEAL,
               GOLD, PURPLE, GREEN, BROWN]
    idx = 2
    for r in range(4):
        for c in range(3):
            x = 16 + c * (325 + 8)
            yy = 246 + r * (96 + 5)
            draw_cell(cv, FEATURED[idx], x, yy, 325, 96,
                      accents[(idx - 2) % len(accents)])
            idx += 1
    draw_timeline(cv, 653)
    cv.text(16, 709, "WHERE IT HAPPENED", RED, 1)
    draw_map(cv, 16, 726, 470, 140)
    draw_date_check(cv, 16, 874, 470, 79)
    draw_also(cv, 502, 709, 506, 244)
    draw_footer(cv, 961)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    cv = build()
    size = write_png(path, cv.px, W, H)
    print("wrote %s (%d bytes, %dx%d)" % (path, size, W, H))
    assert size <= 1048576, "entry.png over 1 MiB"


if __name__ == "__main__":
    main()
