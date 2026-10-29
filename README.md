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

The openly displayed Spotify for Artists snapshot contains historical private
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

The music section embeds Spotify's artist player. Audience figures appear once
in a dedicated data section: current listeners and followers from the weekly
cloud feed, with a check date, plus the dated Spotify for Artists snapshot
shown openly beneath them. No extra polling is introduced.
The player is not followed by extra artist or release links.

## Art, merch and press

Seven cover images and three merch photographs were extracted as original JPEGs
from the supplied 2023 Coochilla portfolio. Artist credits and media come from
that document; its grant narrative, technical memo and historical statistics
are not published. The merch carousel shares the pics viewer and controls,
but adds item-specific descriptions below the image. The art grid keeps each
cover and its credit visible. Verified press links distinguish release news,
interviews and features rather than treating all coverage as reviews.

The weekly public-profile capture also reads exact song play counts from the
public page's initial state, matching both artist and track IDs and titles.
Five of the seven represented songs currently expose counts. Trust You and
the Master Groover title track do not, so no count is invented or copied from
2023. Each exposed song has its own check date. If it drops out of the public
list, its last good count and original date remain. These counts are public
song totals, not the dated 28-day Spotify for Artists snapshot. The EP cover
links specifically to its title track; no track count is presented as an EP total.

## Live history

The archive combines 22 entries from the supplied portfolio with the 15 gigs
provided in chat. The existing verified May 2025 Bar Loose entry is merged with
the supplied month-only entry, not counted twice. Dates retain month or day
precision as supplied. The summary is derived from the deduplicated archive:
37 listed shows, 9 cities, 2018–2025. It does not claim a complete career total.

## Live photography

The pics section shows the four supplied concert photographs without captions.
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

The promotional page uses concise lowercase copy and unnumbered section labels.

Live history is grouped in native, initially collapsed year dropdowns. Each year
shows its gig count; opening it reveals the date, venue and city rows. The overall
37-show summary remains visible while the archive is collapsed.

Main section order: tour, about, pics, data, music, merch, shows, press, booking.
Cover art sits within music; verified press links appear directly below shows. The leading cover is Don't Feel Like Dancing Anymore.

## Visitor analytics

Coochilla has its own GA4 property in Hector's existing Analytics account, with
the `coochilla.github.io` web stream and measurement ID `G-7F0BX5F03V`.
The academic website's property and tag are separate and unchanged.
Reporting uses Finland time and euros. The measurement ID is public, not a secret.

`site/analytics.js` implements basic consent: no Google Analytics script, cookies
or events load before permission. An allow/decline banner and footer privacy
settings retain the choice for 180 days. Withdrawal disables events, clears
Analytics cookies and reloads to remove the loaded Google code. Advertising
storage, Google signals and ad personalization are disabled.

Analytics measures page views, country/city (approximate), traffic sources,
scrolls, outbound clicks, `booking_click` and `rider_download`. Custom events
send only the event name, not the booking address, mail subject or form data.
Page location excludes queries and fragments. Automatic form, search, video,
file-download and history-change measurement are disabled in the web stream.
Visits without permission or with blockers are not counted. Data starts with
installation; it cannot recover earlier visits.
