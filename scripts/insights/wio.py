"""Wio Personal narrative. Names (rs, S, T, find, lo, hi, mentions, month, top_themes, ...) are injected by scripts/build_insights.py."""
ms = [m for m in S["monthly"]["all"] if m["count"] >= 15]
lowm = min(ms, key=lambda m: m["avg"]); highm = max(ms, key=lambda m: m["avg"])
first = T["first"]; yr = lambda y: sum(1 for r in rs if r["date"].startswith(y))
rate_new = avg(lambda r: r["date"] >= "2026-01-01"); rate_old = avg(lambda r: r["date"] < "2025-01-01")
ins = {
 "headline": f"{five_share}% of Wio Personal's {T['all']:,} written reviews are five stars and {low_share}% are one or two. Praise is for onboarding and the interface; the complaints are about support that answers slowly and about access: video verification, device checks and VPN detection.",
 "lede": f"Wio answers {reply_all}% of written reviews, typically within {lag:g} day. The review base is small ({T['all']:,} reviews since {dLabel(first)}), so the months with at least 15 reviews hold {min(m['count'] for m in ms)} to {max(m['count'] for m in ms)} reviews and move on a handful of voices. Written reviews average {T['avg']}; reviews from 2026 average {rate_new}, those before 2025 average {rate_old}.",
 "method": f"Averages here are of written reviews only. Store ratings ({S['app']['store_rating']['ios']['avg']:.2f} App Store, {S['app']['store_rating']['android']['avg']:.2f} Google Play) include star-only ratings, which are not public and skew positive. Sentiment comes from the star rating (1-2 negative, 4-5 positive, 3 resolved by wording). Themes are keyword-tagged, so a review can carry several themes. Months with fewer than 15 reviews are not read as trends. App Store coverage: {S['coverage']['text']}.",
 "events": [
  {"month": "2023-12", "label": "Early transfer delays and a silent call centre", "detail": f"{month('2023-12')['count']} reviews in December 2023. {mentions(r'whatsapp|call centre|call center|customer care|customer service|reach', '2023-12-01', '2024-01-31')} reviews across December and January mention being unable to reach support while a transfer or login OTP failed.", "kind": "pain"},
  {"month": "2024-01", "label": "First outgoing transfer blocked by the address form", "detail": f"{mentions(r'address', '2024-01-01', '2024-01-31')} reviews in January 2024 describe the app rejecting a valid residential address on the first international transfer; the two most upvoted came from the same week.", "kind": "pain"},
  {"month": "2024-05", "label": "Trading fees and a lower rate noticed", "detail": f"{mentions(r'fee|interest rate|rate', '2024-04-01', '2024-06-30')} reviews in spring 2024 mention fees or the savings rate; the most helpful says trading was fee-free and the rate higher a few months earlier.", "kind": "pain"},
  {"month": highm["month"], "label": "Best month with at least 15 reviews", "detail": f"Average {highm['avg']} across {highm['count']} reviews.", "kind": "win"},
  {"month": "2026-02", "label": "New card feature and export complaints", "detail": f"Average {month('2026-02')['avg']} across {month('2026-02')['count']} reviews. Reviewers report a new feature that stopped card payments and an export that splits transactions into two files.", "kind": "pain"},
  {"month": "2026-07", "label": "Device support dropped, custom OS flags", "detail": f"{mentions(r'device|custom operating|rooted|root|vpn', '2026-07-01', '2026-10-31')} reviews between July and October 2026 mention an unsupported device, a custom operating system warning or VPN detection, including users abroad who cannot reach their money.", "kind": "pain"},
  {"month": lowm["month"], "label": "Lowest month with at least 15 reviews", "detail": f"Average {lowm['avg']} across {lowm['count']} reviews. Negative themes: {top_themes(lowm['month'] + '-01', lowm['month'] + '-31', 3)}.", "kind": "pain"},
 ],
 "pains": [
  {"title": "Support that answers slowly, or not at all", "themes": ["support"],
   "summary": f"Support is the most common negative theme ({sum(1 for r in rs if r['sentiment']=='negative' and 'support' in r['themes'])} reviews). People describe WhatsApp messages that go unanswered, calls only possible from inside the UAE, hour-long waits and agents who take several minutes per reply.",
   "quotes": [find(prefer=lo, snippet="customer care basically doesn't exist"), find(prefer=lo, snippet="waiting time is just more than 1 hr"), find(prefer=lo, snippet="the Support is so slow"), find(prefer=lo, snippet="a case was opened but not resolved")]},
  {"title": "Locked out by device and location checks", "themes": ["login","device"],
   "summary": "Video verification repeats, a device stops being supported, a stock Android is read as a custom operating system, and users in Hong Kong or abroad are told they are on a VPN. Each leaves a customer unable to repay a card or move money.",
   "quotes": [find(prefer=lo, snippet="stop supporting my device"), find(prefer=lo, snippet="my device is running a custom operating system"), find(prefer=lo, snippet="it's using standard Google issued Android"), find(prefer=lo, snippet="always says it's VPN"), find(prefer=lo, snippet="doesn't work on GrapheneOS")]},
  {"title": "Transfers that stall at the first step", "themes": ["transfers","stability"],
   "summary": "Early reviews describe local transfers taking an hour or more to land, and the first outgoing international transfer failing at an address form that rejected valid input.",
   "quotes": [find(prefer=lo, snippet="almost always takes atleast half to one Hr"), find(prefer=lo, snippet="it was not accepting even though I didn't commit any error"), find(prefer=lo, snippet="has not reached my wio account even after 12 hrs"), find(prefer=lo, snippet="Not the first time. Want to use - update your app")]},
  {"title": "Fees and rates that changed", "themes": ["fees","products"],
   "summary": "A digital bank that markets itself as low fee is held to it: trading fees, a lower savings rate and a fixed saving rate that fell from 6% to 5% while the app still said 'up to 6%' are the complaints.",
   "quotes": [find(prefer=lo, snippet="There were no fees on trading"), find(prefer=lo, snippet="too many hidden fees"), find(prefer=lo, snippet="Fixed saving is only 5% now")]},
  {"title": "Missing everyday banking features", "themes": ["features","cards"],
   "summary": "Tap-to-withdraw at ATMs, SMS cash withdrawal, one CSV export of all transactions and easy access to card details are the specific absences named.",
   "quotes": [find(prefer=lo, snippet="Tapping phone at ATM can withdrawal not working"), find(prefer=lo, snippet="one export with all transactions in csv"), find(prefer=lo, snippet="advertising billboard")]},
 ],
 "wins": [
  {"title": "Onboarding in minutes, no paperwork", "themes": ["account"],
   "summary": "The most repeated praise is how quickly an account opens, including for people who cannot supply a salary certificate, and that the physical card arrives early.",
   "quotes": [find(prefer=hi, snippet="cannot submit there salary certificates"), find(prefer=hi, snippet="Amazing onboarding process"), find(prefer=hi, snippet="Seamless on-boarding")]},
  {"title": "An interface people call best in class", "themes": ["usability"],
   "summary": "Reviewers across 2024 to 2026 describe the app as easy to navigate and fast, with several adding that the support is what lets it down.",
   "quotes": [find(prefer=hi, snippet="The ux has been worked on and thought of a 100 times"), find(prefer=hi, snippet="amazing UI, Simple / easy navigation"), find(prefer=hi, snippet="The app itself is fantastic")]},
  {"title": "One app for savings, stocks and cards", "themes": ["products"],
   "summary": "Customers like having savings, stocks, crypto and credit card payments in one place, while asking for search and sort on the investment list.",
   "quotes": [find(prefer=hi, snippet="One stop complete solution for Savings, Stocks, Crypto"), find(prefer=hi, snippet="Support reached out (a bit late)")]},
  {"title": "Real people when it works", "themes": ["support"],
   "summary": "When support reaches a customer it is praised: no automated service, professional staff who respond, and follow-up after a public review.",
   "quotes": [find(prefer=hi, snippet="you speak with real people who are very professional"), find(prefer=hi, snippet="the swift resolution")]},
 ],
}
