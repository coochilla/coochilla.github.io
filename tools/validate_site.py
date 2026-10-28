import json
import re
from pathlib import Path

site=Path(__file__).resolve().parents[1]/'site'
data=json.loads((site/'spotify-public.json').read_text())
assert data['artistId']=='2KMHj8v88gQE6fQZNMp9Qc'
assert data['schemaVersion']==1
for key in ['listeners','followers']:
    assert type(data['metrics'][key]) is int and data['metrics'][key]>=0
fallback=(site/'spotify-public-data.js').read_text().removeprefix('window.COOCHILLA_PUBLIC = ').strip().removesuffix(';')
assert json.loads(fallback)==data
html=(site/'index.html').read_text()
for filename in ['content.js','metrics-data.js','spotify-public-data.js','metrics.js','gallery.js']:
    assert filename in html and (site/filename).is_file()
assert 'setInterval' not in (site/'metrics.js').read_text()
assert not any(site.rglob('*.py'))
for asset in re.findall(r'assets/[A-Za-z0-9_.-]+', html+(site/'content.js').read_text()):
    assert (site/asset).is_file(), 'Missing production asset: '+asset
print('Site validated: correct artist, matching data files, no minute polling.')
