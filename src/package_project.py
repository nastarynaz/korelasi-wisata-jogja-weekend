"""Bundle code and derived outputs, excluding raw data and local environments."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import sys

ROOT=Path(__file__).resolve().parents[1]

def main():
    include_launcher='--core' not in sys.argv
    target=ROOT/('ritme-jogja-code.zip' if include_launcher else 'ritme-jogja-colab-core.zip')
    roots=['src','presentation','brag-output/composition','outputs/tourism','data/tourism']
    files=[ROOT/name for name in ['README.md','requirements-colab.txt','SUBMIT_GUIDE.md','REPORT.md','PROJECT_PLAN.md','requirements.txt','run_all.sh','.gitignore','project.json','requirements-voice.txt','requirements-tourism.txt','data/README.md','data/source_manifest.json','data/sheets_sources.json','outputs/VALIDATION.md','brag-output/brag-plan.md','brag-output/composition-brief.md']]
    if include_launcher and (ROOT/'COLAB_RUN.ipynb').exists():
        files.append(ROOT/'COLAB_RUN.ipynb')
    files.extend([ROOT/'presentation/scenes_en.json',ROOT/'src/generate_voice.py'])
    for folder in roots:
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file())
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for p in sorted(set(files)):
            rel=p.relative_to(ROOT)
            if any(part in {'.hyperframes','node_modules','__pycache__','video','voice'} for part in rel.parts):
                continue
            if p.suffix in {'.mp4','.log','.pyc','.wav'} or p.name in {'check-result.json','music-bed.mp3'}:
                continue
            z.write(p,'ritme-jogja/'+str(rel))
    with ZipFile(target) as z:
        assert z.testzip() is None
        assert not any('/data/raw/' in name or '/.venv/' in name for name in z.namelist())
        print(f'{target.name}: {len(z.namelist())} files, {target.stat().st_size:,} bytes; verified')

if __name__=='__main__':
    main()
