"""Build the report and presentation script from computed findings."""
from pathlib import Path
import base64
import html
import json
import re
import shutil
import textwrap
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]

def main():
    team=json.loads((ROOT/'project.json').read_text())['members']
    names=', '.join(member['name'] for member in team)
    team_table='| Anggota | NIM |\n|---|---|\n'+'\n'.join(f"| {m['name']} | {m['student_id']} |" for m in team)
    f=json.loads((ROOT/'outputs/tables/findings.json').read_text())
    q=json.loads((ROOT/'outputs/tables/quality.json').read_text())
    m=f['weather_models'][0]
    effect=f"{m['pct_per_10mm']:.2f}%"
    ci=f"{m['pct_low']:.2f}% sampai +{m['pct_high']:.2f}%"
    report=f'''# Ritme Jogja — Hasil Analisis

{team_table}

Versi analisis 1.0.0. Jadwal presentasi dan pengumpulan mengikuti kelas/eLOK.

## Temuan utama

Pada sampel dan wilayah terpilih, profil kehadiran perangkat mencapai minimum pukul **03.00 WIB** dan maksimum pukul **19.00 WIB** pada kedua periode. Hari kerja dan akhir pekan memiliki bentuk umum yang serupa, dengan perbedaan pada jam tertentu. Analisis ini belum memberikan bukti yang meyakinkan tentang hubungan hujan harian dan kehadiran perangkat di Kota Yogyakarta.

Hasil tersebut menggambarkan kehadiran perangkat yang terekam aplikasi. Hasilnya bukan jumlah perjalanan, jumlah orang, ukuran kemacetan, atau estimasi seluruh penduduk DIY.

## Sumber dan sampel

- JogjaPulse, UGM: https://zenodo.org/records/23157460
- Definisi dan batasan JogjaPulse: https://zenodo.org/records/23157460/files/README.md?download=1
- Open-Meteo Historical Weather API: https://open-meteo.com/en/docs/historical-weather-api
- Rentang utama: 1 Desember 2021–15 Februari 2022, {q['days']} hari.
- File mobilitas penuh: {q['raw_rows']:,} baris; periode analisis: {q['analysis_rows']:,} baris dari {q['areas']} wilayah.
- {q['missing_slots_main_period']:,} dari 144.144 slot wilayah–tanggal–jam tidak dipublikasikan dalam periode utama. Slot tersebut tidak diisi nol.
- {q['eligible_90']} wilayah memenuhi coverage minimal 90% pada **masing-masing** periode sampel; ambang 95% menyisakan {q['eligible_95']} wilayah.
- Perbedaan dari pemeriksaan awal 65 wilayah: angka awal memakai coverage gabungan, sedangkan seleksi akhir lebih ketat dan memeriksa setiap periode.

Cuaca memakai curah hujan harian dan suhu rata-rata ERA5 dengan zona waktu WIB. Permintaan koordinat (-7,80; 110,37) menghasilkan grid ({q['weather_grid']['latitude']}; {q['weather_grid']['longitude']}). Resolusi ERA5 sekitar 25 km; grid ini merupakan proksi cuaca regional bagi analisis kota, bukan pengamatan lokal setiap kemantren. Respons, parameter, dan hash sumber dicatat pada `data/source_manifest.json`.

## Pengolahan dan metrik

Kunci data adalah wilayah × tanggal × jam. Kode administratif dipertahankan sebagai string. Nilai hitungan tidak dijumlahkan menjadi total perangkat unik. Kehadiran berarti setidaknya satu rekaman lokasi pada slot tersebut; pings mengukur volume rekaman.

Desember dan Januari–15 Februari dipisahkan karena perubahan sampel pada 1 Januari. Analisis dihentikan sebelum perubahan berikutnya pada 16 Februari. Perubahan komposisi dalam setiap periode tetap mungkin terjadi.

Profil harian menggunakan `n_maids / rata-rata n_maids per jam pada wilayah dan tanggal yang sama`. Hanya hari dengan minimal 22 jam terbit yang dipakai. Indeks 1 berarti sama dengan rata-rata hari tersebut. Karena pembaginya memakai jam yang terbit, dua slot hilang masih dapat memengaruhi bentuk profil. Indeks ini sengaja menghilangkan skala harian: tidak dapat dipakai untuk menyatakan volume akhir pekan lebih rendah atau tinggi.

Ringkasan dihitung dalam wilayah terlebih dahulu, kemudian dirata-ratakan dengan bobot sama antarwilayah. Heatmap merata-ratakan masing-masing hari dalam minggu; kurva hari kerja/akhir pekan merata-ratakan tanggal dalam kategori itu. Hari kerja berarti Senin–Jumat, sehingga hari libur nasional pada hari tersebut tetap masuk kategori hari kerja. Data ini belum mengendalikan kalender libur dan kebijakan pandemi.

## 1. Profil jam

![Heatmap pola jam](outputs/figures/01_hourly_heatmap.png)

Pola rata-rata mencapai minimum pada jam 03 dan maksimum pada jam 19 pada kedua periode. Kehadiran meningkat pada pagi hari dan tetap relatif tinggi dari siang hingga malam awal. Angka tersebut adalah pola gabungan dengan bobot wilayah sama; bukan klaim bahwa setiap wilayah mencapai puncak pada jam yang identik.

## 2. Hari kerja dan akhir pekan

![Profil hari kerja dan akhir pekan](outputs/figures/02_weekday_weekend.png)

Kedua kurva memiliki pola harian yang serupa. Perbedaan jam tertentu terlihat, terutama pada periode kedua. Kurva ini bersifat deskriptif, tanpa interval kepercayaan atau pengujian per jam; tidak menyatakan semua perbedaan terlihat signifikan. Bentuk yang mirip juga tidak membuktikan volume kehadiran absolut sama.

## 3. Rasio siang dan malam

![Rasio siang dan malam](outputs/figures/03_day_night.png)

Rasio harian membagi rata-rata presence pukul 08–17 dengan rata-rata pukul 00–05. Semua 16 slot pada kedua jendela harus terbit. Ringkasan memakai median rasio harian per wilayah dan periode. Agar masuk pemeringkatan, wilayah memerlukan minimal 14 hari lengkap pada **kedua** periode; {f['sensitivity']['day_night_eligible_areas']} wilayah memenuhi syarat.

Sepuluh wilayah ditampilkan berdasarkan lima nilai terendah dan tertinggi dari rerata dua median periode. Playen berada pada ujung tertinggi dan Gondomanan pada ujung terendah pemeringkatan ini. Nilai setiap periode ditampilkan terpisah agar perbedaan antarsampel terlihat. Tidak ada inferensi fungsi wilayah atau klaim arus komuter: frekuensi penggunaan aplikasi dan perubahan sampel dapat berkontribusi pada rasio.

## 4. Hujan di Kota Yogyakarta

![Estimasi hubungan hujan](outputs/figures/04_rain_association.png)

Model utama memakai {m['rows']:,} observasi wilayah–jam terbit, dari {m['areas']} kemantren dan {m['days']} tanggal. Respons `log(1 + n_maids)` diregresikan pada hujan harian, efek wilayah × periode sampel, efek jam, hari dalam minggu, dan tren tanggal terpisah per periode. Standard error dikelompokkan per tanggal dengan inferensi t; banyaknya tanggal, bukan baris, menentukan pengelompokan tersebut.

Estimasi asosiasi per tambahan 10 mm hujan adalah **{effect} pada skala (presence + 1)**, dengan interval kepercayaan 95% **{ci}**. Perubahan ini diturunkan dari `100 × (exp(10 × koefisien) − 1)`; bukan perubahan jumlah orang. Interval mencakup nol. Dengan data dan model ini, bukti hubungan hujan masih lemah; hasilnya tidak membuktikan bahwa hujan tidak berhubungan dengan aktivitas manusia.

Uji sensitivitas mencakup coverage 95%, penambahan suhu, pengeluaran tanggal di atas persentil ke-95 hujan, serta estimasi terpisah per periode. Semua interval hujan pada spesifikasi tersebut masih mencakup nol. Tabel lengkap tersedia pada `outputs/tables/weather_models.csv`.

Pengelompokan per tanggal menangani ketergantungan dalam hari yang sama, tetapi belum menangani seluruh korelasi antartanggal. Resolusi cuaca kasar, periode pendek, hujan harian yang tidak menunjukkan waktu turunnya, perubahan sampel, hari libur, dan kebijakan pandemi membatasi interpretasi. Model hanya dipasang pada baris terbit sehingga suppression juga dapat memengaruhi hasil.

## Pemeriksaan sensitivitas dan mutu

- Maksimum perubahan indeks heatmap saat ambang coverage dinaikkan dari 90% menjadi 95%: **{f['sensitivity']['max_absolute_index_difference_90_vs_95']:.3f} poin indeks**, pada sel hari-dalam-minggu × jam × periode. Ini pemeriksaan perubahan komposisi wilayah, bukan interval kepercayaan.
- {f['sensitivity']['complete_day_night_pairs']:,} pasangan hari siang/malam lengkap tersedia sebelum syarat minimal 14 hari kedua periode diterapkan.
- Uji otomatis memastikan nilai presence tetap sesuai sumber, rerata indeks harian sama dengan 1, cuaca tunggal per tanggal, dan syarat coverage berlaku pada kedua periode.
- Visual diperiksa untuk label, sumbu, konsistensi periode, dan keterbacaan.

## Kesimpulan

Data menunjukkan ritme kehadiran perangkat yang berulang dari dini hari ke malam awal. Profil berbeda antarwilayah dan sedikit berbeda antara hari kerja dan akhir pekan. Hubungan hujan belum dapat disimpulkan secara meyakinkan. Hasil paling kuat adalah pola waktu yang terlihat konsisten setelah pemisahan periode dan pemeriksaan coverage.

Penggunaan yang masuk akal adalah eksplorasi awal waktu aktivitas. Perencanaan transportasi atau kapasitas layanan memerlukan validasi tambahan dengan data perjalanan, pencatatan lapangan, dan sumber sampel yang lebih stabil.
'''
    (ROOT/'REPORT.md').write_text(report)
    scenes=[
        dict(id='opening',duration=25,title='Ritme Jogja',body='Kapan kehadiran perangkat meningkat,\ndan bagaimana kaitannya dengan hujan?',figure=None,credits='Muhammad Khoirunas · 24/533373/TK/59083\nAulia Nur Fajri Tri Anggoro · 24/535054/TK/59327\nMuhammad Farrel Alghazy · 24/540589/TK/60022\nWangsit Nursyahada · 24/545092/TK/60594',
             narration='Halo, kami tim Ritme Jogja. Proyek ini membahas ritme kehadiran perangkat di Daerah Istimewa Yogyakarta. Kami membandingkan pola jam, hari kerja dan akhir pekan, lalu mengeksplorasi hubungannya dengan hujan. Fokus kami adalah memahami pola yang tercatat, dengan memperhatikan kualitas data.'),
        dict(id='data',duration=40,title='Dua sumber, 77 hari pengamatan',body='JogjaPulse / UGM + Open-Meteo ERA5\n1 Desember 2021–15 Februari 2022\n63 wilayah lolos cakupan kedua periode',figure=None,
             narration='Sumber pertama adalah JogjaPulse dari UGM, berupa jumlah perangkat berbeda yang teramati per wilayah dan per jam. Sumber kedua adalah cuaca historis Open-Meteo, dengan model reanalisis ERA5. Periode utama mencakup 77 hari. Dari 78 wilayah, 63 memiliki setidaknya 90 persen slot terbit pada masing-masing periode. Analisis cuaca dibatasi pada 11 kemantren terpilih di Kota Yogyakarta. Data cuacanya berasal dari satu grid regional, bukan alat ukur pada setiap kemantren.'),
        dict(id='method',duration=40,title='Perubahan sampel perlu diperhitungkan',body='Desember dipisahkan dari Januari–15 Februari\nNilai hilang tidak dianggap nol\nIndeks 1 = rerata kehadiran hari tersebut',figure=None,
             narration='Jumlah perangkat dalam sumber berubah pada awal Januari dan pertengahan Februari. Karena itu, kami memisahkan Desember dari Januari sampai 15 Februari, dan berhenti sebelum perubahan kedua. Kehadiran per jam dibagi rata-rata kehadiran pada hari dan wilayah yang sama. Indeks ini menjelaskan bentuk harian, bukan perubahan volume mobilitas antartanggal. Hanya hari dengan minimal 22 jam terbit yang dipakai. Baris yang tidak diterbitkan tetap hilang, karena hitungan kecil disembunyikan. Setiap wilayah memperoleh bobot yang sama dalam ringkasan profil.'),
        dict(id='rhythm',duration=40,title='Minimum pukul 03, maksimum pukul 19',figure='01_hourly_heatmap',body='',
             narration='Heatmap menampilkan hari dalam minggu pada sumbu vertikal dan jam pada sumbu horizontal. Warna lebih gelap menunjukkan indeks kehadiran relatif lebih tinggi. Pada ringkasan kedua periode, titik terendah berada sekitar pukul tiga dini hari dan tertinggi sekitar pukul tujuh malam. Kehadiran naik pada pagi hari lalu relatif tinggi dari siang hingga malam awal. Ini pola gabungan wilayah yang lolos seleksi, bukan total penduduk DIY. Puncak rata-rata tersebut juga tidak berarti semua wilayah memiliki jam puncak yang sama.'),
        dict(id='weekend',duration=35,title='Bentuk hari kerja dan akhir pekan serupa',figure='02_weekday_weekend',body='',
             narration='Kurva hijau menunjukkan hari kerja, sedangkan kurva jingga menunjukkan akhir pekan. Keduanya memiliki bentuk umum yang serupa: rendah pada dini hari dan lebih tinggi pada siang sampai malam awal. Perbedaan beberapa jam tampak lebih jelas pada periode kedua. Namun, kami tidak menguji perbedaan setiap jam sebagai temuan signifikan. Karena indeks dinormalisasi dalam hari, grafik ini juga tidak membuktikan bahwa volume kehadiran akhir pekan sama dengan hari kerja. Hari kerja di sini berarti Senin sampai Jumat.'),
        dict(id='daynight',duration=35,title='Profil siang dan malam berbeda antarwilayah',figure='03_day_night',body='',
             narration='Kami membandingkan rata-rata kehadiran pukul delapan sampai tujuh belas dengan pukul nol sampai lima. Hari harus memiliki semua slot pada dua jendela tersebut. Sebanyak 58 wilayah memiliki minimal 14 hari lengkap pada kedua periode. Grafik memperlihatkan lima rasio terendah dan tertinggi dari ringkasan dua periode. Playen berada pada ujung tinggi dan Gondomanan pada ujung rendah pemeringkatan ini. Rasio tersebut bukan bukti fungsi wilayah atau arus komuter; pola pencatatan aplikasi juga dapat memengaruhinya.'),
        dict(id='rain',duration=50,title='Hubungan dengan hujan belum meyakinkan',figure='04_rain_association',body='',
             narration=f'Untuk Kota Yogyakarta, model menghubungkan hujan harian dengan log satu ditambah kehadiran perangkat. Model menyesuaikan wilayah dan periode sampel, jam, hari dalam minggu, serta tren tanggal dalam tiap periode. Pengelompokan ketidakpastian memakai tanggal, karena banyak baris pada hari yang sama berbagi kondisi cuaca. Estimasi utama per tambahan sepuluh milimeter hujan sekitar minus nol koma dua dua persen pada skala kehadiran ditambah satu. Interval kepercayaan 95 persen berkisar minus satu koma sembilan enam sampai plus satu koma lima enam persen. Semua variasi model masih mencakup nol. Jadi bukti hubungan masih lemah; ini bukan bukti bahwa hujan tidak berhubungan dengan aktivitas.'),
        dict(id='closing',duration=35,title='Ritme terlihat; klaim tetap dibatasi data',body='Pola waktu konsisten pada dua periode\nCuaca belum memberi kesimpulan kuat\nPerangkat teramati ≠ orang atau perjalanan',figure=None,credits='Voice: Kokoro af_heart · Music: Sascha Ende, ende.app (CC BY 4.0)',
             narration='Ketika ambang cakupan dinaikkan menjadi 95 persen, perubahan terbesar heatmap hanya sekitar nol koma nol dua empat poin indeks. Namun, sampel aplikasi bukan sampel acak penduduk. Cuaca memakai grid sekitar 25 kilometer, dan model belum mengatasi semua korelasi antartanggal atau faktor kalender. Kesimpulan kami: ritme kehadiran terlihat konsisten, sedangkan hubungan hujan belum meyakinkan. Kode, tabel, grafik, dan sumber disertakan agar analisis dapat diperiksa ulang. Kode dan notebook disertakan dalam paket proyek di Google Drive. Terima kasih.'),
    ]
    assert sum(s['duration'] for s in scenes)==300
    (ROOT/'presentation/scenes.json').write_text(json.dumps(scenes,indent=2,ensure_ascii=False)+'\n')
    script=['# Naskah presentasi lima menit','', 'Tim: Muhammad Khoirunas, Aulia Nur Fajri Tri Anggoro, Muhammad Farrel Alghazy, Wangsit Nursyahada. Naskah ini merupakan referensi bahasa Indonesia; video rilis menggunakan narasi sintetis bahasa Inggris.','']
    start=0
    for s in scenes:
        end=start+s['duration']
        script += [f"## {start//60:02}:{start%60:02}–{end//60:02}:{end%60:02} — {s['title']}",'',s['narration'],'']
        start=end
    (ROOT/'presentation/NASKAH.md').write_text('\n'.join(script))
    for name in ['01_quality','02_analysis']:
        nb=nbf.v4.new_notebook()
        nb.metadata['kernelspec']={'display_name':'Python 3','language':'python','name':'python3'}
        tables=['quality.json','coverage_by_area_segment.csv'] if name=='01_quality' else ['findings.json','weather_models.csv']
        nb.cells=[nbf.v4.new_markdown_cell('# '+('Pemeriksaan mutu sumber' if name=='01_quality' else 'Hasil dan visualisasi')+'\n'+team_table+'\nJalankan pipeline dari README sebelum notebook. Angka tersimpan berasal dari keluaran pipeline.'),
                  nbf.v4.new_code_cell("from pathlib import Path\nimport json\nimport pandas as pd\nfrom IPython.display import display, Image\nroot = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()")]
        for table in tables:
            code=f"print((root / 'outputs/tables/{table}').read_text())" if table.endswith('json') else f"display(pd.read_csv(root / 'outputs/tables/{table}').head(20))"
            cell=nbf.v4.new_code_cell(code)
            # Include verified cached results, with execution_count=None until run by the reader.
            cell.outputs=[nbf.v4.new_output('stream',name='stdout',text=(ROOT/'outputs/tables'/table).read_text())] if table.endswith('json') else []
            nb.cells.append(cell)
        if name=='02_analysis':
            for s in scenes:
                if s['figure']:
                    cell=nbf.v4.new_code_cell(f"display(Image(filename=str(root / 'outputs/figures/{s['figure']}.png')))")
                    cell.outputs=[nbf.v4.new_output('display_data',data={'image/png':base64.b64encode((ROOT/f"outputs/figures/{s['figure']}.png").read_bytes()).decode()})]
                    nb.cells.append(cell)
        nbf.write(nb, ROOT/f'notebooks/{name}.ipynb')
    make_video(scenes)
    print('Built REPORT.md, presentation/NASKAH.md, scenes.json, notebooks and video source.')

def make_video(scenes, video=None):
    video=Path(video) if video else ROOT/'presentation/video'
    (video/'compositions').mkdir(parents=True,exist_ok=True)
    (video/'assets').mkdir(exist_ok=True)
    gsap_source=ROOT/'presentation/video/assets/gsap.min.js'
    gsap_target=video/'assets/gsap.min.js'
    if gsap_source.exists() and gsap_source.resolve()!=gsap_target.resolve():
        shutil.copy(gsap_source,gsap_target)
    audio_tracks=[]
    manifest_path=ROOT/'brag-output/audio_manifest.json'
    is_release=video.resolve()==(ROOT/'brag-output/composition').resolve()
    manifest=json.loads(manifest_path.read_text()) if is_release and manifest_path.exists() else None
    hosts=[]
    start=0
    for s in scenes:
        sid=s['id']
        dur=s['duration']
        if s['figure']:
            shutil.copy(ROOT/f"outputs/figures/{s['figure']}_video.png",video/f"assets/{s['figure']}.png")
            visual=f'<img id="{sid}-chart" src="assets/{s["figure"]}.png" alt="{html.escape(s["title"])}" />'
        else:
            visual='<p class="body">'+html.escape(s['body']).replace('\n','<br>')+'</p>'
        if s.get('credits'):
            visual += '<p class="credits">'+html.escape(s['credits']).replace('\n','<br>')+'</p>'
        # Four reading beats per scene; transcript is retained in full for human narration.
        sentences = re.split(r'(?<=[.!?])\s+', s['narration'])
        groups=[]
        for sentence in sentences:
            if groups and len(groups[-1]) + len(sentence) + 1 <= 280:
                groups[-1] += ' ' + sentence
            else:
                groups.append(sentence)
        total_words=sum(len(g.split()) for g in groups)
        captions=''
        voice_clip=next((c for c in manifest['clips'] if c['scene']==sid),None) if manifest else None
        caption_duration=voice_clip['duration_seconds'] if voice_clip else dur
        elapsed=voice_clip['start_seconds'] if voice_clip else 0.0
        for i,text in enumerate(groups):
            duration=caption_duration*len(text.split())/total_words
            captions+=f'<div id="{sid}-caption-{i}" class="clip caption" data-start="{elapsed:.4f}" data-duration="{duration:.4f}" data-track-index="2"><p>{html.escape(text)}</p></div>'
            elapsed+=duration
        source=s.get('source', 'Sumber: JogjaPulse / UGM · Zenodo 23157460; Open-Meteo ERA5. Analisis kelompok.')
        content=f'''<template>
<style>
#root {{ position:absolute; inset:0; background:#fff; color:#172f2d; font-family:Inter,sans-serif; }}
* {{ box-sizing:border-box; margin:0; }}
.scene {{ position:absolute; inset:0; background:#fff; }}
h1 {{ position:absolute; left:196px; top:112px; width:1528px; font-size:56px; font-weight:700; line-height:1.12; }}
.body {{ position:absolute; left:196px; top:300px; width:1528px; font-size:49px; line-height:1.6; color:#146b66; }}
img {{ position:absolute; left:196px; top:245px; width:1528px; height:520px; object-fit:contain; }}
.caption {{ position:absolute; left:196px; top:808px; width:1528px; height:145px; background:#eef5f4; padding:18px 24px; }}
.credits {{position:absolute;left:196px;top:558px;width:1528px;font-size:28px;line-height:1.25;color:#172f2d;}}
.caption p {{font-size:28px; line-height:1.35; color:#172f2d;}}
.source {{ position:absolute; left:196px; top:972px; width:1528px; font-size:28px; color:#435e5b; }}
</style>
<div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">
<div id="{sid}-scene" class="clip scene" data-start="0" data-duration="{dur}" data-hold="true"><h1>{html.escape(s['title'])}</h1>{visual}<p class="source">{source}</p></div>
{captions}
</div>
<script>
const tl=gsap.timeline({{paused:true}});
tl.fromTo('#{sid}-scene h1',{{opacity:1}},{{opacity:1,duration:{dur-.01}}},0);
window.__timelines['{sid}']=tl;
</script>
</template>'''
        (video/f'compositions/{sid}.html').write_text(content)
        hosts.append(f'<div id="{sid}" class="clip" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{start}" data-duration="{dur}" data-track-index="0" data-track-kind="graphics" data-width="1920" data-height="1080"></div>')
        if manifest:
            clip=next(c for c in manifest['clips'] if c['scene']==sid)
            audio_tracks.append(f'<audio id="voice-{sid}" class="clip" data-start="{start+clip["start_seconds"]:.3f}" data-duration="{clip["duration_seconds"]:.3f}" data-track-index="3" data-volume="1" src="{clip["file"]}"></audio>')
        start+=dur
    if manifest:
        audio_tracks.append('<audio id="music-bed" class="clip" data-start="0" data-duration="300" data-track-index="10" data-volume="0.09" data-fade-in="2" data-fade-out="4" src="assets/music/music-bed.mp3"></audio>')
        for sid, t in [('rhythm',105),('closing',265)]:
            audio_tracks.append(f'<audio id="accent-{sid}" class="clip" data-start="{t}" data-duration="0.11" data-track-index="11" data-volume="0.12" src="assets/sfx/drop_001.ogg"></audio>')
    tracks=''.join(audio_tracks)
    html_doc='''<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920,height=1080"><script src="assets/gsap.min.js"></script><style>*{margin:0;padding:0;box-sizing:border-box}html,body{width:1920px;height:1080px;overflow:hidden;background:white}#root{position:absolute;inset:0}</style></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="300" data-fps="30" data-width="1920" data-height="1080">'''+''.join(hosts)+tracks+'''</div><script>window.__timelines=window.__timelines||{};window.__timelines.main=gsap.timeline({paused:true});</script></body></html>'''
    (video/'index.html').write_text(html_doc)

if __name__=='__main__':
    main()
