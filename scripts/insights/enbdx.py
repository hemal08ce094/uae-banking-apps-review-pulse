"""ENBD X narrative. Names (rs, S, T, find, lo, hi, mentions, ...) are injected by scripts/build_insights.py."""
neg_login = sum(1 for r in rs if r["sentiment"]=="negative" and ({"login","smartpass","device"} & set(r["themes"])))
may26 = month("2026-05"); sep26 = month("2026-09")
best = max((m for m in S["monthly"]["all"] if m["count"] >= 100), key=lambda m: m["avg"])
_b5 = [r for r in rs if r["date"].startswith(best["month"]) and r["rating"] == 5]
short5 = f"{round(100*sum(r['len'] < 40 for r in _b5)/max(1,len(_b5)))}%"

ins = {
 "headline": f"{five_share}% of written reviews give ENBD X five stars, yet {low_share}% give one or two. The deepest dips in the monthly rating follow changes to access: the forced migration, Smart Pass approvals, mandatory biometrics and device checks.",
 "lede": f"Emirates NBD answers {reply_rate}% of Google Play reviews and {ios_reply_rate}% of App Store reviews, typically within a day, and customers notice when fixes land. The recurring damage comes from access: forced migration in 2022-23, Smart Pass approvals in 2024, mandatory biometrics in May 2026 and device-integrity checks in the 26.x releases. {neg_login:,} of {neg_all:,} negative reviews ({round(100*neg_login/neg_all)}%) mention login, approvals or device checks.",
 "method": f"Averages here are of written reviews only. Store ratings ({S['app']['store_rating']['ios']['avg']:.2f} App Store, {S['app']['store_rating']['android']['avg']:.2f} Google Play) include star-only ratings, which are not public and skew positive: {round(100*S['app']['store_rating']['android']['histogram'][4]/sum(S['app']['store_rating']['android']['histogram']))}% of Google Play's star ratings are five stars against {round(100*T['hist_android'][4]/T['android'])}% of its written reviews. Sentiment comes from the star rating (1-2 negative, 4-5 positive, 3 resolved by wording). Themes are keyword-tagged in English and Arabic, so a review can carry several themes and short reviews such as 'good app' carry none. Counts are written reviews only; star-only ratings are not public.",
 "events": [
  {"month": "2021-12", "label": "ENBD X appears on Google Play", "detail": f"Google Play lists the release date as 12 December 2021. The oldest public iOS review Apple serves is dated {dLabel(min(r['date'] for r in rs if r['platform']=='ios'))}, so both stores' review history starts together.", "kind": "release"},
  {"month": "2022-12", "label": "Old app switched off, customers moved over", "detail": f"{mentions(r'old (app|version)|previous (app|version)|go back', '2022-10', '2023-06')} reviews between Oct 2022 and Jun 2023 compare ENBD X with the old blue app. The most common ask is to be allowed back.", "kind": "pain"},
  {"month": "2023-07", "label": "Quick Actions redesign and a wave of bugs", "detail": f"Developer replies in July 2023 describe a UI change that introduced a Quick Actions tab. {mentions(r'crash|not work|bug|error', '2023-07-01', '2023-08-31')} reviews that July and August report crashes or errors.", "kind": "pain"},
  {"month": "2024-01", "label": "Smart Pass approvals replace OTP", "detail": f"{mentions(r'smart ?pass|smart token|authoris|authoriz|approv', '2023-10', '2024-12')} reviews from Oct 2023 to Dec 2024 mention Smart Pass, tokens or approvals. Expired tokens and missed approval notifications dominate.", "kind": "pain"},
  {"month": best["month"], "label": "Best month on record", "detail": f"Average {best['avg']} across {best['count']} reviews. {short5} of the five-star reviews that month are under 40 characters, so volume rose faster than detail.", "kind": "win"},
  {"month": "2026-05", "label": "Biometric-only login goes mandatory", "detail": f"{may26['count']} reviews in May 2026, {may26['neg']} negative, average {may26['avg']}. {mentions(r'fingerprint|biometric|face ?id|touch ?id', '2026-05-01', '2026-05-31')} of them mention fingerprint or Face ID; {mentions(r'voice ?over', '2026-05-01', '2026-07-31')} between May and July report the 'cannot be used with VoiceOver enabled' lockout.", "kind": "pain"},
  {"month": "2026-08", "label": "Dark mode ships", "detail": f"{mentions(r'dark (mode|theme)', '2022-01', '2026-07-31')} earlier reviews had asked for a dark theme. Reviews in August 2026 thank the team for adding it.", "kind": "win"},
  {"month": "2026-09", "label": "26.x releases: integrity checks and an outage", "detail": f"{sep26['count']} reviews in September 2026, {sep26['neg']} negative, average {sep26['avg']}, the lowest month since the migration. {mentions(r'integrity', '2026-08-01', '2026-10-31')} reviews mention the device integrity check; the most upvoted review of the year reports the app and mobile banking down on 30 September.", "kind": "pain"},
 ],
 "pains": [
  {"title": "Locked out by mandatory biometrics", "themes": ["login","device"],
   "summary": "From May 2026 the app insists on fingerprint or face login. Phones with a broken sensor, Pixel face unlock, enterprise profiles or an accessibility setting cannot get in, and account recovery loops back to the same screen.",
   "quotes": [find(prefer=lo, snippet="They turned on login only with fingerprints"), find(prefer=lo, snippet="Google Pixel Fold phone"), find(prefer=lo, snippet="This app cannot be used with VoiceOver enabled"), find(prefer=lo, snippet="Device integrity check failed")]},
  {"title": "Payment approvals that fail at the last step", "themes": ["smartpass","transfers"],
   "summary": "Smart Pass replaced SMS codes. When the token expires, the approval notification is missed or the app logs out mid-flow, the customer cannot pay, and the web banking session depends on the phone working.",
   "quotes": [find(prefer=lo, snippet="smart token is expired"), find(prefer=lo, snippet="Transaction authorization fails 70% of the time"), find(prefer=lo, snippet="difficult to find the approve transaction tab"), find(prefer=lo, snippet="The whole mobile banking and app are down")]},
  {"title": "Losing what the old app did in two taps", "themes": ["liv","features"],
   "summary": "The 2022-23 migration removed per-card daily limits, amount-due on bill payments, CSV statements and one-tap full card payment. Some came back; the one-tap payment was removed again in the August 2026 update.",
   "quotes": [find(prefer=lo, snippet="take 5-6 clicks now"), find(prefer=lo, snippet="setting daily transaction limits for each debit and credit card"), find(prefer=lo, snippet="pay the full outstanding amount with one click"), find(prefer=lo, snippet="download my current and Previous months Credit card statement in CSV")]},
  {"title": "A screen that is hard to read and navigate", "themes": ["usability"],
   "summary": "Low contrast, thin fonts, a large blue diamond button and unpredictable navigation are the design complaints that repeat across three years of redesigns, most loudly after each major UI change.",
   "quotes": [find(prefer=lo, snippet="zero contrast, can't tell sections apart"), find(prefer=lo, snippet="There is no visual hierarchy"), find(prefer=lo, snippet="stare hard in order to read the tiny"), find(prefer=lo, snippet="The navigation is totally unpredictable")]},
  {"title": "False security flags on ordinary phones", "themes": ["device","security"],
   "summary": "Work phones managed by Intune are detected as VPN or developer-mode devices, some handsets are declared rooted, and the 26.x integrity check rejects updated official devices. The only advice given is to change phones.",
   "quotes": [find(prefer=lo, snippet="MS intune/windows defender is running"), find(prefer=lo, snippet="due to developer options enabled in Android"), find(prefer=lo, snippet="repair the fingerprint sensor or change my phone"), find(prefer=lo, snippet="your divce is rooted")]},
  {"title": "Products and service outside the app", "themes": ["products","branch","disputes"],
   "summary": "A share of one-star reviews is about the bank, not the software: loan balances shown wrongly, card applications that stall, in-app adverts, complaints raised in branch and online that go nowhere, and agents logging the wrong case.",
   "quotes": [find(prefer=lo, snippet="Doesn't show loan payments correctly"), find(prefer=lo, snippet="raised several complaints online as well as in the branch"), find(prefer=lo, snippet="the pop-up advertisements are super annoying"), find(prefer=lo, snippet="the agent raised a complaint for the wrong transaction")]},
  {"title": "Support loops when the app fails", "themes": ["support","disputes"],
   "summary": "When the app blocks someone, the fallback is a paid call with long waits, chat replies that take days, and disputes closed without explanation. Review replies are fast, but the resolution behind them often is not.",
   "quotes": [find(prefer=lo, snippet="took me 2 weeks to speak with someone"), find(prefer=lo, snippet="the call is not free"), find(prefer=lo, snippet="called the call center multiple times every day with no solution"), find(prefer=lo, snippet="the bank informed me that my case was closed")]},
 ],
 "wins": [
  {"title": "Every Play review gets an answer", "themes": ["support"],
   "summary": f"Emirates NBD replied to {reply_rate}% of the Google Play reviews and {ios_reply_rate}% of the App Store reviews collected, with a median gap of {S['replies']['median_lag_days']:.0f} day. Several one-star reviewers came back to raise their rating after a callback.",
   "quotes": [find(prefer=hi, snippet="followed up proactively to resolve the issue"), find(prefer=hi, snippet="All reported issues with app has been fixed"), find(prefer=hi, snippet="Feels really good to see that concerns are being addressed"), find(prefer=hi, snippet="All my previous problems have been resolved")]},
  {"title": "In-app messaging beats the phone queue", "themes": ["support","features"],
   "summary": "Customers who discover the messaging feature describe it as the best part of the app: a written question, an answer within a day, no hold music.",
   "quotes": [find(prefer=hi, snippet="The best feature in this app is messaging"), find(prefer=hi, snippet="Customer support on mail was quick")]},
  {"title": "Requests that were shipped", "themes": ["features","usability"],
   "summary": "Dark mode was the most repeated design request from 2022 onward and arrived in August 2026. Reviewers explicitly thank the team for listening.",
   "quotes": [find(prefer=hi, snippet="Thank you for listening"), find(prefer=hi, snippet="يضيفوا سمة الوضع الداكن")]},
  {"title": "Everyday banking feels fast", "themes": ["transfers","usability"],
   "summary": f"{five_share}% of written reviews are five stars. The long ones praise instant transfers, bill payments, card controls and quick cash on a credit card.",
   "quotes": [find(prefer=hi, snippet="Transactions are fast, and I love how easy it is"), find(prefer=hi, snippet="quick cash up to 90 % of my limit"), find(prefer=hi, snippet="Managing my accounts, cards, and transactions feels effortless")]},
  {"title": "Arabic-speaking agents who fix it", "themes": ["support"],
   "summary": "Arabic reviews single out named call-centre agents who resolved login problems in one call, even while asking for Arabic UI and a dark theme.",
   "quotes": [find(prefer=hi, snippet="شكر خاص لموظف خدمة العملاء"), find(prefer=hi, snippet="تم التواصل معي وحل المشكلة بوقت قياسي")]},
 ],
}
