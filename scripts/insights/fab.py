"""FAB Mobile narrative. Names (rs, S, T, find, lo, hi, mentions, month, top_themes, ...) are injected by scripts/build_insights.py."""
low = low_share; five = five_share
sw = lambda r: r["rating"] <= 3
best = max((m for m in S["monthly"]["all"] if m["count"] >= 100), key=lambda m: m["avg"])
worst = min((m for m in S["monthly"]["all"] if m["count"] >= 100), key=lambda m: m["avg"])
typical = statistics.median([m['count'] for m in S['monthly']['all'] if m['month'].startswith('2026-0') and m['month'] != '2026-03'])
m2022 = month("2022-01"); m2603 = month("2026-03"); m2511 = month("2025-11"); m1810 = month("2018-12"); m2110 = month("2021-10")
ins = {
 "headline": f"{five}% of written reviews give FAB Mobile five stars and {low}% give one or two. Most of the low months follow a release: sign-in changes in 2021 and 2022, and an update in March 2026 that broke OTP delivery and device checks.",
 "lede": f"First Abu Dhabi Bank answered {reply_all}% of the written reviews collected, but the median wait for a reply is {lag:g} days. The most common reasons for one and two stars are {top_themes('2018-01-01', None, 4)}. The best month on record is {best['month']} (average {best['avg']}); the worst with at least 100 reviews is {worst['month']} (average {worst['avg']}).",
 "method": f"Averages here are of written reviews only. Store ratings ({S['app']['store_rating']['ios']['avg']:.2f} App Store, {S['app']['store_rating']['android']['avg']:.2f} Google Play) include star-only ratings, which are not public and skew positive. Sentiment comes from the star rating (1-2 negative, 4-5 positive, 3 resolved by wording). Themes are keyword-tagged in English and Arabic, so a review can carry several themes and short reviews such as 'good app' carry none. The App Store side of this app is {S['coverage']['text']}; Google Play holds {pct(T['android'], T['all'])}% of the reviews here.",
 "events": [
  {"month": "2018-12", "label": "New app arrives and customers compare it with NBAD", "detail": f"{m1810['count']} reviews in December 2018, average {m1810['avg']}. {mentions(r'nbad|merger|previous app|old app|previous one|old one', '2018-12-01', '2019-03-31')} reviews between December 2018 and March 2019 compare it with the earlier NBAD app or blame the merger; the top complaint is a system that hangs or is 'under maintenance'.", "kind": "pain"},
  {"month": "2021-10", "label": "Update loops on Emirates ID authentication", "detail": f"{m2110['count']} reviews in October 2021, average {m2110['avg']}. {mentions(r'emirates id|face|facial|authenticat', '2021-10-01', '2021-11-30')} reviews in the next two months mention ID or face authentication, and {mentions(r'update', '2021-10-01', '2021-10-31')} mention the update itself.", "kind": "pain"},
  {"month": "2022-01", "label": "Lowest month: swipe, PIN and two OTPs to log in", "detail": f"Average {m2022['avg']} across {m2022['count']} reviews, {m2022['neg']} of them negative. {mentions(r'swipe', '2022-01-01', '2022-12-31')} reviews in 2022 mention the swipe step, and several describe a login that needs fingerprint, PIN and an OTP by both SMS and email.", "kind": "pain"},
  {"month": best["month"], "label": "Best month on record", "detail": f"Average {best['avg']} across {best['count']} reviews.", "kind": "win"},
  {"month": "2025-11", "label": "Autumn 2025 dip", "detail": f"Average {m2511['avg']} across {m2511['count']} reviews in November 2025 and {month('2025-10')['avg']} in October. The main negative themes were {top_themes('2025-10-01', '2025-11-30', 3)}. {mentions(r'screen ?shar|screen mirror', '2025-10-01', '2026-03-31')} reviews report a 'screen sharing detected' block that stops the app opening.", "kind": "pain"},
  {"month": "2026-03", "label": "March 2026 update: OTP delays and device limit", "detail": f"{m2603['count']} reviews in March 2026, against a typical {typical:g} a month in 2026, average {m2603['avg']}. {mentions(r'otp|sms', '2026-03-01', '2026-03-31')} mention an OTP and {mentions(r'device limit|delink|another device|new device', '2026-03-01', '2026-04-30')} mention the device limit or delinking. Negative themes: {top_themes('2026-03-01', '2026-03-31', 3)}.", "kind": "pain"},
 ],
 "pains": [
  {"title": "Signing in and re-registering on a new phone", "themes": ["login","device"],
   "summary": "Logging in has changed shape in almost every major release: swipe, PIN, fingerprint and now OTPs by SMS and email. A new phone or a reinstall can trigger the device limit, an Emirates ID camera scan, or both, and the app gives no way to unlink the old device itself.",
   "quotes": [find(prefer=lo, snippet="scanning the Emirates Id through the phone camera"), find(prefer=lo, snippet="maximum device limit reached"), find(prefer=lo, snippet="the phone doesn't have camera"), find(prefer=lo, snippet="sending 1 OTP by SMS and a 2nd OTP by email")]},
  {"title": "Updates that stop the app opening", "themes": ["update","stability"],
   "summary": "Several of the lowest months follow a release: authentication that loops, OTP texts that arrive half an hour late, a security check that claims screen sharing is on. Reviewers describe the app as fine until the update and unusable after it.",
   "quotes": [find(prefer=lo, snippet="stopped working after update"), find(prefer=lo, snippet="Screen sharing detected Issue"), find(prefer=lo, snippet="I got the SMS with the otpnearly 30 mins"), find(prefer=lo, snippet="takes me back to the homepage where I have to enter my account number")]},
  {"title": "Reaching a person when the app fails", "themes": ["support"],
   "summary": "The most upvoted complaints are about the bank phone line, not the screens: a voice assistant before any agent, 30-minute waits, emails answered by a no-reply message, and a help section that sends people back to the call centre.",
   "quotes": [find(prefer=lo, snippet="It makes you wait for more than 30 minutes"), find(prefer=lo, snippet="Very difficult to reach a customer care executive"), find(prefer=lo, snippet="IVR is irritating"), find(prefer=lo, snippet="no online chat support")]},
  {"title": "Money that is sent but not received", "themes": ["transfers","fees"],
   "summary": "Transfers are praised when they are instant and criticised when they stall. The unhappy reviews describe local and overseas payments marked completed that do not arrive for days, with no transaction number to chase.",
   "quotes": [find(prefer=lo, snippet="Very high payment processing time"), find(prefer=lo, snippet="showing as “Completed,” but the amount has still not been credited"), find(prefer=lo, snippet="almost ten days money not yet credited")]},
  {"title": "Opening and closing accounts", "themes": ["account","branch"],
   "summary": "The promise of an instant account in the app meets Emirates ID and UAE Pass steps that freeze, and closing an account from the app is reported as declined for 'internal bank procedures' while fees continue.",
   "quotes": [find(prefer=lo, snippet="Open an account instantly on the FAB Mobile App"), find(prefer=lo, snippet="close account from the app does not work"), find(prefer=lo, snippet="tried for 1 hour just to open an account"), find(prefer=lo, snippet="blocked my account")]},
  {"title": "Fraud and cards handled slowly", "themes": ["security","cards","disputes"],
   "summary": "A smaller group of one-star reviews concerns card fraud and card service: unauthorised transactions that stay unresolved for months, a card that cannot be unblocked, and credit card sections that spam notifications.",
   "quotes": [find(prefer=lo, snippet="unauthorized transactionsappeared"), find(prefer=lo, snippet="they didn't resolve the fraud"), find(prefer=lo, snippet="status of my atm card"), find(prefer=lo, snippet="Never open credit card section")]},
 ],
 "wins": [
  {"title": "Transfers and beneficiaries are fast", "themes": ["transfers"],
   "summary": f"Transfers and adding a beneficiary are the most repeated praise in the {five}% of reviews that give five stars: no waiting period after adding someone, instant local transfers, and inward and outward payments that go through.",
   "quotes": [find(prefer=hi, snippet="super fast for money transfers and adding beneficiaries"), find(prefer=hi, snippet="You don't have to wait after adding a beneficiary"), find(prefer=hi, snippet="I appreciate fab for there instant transfer")]},
  {"title": "Card control that works in an emergency", "themes": ["cards"],
   "summary": "Blocking a lost card and getting a replacement from the app is the concrete story customers tell when they recommend it.",
   "quotes": [find(prefer=hi, snippet="block a lost card and get a new one instantly"), find(prefer=hi, snippet="I recently received a credit card from Fab Bank")]},
  {"title": "The redesigns were noticed", "themes": ["usability"],
   "summary": "A few reviews single out the redesigned app, in 2023 and again in 2025, as clear and quick.",
   "quotes": [find(prefer=hi, snippet="NEW DESIGN in mobile banking app"), find(prefer=hi, snippet="The new look is good")]},
  {"title": "Easy to open an account when it works", "themes": ["account"],
   "summary": "Customers who get through onboarding describe it as quick, and some say FAB is the best bank in the UAE for it.",
   "quotes": [find(prefer=hi, snippet="I think FAB is the best bank in the UAE"), find(prefer=hi, snippet="Excellent banking experience")]},
 ],
}
