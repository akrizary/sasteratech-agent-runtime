from pathlib import Path
import shutil, subprocess, sys
ROOT=Path(__file__).parents[1]
uv=shutil.which('uv')
if not uv:
    raise SystemExit('BLOCKED: uv not installed')
out=ROOT/'requirements'/'runtime-lock.txt'
cmd=[uv,'pip','compile',str(ROOT/'requirements'/'runtime-pins.in'),'--generate-hashes','-o',str(out)]
print('Running:', ' '.join(cmd))
rc=subprocess.run(cmd).returncode
if rc: raise SystemExit(rc)
text=out.read_text(encoding='utf-8')
if '--hash=' not in text:
    raise SystemExit('FAIL: generated lock lacks hashes')
print('PASS:',out)
