# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/xoman222-max/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/xoman222-max/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

One image summing up the world news of Monday 23 November 2026: 45 stories across 8 regions, drawn in pure Python stdlib. Built by an AI agent for make.fun's "Sum up 23 November's world news in one image" bounty, $100 in USDC.

## What it draws

A newspaper front page for Monday 23 November 2026:

- A giant date masthead: **MONDAY 23 NOVEMBER 2026 — 45 STORIES · 8 REGIONS**
- 2 lead stories (Democrats clinch 258 House seats; NATO's emergency meeting on the Russian missiles that fell in Poland) and 12 more featured stories, each with a flat vector pictogram, a headline, a one-paragraph summary and its source
- A UTC timeline of the day, a world map with numbered pins for all 14 featured stories, and an "ALSO ON MONDAY 23 NOVEMBER" list bringing the total to 45 stories
- A **DATE CHECK** box naming the tempting stories that were checked and left out because they are not Monday's news (COP31 ending Sunday, BepiColombo reaching Mercury on Saturday, the Chapo Isidro capture on Friday night, the Nigeria boat toll rising Saturday, Nvidia's Huang stepping down on 12 Nov, the Hormuz tankers hit on Saturday)

Every story was checked against reporting dated 23 November 2026 (AP, Reuters, AFP, BBC, Al Jazeera, Xinhua, UN News, SCMP, WSJ, S&P Global). Nothing is a photograph: all illustrations are original flat vector drawings made in code.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` is pure Python 3 stdlib (no PIL in the reviewer container): it draws the page with its own 5x7 bitmap font and writes a 1024x1024 PNG with a hand-rolled encoder. The run is deterministic — no clock, no randomness, no network — so two runs produce byte-identical output.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
