"""Guard public count parsing against cross-artist or misidentified song totals."""
import base64
import json
import unittest
from refresh_spotify import ARTIST, URL, extract, extract_tracks

TRACK='5w3CG310MBfGUhKDloWWbu'

def response(artist=ARTIST,name="Don't Feel Like Dancing Anymore",count='1613028'):
    state={'entities':{'items':{'spotify:artist:'+ARTIST:{
        'uri':'spotify:artist:'+artist,'profile':{'name':'Coochilla'},
        'discography':{'topTracks':{'items':[{'track':{
            'uri':'spotify:track:'+TRACK,'name':name,'playcount':count,
            'artists':{'items':[{'uri':'spotify:artist:'+ARTIST}]}
        }}]}}
    }}}}
    encoded=base64.b64encode(json.dumps(state).encode()).decode()
    return '<meta property="og:title" content="Coochilla"><meta property="og:url" content="'+URL+'"><div>2,323 monthly listeners</div><div>1,322</div><div>Followers</div><script id="initialState" type="text/plain">'+encoded+'</script>'

class PublicCounts(unittest.TestCase):
    def test_exact_counts_not_popularity(self):
        html=response()
        self.assertEqual(extract(html),{'listeners':2323,'followers':1322})
        self.assertEqual(extract_tracks(html)[TRACK]['streams'],1613028)
        self.assertNotIn('6Ng3GH0pgu0sB7EjkMeKAi',extract_tracks(html))
    def test_reject_wrong_artist(self):
        with self.assertRaises(ValueError):extract_tracks(response(artist='someoneelse'))
    def test_reject_wrong_title_for_id(self):
        with self.assertRaises(ValueError):extract_tracks(response(name='Another song'))
    def test_reject_negative_and_non_numeric_counts(self):
        for value in ['-1','unknown','1.6m']:
            with self.subTest(value=value),self.assertRaises(ValueError):extract_tracks(response(count=value))
    def test_missing_or_changed_state_fails_safely(self):
        with self.assertRaises((ValueError,KeyError)):extract_tracks('<html></html>')
    def test_inconsistent_profile_totals_are_rejected(self):
        with self.assertRaises(ValueError):extract(response()+'<div>9,999 monthly listeners</div>')

if __name__=='__main__':unittest.main()
