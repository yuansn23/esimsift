---
title: "How to Install a Travel eSIM on iPhone and Android"
hero: "travel-esim-illustration-007.webp"
hero_alt: "A traveler following a step-by-step checklist on a phone to install a travel eSIM"
date: 2026-10-01
description: "How to install an eSIM in five minutes: eSIM Sift covers activation timing, QR and app installs, and the errors to avoid before you fly."
faq_heading: "What should you know before installing an eSIM"
faqs:
  - q: "How long before a flight should I install an eSIM?"
    a: "One to three days before departure is the sweet spot. The profile sits dormant until the plan's validity starts, so an early install is safe, and doing it at home means any problem happens on your own Wi-Fi with time to fix it. Avoid installing at the airport gate on 2% battery."
  - q: "Can I install an eSIM without Wi-Fi?"
    a: "Yes, but Wi-Fi is safer. The profile download is a few hundred kilobytes, small enough for mobile data, yet a dropped connection mid-install is the classic cause of a half-installed profile that then needs the provider to reissue. If you must install on the road, use a stable connection."
  - q: "Why does my eSIM say no service after landing?"
    a: "In order of likelihood: Data Roaming is off for the eSIM line, the phone is still using the home SIM for data, the profile hasn't registered on a partner network yet, or the plan's validity hasn't started. Toggle airplane mode for ten seconds, check the roaming toggle first, and give registration a few minutes after landing."
  - q: "Can I reinstall an eSIM on another phone?"
    a: "Not by rescanning the same QR code. Travel eSIM profiles bind to the first device that installs them, and most QR codes are single-use. Moving phones means contacting the provider to reissue, or buying a fresh package — plan accordingly if you upgrade handsets mid-trip."
  - q: "Do I need to remove my home SIM to install an eSIM?"
    a: "No. The eSIM installs as a second line that lives alongside the physical SIM, and both stay active at once. Your home number keeps receiving calls and texts while the eSIM carries data abroad, which is exactly how the dual SIM setup is meant to work."
  - q: "Does installing an eSIM use much data?"
    a: "Very little. The profile download is typically a few hundred kilobytes, smaller than a single photo, so even a small mobile allowance covers it. Wi-Fi is still the safer choice because an interrupted download can leave a half-installed profile that needs a provider reissue."
  - q: "What is an SM-DP+ address?"
    a: "It is the address of the server your phone contacts to download the eSIM profile, written like a web domain. Providers send it with the confirmation alongside a matching activation code, and you only type it yourself when installing manually because a QR code will not scan."
---

Installing a travel eSIM takes about five minutes and works best *before* you leave home, on the Wi-Fi you trust. The exact screens differ between providers, but the flow is the same everywhere: buy a package, install the profile, leave it dormant until the plan's validity starts. One distinction solves most confusion: **installing** puts the profile on your phone, **activating** starts the clock — they are separate events.

This guide walks the whole path in order: the checks worth doing before you pay, the install steps on both platforms, both install routes including the manual code entry most guides skip, the first minutes after landing, and the errors that actually happen — each with its fix.

## Two 30-second checks before you buy

1. **Confirm your phone supports eSIM.** Dial `*#06#` — if an EID number appears alongside the IMEI, the hardware is there. The model-by-model list, including the iPhone and Pixel cutoffs, sits in the [eSIM compatibility check](/guides/esim-compatibility-check/).
2. **Confirm it isn't carrier-locked.** A phone still locked to its original carrier refuses third-party eSIM profiles; it accepts eSIMs only from the carrier that locked it. If your contract device is paid off, the unlock is usually a free request to that carrier and typically takes effect within a day or two.

A third check decides *how* the install will go: {{< count-app-providers >}} of the {{< count-providers >}} providers we track install through their own app, the other {{< count-direct-providers >}} from a plain QR code or website. The live table below shows which is which — [Airalo](/esim-providers/airalo/), [Holafly](/esim-providers/holafly/) and [Roamic](/esim-providers/roamic/) install directly from a code, while app-based brands are best installed at home before an app-store login becomes a problem on travel day.

## How to install an eSIM on iPhone

1. Buy the package; the provider emails a QR code, or its app offers a direct install.
2. Open *Settings → Cellular → Add eSIM* (older iOS versions label this *Cellular Plans*).
3. Scan the QR code with the camera, or approve the provider-app install prompt when it appears.
4. Choose **Secondary** for the new line and keep your home line as Primary.
5. On the final screen pick **Use Secondary for Cellular Data**, then turn **Data Roaming on for the eSIM line only**. This is the step most people miss; without it, the eSIM cannot register on foreign networks.

The profile sits dormant until the plan's validity starts, so an early install is safe on most plans. How the two lines coexist — calls on one, data on the other — is covered in the [dual SIM setup](/guides/dual-sim-and-esim/) guide.

## How to install an eSIM on Android

1. Open *Settings → Network & internet → SIMs*; Samsung keeps this under *Connections → SIM manager*.
2. Tap **Add eSIM** — labeled **Download a SIM** on some skins — and scan the provider's QR code.
3. Confirm the download on Wi-Fi; the profile appears in the list as a second SIM.
4. Set **Mobile data** to the new eSIM and switch on its **Data Roaming** toggle.
5. If the provider lists APN settings, enter exactly the APN string shown — one field, nothing more.

Menu names wander across Android skins — Pixel, One UI and MIUI each phrase the same screen differently — but every one of them hides two things behind the word SIM: the add-eSIM button and the per-line roaming switch. Find those two and the flow is identical everywhere.

## QR code install versus app install

Every provider uses one of two routes, and knowing which shapes the whole experience.

The **QR or direct route** runs entirely from the purchase confirmation. The provider emails a QR code, sometimes alongside a plain link that installs on tap. You scan it in settings, the profile downloads, and you are done — no app, no account, nothing left to manage. This route works with any app-store situation and is the one to prefer when you are already traveling or installing remotely on a family member's phone.

The **app route** bundles purchase and install. The provider's app takes payment, triggers the install prompt itself, and later handles top-ups, extensions and multi-country hopping in one place. The tradeoffs are an extra account to keep access to and a dependency on the app store — a region-blocked app is a real failure mode, covered below in troubleshooting.

Both routes deliver the same profile to the same slot. Pick by convenience, not by fear.

### Enter the activation code manually

A QR code is two strings in disguise: the address of the provider's download server — the SM-DP+ address, which looks like a web domain — and a matching activation code. Both arrive in the confirmation email or the provider's app, which is why the install still works when the code itself won't scan: a smudged printout, a compressed screenshot, or a QR displayed on the very phone that needs to scan it.

On iPhone, open *Settings → Cellular → Add eSIM*, ignore the camera and tap **Enter Details Manually** at the bottom of the scanner. On Android the QR screen on most skins hides a small **enter code manually** or **need help** link that opens the same fields. Type the SM-DP+ address into the first box and the activation code into the second. The two strings must come from the same confirmation — the server rejects a mismatched pair, so copy both fresh from the email rather than retyping from memory.

## When an eSIM plan actually starts

Providers start the validity clock in one of three ways, and each dictates different install timing:

| Clock starts | How it behaves | When to install |
|---|---|---|
| First connection in the destination | Dormant until the phone registers on a network abroad | Any day before you fly |
| At installation | Running from the moment the profile downloads | A day or two before departure |
| First use anywhere | Starts on the first data session in any country | Just before or after landing |

The first row is the most common and the most forgiving: the plan sleeps until your phone touches a foreign network. The second punishes early installs — a 7-day package installed a week before a 7-day trip can be spent by touchdown. The third sounds like the first but differs in one word: anywhere. A first-use plan that moves its first megabyte on your home network the day you install has already started, even though you never left. The plan's terms state its trigger, and every provider page we publish quotes that line in the same place.

## Do you install an eSIM before or after you fly

Before — with the caveat the table just settled. Install one to three days out: late enough that an at-installation clock isn't burning days, early enough that any problem happens on home Wi-Fi with time to fix it. A locked phone discovered at the departure gate has no good outcome; the same phone discovered on Tuesday is a phone call.

Two situations justify installing on arrival instead: the provider starts the clock at first use, or the pre-trip calendar simply never allowed it. Both work — the landing routine below just absorbs the install as an extra step.

Match the validity window to the actual trip rather than the round number. Country pages sort every plan by length so the right one surfaces fast — [Japan](/compare/japan/) and [Portugal](/compare/portugal/) show the pattern.

## How to activate an eSIM after landing

The routine takes under two minutes.

1. **Cycle airplane mode for ten seconds.** On, count to ten, off. This forces the modem to drop the last network it saw and re-scan everything available.
2. **Check the eSIM line's Data Roaming toggle.** It must be on for the eSIM line specifically; the home line's roaming toggle is a separate switch that stays off. Confirm the eSIM is also the line chosen for cellular data.
3. **Give registration a few minutes.** First contact with a partner network is not instant, and for first-connection plans the clock starts at that moment. A minute of patience replaces most support tickets.

Then learn to read the two failure states, because they have different fixes. **No Service** means the line hasn't registered on anything — a profile problem, a wrong-country package, or a network the plan doesn't cover. **Signal bars but no data** means registration worked and the problem is in settings: the roaming toggle, the data-line choice, or a missing APN. Bars first, settings second — that order resolves most arrivals.

## What to do if an eSIM won't activate

- **"eSIM cannot be activated"** — usually a carrier-locked phone, or a QR profile already scanned once. Codes are mostly single-use; the provider must reissue.
- **No data after landing** — Data Roaming off on the eSIM line, or the phone still routing data through the home SIM. Check both before anything else.
- **Full bars but nothing loads** — missing APN on Android, or slow partner registration; ten seconds of airplane mode forces a fresh attach.
- **Wrong country package** — don't let it connect. Contact the provider before validity starts; most swap or refund an unused plan, and each brand's policy is summarized in its [provider reviews](/esim-providers/).
- **Half-installed profile** — a download interrupted mid-install. Delete the partial profile and ask for a reissue rather than rescanning the dead QR code.
- **No free eSIM slot** — phones store a limited number of profiles; recent iPhones keep a handful with two active, and many Androids cap lower. Free a slot by deleting a profile you no longer use, on iPhone via *Settings → Cellular →* the plan → *Delete eSIM*. Deleting a still-valid travel profile usually burns it, so check what is live before clearing space.
- **Provider app unavailable** — the app store refuses the download because your account's region doesn't carry the provider's app. This is why the app route belongs at home: install and log in before departure, or switch to a QR-based provider when it is too late to change store regions.

## Can you move an eSIM to a new phone

Travel eSIM profiles bind to the device that installed them. The QR code is consumed, the profile lives in that phone's secure storage, and scanning the same code on a second phone will not resurrect it.

The confusion comes from Apple's **Quick Transfer**, which moves carrier plans between iPhones and looks like it should apply here. It doesn't, for a structural reason: Quick Transfer asks the carrier's own systems to push the plan to the new phone, and travel-eSIM providers don't participate in that process. Their equivalent is a reissue — contact support, ask for the profile to be reissued to the new device, and expect the old install to stop working when the new one activates. Policies differ by brand, so check before assuming.

The practical rule is simpler. Don't buy a long-duration plan the same week you plan a phone upgrade — install travel profiles on the phone making the trip.

## Two habits that prevent 90% of problems

Install on home Wi-Fi with the phone charged, and screenshot the confirmation — it holds the QR code, the SM-DP+ address and the activation code, which is everything support will ask for. Then on landing: airplane mode for ten seconds, off, wait a minute. Still choosing a package? eSIM Sift's [price comparison](/compare/) lists every provider for your destination — [France](/compare/france/) and [Greece](/compare/greece/) are popular starts — and the [cost calculator](/tools/) picks the cheapest plan that covers your dates and data.
