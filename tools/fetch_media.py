#!/usr/bin/env python3
"""Скачивает исходники видео из src/media.json (Google Drive / YouTube),
сжимает в лёгкий MP4 (H.264, ≤1280px, faststart) и делает постер JPG в media/.
Уже скачанные файлы пропускаются. Запускается в GitHub Actions автоматически."""
import json, os, subprocess, sys, tempfile, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA = json.load(open(os.path.join(ROOT, 'src', 'media.json'), encoding='utf-8'))
OUT = os.path.join(ROOT, 'media')
os.makedirs(OUT, exist_ok=True)


def run(cmd):
    print('$', ' '.join(cmd)[:200], flush=True)
    return subprocess.run(cmd).returncode == 0


def download(m, tmp):
    if 'drive' in m:
        dst = os.path.join(tmp, 'src')
        if run(['gdown', '--fuzzy', '-q', '-O', dst, f'https://drive.google.com/file/d/{m["drive"]}/view']) and os.path.getsize(dst) > 50000:
            return dst
    ids = [m['yt']] if 'yt' in m else []
    ids += [o for o in m.get('old', []) if len(o) == 11]
    for y in ids:
        if run(['yt-dlp', '-q', '--no-warnings', '-f', 'bv*[height<=1080]+ba/b', '--merge-output-format', 'mp4',
                '-o', os.path.join(tmp, 'yt.%(ext)s'), f'https://www.youtube.com/watch?v={y}']):
            f = glob.glob(os.path.join(tmp, 'yt.*'))
            if f:
                return f[0]
    return None


failed = []
for slug, m in MEDIA.items():
    mp4, jpg = os.path.join(OUT, slug + '.mp4'), os.path.join(OUT, slug + '.jpg')
    if os.path.exists(mp4) and os.path.exists(jpg):
        continue
    with tempfile.TemporaryDirectory() as tmp:
        src = download(m, tmp)
        if not src:
            failed.append(slug)
            continue
        ok = run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src,
                  '-vf', "scale='min(1280,iw)':'min(1280,ih)':force_original_aspect_ratio=decrease,scale=trunc(iw/2)*2:trunc(ih/2)*2",
                  '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '27', '-maxrate', '2M', '-bufsize', '4M',
                  '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-ac', '2', '-movflags', '+faststart', mp4])
        if not ok:
            failed.append(slug)
            if os.path.exists(mp4):
                os.remove(mp4)
            continue
        run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '1', '-i', mp4, '-frames:v', '1',
             '-vf', "scale='min(720,iw)':-2", '-q:v', '4', jpg]) or \
            run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-frames:v', '1', '-q:v', '4', jpg])
        print(f'OK {slug}: {os.path.getsize(mp4) // 1024} KB', flush=True)

open(os.path.join(OUT, '_missing.txt'), 'w').write('\n'.join(failed) + ('\n' if failed else ''))
print('missing:', failed or 'none')
