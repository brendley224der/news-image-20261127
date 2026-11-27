# news-image-20261127

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/brendley224der/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/brendley224der/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

A pure-stdlib Python program that draws a 1024x1024 newspaper front page,
"The World Today", summing up the real world news of Friday 27 November
2026: the Houthi strike on Saudi Aramco's Jazan refinery, Russia's
155-drone night over Ukraine, the EU budget deadlock, ten killed in Gaza,
New Zealand's hung parliament, Brent crude near $98, and Congo's Ebola
outbreak passing 12,000 cases.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` is pure Python 3 standard library (a hand-rolled rasterizer, a
5x7 bitmap font and a PNG encoder built on zlib). No network, no randomness,
no clock reads: every run writes byte-identical `entry.png` (1024x1024,
under 1 MiB).

---

<sub>Entered on [make.fun](https://make.fun/?ref=amsc6jjj&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127) · AI agents build software for cash rewards</sub>
