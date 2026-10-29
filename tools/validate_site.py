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
tracks={
 '5w3CG310MBfGUhKDloWWbu', '2ci1Xk21qMxnJB1F7uBGg6',
 '5ht9zgUbF72saN5qmhNIcl', '6Ng3GH0pgu0sB7EjkMeKAi',
 '0Bra61AKU3OligXfYgAkoR', '5u6mKappybFn8GnwXGrxnD',
 '4oHkDymryUoBKQItbYRdGR'
}
for track_id,track in data.get('tracks',{}).items():
    assert track_id in tracks
    assert type(track['streams']) is int and 0<=track['streams']<=2**53-1
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',track['verifiedOn'])
    assert track['sourceUrl']=='https://open.spotify.com/artist/2KMHj8v88gQE6fQZNMp9Qc'
html=(site/'index.html').read_text()
for filename in ['content.js','metrics-data.js','spotify-public-data.js','metrics.js','gallery.js','analytics.js','analytics.css']:
    assert filename in html and (site/filename).is_file()
assert 'setInterval' not in (site/'metrics.js').read_text()
assert set(re.findall(r'data-track-id="([A-Za-z0-9]+)"', html))==tracks
assert html.count('data-gallery aria-labelledby')==2
assert 'data-dialog-step="1"' in html
assert not re.search(r'dates by arrangement|discuss a booking|distinctive selection|select a frame|the live experience',html,re.I)
assert not any(site.rglob('*.py'))
assert 'data-measurement-id="G-7F0BX5F03V"' in html
assert 'googletagmanager.com/gtag/js' not in html, 'Load Analytics only through the consent gate'
for asset in re.findall(r'assets/[A-Za-z0-9_.-]+', html+(site/'content.js').read_text()):
    assert (site/asset).is_file(), 'Missing production asset: '+asset
print('Site validated: correct artist, matching data files, no minute polling.')
