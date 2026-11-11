# Sebastian Montemayor Trujillo

Simple personal website, with project demos and a separate Spanish WordPress blog.

## Build and deploy

GitHub Pages publishes the built `dist/` directory through `.github/workflows/pages.yml` whenever the website changes on `main`. The workflow runs the build checks before deployment. The personal site uses the GitHub Pages origin configured in `site.json`.

Set the verified public addresses in `site.json`. Empty blog/demo URLs are omitted until those sites are live. Run `python3 scripts/build.py` to generate only public HTML/CSS, robots.txt and sitemap.xml in `dist/`.

Vercel uses `vercel.json`; import this repository with framework **Other**. The build uses the Vercel production domain automatically unless `site_url` or `SITE_URL` is set. `VERCEL_ENV=production` enables indexing; previews are noindex and disallowed by robots.txt. No paid services or runtime database are needed.

Validation: `python3 -m unittest discover -s scripts -p 'test_*.py'`.

## Project showcase and WordPress links

The dedicated showcase is `/projects.html`, linked from every page. Stable individual links are `/projects.html#crab-chess` and `/projects.html#voces-de-la-plaza`. Repository links work immediately; demo buttons appear when their actual addresses are entered in site.json.

Set `blog_url` in site.json to the real WordPress address and rebuild to show the blog section at `/projects.html#blog`, including links to its two project articles. In WordPress, set `PORTFOLIO_URL` to the personal site's verified base URL: the setup adds a **Portafolio de proyectos** navigation/footer link and article links to the corresponding showcase sections. Use the same base URL after the Vercel migration. The blog navigation and footer return to the same `#blog` section on the GitHub Pages site.

## Migration and search engines

After the new production URL is reachable, save it in `site.json`, rebuild, and run `python3 scripts/prepare_redirects.py`. Publish only the generated `github-pages/` directory to a separate GitHub Pages branch and change Pages' source to that branch. This preserves all three old page paths with immediate HTML redirects and canonical URLs. Keep those redirects indefinitely. Vercel deployments continue to use the source branch, not the redirects branch.

Verify both old and new URL-prefix properties in Google Search Console. Use an HTML verification meta tag/file supplied by Google; copy that exact value into the deployed site, never invent one. Submit the new `/sitemap.xml`, inspect the homepage and projects page, and request indexing. Change of Address may require server redirects that GitHub Pages cannot provide; do not report that action as completed if its validation fails. Monitor old/new properties after migration.

Add the new portfolio and WordPress blog in Bing Webmaster Tools (or import verified Search Console properties), verify ownership, and submit each sitemap. WordPress with Yoast uses `/sitemap_index.xml`. Confirm both sitemaps are fetchable by the services, especially on free hosting. Submission does not guarantee indexing.

## WordPress

See [wordpress/README.md](wordpress/README.md) for Spanish content, a local WordPress environment, the hosting import, Stripe Payment Link setup, backups and maintenance. Credentials, generated backups and local evidence are excluded from git and from the Vercel output.

## Rollback

Vercel can promote the previous known-good deployment. Keep the current GitHub Pages source unchanged until the Vercel site is verified; to undo a later migration, restore Pages' source branch to the original main branch. Before updating WordPress, save SQL and wp-content outside the public web directory.
