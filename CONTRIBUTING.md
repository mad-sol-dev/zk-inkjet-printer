# Contributing

Written by Claude (Opus 5.5); read and checked by the maintainer,
@mad-sol-dev.

Help is welcome, and the maintainer wants to encourage it. You do not need
to write code to make a difference here. So far everything rests on a single
printer, so a report about a second one is worth more than most patches.

## You own one of these printers

Open an [issue](https://github.com/mad-sol-dev/zk-inkjet-printer/issues) and
tell us what you have. Any of these helps:

- the name it was sold under, the model on its label, and where you bought it;
- photos of the start screen, the About screen, the main board from both
  sides, and the SD card, whose print matters;
- whether the [card image](https://github.com/mad-sol-dev/zk-inkjet-printer/releases/tag/SD-Card-clone)
  from this repository boots on your printer, as in
  [issue #1](https://github.com/mad-sol-dev/zk-inkjet-printer/issues/1);
- a raw image of your own card, if you are comfortable sharing it. It holds
  your saved labels and settings, so look before you send.

Before you write anything to your card, take a full image of it:

```bash
sudo dd if=/dev/sdX of=my_card.img bs=4M status=progress
```

The card is the printer's only boot medium. A bad write leaves the printer
dead until the card is restored.

## You want to work on the analysis

- Start with `python3 tools/scripts/next.py`. It lists the open questions,
  each with the experiment that would answer it.
- Findings go into [`research/TRUTH.csv`](research/TRUTH.csv), and only
  through `tools/scripts/truth.py`. Each row carries a verdict, its evidence,
  a test level and the rows it depends on. The rules are in
  [`research/TRUTH.md`](research/TRUTH.md) and at the top of
  [`CLAUDE.md`](CLAUDE.md), both in German; [METHOD.md](METHOD.md) explains
  why they exist.
- A negative result counts only after the same method has found a known
  case. A number or count in the register names the command that reproduces
  it.
- For device tests, say what ran, from which card (a copy or the original),
  and what you saw.
- Everything new in the repository is written in English.
- Do not commit Nuvoton SDKs, tools or datasheets, and nothing private:
  home paths, host names, real names. A pre-push hook checks for that once
  you enable the hooks with `git config core.hooksPath .githooks`.

Pull requests are welcome. If you are unsure whether something fits, open
an issue first.

## Licence

By contributing you agree that code is licensed under MIT, and
documentation and images under CC BY 4.0, like the rest of the repository.
