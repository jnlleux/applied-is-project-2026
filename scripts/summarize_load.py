import csv
import html
import json
from pathlib import Path
import statistics
import xml.etree.ElementTree as ET
out=Path('reports/lab8')
rows=[]
for users in [5,20,50,100]:
    stats=list(csv.DictReader((out/f'load-{users}_stats.csv').open()))[-1]
    resources=json.loads((out/f'resources-{users}.json').read_text())
    samples=resources['samples']
    rows.append({'users':users,'seconds':resources['duration_s'],'requests':int(stats['Request Count']),'errors':int(stats['Failure Count']),'avg_ms':float(stats['Average Response Time']),'p95_ms':float(stats['95%']),'rps':float(stats['Requests/s']),'cpu_avg':statistics.mean(x['cpu_percent'] for x in samples),'cpu_peak':max(x['cpu_percent'] for x in samples),'rss_peak':max(x['rss_mb'] for x in samples)})
(out/'summary.json').write_text(json.dumps(rows,indent=2))
text='# Нагрузочное тестирование AutoRent\n\nФактические результаты Locust и psutil на локальном сервере; отдельная временная SQLite.\n\n| Пользователи | Секунды | Запросы | Ошибки | Среднее, мс | p95, мс | Запросов/с | CPU среднее / пик, % | Пик RSS, МБ |\n|---|---|---|---|---|---|---|---|---|\n'
for r in rows:text+=f"| {r['users']} | {r['seconds']} | {r['requests']} | {r['errors']} ({100*r['errors']/max(r['requests'],1):.2f}%) | {r['avg_ms']:.2f} | {r['p95_ms']:.2f} | {r['rps']:.2f} | {r['cpu_avg']:.1f} / {r['cpu_peak']:.1f} | {r['rss_peak']:.1f} |\n"
a,b=rows[2:];text+=f"\nПри 50 → 100 пользователях средний ответ изменился с {a['avg_ms']:.2f} до {b['avg_ms']:.2f} мс; p95 — с {a['p95_ms']:.2f} до {b['p95_ms']:.2f} мс. Ошибок: {a['errors']} → {b['errors']}. Средний CPU: {a['cpu_avg']:.1f}% → {b['cpu_avg']:.1f}%; пиковая память: {a['rss_peak']:.1f} → {b['rss_peak']:.1f} МБ.\n"
text+='\nЭто измерения небольшого каталога на одном компьютере с генератором нагрузки. Они не позволяют доказать предельную ёмкость системы или назвать CPU/память узким местом только по процентам. Для роста данных сначала измерить запросы, добавить пагинацию и индексы; при интенсивной конкурентной записи перейти с SQLite на PostgreSQL. Кеширование каталога снизит число повторных чтений.\n\n![Графики нагрузки](load8.svg)\n'
Path('docs/labs/LOAD_8.md').write_text(text)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="560"><rect width="1000" height="560" fill="#f4f6fa"/><style>text{font-family:Arial;fill:#233347;font-size:14px}</style><text x="40" y="35" style="font-size:24px">AutoRent — фактическая нагрузка Locust</text>']
for panel,(key,label) in enumerate([('avg_ms','Средний ответ, мс'),('rps','Запросов / секунду')]):
    left=50+panel*490;top=90;maxval=max(r[key] for r in rows)*1.15
    svg.append(f'<text x="{left}" y="70">{label}</text>')
    for i,r in enumerate(rows):
        height=r[key]/maxval*330;x=left+i*105
        svg.append(f'<rect x="{x}" y="{450-height}" width="65" height="{height}" rx="5" fill="#428c83"/><text x="{x}" y="{440-height}">{r[key]:.1f}</text><text x="{x}" y="478">{r["users"]} users</text>')
svg.append('<text x="50" y="530">5 × 60 с · 20 × 120 с · 50 × 180 с · 100 × 180 с</text></svg>')
Path('docs/labs/load8.svg').write_text(''.join(svg))
root=ET.parse(out/'pytest.xml').getroot()
cases=root.findall('.//testcase')
report='<!doctype html><meta charset="utf-8"><title>AutoRent — pytest</title><style>body{font:16px system-ui;background:#f4f7fa;color:#24344a;padding:30px}li{padding:8px;background:white;margin:5px}h1{color:#167d58}</style><h1>AutoRent: результаты pytest</h1><p>Отчёт построен из сохранённого pytest.xml. Это результаты реального запуска, не терминальный скриншот.</p>'
report+=f'<h2>{len(cases)} тестов · {len(root.findall(".//failure"))} ошибок</h2><ul>'
for case in cases:report+='<li>'+html.escape(case.attrib['name'])+' — '+('FAIL' if case.find('failure') is not None else 'PASS')+'</li>'
(out/'pytest.html').write_text(report+'</ul>')
print(text)
