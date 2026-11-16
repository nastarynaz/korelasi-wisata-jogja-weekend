"""Produce region-balanced profiles and exploratory weather associations."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
FIG, TAB = ROOT/'outputs/figures', ROOT/'outputs/tables'
COLORS = ['#146b66', '#c15c30']
SEGMENTS = ['Des 2021', 'Jan–15 Feb 2022']

def save(fig, name):
    fig.savefig(FIG/f'{name}.png', dpi=180, bbox_inches='tight', facecolor='white')
    fig.savefig(FIG/f'{name}.pdf', bbox_inches='tight', facecolor='white')
    # Reuse the same plotted data with larger labels for the 1080p video.
    fig.set_size_inches(15, 5)
    if fig._suptitle:
        fig._suptitle.set_visible(False)
    from matplotlib.text import Text
    for text in fig.findobj(Text):
        text.set_fontsize(20)
    for ax in fig.axes:
        if 'Indeks profil' in ax.get_ylabel():
            ax.set_ylabel('Indeks harian')
        if name == '03_day_night':
            ax.set_title('')
            ax.set_xlabel('Median rasio siang / malam')
        if name == '04_rain_association':
            ax.set_title('')
            ax.set_xlabel('Estimasi % per +10 mm hujan (presence + 1)')
            ax.set_yticklabels(['Utama','Cakupan 95%','Dengan suhu','Tanpa hujan ekstrem','Desember','Jan–15 Feb'])
    fig.tight_layout(pad=.6)
    fig.savefig(FIG/f'{name}_video.png', dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)

def profile(df, threshold=.90):
    d = df[(df.coverage_min_segment >= threshold) & (df.slots_day >= 22)]
    # Each region contributes one mean per calendar group, regardless of its number of rows.
    return d.groupby(['segment','kapanewon_code','dow','hour']).daily_index.mean().reset_index()

def weather_fit(df, label, extra='', threshold=.90, segment=None, no_extreme=False):
    d = df[(df.kab_kota == 'YOGYAKARTA') & (df.coverage_min_segment >= threshold)
           & (df.slots_day >= 22)].copy()
    if segment:
        d = d[d.segment == segment]
    if no_extreme:
        cutoff = d[['date','rain_mm']].drop_duplicates().rain_mm.quantile(.95)
        d = d[d.rain_mm <= cutoff]
    formula = ('np.log1p(n_maids) ~ rain_mm + C(kapanewon_code)*C(segment)'
               ' + C(hour) + C(dow) + trend:C(segment)' + extra)
    fit = smf.ols(formula, data=d).fit(cov_type='cluster', cov_kwds={'groups': d.date}, use_t=True)
    lo, hi = fit.conf_int().loc['rain_mm']
    b = fit.params['rain_mm']
    row = {'model':label, 'coef_log_per_mm':b, 'ci_low':lo, 'ci_high':hi,
           'pct_per_10mm':100*np.expm1(10*b), 'pct_low':100*np.expm1(10*lo),
           'pct_high':100*np.expm1(10*hi), 'pvalue':fit.pvalues['rain_mm'],
           'rows':len(d), 'days':d.date.nunique(), 'areas':d.kapanewon_code.nunique(),
           'formula':formula}
    (TAB / f'model_{label}.txt').write_text(
        f'Formula: {formula}\nCovariance: cluster by date; t inference\n'
        f'N={len(d)}; dates={d.date.nunique()}; rank={np.linalg.matrix_rank(fit.model.exog)}\n'
        + pd.DataFrame({'coef':fit.params, 'se':fit.bse, 'pvalue':fit.pvalues,
                        'ci_low':fit.conf_int()[0], 'ci_high':fit.conf_int()[1]}).to_string())
    return row

def main():
    FIG.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(ROOT/'data/processed/presence_weather.csv', parse_dates=['date'],
                     dtype={'kapanewon_code':str, 'kab_code':str})
    sns.set_theme(style='whitegrid', font_scale=1.05)
    plt.rcParams.update({'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Sans'})
    p = profile(df)
    p.to_csv(TAB/'profiles_area_dow_hour.csv', index=False)
    heat = p.groupby(['segment','dow','hour']).daily_index.mean()
    fig, axes = plt.subplots(1,2,figsize=(15,5),sharey=True)
    for ax, seg in zip(axes,SEGMENTS):
        mat = heat.loc[seg].unstack().reindex(range(7))
        sns.heatmap(mat,ax=ax,cmap='YlGnBu',vmin=.3,vmax=1.5,
                    xticklabels=3,yticklabels=['Sen','Sel','Rab','Kam','Jum','Sab','Min'],
                    cbar_kws={'label':'Indeks profil (1 = rerata hari)'})
        ax.set(title=seg,xlabel='Jam WIB',ylabel='')
    fig.suptitle('Bentuk kehadiran per jam, dengan bobot sama per wilayah',fontsize=18)
    fig.tight_layout()
    save(fig,'01_hourly_heatmap')
    d = df[(df.coverage_min_segment >= .9)&(df.slots_day >= 22)]
    curves = d.groupby(['segment','kapanewon_code','weekend','hour']).daily_index.mean().reset_index()
    curves = curves.groupby(['segment','weekend','hour']).daily_index.mean().reset_index()
    curves.to_csv(TAB/'weekday_weekend_profiles.csv',index=False)
    fig, axes = plt.subplots(1,2,figsize=(14,5),sharey=True)
    for ax,seg in zip(axes,SEGMENTS):
        for group,color in zip(['Hari kerja','Akhir pekan'],COLORS):
            c = curves[(curves.segment==seg)&(curves.weekend==group)]
            ax.plot(c.hour,c.daily_index,label=group,color=color,lw=2.8)
        ax.axhline(1,c='gray',ls='--',lw=1)
        ax.set(title=seg,xlabel='Jam WIB',xticks=range(0,24,3),ylim=(.25,1.6))
        ax.legend(frameon=False)
    axes[0].set_ylabel('Indeks profil harian')
    fig.suptitle('Hari kerja dan akhir pekan: bandingkan bentuk, bukan total',fontsize=18)
    fig.tight_layout()
    save(fig,'02_weekday_weekend')
    windows = df[(df.coverage_min_segment>=.9) & ((df.hour<6)|df.hour.between(8,17))].copy()
    windows['window'] = np.where(windows.hour<6,'night','day')
    group = windows.groupby(['segment','kapanewon_code','kapanewon','date','window']).n_maids.agg(['mean','size']).reset_index()
    group = group[((group.window=='night')&(group['size']==6))|((group.window=='day')&(group['size']==10))]
    paired = group.pivot(index=['segment','kapanewon_code','kapanewon','date'],columns='window',values='mean').dropna().reset_index()
    paired['ratio'] = paired.day / paired.night
    ratios = paired.groupby(['segment','kapanewon_code','kapanewon']).ratio.agg(['median','size']).reset_index()
    ratios.to_csv(TAB/'day_night_ratios.csv',index=False)
    # Require >=14 complete paired days in BOTH periods before ranking.
    enough = ratios.groupby('kapanewon_code')['size'].agg(['min','count'])
    codes = enough[(enough['min']>=14)&(enough['count']==2)].index
    comparable = ratios[ratios.kapanewon_code.isin(codes)]
    ranking = comparable.groupby(['kapanewon_code','kapanewon'])['median'].mean().sort_values()
    selected = pd.concat([ranking.head(5),ranking.tail(5)]).drop_duplicates()
    names = selected.index.get_level_values('kapanewon')
    fig, ax = plt.subplots(figsize=(11,6))
    for seg,color,offset in zip(SEGMENTS,COLORS,[-.13,.13]):
        s = comparable[comparable.segment==seg].set_index(['kapanewon_code','kapanewon']).reindex(selected.index)
        ax.scatter(s['median'],np.arange(len(selected))+offset,label=seg,color=color,s=60)
    ax.axvline(1,color='gray',ls='--')
    ax.set(yticks=range(len(selected)),yticklabels=names,xlabel='Median rasio rerata presence siang / malam',
           title='Lima rasio terendah dan tertinggi pada wilayah yang cukup lengkap')
    ax.legend(frameon=False)
    fig.tight_layout()
    save(fig,'03_day_night')
    models = [weather_fit(df,'utama'), weather_fit(df,'coverage95',threshold=.95),
              weather_fit(df,'dengan_suhu',extra=' + temp_c'),
              weather_fit(df,'tanpa_hujan_teratas',no_extreme=True)]
    for seg,label in zip(SEGMENTS,['desember','januari_februari']):
        models.append(weather_fit(df,label,segment=seg))
    modeltab = pd.DataFrame(models)
    modeltab.to_csv(TAB/'weather_models.csv',index=False)
    fig,ax=plt.subplots(figsize=(11,5))
    for i,row in modeltab.iterrows():
        ax.errorbar(row.pct_per_10mm,i,xerr=[[row.pct_per_10mm-row.pct_low],[row.pct_high-row.pct_per_10mm]],
                    fmt='o',color=COLORS[0] if i==0 else '#676767',capsize=5)
    ax.axvline(0,color='gray',ls='--')
    ax.set(yticks=range(len(modeltab)),yticklabels=modeltab.model,
           xlabel='Perubahan estimasi (presence + 1), % per tambahan 10 mm hujan',
           title='Hubungan hujan dan kehadiran tercatat di Kota Yogyakarta\nInterval kepercayaan 95%; standard error dikelompokkan per tanggal')
    ax.invert_yaxis()
    fig.tight_layout()
    save(fig,'04_rain_association')
    # Shape sensitivity: maximum hourly difference between area-coverage thresholds.
    p95=profile(df,.95).groupby(['segment','dow','hour']).daily_index.mean()
    differences=(heat-p95).abs()
    sens={'max_absolute_index_difference_90_vs_95':float(differences.max()),
          'day_night_eligible_areas':len(codes), 'complete_day_night_pairs':len(paired)}
    peaks = heat.groupby(['segment','hour']).mean()
    peak_info={seg:{'peak_hour':int(peaks.loc[seg].idxmax()),'lowest_hour':int(peaks.loc[seg].idxmin())} for seg in SEGMENTS}
    findings={'period_start':'2021-12-01','period_end':'2022-02-15','peaks':peak_info,
              'weather_models':models,'sensitivity':sens,
              'highest_day_night':ranking.tail(5).reset_index().to_dict(orient='records'),
              'lowest_day_night':ranking.head(5).reset_index().to_dict(orient='records')}
    (TAB/'findings.json').write_text(json.dumps(findings,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(findings,indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
