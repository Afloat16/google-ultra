# google-ultra

[简体中文](README.md) | English

Google One ships a 12-month free trial for **AI Ultra**. It never shows up in any UI — not on the plans page, not in the app. It only exists inside the offers returned by Play Billing. This repo gets that offer, opens the Play checkout with it, and stops at $0.

Two ways to use it: a single HTML page with no install, or a Python script that talks to your phone.

## What you get

**Ultra 5x — 20 TB, 12 months at $0.** Cancel before the trial ends and you never pay.

After activation the Play subscription page reads:

```
Next payment    Starts 2027-11-17
                US$99.99/month
```

That date is 12 months out. Nothing is charged today.

There is also a 30 TB tier (20x). Its offers exist too, but Play re-checks eligibility at checkout and most accounts get "You're not eligible for a free trial". The script will not click that.

## Option A — the web page

Open this, or download `web/index.html` and double-click it:

https://gylive.github.io/google-ultra/web/

1. **Sign in** with the Google account you want the trial on
2. **Add a card** — $1 on it is enough, nothing is charged during the trial
3. **Pick a plan** — it opens Google's checkout; confirm the price says $0, then subscribe

That's it. No install, no root, no cable.

English page: https://gylive.github.io/google-ultra/web/en.html

## Option B — the script

Needs a rooted Android phone connected over USB, plus Python and Frida.

```bash
pip3 install frida
python3 ultra0.py --check     # checks adb, root, frida-server, module
python3 ultra0.py accounts.txt
```

Account file, one per line, fields separated by four dashes:

```
email----password----recovery----2fa_secret----card----expiry----cvc----holder----zip
```

Trailing fields can be empty. A fresh account without 2FA:

```
someone@gmail.com----mypassword----
```

Single account:

```bash
python3 ultra0.py --account "someone@gmail.com:password"
```

Options:

```bash
--plan 5x      # 20 TB only
--plan 20x     # 30 TB only (most accounts are not eligible)
--plan auto    # default: check both, take the longest free period
--no-add       # account is already on the phone
--no-switch    # don't switch Play accounts, only verify the current one
```

Why the script: it pulls the offer from the phone's own Play client, so the browser fingerprint never enters the picture. Slower to set up, more reliable across environments.

## How it works

Google One is a Play Billing client itself, so it can already open the Play purchase sheet. The script injects Frida into that process, loads a BillingClient build through `DexClassLoader`, and asks Play what offers exist for `g1.play.20tb`.

Play answers with five: four with a $0 first phase (`eft-1month` through `eft-12month`) and one at full price. The script picks the longest free period and calls `launchBillingFlow` on the main thread with that offer token.

Two hard requirements for the trial, straight from Play's side:

- the account has a payment method attached
- the account has no active subscription

Miss either one and checkout says "not eligible". And once a trial has been initiated, the offers disappear even if you never confirmed — one shot per account.

## Troubleshooting

**400 on the web page.** Google compares the browser fingerprint inside the URL with your real User-Agent. The page rebuilds the fingerprint from your own browser, so this should be rare. If it happens, tick "兼容模式" (compatibility mode) and retry, or copy the link and open it in the browser where the target account is signed in.

**"You're not eligible for a free trial."** Wrong account, or it already used the trial. Use a fresh one.

**Nothing happens at checkout.** Run it again. If it repeats, check for a proxy or VPN on the phone: `adb shell settings get global http_proxy` should be `null`, and Clash-style VPNs hijack DNS in a way Play dislikes.

**No root.** The script injects into another app's process; root is required.

## Repo layout

```
web/index.html         web tool (Chinese), also served by GitHub Pages
web/en.html            web tool (English)
simple/ultra.py        minimal script, one file
ultra0.py              full script: batch, plan selection, account switching
assets/                WeChat group QR codes (Chinese community)
```

## Notes

Cancel the subscription before the trial ends. Play → profile → Payments & subscriptions → Subscriptions.

Accounts, passwords, and card numbers stay on your machine. Nothing is uploaded anywhere. Reports land in `ultra0-report/`.

Questions in English: open an issue. The chat groups are Chinese-language.

## Disclaimer

This repository exists for technical research and discussion: how Play Billing reports offers, and how a client parses what the server sends back.

- No accounts, no proxy purchasing, no cards are sold or provided here
- You are responsible for anything you do with this code; the authors accept no liability
- Check your local laws and Google's Terms of Service yourself — whether and how you use this is your call
- If you disagree with any of the above, don't use the code

Provided as-is under MIT, without warranty of any kind.

## License

MIT, see [LICENSE](LICENSE).
