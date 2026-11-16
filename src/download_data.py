"""Download source snapshots and record provenance without redistributing raw data."""
from pathlib import Path
import hashlib
import json
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
WEATHER_URL = ('https://archive-api.open-meteo.com/v1/archive?latitude=-7.80&longitude=110.37'
               '&start_date=2021-12-01&end_date=2022-02-15'
               '&daily=precipitation_sum,temperature_2m_mean&timezone=Asia%2FJakarta&models=era5')
SOURCES = {
    'presence_kapanewon_hourly.csv': 'https://zenodo.org/records/23157460/files/presence_kapanewon_hourly.csv?download=1',
    'JogjaPulse_README.txt': 'https://zenodo.org/records/23157460/files/README.md?download=1',
    'tier1_summary.csv': 'https://zenodo.org/records/23157460/files/tier1_summary.csv?download=1',
    'weather.json': WEATHER_URL,
}

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    records = []
    for name, url in SOURCES.items():
        path = RAW / name
        if not path.exists():
            temporary = path.with_suffix('.part')
            subprocess.run(['curl', '-L', '--fail', '--retry', '3', '--max-time', '180',
                            '--silent', '--show-error', url, '-o', str(temporary)], check=True)
            temporary.replace(path)
        records.append({'file': name, 'url': url, 'bytes': path.stat().st_size,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    out = ROOT / 'data/source_manifest.json'
    out.write_text(json.dumps({'verified_at_utc': datetime.now(timezone.utc).isoformat(),
                              'cache_policy': 'Existing snapshots retained; delete a raw file to refresh.',
                              'sources': records}, indent=2) + '\n')
    print(f'Source manifest: {out.relative_to(ROOT)}')

if __name__ == '__main__':
    main()
