"""Read public Spotify profile counts; never use Spotify account credentials."""
import argparse
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

class ProfileParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts, self.meta, self.skip = [], {}, 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style'):
            self.skip += 1
        if tag == 'meta':
            self.meta[attrs.get('property', attrs.get('name', ''))] = attrs.get('content', '')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
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
    now = datetime.now(timezone.utc)
    data = {'schemaVersion': 1, 'artistId': ARTIST, 'artistName': 'Coochilla',
        'source': 'Spotify public artist profile', 'sourceUrl': URL,
        'checkedAt': now.isoformat(),
        'verifiedOn': args.verified_on or now.astimezone(ZoneInfo('Europe/Helsinki')).date().isoformat(),
        'metrics': metrics}
    encoded = json.dumps(data, ensure_ascii=False, indent=2)
    write(SITE / 'spotify-public.json', encoded + '\n')
    write(SITE / 'spotify-public-data.js', 'window.COOCHILLA_PUBLIC = ' + encoded + ';\n')
    print('Read public Spotify counts: ' + str(metrics['listeners']) + ' monthly listeners; '
        + str(metrics['followers']) + ' followers')

if __name__ == '__main__':
    main()
