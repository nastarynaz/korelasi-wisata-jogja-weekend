"""Validate source semantics and retain only observed hourly presence values."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
START, END = '2021-12-01', '2022-02-15'

def main():
    raw = pd.read_csv(ROOT / 'data/raw/presence_kapanewon_hourly.csv',
                      dtype={'kab_code': str, 'kapanewon_code': str})
    keys = ['kapanewon_code', 'date', 'hour']
    assert not raw.duplicated(keys).any(), 'Duplicate area-date-hour keys'
    assert raw[keys + ['n_maids', 'n_pings']].notna().all().all()
    assert raw.hour.between(0, 23).all() and (raw.n_maids >= 5).all()
    assert (raw.n_pings >= raw.n_maids).all()
    raw['date'] = pd.to_datetime(raw.date)
    df = raw.loc[raw.date.between(START, END)].copy()
    df['segment'] = np.where(df.date < '2022-01-01', 'Des 2021', 'Jan–15 Feb 2022')
    df['dow'] = df.date.dt.day_of_week
    df['weekend'] = np.where(df.dow >= 5, 'Akhir pekan', 'Hari kerja')
    df['trend'] = df.groupby('segment').date.transform(lambda s: (s - s.min()).dt.days)
    df['slots_day'] = df.groupby(['kapanewon_code', 'date']).hour.transform('size')
    df['daily_index'] = df.n_maids / df.groupby(['kapanewon_code', 'date']).n_maids.transform('mean')
    area = df[['kapanewon_code', 'kapanewon', 'kab_kota']].drop_duplicates()
    cover = pd.MultiIndex.from_product([area.kapanewon_code, df.segment.unique()],
                                      names=['kapanewon_code', 'segment']).to_frame(index=False)
    cover = cover.merge(df.groupby(['kapanewon_code', 'segment']).size().rename('published_slots'),
                        on=['kapanewon_code', 'segment'], how='left')
    days = df.groupby('segment').date.nunique()
    cover['expected_slots'] = cover.segment.map(days) * 24
    cover['published_slots'] = cover.published_slots.fillna(0).astype(int)
    cover['coverage'] = cover.published_slots / cover.expected_slots
    cover = cover.merge(area, on='kapanewon_code', validate='many_to_one')
    eligible = cover.groupby('kapanewon_code').coverage.min()
    df['coverage_min_segment'] = df.kapanewon_code.map(eligible)
    weather_raw = json.loads((ROOT / 'data/raw/weather.json').read_text())
    weather = pd.DataFrame(weather_raw['daily']).rename(columns={'time': 'date',
                         'precipitation_sum': 'rain_mm', 'temperature_2m_mean': 'temp_c'})
    weather['date'] = pd.to_datetime(weather.date)
    assert not weather.date.duplicated().any()
    assert len(weather) == 77 and weather[['rain_mm', 'temp_c']].notna().all().all()
    assert weather.date.min() == pd.Timestamp(START) and weather.date.max() == pd.Timestamp(END)
    assert (weather.rain_mm >= 0).all()
    df = df.merge(weather, on='date', how='left', validate='many_to_one')
    assert len(df) == len(raw.loc[raw.date.between(START, END)])
    assert df.rain_mm.notna().all()
    processed = ROOT / 'data/processed'
    tables = ROOT / 'outputs/tables'
    processed.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed / 'presence_weather.csv', index=False)
    weather.to_csv(processed / 'weather_daily.csv', index=False)
    cover.to_csv(tables / 'coverage_by_area_segment.csv', index=False)
    df.groupby(['date', 'kab_kota']).size().rename('published_slots').to_csv(tables / 'coverage_by_date_regency.csv')
    quality = {'raw_rows': len(raw), 'analysis_rows': len(df), 'days': df.date.nunique(),
               'areas': len(area), 'eligible_90': int((eligible >= .90).sum()),
               'eligible_95': int((eligible >= .95).sum()),
               'missing_slots_main_period': int(78*77*24-len(df)),
               'weather_days': len(weather),
               'weather_grid': {k: weather_raw.get(k) for k in ['latitude','longitude','elevation','timezone']},
               'rules': ['Missing/suppressed rows are never zero-filled.',
                         'Counts are not summed into unique people or unique DIY devices.',
                         'Daily shape indices do not estimate absolute mobility changes.']}
    (tables / 'quality.json').write_text(json.dumps(quality, indent=2) + '\n')
    print(json.dumps(quality, indent=2))

if __name__ == '__main__':
    main()
