#!/bin/sh
set -eu
# Run through the CLI container; credentials arrive through its environment.
if ! wp core is-installed; then
  wp core install --url="$BLOG_URL" --title="Notas de Sebastian" \
    --admin_user="$WP_ADMIN_USER" --admin_password="$WP_ADMIN_PASSWORD" \
    --admin_email="$WP_ADMIN_EMAIL" --skip-email
  wp post update 1 2 --post_status=draft
fi
wp language core install es_MX --activate
wp theme install twentytwentyfive --activate
wp language theme install twentytwentyfive es_MX
wp plugin install wordpress-seo wordpress-importer --activate
wp language plugin install wordpress-seo es_MX
wp eval-file /setup/seed.php
wp rewrite structure '/%postname%/' --hard
wp cache flush
