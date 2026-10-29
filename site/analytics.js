(() => {
  'use strict';
  const measurementId = document.currentScript.dataset.measurementId;
  if (!/^G-[A-Z0-9]+$/.test(measurementId || '')) return;

  const preferenceKey = 'coochilla.analytics-consent.v1';
  const preferenceLifetime = 180 * 24 * 60 * 60 * 1000;
  const banner = document.getElementById('analytics-consent');
  const privacy = document.getElementById('privacy-dialog');
  const status = document.getElementById('analytics-choice');
  let choice = null;
  let started = false;

  try {
    const saved = JSON.parse(localStorage.getItem(preferenceKey));
    if (saved && ['granted', 'denied'].includes(saved.value) &&
        saved.expires > Date.now()) choice = saved.value;
  } catch (_) { /* Storage may be unavailable; keep the choice for this visit. */ }

  const denied = {
    analytics_storage: 'denied', ad_storage: 'denied',
    ad_user_data: 'denied', ad_personalization: 'denied'
  };

  function startAnalytics() {
    if (started || choice !== 'granted') return;
    started = true;
    window['ga-disable-' + measurementId] = false;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', denied);
    window.gtag('consent', 'update', { ...denied, analytics_storage: 'granted' });
    window.gtag('js', new Date());
    window.gtag('config', measurementId, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      // Enquiries and identifiers in URL queries must not enter Analytics.
      page_location: location.origin + location.pathname,
      page_title: document.title
    });
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
    document.head.append(tag);
  }

  function clearAnalyticsCookies() {
    for (const item of document.cookie.split(';')) {
      const name = item.split('=')[0].trim();
      if (!/^_ga(?:_|$)|^_gid$|^_gat(?:_|$)/.test(name)) continue;
      for (const domain of ['', '; domain=' + location.hostname, '; domain=.' + location.hostname]) {
        document.cookie = name + '=; Max-Age=0; path=/; SameSite=Lax' + domain;
      }
    }
  }

  function updateInterface() {
    banner.hidden = choice !== null;
    status.textContent = choice === 'granted' ? 'visit statistics: allowed' :
      choice === 'denied' ? 'visit statistics: declined' : 'visit statistics: not enabled';
  }

  function choose(value) {
    choice = value;
    try {
      localStorage.setItem(preferenceKey, JSON.stringify({
        value, expires: Date.now() + preferenceLifetime
      }));
    } catch (_) { /* The current visit still respects the selected choice. */ }
    updateInterface();
    if (value === 'granted') startAnalytics();
    else {
      window['ga-disable-' + measurementId] = true;
      clearAnalyticsCookies();
      // Reload after withdrawal so previously loaded Google code is removed.
      if (started) location.reload();
    }
    if (privacy.open) privacy.close();
  }

  document.querySelectorAll('[data-analytics-choice]').forEach(button => {
    button.addEventListener('click', () => choose(button.dataset.analyticsChoice));
  });
  document.getElementById('privacy-settings').hidden = false;
  document.getElementById('privacy-settings').addEventListener('click', () => privacy.showModal());
  document.getElementById('privacy-details').addEventListener('click', () => privacy.showModal());
  document.getElementById('privacy-close').addEventListener('click', () => privacy.close());

  document.addEventListener('click', event => {
    if (choice !== 'granted' || !started) return;
    const link = event.target.closest('a');
    if (!link) return;
    let name;
    if (link.hasAttribute('data-rider-download')) name = 'rider_download';
    else if (link.getAttribute('href')?.startsWith('mailto:')) name = 'booking_click';
    if (name) window.gtag('event', name, { send_to: measurementId });
  });

  updateInterface();
  if (choice === 'granted') startAnalytics();
  else clearAnalyticsCookies();
})();
