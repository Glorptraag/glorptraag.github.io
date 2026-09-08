/*!
 * Coastal Demolitions — click attribution and call tracking.
 *
 * Two jobs:
 *
 *   1. Remember where a visitor came from. Google Ads puts a gclid (or gbraid /
 *      wbraid on iOS app and web-to-app journeys) on the landing URL and then it
 *      is gone. We stash it in a first-party cookie for 90 days — the same window
 *      Google Ads uses for offline conversion imports — so a lead that arrives on
 *      a later visit still carries the click that paid for it.
 *
 *   2. Attach it to the two things that turn into money: the quote form, and a
 *      tap on the phone number.
 *
 * On the phone number: a gclid cannot literally travel inside a tel: link — the
 * dialler takes a number and nothing else. What is possible, and what this does,
 * is fire a dataLayer event carrying the gclid at the moment of the tap, so GTM
 * can send an Ads call conversion and GA4 a phone_call event with the click
 * attached. Matching a booked job back to a keyword later is then a gclid lookup.
 */
(function (w, d) {
  'use strict';

  var COOKIE = 'cd_attr';
  var DAYS = 90;
  var CLICK_IDS = ['gclid', 'gbraid', 'wbraid', 'msclkid', 'fbclid'];
  var UTMS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];

  function readCookie(name) {
    var m = d.cookie.match('(?:^|; )' + name + '=([^;]*)');
    return m ? decodeURIComponent(m[1]) : '';
  }

  function writeCookie(name, value, days) {
    var exp = new Date(Date.now() + days * 864e5).toUTCString();
    // Host-only cookie, Lax: it never leaves our own pages.
    d.cookie = name + '=' + encodeURIComponent(value) + ';expires=' + exp +
               ';path=/;SameSite=Lax' + (location.protocol === 'https:' ? ';Secure' : '');
  }

  function params() {
    var out = {}, q = location.search.slice(1);
    if (!q) return out;
    q.split('&').forEach(function (pair) {
      if (!pair) return;
      var i = pair.indexOf('=');
      var k = decodeURIComponent((i < 0 ? pair : pair.slice(0, i)).replace(/\+/g, ' '));
      var v = i < 0 ? '' : decodeURIComponent(pair.slice(i + 1).replace(/\+/g, ' '));
      if (k) out[k] = v;
    });
    return out;
  }

  /* Current attribution: this visit's parameters win, otherwise whatever the
   * cookie already holds. First touch is not overwritten by an organic revisit,
   * because an organic revisit carries no click id to overwrite it with. */
  function resolve() {
    var stored = {};
    try { stored = JSON.parse(readCookie(COOKIE) || '{}') || {}; } catch (e) { stored = {}; }

    var p = params();
    var fresh = {};
    var sawClick = false;

    CLICK_IDS.forEach(function (k) { if (p[k]) { fresh[k] = p[k]; sawClick = true; } });
    UTMS.forEach(function (k) { if (p[k]) { fresh[k] = p[k]; sawClick = true; } });

    if (sawClick) {
      fresh.landing_page = location.pathname + location.search;
      fresh.first_seen = new Date().toISOString();
      fresh.referrer = d.referrer || '';
      try { writeCookie(COOKIE, JSON.stringify(fresh), DAYS); } catch (e) {}
      return fresh;
    }

    // No new click: keep what we had, but record where this session started if
    // we have never recorded anything at all.
    if (!stored.first_seen) {
      stored.first_seen = new Date().toISOString();
      stored.landing_page = location.pathname + location.search;
      stored.referrer = d.referrer || '';
      try { writeCookie(COOKIE, JSON.stringify(stored), DAYS); } catch (e) {}
    }
    return stored;
  }

  var attr = resolve();

  function summary() {
    var bits = [];
    CLICK_IDS.concat(UTMS).forEach(function (k) {
      if (attr[k]) bits.push(k + '=' + attr[k]);
    });
    return bits.join(' ');
  }

  /* ---- 1. Feed the quote form -------------------------------------------- */

  function hidden(form, name, value) {
    if (!value) return;
    var existing = form.querySelector('input[name="' + name + '"]');
    if (existing) { existing.value = value; return; }
    var input = d.createElement('input');
    input.type = 'hidden';
    input.name = name;
    input.value = value;
    form.appendChild(input);
  }

  function decorateForms() {
    var forms = d.querySelectorAll('form.wpforms-form, form[data-coastal-lead]');
    for (var i = 0; i < forms.length; i++) {
      var f = forms[i];
      CLICK_IDS.concat(UTMS).forEach(function (k) { hidden(f, k, attr[k]); });
      hidden(f, 'landing_page', attr.landing_page || '');
      hidden(f, 'attribution_referrer', attr.referrer || '');
      hidden(f, 'attribution_first_seen', attr.first_seen || '');
      // page_url exists already on the WPForms markup but is baked in at build
      // time; overwrite it with where the visitor actually is.
      hidden(f, 'page_url', location.pathname);
      hidden(f, 'page_href', location.href);
    }
  }

  /* ---- 2. Report phone taps ---------------------------------------------- */

  function digits(href) {
    return String(href || '').replace(/^tel:/i, '').replace(/[^\d+]/g, '');
  }

  function onTelClick(e) {
    var el = e.target && e.target.closest ? e.target.closest('a[href^="tel:"]') : null;
    if (!el) return;

    var payload = {
      event: 'phone_call_click',
      phone_number: digits(el.getAttribute('href')),
      link_text: (el.textContent || '').trim().slice(0, 80),
      page_path: location.pathname,
      attribution: summary()
    };
    CLICK_IDS.concat(UTMS).forEach(function (k) { if (attr[k]) payload[k] = attr[k]; });

    try {
      w.dataLayer = w.dataLayer || [];
      w.dataLayer.push(payload);
    } catch (err) {}
  }

  function ready(fn) {
    if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
    decorateForms();
    // Capture phase, because the Call Now Button and some theme handlers stop
    // propagation on their own click listeners.
    d.addEventListener('click', onTelClick, true);
  });

  // Expose for GTM and for debugging in the console.
  w.coastalAttribution = { get: function () { return attr; }, summary: summary };
})(window, document);
