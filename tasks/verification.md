# Verification — 3 November 2026

- Portfolio: two build checks pass, covering HTTPS URLs, exclusion of private files, production sitemap, project/blog links and preview noindex. Three pages tested in Chromium at 320, 768, 1024 and 1440 px without horizontal overflow. Original design retained.
- Crab Chess: 65 existing tests pass; production build passes; npm audit reports zero vulnerabilities. Browser accepts e2–e4 with no page errors. Deployment configuration committed on `chore/vercel-deployment`.
- Voces de la Plaza: 16 public export files verified against the submission SHA-256 manifest; 41 existing Python tests pass. Chromium loads the Godot canvas without page errors. No claim of a fresh full-game journey. Vercel files remain local under the repository's no-commit instruction.
- WordPress: WordPress 7.1.4, Twenty Twenty-Five 1.5, Yoast SEO 28.8 and WordPress Importer 0.9.7 run locally. Mexican Spanish language packs installed. Six routes return HTTP 200. Blog/articles checked at 320, 375, 768 and 1280 px, with the image overflow corrected. Admin login and plugin screen verified. Local indexing disabled; Yoast sitemap responds HTTP 200.
- Backups: WXR parses successfully, wp-content archive reads successfully, and SQL restores into the separate `wordpress_restore_check` database with the expected published/draft content. Full public-host restoration remains pending.
- Public deployment, migration redirects, search-console submissions and live/test Stripe checkout have not been performed. Vercel has no authorized login; hosting access, payment link and search-console access are absent.

Local preview: http://localhost:8085. Local admin credentials are in the ignored, mode-0600 `wordpress/.env`; never include this file in a public upload.

Next: authenticate Vercel, supply/access the free WordPress hosting site and public Stripe Payment Link, deploy and verify, update the public links, migrate GitHub Pages, then verify and submit the Google/Bing properties. Keep the skills evidence post in draft until the missing SEO/payment evidence exists.

## Showcase follow-up

Added projects.html with stable #crab-chess and #voces-de-la-plaza anchors and navigation from all four personal-site pages. Build checks now cover the four-page sitemap and the configured WordPress link. Chromium checks passed at 320, 768 and 1280 px, including homepage navigation and both WordPress article backlinks, with no page errors. WordPress navigation/footer also link to the showcase. Real external URLs still require deployment and the blog's public address.

Vercel authentication was subsequently verified read-only; its Hobby team had no projects at that check. Earlier authentication-blocker text above is historical. Public deployment remains pending.
