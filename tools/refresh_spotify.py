"""Read public Spotify profile counts; never use Spotify account credentials."""
import argparse
import base64
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

ARTIST = '2KMHj8v88gQE6fQZNMp9Qc'
URL = 'https://open.spotify.com/artist/' + ARTIST
SITE = Path(__file__).resolve().parents[1] / 'site'
TRACKS = {
    '5w3CG310MBfGUhKDloWWbu': "Don't Feel Like Dancing Anymore",
    '2ci1Xk21qMxnJB1F7uBGg6': 'Tone of the New Day',
    '5ht9zgUbF72saN5qmhNIcl': 'Gotta Keep Loving',
    '6Ng3GH0pgu0sB7EjkMeKAi': 'Trust You',
    '0Bra61AKU3OligXfYgAkoR': 'Miasma',
    '5u6mKappybFn8GnwXGrxnD': 'Your World',
    '4oHkDymryUoBKQItbYRdGR': 'Master Groover',
}

class ProfileParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts, self.meta, self.skip = [], {}, 0
        self.in_state, self.state = False, ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style'):
            self.skip += 1
        if tag == 'script' and attrs.get('id') == 'initialState':
            self.in_state = True
        if tag == 'meta':
            self.meta[attrs.get('property', attrs.get('name', ''))] = attrs.get('content', '')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
        if tag == 'script':
            self.in_state = False

    def handle_data(self, data):
        if self.in_state:
            self.state += data
        if not self.skip and data.strip():
            self.texts.append(data.strip())

def extract(html):
    parser = ProfileParser()
    parser.feed(html)
    if parser.meta.get('og:title', '').casefold() != 'coochilla':
        raise ValueError('Spotify did not return the Coochilla artist page')
    if parser.meta.get('og:url', '').rstrip('/') != URL:
        raise ValueError('Spotify returned a different artist')
    counts = set()
    followers = set()
    for i, text in enumerate(parser.texts):
        match = re.fullmatch(r'([\d,\s\u00a0]+)\s+monthly listeners', text, flags=re.I)
        if match:
            counts.add(int(re.sub(r'\D', '', match[1])))
        if text.casefold() == 'followers' and i:
            value = parser.texts[i - 1]
            if re.fullmatch(r'[\d,\s\u00a0]+', value):
                followers.add(int(re.sub(r'\D', '', value)))
    if len(counts) != 1 or len(followers) != 1:
        raise ValueError('Exact public counts unavailable or inconsistent; preserving the previous data')
    return {'listeners': counts.pop(), 'followers': followers.pop()}

def extract_tracks(html):
    """Read only the same public profile response, without account/API credentials."""
    parser = ProfileParser()
    parser.feed(html)
    state = json.loads(base64.b64decode(parser.state, validate=True))
    artist = state['entities']['items']['spotify:artist:' + ARTIST]
    if artist.get('uri') != 'spotify:artist:' + ARTIST or artist.get('profile', {}).get('name', '').casefold() != 'coochilla':
        raise ValueError('Wrong artist in public track counts')
    counts = {}
    for row in artist['discography']['topTracks']['items']:
        track = row['track']
        track_id = track.get('uri', '').removeprefix('spotify:track:')
        if track_id not in TRACKS:
            continue
        if track.get('name', '').casefold() != TRACKS[track_id].casefold():
            raise ValueError('Track name does not match its ID')
        if not any(a.get('uri') == 'spotify:artist:' + ARTIST for a in track.get('artists', {}).get('items', [])):
            raise ValueError('Track belongs to another artist')
        value = str(track.get('playcount', ''))
        if not re.fullmatch(r'\d+', value) or int(value) > 2**53 - 1:
            continue
        if track_id in counts:
            raise ValueError('Duplicate public track count')
        counts[track_id] = {'name': TRACKS[track_id], 'streams': int(value)}
    if not counts:
        raise ValueError('No verified public track counts available')
    return counts

def write(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(value, encoding='utf-8')
    os.replace(temporary, path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--html', type=Path, help='Use a saved public response for a parser check')
    parser.add_argument('--verified-on', help='Override the local verification date for the initial capture')
    args = parser.parse_args()
    if args.html:
        html = args.html.read_text(encoding='utf-8')
    else:
        response = subprocess.run(['curl', '--fail', '--silent', '--show-error', '--location',
            '--proto', '=https', '--max-time', '45', '--header', 'Accept-Language: en',
            '--retry', '2', '--retry-delay', '5', '--retry-max-time', '30',
            '--user-agent', 'Mozilla/5.0 (compatible; CoochillaBookingWebsite/1.0)', URL],
            capture_output=True, timeout=100, check=False)
        if response.returncode:
            raise RuntimeError('Spotify public request failed: ' + response.stderr.decode('utf-8', errors='replace').strip())
        if len(response.stdout) > 5_000_000:
            raise ValueError('Unexpectedly large Spotify response')
        html = response.stdout.decode('utf-8')
    metrics = extract(html)
    tracks = extract_tracks(html)
    now = datetime.now(timezone.utc)
    verified_on = args.verified_on or now.astimezone(ZoneInfo('Europe/Helsinki')).date().isoformat()
    # A track can drop out of Spotify's public top list. Retain its last good
    # count with its own original date rather than pretending it was refreshed.
    old = json.loads((SITE / 'spotify-public.json').read_text())
    previous = old.get('tracks', {}) if old.get('artistId') == ARTIST else {}
    previous = {k: v for k, v in previous.items() if k in TRACKS}
    for track_id, track in tracks.items():
        previous[track_id] = {**track, 'verifiedOn': verified_on, 'sourceUrl': URL}
    data = {'schemaVersion': 1, 'artistId': ARTIST, 'artistName': 'Coochilla',
        'source': 'Spotify public artist profile', 'sourceUrl': URL,
        'checkedAt': now.isoformat(),
        'verifiedOn': verified_on, 'metrics': metrics, 'tracks': previous}
    encoded = json.dumps(data, ensure_ascii=False, indent=2)
    write(SITE / 'spotify-public.json', encoded + '\n')
    write(SITE / 'spotify-public-data.js', 'window.COOCHILLA_PUBLIC = ' + encoded + ';\n')
    print('Read public Spotify counts: ' + str(metrics['listeners']) + ' monthly listeners; '
        + str(metrics['followers']) + ' followers')
    print('Refreshed ' + str(len(tracks)) + ' verified public song counts; unexposed songs are not estimated.')

if __name__ == '__main__':
    main()
