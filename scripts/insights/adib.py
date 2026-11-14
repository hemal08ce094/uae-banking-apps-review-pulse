"""ADIB Mobile Banking narrative. Names (rs, S, T, find, lo, hi, mentions, month, top_themes, ...) are injected by scripts/build_insights.py."""
ms = [m for m in S["monthly"]["all"] if m["count"] >= 100]
best = max(ms, key=lambda m: m["avg"]); worst = min(ms, key=lambda m: m["avg"])
b = [r for r in rs if r["date"].startswith(best["month"])]; topver = collections.Counter(r['version'] for r in b if r['version']).most_common(1)[0][0]; short_b = pct(sum(r["len"] < 40 for r in b), len(b))
m1906 = month("2019-06"); m2605 = month("2026-05")
face = mentions(r"selfie|face scan|face verif|facial|face recog", "2023-01-01", "2026-12-31")
ins = {
 "headline": f"{five_share}% of ADIB's written reviews give five stars and {low_share}% give one or two. The complaints that recur are release loops, face verification on a new phone and the move from SMS to push notifications.",
 "lede": f"ADIB answers {reply_all}% of written reviews, with a median gap of {'under a day' if lag == 0 else f'{lag:g} days'}. The best month with at least 100 reviews is {best['month']} (average {best['avg']}); {short_b}% of that month's reviews are under 40 characters, so volume rose faster than detail. {face} reviews since 2023 mention the selfie or face scan.",
 "method": f"Averages here are of written reviews only. Store ratings ({S['app']['store_rating']['ios']['avg']:.2f} App Store, {S['app']['store_rating']['android']['avg']:.2f} Google Play) include star-only ratings, which are not public and skew positive. Sentiment comes from the star rating (1-2 negative, 4-5 positive, 3 resolved by wording). Themes are keyword-tagged in English and Arabic, so a review can carry several themes. App Store coverage: {S['coverage']['text']}.",
 "events": [
  {"month": "2018-06", "label": "Update prompt that never clears", "detail": f"{mentions(r'update|تحديث', '2018-06-01', '2018-07-31')} reviews in June and July 2018 mention an update prompt; several say the store offers no update and the app stops working.", "kind": "pain"},
  {"month": "2019-06", "label": "The same update loop, a year later", "detail": f"{m1906['count']} reviews in June 2019, average {m1906['avg']}. {mentions(r'update|updated|upgrade|تحديث', '2019-06-01', '2019-06-30')} mention an update; reviewers say it keeps asking to update after installing, even after a reinstall.", "kind": "pain"},
  {"month": best["month"], "label": "Best month on record", "detail": f"Average {best['avg']} across {best['count']} reviews, mostly version {topver}. {short_b}% of that month's reviews are under 40 characters.", "kind": "win"},
  {"month": "2023-05", "label": "Face scan fails on a new phone", "detail": f"{face} reviews since January 2023 mention the selfie or face check. The common story: it worked on the old phone, fails on the new one, and the daily attempt limit runs out.", "kind": "pain"},
  {"month": "2025-01", "label": "Transaction approvals move to push notifications", "detail": f"{mentions(r'notification', '2025-01-01', '2025-12-31')} reviews in 2025 mention notifications; the most upvoted dislikes a pop-up asking to enable them in place of SMS alerts, and others report approvals that never arrive on Android.", "kind": "pain"},
  {"month": "2026-04", "label": "Recent months stay steady", "detail": f"April 2026 averages {month('2026-04')['avg']} across {month('2026-04')['count']} reviews and May {m2605['avg']} across {m2605['count']}; the negative themes are {top_themes('2026-01-01', '2026-10-31', 3)}.", "kind": "release"},
 ],
 "pains": [
  {"title": "Face verification that will not pass", "themes": ["login","device"],
   "summary": "Registering on a new phone needs a selfie scan. Reviewers describe the camera freezing, repeated 'could not capture' messages, handset-specific failures and a daily attempt limit that locks them out for a day.",
   "quotes": [find(prefer=lo, snippet="face verification getting freezed"), find(prefer=lo, snippet="I can't go past the selfie scan"), find(prefer=lo, snippet="stuck in face scanning the camera it is not opening"), find(prefer=lo, snippet="الكاميرا بشكل جيد")]},
  {"title": "Updates that loop or change the rules", "themes": ["update","stability"],
   "summary": "The most common negative theme after crashes. Two generations of reviews describe an app that demands an update it cannot complete, and later ones a release that changed services without notice.",
   "quotes": [find(prefer=lo, snippet="Keeps promoting to upgrade the app"), find(prefer=lo, snippet="it's still asking for update"), find(prefer=lo, snippet="changes services and site without notice"), find(prefer=lo, snippet="Just revert to the older version")]},
  {"title": "OTPs and notifications that do not arrive", "themes": ["login","notifications"],
   "summary": "Login and payment approval depend on an OTP or a push message. Reviewers report OTPs that never arrive, a push-notification switch forced on them, and approvals that show only when the app is open.",
   "quotes": [find(prefer=lo, snippet="OTP sometimes doesnt arrive on phone"), find(prefer=lo, snippet="stupid pop-up message asking me to enable"), find(prefer=lo, snippet="Unable to get any notification to approve transactions")]},
  {"title": "Opening an account by scanning documents", "themes": ["account"],
   "summary": "Digital onboarding is where patience runs out: document scans that take half an hour, a passport page rejected as 'incorrect document', and people who give up after a month.",
   "quotes": [find(prefer=lo, snippet="Opening of account takes more than 30 minutes"), find(prefer=lo, snippet="says \"incorrect document\""), find(prefer=lo, snippet="Trying to open an account since more then a month")]},
  {"title": "Missing features and fees", "themes": ["features","fees","transfers"],
   "summary": "Requests that repeat: Google Wallet, utility and SIM recharge payments, a hidden-balance toggle, per-transaction cash-back detail, and clearer fees on the account.",
   "quotes": [find(prefer=lo, snippet="support Google Wallet"), find(prefer=lo, snippet="can't add utility payment"), find(prefer=lo, snippet="the fees are absolutely ridiculous"), find(prefer=lo, snippet="removing the ability to change individual icons")]},
 ],
 "wins": [
  {"title": "A calm, well-liked app for most customers", "themes": ["usability"],
   "summary": f"{five_share}% of written reviews are five stars. The long ones call it easy, secure and quick, and say it saved a trip to the branch.",
   "quotes": [find(prefer=hi, snippet="I rarely face any problems or delays"), find(prefer=hi, snippet="saving you time from making travels to the bank"), find(prefer=hi, snippet="The App is excellent")]},
  {"title": "Complaints that get resolved fast", "themes": ["support"],
   "summary": "Several reviewers raise a problem in the review or by complaint and return to say it was fixed, including an Android notification fault and a blocked card activation.",
   "quotes": [find(prefer=hi, snippet="the concerned teams quickly got in touch"), find(prefer=hi, snippet="Issue had been fixed, Thank you for your fast support"), find(prefer=hi, snippet="Thanks for Mr Talla")]},
  {"title": "Everyday banking with clear sections", "themes": ["transfers","usability"],
   "summary": "Customers describe simple transfers, international payments without trouble and clear instructions in the app.",
   "quotes": [find(prefer=hi, snippet="I made i international transactions no worries"), find(prefer=hi, snippet="easy to use, great services and clear instructions")]},
 ],
}
