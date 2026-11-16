"""Read the private project Google Sheets using Colab Google credentials."""
from pathlib import Path
import csv, io, json, hashlib
from datetime import datetime, timezone
import google.auth
from google.auth.transport.requests import AuthorizedSession
ROOT=Path(__file__).resolve().parents[1]

def main():
    config=json.loads((ROOT/'data/sheets_sources.json').read_text())
    credentials,_=google.auth.default()
    session=AuthorizedSession(credentials)
    raw=ROOT/'data/raw'; raw.mkdir(parents=True,exist_ok=True)
    records=[]
    for key,expected in [('mobility',8),('weather',3)]:
        source=config[key]
        rows=[]
        for start in range(1,source['rows']+2,10000):
            end=min(start+9999,source['rows']+1)
            column='H' if key=='mobility' else 'C'
            a1=f"'{source['tab']}'!A{start}:{column}{end}"
            from urllib.parse import quote
            response=session.get(f"https://sheets.googleapis.com/v4/spreadsheets/{source['id']}/values/{quote(a1,safe='')}",params={'valueRenderOption':'FORMATTED_VALUE'},timeout=120)
            response.raise_for_status()
            batch=response.json().get('values',[])
            rows.extend(batch)
            print(f'{key}: read through row {end}',flush=True)
        if len(rows)!=source['rows']+1 or any(len(row)!=expected for row in rows):
            raise ValueError(f'{key}: incomplete Sheet data; expected {source["rows"]} rows')
        if rows[0]!=source['columns']:
            raise ValueError(f'{key}: Sheet header differs from expected schema')
        if key=='mobility':
            target=raw/'presence_kapanewon_hourly.csv'
            with target.open('w',newline='') as out: csv.writer(out).writerows(rows)
        else:
            template=config['weather_metadata'].copy()
            template['daily']={'time':[r[0] for r in rows[1:]],'precipitation_sum':[float(r[1]) for r in rows[1:]],'temperature_2m_mean':[float(r[2]) for r in rows[1:]]}
            target=raw/'weather.json'
            target.write_text(json.dumps(template,indent=2)+'\n')
        records.append({'source':key,'spreadsheet_id':source['id'],'tab':source['tab'],'rows':len(rows)-1,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    (ROOT/'data/sheets_run_manifest.json').write_text(json.dumps({'read_at_utc':datetime.now(timezone.utc).isoformat(),'sources':records},indent=2)+'\n')
    print('Both data sources loaded from private Google Sheets.')

if __name__=='__main__':main()
