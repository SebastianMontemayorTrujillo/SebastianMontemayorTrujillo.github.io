const { cp, mkdir, stat } = require('node:fs/promises');

async function build() {
    require('sqlite3');
    await mkdir('public', { recursive: true });
    const directories = ['wp-admin', 'wp-includes', 'wp-content/plugins', 'wp-content/themes', 'wp-content/mu-plugins'];
    for (const directory of directories) {
        await cp('wp/' + directory, 'public/wp/' + directory, {
            recursive: true,
            filter: async (source) => (await stat(source)).isDirectory() || /\.(css|js|svg|png|gif|jpg|jpeg|webp|woff|woff2|ico|otf)$/.test(source),
        });
    }
}

build().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
