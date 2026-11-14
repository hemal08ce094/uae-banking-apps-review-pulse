"""Mashreq UAE narrative. Names (rs, S, T, find, lo, hi, mentions, month, top_themes, ...) are injected by scripts/build_insights.py."""
ms = [m for m in S["monthly"]["all"] if m["count"] >= 100]
best = max(ms, key=lambda m: m["avg"]); worst = min(ms, key=lambda m: m["avg"])
m2101 = month("2021-01"); m2608 = month("2026-08"); m2512 = month("2025-12")
bio26 = mentions(r"biometric", "2026-01-01", "2026-12-31"); sec = mentions(r"not secure|unmodified|modified device|rooted", "2024-06-01", "2025-12-31")
lagtxt = 'the same day' if lag == 0 else f'{lag:g} days'
ins = {
 "headline": f"{five_share}% of Mashreq UAE's written reviews give five stars and {low_share}% give one or two. The deepest low was the January 2021 app release that broke sign-in; later complaints are about a 'not secure' device block in 2024-25 and mandatory biometrics in 2026.",
 "lede": f"Mashreq answers {reply_all}% of written reviews, typically {lagtxt}, though the replies are mostly short thanks. The lowest month with at least 100 reviews is {worst['month']} (average {worst['avg']}); the highest is {best['month']} (average {best['avg']}). In 2026, {bio26} reviews mention biometrics, {mentions(r'biometric', '2026-08-01', '2026-12-31')} of them dated August or later.",
 "method": f"Averages here are of written reviews only. Store ratings ({S['app']['store_rating']['ios']['avg']:.2f} App Store, {S['app']['store_rating']['android']['avg']:.2f} Google Play) include star-only ratings, which are not public and skew positive. Sentiment comes from the star rating (1-2 negative, 4-5 positive, 3 resolved by wording). Themes are keyword-tagged in English and Arabic, so a review can carry several themes. This app and Mashreq's separate Neo digital bank share the Mashreq name in reviews, so some complaints are about Neo. App Store coverage: {S['coverage']['text']}.",
 "events": [
  {"month": "2021-01", "label": "New app release breaks sign-in", "detail": f"{m2101['count']} reviews in January 2021, average {m2101['avg']}, {m2101['neg']} negative. {mentions(r'update|upgrade|new version', '2021-01-01', '2021-02-28')} reviews across January and February mention the update; the usual fix described is to uninstall and reinstall, and some say the card-number sign-in is refused.", "kind": "pain"},
  {"month": "2021-02", "label": "Blank page and missing features after the upgrade", "detail": f"Average {month('2021-02')['avg']} across {month('2021-02')['count']} reviews. The most upvoted review that month reports a blank page after login and functions missing from the new version.", "kind": "pain"},
  {"month": "2024-07", "label": "'App is not secure' device block begins", "detail": f"{sec} reviews between June 2024 and December 2025 say the app detects an unsecure or modified device, including people who had used the same phone for years and users travelling abroad.", "kind": "pain"},
  {"month": best["month"], "label": "Best month with at least 100 reviews", "detail": f"Average {best['avg']} across {best['count']} reviews.", "kind": "win"},
  {"month": "2026-08", "label": "Biometric security becomes mandatory at login", "detail": f"Average {m2608['avg']} across {m2608['count']} reviews. {mentions(r'biometric', '2026-08-01', '2026-10-31')} reviews from August onward mention biometrics; several describe a login that shows 'biometric security is mandatory' with no way to set it up.", "kind": "pain"},
 ],
 "pains": [
  {"title": "Locked out of login", "themes": ["login"],
   "summary": "Login is the largest complaint theme. Reviewers describe screens stuck on loading, password reset loops, card activation that fails in the app and a call centre that cannot unlock the account.",
   "quotes": [find(prefer=lo, snippet="none has been this difficult to load"), find(prefer=lo, snippet="it again asks me to reset it"), find(prefer=lo, snippet="unable to activate through the app"), find(prefer=lo, snippet="cannot log-in the app")]},
  {"title": "Mandatory biometrics with no set-up path", "themes": ["login","device"],
   "summary": "From August 2026 users are told biometric security is mandatory, but the screen offers no way to enable it, the chat will not send and customer care does not pick up.",
   "quotes": [find(prefer=lo, snippet="biometric security is mandatory"), find(prefer=lo, snippet="the application shows a prompt stating that biometrics are required"), find(prefer=lo, snippet="facial recognition, despite applying biometric log in")]},
  {"title": "'Your app is not secure' on an ordinary phone", "themes": ["device","security"],
   "summary": "In 2024 and 2025 a device check refuses ordinary phones: the same handset that worked for two years, a phone abroad, an unmodified system. The advice given in review replies is to raise a complaint through the app the user cannot open.",
   "quotes": [find(prefer=lo, snippet="It's the same device I've been using for last 2 years"), find(prefer=lo, snippet="I'm using modified device. Which is not true"), find(prefer=lo, snippet="i travelled to lebanon for 3 weeks")]},
  {"title": "An update that stops the app", "themes": ["update","stability"],
   "summary": "The January 2021 release is the clearest case: no sign-in, a blank page, then reinstalling. Later reports describe an unfinished app with limits such as an IBAN box that stops at 19 characters.",
   "quotes": [find(prefer=lo, snippet="After the App update, I am unable to open it"), find(prefer=lo, snippet="page is blank"), find(prefer=lo, snippet="IBAN because the text box is limited to 19 characters")]},
  {"title": "Support that loops or costs money to reach", "themes": ["support","disputes"],
   "summary": "Customers describe an automated line that never reaches a person, a need to top up a phone to wait on hold, and written complaints closed as 'settled' with no contact.",
   "quotes": [find(prefer=lo, snippet="goes in loop without redire"), find(prefer=lo, snippet="You must recharge at least AED 100"), find(prefer=lo, snippet="processed and \"settled\" automatically"), find(prefer=lo, snippet="no single proper customer care email")]},
  {"title": "Fees noticed late", "themes": ["fees","account"],
   "summary": "A balance-maintenance fee that begins after the first months, charged twice in one month, and a closure that continues to be charged are the fee stories.",
   "quotes": [find(prefer=lo, snippet="charged twice in the same month for fall below fee"), find(prefer=lo, snippet="fall below fee has been deducted"), find(prefer=lo, snippet="they are charging me for a fall maintaining balan")]},
 ],
 "wins": [
  {"title": "Easy account, no hidden fees", "themes": ["account","fees"],
   "summary": f"Five-star reviews ({five_share}% of the total) praise fast account opening, card delivery without hidden charges and cheap international transfers.",
   "quotes": [find(prefer=hi, snippet="very easy to open up account and they deliver the visa card without hidden fees"), find(prefer=hi, snippet="no hidden charges"), find(prefer=hi, snippet="Everything is easy, very effective")]},
  {"title": "Fast digital banking and bill payments", "themes": ["transfers","usability"],
   "summary": "Long-time customers describe transfers, bills and card controls as quick, with ATMs everywhere and answers by phone.",
   "quotes": [find(prefer=hi, snippet="fast digital banking"), find(prefer=hi, snippet="paying bills and transfers very convenient"), find(prefer=hi, snippet="atm machines are everywhere")]},
  {"title": "Neo NXT for children", "themes": ["products"],
   "summary": "Parents single out Mashreq's family product for pocket money and debit cards for kids.",
   "quotes": [find(prefer=hi, snippet="NEO NXT for giving pocket money to kids"), find(prefer=hi, snippet="strong digital banking services through Mashreq Neo")]},
  {"title": "Replies arrive the same day", "themes": ["support"],
   "summary": f"Mashreq replied to {reply_all}% of written reviews with a median gap of {lagtxt}, though replies to praise are short thanks and replies to problems point to other channels.",
   "quotes": [find(prefer=hi, snippet="has always been my favorite"), find(prefer=hi, snippet="best bank to keep your money safer")]},
 ],
}
