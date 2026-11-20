"""Actual HTTP integration evidence, using a temporary local database and accounts."""
import json, os, secrets, subprocess, sys, tempfile, time
from pathlib import Path
import requests
from app.security import hash_password
out=Path('reports/lab8')
with tempfile.TemporaryDirectory() as tmp:
    password=secrets.token_urlsafe(20)+'1'
    users=Path(tmp)/'users.json'
    users.write_text(json.dumps({'admin':{'role':'admin','password_hash':hash_password(password)},'reader':{'role':'viewer','password_hash':hash_password(password)}}))
    env={**os.environ,'DATABASE_URL':'sqlite:///'+tmp+'/db.sqlite','AUTORENT_USERS_FILE':str(users)}
    with open(out/'http-server.log','w') as log:
        server=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','18009','--no-access-log'],env=env,stdout=log,stderr=log)
        try:
            for _ in range(60):
                try:
                    if requests.get('http://127.0.0.1:18009/',timeout=1).ok:break
                except requests.RequestException: pass
                time.sleep(.25)
            records=[]
            def call(method,path,expected,role='admin',**kwargs):
                r=requests.request(method,'http://127.0.0.1:18009'+path,auth=(role,password) if role else None,timeout=10,**kwargs)
                records.append({'method':method,'path':path,'expected':expected,'actual':r.status_code,'body':r.json() if r.content else None,'passed':r.status_code==expected})
                return r
            call('GET','/categories',200)
            key=call('POST','/categories',201,json={'name':'HTTP example','daily_rate':1000}).json()['id']
            call('PUT',f'/categories/{key}',200,json={'name':'HTTP updated','daily_rate':2000})
            call('GET',f'/categories/{key}',200)
            call('POST','/categories',422,json={})
            call('POST','/categories',400,data='{broken',headers={'Content-Type':'application/json'})
            call('GET','/clients/9999',404)
            call('GET','/clients',401,role=None)
            call('GET','/auth/me',401,role='missing')
            call('DELETE',f'/categories/{key}',403,role='reader')
            call('DELETE',f'/categories/{key}',204)
            call('GET',f'/categories/{key}',404)
            (out/'http-results.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
            print(f'HTTP checks: {sum(r["passed"] for r in records)}/{len(records)} passed')
            if not all(r['passed'] for r in records):sys.exit(1)
        finally:server.terminate();server.wait(timeout=10)
