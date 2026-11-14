import json,datetime,sys
base=sys.argv[1]; out=sys.argv[2]
end=datetime.date.today(); days=120; start=(end-datetime.timedelta(days=days-1)).isoformat()
res={'end':end.isoformat(),'days':days,'apps':{}}
for a in ['enbdx','fab','adcb','wio','mashreq','adib']:
    o={'ios':{},'android':{}}
    for y in ('2026',):
        for r in json.load(open(f'{base}/{a}/reviews/{y}.json')):
            if r['date']>=start and r['platform'] in o and 1<=r['rating']<=5:
                o[r['platform']].setdefault(r['date'],[0]*5)[r['rating']-1]+=1
    res['apps'][a]=o
json.dump(res,open(out,'w'),separators=(',',':'))
print({a:sum(sum(v) for p in o.values() for v in p.values()) for a,o in res['apps'].items()}, start)
