# coastaldemolitions.com — static site

Full static clone of the Coastal Demolitions website, migrated off managed
WordPress (WP Engine) and hosted free on **GitHub Pages**.

## What this is

- All 91 pages (home, services, projects, 47 blog posts, location landing
  pages) captured from the live WordPress site on 23 Jul 2026.
- Every image, video, stylesheet, script and font the site serves —
  including lazy-loaded images and Google Fonts, which are now self-hosted
  (`/wp-content/fonts/`). Zero runtime dependency on WP Engine or Google's
  font CDN.
- Yoast sitemaps, robots.txt, RSS feed snapshot, canonical/OG tags and
  JSON-LD schema preserved for SEO.
- The full WordPress content export (pages/posts/media JSON via REST API)
  and all 371 original full-resolution media files are attached to the
  **wordpress-backup** GitHub Release on this repo.

## What changed vs WordPress

| Thing | Before | Now |
|---|---|---|
| Hosting | WP Engine (~$100/mo) | GitHub Pages ($0) |
| Contact / quote form | WPForms (PHP) | Same form UI, posts to [FormSubmit](https://formsubmit.co) → admin@coastaldemolitions.com, then redirects to `/contact-us-ty/` |
| reCAPTCHA | v3, verified by WordPress | Removed (no server to verify); honeypot field added |
| Google Fonts | fonts.googleapis.com | Self-hosted in `/wp-content/fonts/` |
| Blog/admin | wp-admin | Static — edit HTML here, or rebuild pages from the content JSON in the backup release |

Still working unchanged: Trustindex Google-reviews widget, Call Now Button,
Google Tag Manager, Facebook pixel, Bing/Google ads tags (all third-party JS).

## ⚠️ One-time setup after deploy

1. **FormSubmit activation** — the first submission to the contact form
   emails admin@coastaldemolitions.com an activation link. Click it once and
   all later submissions flow normally.

   **Status 7 Sep 2026:** a pre-flight submission from the preview site has
   already triggered this, so the activation mail is sitting in admin@ and
   only needs the link clicked. Until it is clicked FormSubmit holds
   submissions and forwards nothing. Re-test the form after DNS cutover.

## DNS cutover (when ready to leave WP Engine)

DNS for coastaldemolitions.com is **not** on Cloudflare. The nameservers are
Google Cloud DNS (`ns-cloud-c1..c4.googledomains.com`) and the zone is managed
from the **Squarespace Domains** account (dankay1711@ family account). The
current apex `A` records — `141.193.213.10` / `.11` — are WP Engine.

1. Screenshot the existing zone before touching it.
2. Replace the apex `A` records with GitHub Pages':
   `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   and add `AAAA`: `2606:50c0:8000::153`, `2606:50c0:8001::153`,
   `2606:50c0:8002::153`, `2606:50c0:8003::153`
3. Point `www` → `glorptraag.github.io` (CNAME). It is currently
   `wp.wpenginepowered.com`.
4. **Leave every other record exactly as it is** — in particular the Google
   Workspace `MX`, the `v=spf1 include:_spf.google.com ~all` TXT and the
   `google-site-verification` TXT. Mail for @coastaldemolitions.com rides on
   those; changing them takes the mailboxes down.
5. In this repo: Settings → Pages → confirm custom domain
   `coastaldemolitions.com` is verified, then tick **Enforce HTTPS** once the
   certificate provisions (usually < 1 hour).
6. Confirm the site loads on the domain, submit a test enquiry, then give
   Embark written notice.

## Deploys

Push to `main` → GitHub Pages redeploys automatically (~1 min).
