import json,datetime,sys,collections
base=sys.argv[1]; out=sys.argv[2]
apps=['enbdx','fab','adcb','wio','mashreq','adib']
def wk(d):
    dt=datetime.date.fromisoformat(d); return (dt-datetime.timedelta(days=dt.weekday())).isoformat()
end=datetime.date.fromisoformat('2026-11-13')
last_mon=end-datetime.timedelta(days=end.weekday())
weeks=[(last_mon-datetime.timedelta(weeks=i)).isoformat() for i in range(77,-1,-1)]
wi={w:i for i,w in enumerate(weeks)}
res={'weeks':weeks,'apps':{}}
for a in apps:
    o={p:{'n':[0]*len(weeks),'s':[0]*len(weeks)} for p in ('ios','android')}
    for y in ('2025','2026'):
        for r in json.load(open(f'{base}/{a}/reviews/{y}.json')):
            w=wk(r['date'])
            if w in wi and r['platform'] in o:
                i=wi[w]; o[r['platform']]['n'][i]+=1; o[r['platform']]['s'][i]+=r['rating']
    res['apps'][a]=o
json.dump(res,open(out,'w'),separators=(',',':'))
print(out, {a:(sum(v['ios']['n']),sum(v['android']['n'])) for a,v in res['apps'].items()})
