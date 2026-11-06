#!/usr/bin/env bash
# Reproduce the ICHmw2 BA/TPH evidence from the pinned candidate.
# Usage: ./04-reproduce.sh [OUTPUT_DIR]
set -euo pipefail

ROOT=/srv/shared-data/gep/ws4/tmp/fresh-fvsbc
OUT=${1:-/tmp/ichmw2-replay}
PSP=/srv/shared-data/gep/ws4/tmp/inv01-data/psp
PYTHON=${PYTHON:-python3}

cd "$ROOT"
rm -rf "$OUT"
PYTHONPATH=src:scripts "$PYTHON" scripts/run_calibration_probe.py \
  --data-dir runtime/ichmw2 \
  --psp-dir "$PSP" \
  --out-dir "$OUT" \
  --domain ICHmw2 \
  --per-bec 1000 \
  --min-dbh 4 \
  --candidates notes/reference/calibration/d9-ichmw2-candidates.json

PYTHONPATH=src "$PYTHON" - "$OUT" <<'PY'
import sys
from pathlib import Path
import pandas as pd
out=Path(sys.argv[1])
p=pd.read_csv(out/'probe.csv'); p=p[p.candidate=='bai0.75'].copy()
p['site']=p.interval_id.str.split('|').str[0]
n=p.groupby('site').size(); p['n']=p.site.map(n)
i=pd.read_csv('runtime/ichmw2/intervals.csv'); p['TSA']=p.interval_id.map(i.set_index('interval_id').TSA_DESC)
p=p[(p.n>=5)&p.TSA.isin(['Arrow TSA','Cascadia TSA'])]
g=p.groupby('site')
print('sites',g.ngroups,'intervals',len(p))
print('BA%',round(100*p.ba_error.mean()/p.observed_ba1.mean(),2))
print('TPH%',round(100*p.tph_error.mean()/p.observed_tph1.mean(),2))
print('site pass',sum(abs(100*x.ba_error.mean()/x.observed_ba1.mean())<=10 and abs(100*x.tph_error.mean()/x.observed_tph1.mean())<=15 for _,x in g),'of',g.ngroups)
PY
