"""Isolated local-only 5/20/50/100 user benchmark with backend CPU/RSS sampling."""
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import requests
import psutil

out=Path('reports/lab8');out.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    env={**os.environ,'DATABASE_URL':'sqlite:///'+tmp+'/load.db'}
    subprocess.run([sys.executable,'seed.py'],env=env,check=True)
    with open(out/'server.log','w') as log:
        server=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','18008','--no-access-log'],env=env,stdout=log,stderr=log)
        try:
            for _ in range(60):
                try:
                    if requests.get('http://127.0.0.1:18008/',timeout=1).status_code==200:break
                except requests.RequestException: pass
                time.sleep(.5)
            else: raise RuntimeError('Backend failed to start')
            process=psutil.Process(server.pid)
            for users,seconds in [(5,60),(20,120),(50,180),(100,180)]:
                print(f'START {users} users / {seconds}s',flush=True)
                with open(out/f'load-{users}.log','w') as log:
                    locust=subprocess.Popen([sys.executable,'-m','locust','-f','load/locustfile.py','--headless','--host','http://127.0.0.1:18008','-u',str(users),'-r',str(users),'-t',str(seconds)+'s','--csv',str(out/f'load-{users}'),'--html',str(out/f'load-{users}.html'),'--only-summary'],stdout=log,stderr=log)
                    samples=[];process.cpu_percent()
                    while locust.poll() is None:
                        samples.append({'cpu_percent':process.cpu_percent(interval=1),'rss_mb':process.memory_info().rss/1024**2})
                    (out/f'resources-{users}.json').write_text(json.dumps({'users':users,'duration_s':seconds,'exit_code':locust.returncode,'samples':samples},indent=2))
                    print(f'DONE {users}: exit={locust.returncode}',flush=True)
        finally:
            server.terminate();server.wait(timeout=15)
