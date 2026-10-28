# Coochilla booking website

A booking dossier for venues, agents and promoters, published at
https://coochilla.github.io/ with GitHub Pages.

Owned by the Coochilla organization, managed through Hector's existing GitHub login.
The original personal-account repository is preserved separately.

## Automatic Spotify updates

GitHub Actions reads Coochilla's public Spotify artist page every Monday at
10:15 Europe/Helsinki and republishes the website. It runs in GitHub's cloud;
no Mac, signed-in browser, API subscription or Spotify password is required.
The website does not poll every minute. It reads the published data when opened.
Code pushes and manually dispatched runs also publish and check the public counts.

Monthly listeners and followers come from exact values in the public page.
This is a public-page integration, not an official Spotify analytics API. If
Spotify changes the page or blocks access, the workflow fails visibly and
retains the previous valid data with its original check date.

The expandable Spotify for Artists snapshot contains historical private
dashboard metrics with their own reporting dates. Streams, saves, playlist
adds and monthly active listeners are **not** refreshed by the public-page job.
Refreshing those fields requires a separately supported analytics source.

## Editing

Edit `site/content.js` for band information, materials and approved shows.
Production details and footage without supplied material stay hidden.
The `site/` directory alone is deployed. Email outreach and private tour planning
do not belong in this repository.

Run `python3 tools/refresh_spotify.py` to check the public counts and
`python3 tools/validate_site.py` to validate the generated files.

## Music

The Music section embeds Spotify's artist player for Coochilla. Its monthly
listener count uses the same validated weekly cloud feed as the artist overview,
including the check date and stale-data notice. No extra polling is introduced.
Direct artist and release links remain available alongside the player.

## Live photography

The four supplied concert photographs appear near the top of the dossier.
Select a thumbnail, use the arrow buttons or keyboard arrows, or swipe on a
touchscreen. Opening a photo displays a full-size viewer with a download link;
Escape closes it. Portrait and landscape images are shown without cropping.
The gallery has no automatic rotation. Original JPEGs are in `site/assets/`,
and `site/gallery.js` controls the viewer. Image links also work without JavaScript.

## Technical rider

The promotional landing page shows download links only. Stage plots, patch
lists, microphone requirements and routing belong in the downloadable PDF.
The two-page technical rider includes the audience-view stage plot and both
instrument modes. IR mode uses three mono instrument feeds (one per guitar
and bass). Amp mode uses three cabinet mics plus a separate bass IR feed,
for four instrument channels. Both modes have three vocals and a basic
six-mic drum package: kick, snare top, rack tom, floor tom and two overheads.

The suggested patch reserves channel 4 for the additional bass IR in amp mode:
12 active inputs in IR mode, 13 in amp mode. Drum configuration and any extra
toms are confirmed in advance. Technical PDFs and the supporting SVG are in
`site/assets/`. Rebuild with `python3 tools/build_rider.py` using ReportLab.
After rebuilding, update the PDF version queries in `site/content.js` and the
landing-page download links, then update the content.js hash in index.html.
