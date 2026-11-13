#!/bin/sh
set -eu

# Write the deployable source to a new directory supplied by the caller.
destination=${1:?Usage: sh prepare.sh NEW_DIRECTORY}
overlay=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir "$destination"
destination=$(CDPATH= cd -- "$destination" && pwd)
downloads=$(mktemp -d)
trap 'rm -rf -- "$downloads"' EXIT HUP INT TERM

revision=70f2a045938100f76f8e68ef496dadc49754ad23
curl -fsSL "https://codeload.github.com/mitchmac/ServerlessWP/tar.gz/$revision" -o "$downloads/wordpress.tgz"
tar -xzf "$downloads/wordpress.tgz" -C "$destination" --strip-components=1 \
    "ServerlessWP-$revision/wp" "ServerlessWP-$revision/api/vercel.js" "ServerlessWP-$revision/LICENSE"

cd "$destination"
cp "$overlay/package.json" "$overlay/package-lock.json" "$overlay/vercel.json" "$overlay/build.cjs" .
cp "$overlay/handler.cjs" api/vercel.js
patch -p1 < "$overlay/wp-config.patch"

install_zip() {
    curl -fsSL "$1" -o "$downloads/package.zip"
    unzip -oq "$downloads/package.zip" -d "$2"
}

install_zip https://downloads.wordpress.org/plugin/wordpress-seo.28.8.zip wp/wp-content/plugins
install_zip https://downloads.wordpress.org/translation/core/7.1.4/es_MX.zip wp/wp-content/languages
install_zip https://downloads.wordpress.org/translation/theme/twentytwentyfive/1.5/es_MX.zip wp/wp-content/languages/themes
install_zip https://downloads.wordpress.org/translation/plugin/wordpress-seo/28.8/es_MX.zip wp/wp-content/languages/plugins
