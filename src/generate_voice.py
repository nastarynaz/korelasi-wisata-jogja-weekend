"""Generate English scene narration with HyperFrames' local Kokoro voice."""
from pathlib import Path
import hashlib, json, os, subprocess
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'brag-output/composition/assets/voice'
SCENES = ROOT / 'presentation/scenes_en.json'
MANIFEST = ROOT / 'brag-output/audio_manifest.json'
PYTHON = ROOT / '.voice-venv/bin/python'
OUT.mkdir(parents=True, exist_ok=True)
env = os.environ.copy()
env['HYPERFRAMES_PYTHON'] = str(PYTHON)
scenes = json.loads(SCENES.read_text())
old_manifest=json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
old_clips={clip['scene']:clip for clip in old_manifest.get('clips',[])}
manifest = {'provider':'Kokoro local via HyperFrames','voice':'af_heart','language':'en-us','clips':[]}
for scene in scenes:
    target = OUT / f"{scene['id']}.wav"
    text = scene['narration'].strip()
    digest = hashlib.sha256(text.encode()).hexdigest()
    if not target.exists() or old_clips.get(scene['id'],{}).get('text_sha256') != digest:
        txt = OUT / f"{scene['id']}.txt"
        txt.write_text(text)
        subprocess.run(['npx','hyperframes','tts','--text-file',str(txt),'--voice','af_heart','--lang','en-us','--output',str(target),'--json'], cwd=ROOT, env=env, check=True)
    duration = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(target)], text=True).strip())
    scene_duration = scene['duration']
    speed = 1.0
    if duration + 2.5 > scene_duration:
        speed = min(1.18, duration / (scene_duration - 2.7))
        sped = OUT / f"{scene['id']}-fit.wav"
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(target),'-filter:a',f'atempo={speed:.5f}',str(sped)],check=True)
        target.unlink(); sped.rename(target)
        duration = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(target)], text=True).strip())
    if duration + 2.5 > scene_duration:
        raise SystemExit(f"Voiceover too long for {scene['id']}: {duration:.2f}s in {scene_duration}s")
    manifest['clips'].append({'scene':scene['id'],'file':f'assets/voice/{target.name}','duration_seconds':round(duration,3),'start_seconds':0.8,'speed':round(speed,4),'text_sha256':digest})
    print(f"{scene['id']}: {duration:.2f}s / {scene_duration}s (speed {speed:.3f})",flush=True)
MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
