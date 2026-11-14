"""ADCB narrative, two app generations merged. Names (rs, S, T, find, lo, hi, mentions, month, ...) are injected by scripts/build_insights.py."""
isnew = lambda r: r.get("generation") == "new"
isold = lambda r: r.get("generation") == "old"
nn = sum(isnew(r) for r in rs); no = sum(isold(r) for r in rs)
av_new = avg(isnew); av_old = avg(isold)
low_new = pct(sum(1 for r in rs if isnew(r) and r["rating"] <= 2), nn); low_old = pct(sum(1 for r in rs if isold(r) and r["rating"] <= 2), no)
first_new = min(r["date"] for r in rs if isnew(r))
m1812 = month("2018-12"); m2607 = month("2026-07"); m2606 = month("2026-06"); m2608 = month("2026-08")
best = max((m for m in S["monthly"]["all"] if m["count"] >= 100), key=lambda m: m["avg"])
def gen_month(m, g):
    v = [r["rating"] for r in rs if r["date"].startswith(m) and r.get("generation") == g]
    return (round(statistics.mean(v), 2), len(v)) if v else (None, 0)
n07 = gen_month("2026-07", "new"); n08 = gen_month("2026-08", "new"); n10 = gen_month("2026-10", "new")
ins = {
 "headline": f"ADCB's new app, launched on {dLabel(first_new)}, averages {av_new} across {nn:,} written reviews; the previous app averaged {av_old} across {no:,}. One and two stars are {low_new}% of the new app's reviews against {low_old}% of the old one's.",
 "lede": f"ADCB answers {reply_all}% of written reviews, typically within {lag:g} day. The new app drew its first complaints about being forced on customers, then about mandatory face or fingerprint set-up and a SecurePass set-up that loops. July 2026 was the low point (average {n07[0]} across {n07[1]:,} new-app reviews). The older app's history stretches back to 2013 and its worst month was the December 2018 redesign (average {m1812['avg']}).",
 "method": f"ADCB is treated as one bank: the new ADCB. app (Google Play {S['app']['gens'][0]['play_id']}, App Store {S['app']['gens'][0]['ios_id']}) and the previous ADCB app ({S['app']['gens'][1]['play_id']}, {S['app']['gens'][1]['ios_id']}) are merged, and each review carries a generation tag. Averages are of written reviews only; store ratings combine both apps by number of ratings and include star-only ratings, which are not public. Sentiment comes from the star rating (1-2 negative, 4-5 positive, 3 resolved by wording). Themes are keyword-tagged, so a review can carry several themes. App Store coverage: {S['coverage']['text']}.",
 "events": [
  {"month": "2018-12", "label": "Redesign: customers ask for the previous version", "detail": f"Average {m1812['avg']} across {m1812['count']} reviews. {mentions(r'previous|older|old version|earlier', '2018-11-01', '2019-03-31', isold)} reviews between November 2018 and March 2019 ask for the previous version; the complaints are an animated welcome screen, too many taps to see balances, and an 'Invalid Device ID' lockout on some phones.", "kind": "pain"},
  {"month": best["month"], "label": "Best month on record", "detail": f"Average {best['avg']} across {best['count']} reviews, all from the earlier app.", "kind": "win"},
  {"month": "2026-04", "label": "New ADCB. app launches", "detail": f"The first new-app review is dated {dLabel(first_new)}. By the end of June it had {sum(1 for r in rs if isnew(r) and r['date'] <= '2026-06-30'):,} written reviews, against {sum(1 for r in rs if isold(r) and r['date'] >= '2026-01-01'):,} for the old app so far in 2026.", "kind": "release"},
  {"month": "2026-05", "label": "Mandatory biometrics and camera", "detail": f"{mentions(r'forc|mandatory|no option|no alternative|opt out', '2026-05-01', '2026-06-30', isnew)} new-app reviews in May and June say face or fingerprint set-up is forced; {mentions(r'camera', '2026-05-01', '2026-07-31', isnew)} mention a camera requirement; {mentions(r'vpn', '2026-05-01', '2026-10-31', isnew)} mention the app refusing to run on a VPN.", "kind": "pain"},
  {"month": "2026-07", "label": "Lowest month: beneficiaries vanish, 'Under Maintenance'", "detail": f"New-app reviews average {n07[0]} across {n07[1]:,} in July 2026, down from {gen_month('2026-06','new')[0]} in June. {mentions(r'beneficiar|payee', '2026-07-01', '2026-07-31', isnew)} July reviews mention beneficiaries or payees and {mentions(r'maintenance', '2026-07-01', '2026-07-31', isnew)} mention 'under maintenance'. Negative themes: {top_themes('2026-07-01', '2026-07-31', 3)}.", "kind": "pain"},
  {"month": "2026-08", "label": "Partial recovery, SecurePass loop persists", "detail": f"New-app average {n08[0]} across {n08[1]:,} reviews in August and {n10[0]} across {n10[1]:,} in October. {mentions(r'secure ?pass', '2026-08-01', '2026-10-31', isnew)} reviews since August still describe the SecurePass PIN set-up looping.", "kind": "pain"},
 ],
 "pains": [
  {"title": "A new app that replaced the old one overnight", "themes": ["liv","update"],
   "summary": f"{mentions(r'old app|previous app|old version|forced', '2026-04-01', '2026-10-31', isnew)} new-app reviews compare it with the old app, almost all unfavourably. Customers describe being moved without a choice, a lost transfer flow, and nowhere to go back to.",
   "quotes": [find(prefer=lo, snippet="I have been forced to install the new app"), find(prefer=lo, snippet="The new adcb app was forced on end users"), find(prefer=lo, snippet="I cannot access the old app anymore"), find(prefer=lo, snippet="Another pointless \"upgrade\"")]},
  {"title": "Set-up that cannot be completed", "themes": ["login","device"],
   "summary": "The new security model needs biometrics, a camera, a SecurePass PIN and no VPN. Customers without a fingerprint sensor or camera, on work phones or abroad, cannot get in, and the PIN set-up screen can loop forever.",
   "quotes": [find(prefer=lo, snippet="I don't have a fingerprinting option on my phone"), find(prefer=lo, snippet="Frustrated by the lack of support for cameless smartphones"), find(prefer=lo, snippet="Does not work with VPN enabled"), find(prefer=lo, snippet="endless loop")]},
  {"title": "Transfers and beneficiaries that disappear", "themes": ["transfers","stability"],
   "summary": "July 2026 reviews describe saved payees gone, a missing local transfer option, 'Unauthorized Access' on the beneficiary screen and a maintenance message at the moment of paying.",
   "quotes": [find(prefer=lo, snippet="All my saved payees have disappeared"), find(prefer=lo, snippet="I can't find the money transfer options anymore"), find(prefer=lo, snippet="Could not transfer to my existing beneficiary"), find(prefer=lo, snippet="can't pay our due bill on the credit card")]},
  {"title": "Features the old app had", "themes": ["features","usability"],
   "summary": "Card statements that only share as PDF, no total on the transaction list, the minimum payment figure gone, and the advanced transaction filter missing are the specific losses customers name.",
   "quotes": [find(prefer=lo, snippet="Impossible to download a card statement"), find(prefer=lo, snippet="advanced transaction filtering"), find(prefer=lo, snippet="The grey design does not look appealing"), find(prefer=lo, snippet="the fonts became too small")]},
  {"title": "Face Pass on every transfer (the previous app)", "themes": ["login","transfers"],
   "summary": "In 2024 the older app asked for Face Pass on transfers. Reviewers say it fails in low light, cannot be switched off for good and sends them back to the start.",
   "quotes": [find(prefer=lo, snippet="Face pass is so annoying"), find(prefer=lo, snippet="face pass is an annoying feature that I don't use"), find(prefer=lo, snippet="FaceId is a another peice of idiotic implementation")]},
  {"title": "The 2018 redesign (the previous app)", "themes": ["usability","update"],
   "summary": "The worst month in the older app's history was the version 5.9 redesign: balances that took many taps, a long welcome animation and crashes, with customers asking for the old version back.",
   "quotes": [find(prefer=lo, snippet="Too many movements to look the figures"), find(prefer=lo, snippet="30 second animation"), find(prefer=lo, snippet="Invalid Device ID")]},
 ],
 "wins": [
  {"title": "Fast bills and transfers in the older app", "themes": ["transfers"],
   "summary": f"The previous app averaged {av_old} over {no:,} reviews. Its long-time users describe fast bill payments and money transfers linked to partners.",
   "quotes": [find(prefer=hi, snippet="I pay most of my bills on it and it's super fast"), find(prefer=hi, snippet="I've had an exceptional experience with ADCB's mobile banking app")]},
  {"title": "Some customers prefer the new app", "themes": ["usability"],
   "summary": f"The new app has {sum(1 for r in rs if isnew(r) and r['rating'] >= 4):,} four and five star reviews. The converts mention a cleaner interface and navigation, and from October the AI guidance.",
   "quotes": [find(prefer=hi, snippet="this one is way better and UI is very easy"), find(prefer=hi, snippet="The recently added AI feature"), find(prefer=hi, snippet="very fast Transfer money and recharge bill")]},
  {"title": "Fast fixes after complaints", "themes": ["support"],
   "summary": f"ADCB answers {reply_all}% of written reviews, mostly within a day, and some reviewers return to say the problem was solved.",
   "quotes": [find(prefer=hi, snippet="Thank you now it works"), find(prefer=hi, snippet="Best Bank in the UAE")]},
 ],
}
