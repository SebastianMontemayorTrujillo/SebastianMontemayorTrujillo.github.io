<?php
// Run with wp eval-file; this file is never a public endpoint.
if (!defined('WP_CLI') || !WP_CLI) {
    exit(1);
}

function save_blog_post($slug, $type, $fields, $existing_id) {
    $id = wp_insert_post($fields + [
        'ID' => $existing_id,
        'post_name' => $slug,
        'post_type' => $type,
        'post_status' => 'publish',
    ], true);
    if (is_wp_error($id)) {
        WP_CLI::error($id->get_error_message());
    }
    return $id;
}

$config = [];
foreach (['PORTFOLIO_URL', 'XDCHESS_URL', 'INEHACK_URL'] as $key) {
    $url = getenv($key);
    $parts = wp_parse_url($url);
    if (!$parts || ($parts['scheme'] ?? '') !== 'https' || empty($parts['host']) || isset($parts['user']) || isset($parts['pass'])) {
        WP_CLI::error("URL HTTPS inválida: $key");
    }
    $config['{{' . $key . '}}'] = esc_url($url);
}
$projects_url = rtrim(getenv('PORTFOLIO_URL'), '/') . '/projects.html';
$config['{{PROJECTS_URL}}'] = esc_url($projects_url);
$stripe = getenv('STRIPE_PAYMENT_LINK') ?: '';
if ($stripe !== '') {
    $parts = wp_parse_url($stripe);
    if (!$parts || ($parts['scheme'] ?? '') !== 'https' || ($parts['host'] ?? '') !== 'buy.stripe.com' ||
        isset($parts['user']) || isset($parts['pass']) || isset($parts['port']) || empty($parts['path'])) {
        WP_CLI::error('Usar un Payment Link HTTPS de buy.stripe.com');
    }
}
$config['{{STRIPE_BUTTON}}'] = $stripe ? '<p><a href="' . esc_url($stripe) . '">Apoya mis proyectos con Stripe →</a></p>' :
    '<p>Las aportaciones todavía no están habilitadas.</p>';
require_once ABSPATH . 'wp-admin/includes/image.php';
foreach (['xdchess' => 'Partida de Crab Chess después del movimiento e2 a e4',
          'inehack' => 'Pantalla de bienvenida de Voces de la Plaza en el navegador'] as $slug => $alt) {
    $id = (int) get_option('seb_screenshot_' . $slug);
    if (!$id || !get_post($id)) {
        $name = $slug . '.png';
        $upload = wp_upload_bits($name, null, file_get_contents(__DIR__ . '/media/' . $name));
        if ($upload['error']) { WP_CLI::error($upload['error']); }
        $id = wp_insert_attachment(['post_mime_type' => 'image/png', 'post_title' => $alt,
                                   'post_status' => 'inherit'], $upload['file'], 0, true);
        if (is_wp_error($id)) { WP_CLI::error($id->get_error_message()); }
        wp_update_attachment_metadata($id, wp_generate_attachment_metadata($id, $upload['file']));
        update_post_meta($id, '_wp_attachment_image_alt', $alt);
        update_option('seb_screenshot_' . $slug, $id);
    }
    $config['{{' . strtoupper($slug) . '_IMAGE}}'] = '<!-- wp:image {"id":' . $id . ',"sizeSlug":"large","linkDestination":"none"} -->' .
        '<figure class="wp-block-image size-large">' . wp_get_attachment_image($id, 'large', false, ['class' => 'wp-image-' . $id]) .
        '</figure><!-- /wp:image -->';
}
$posts = json_decode(file_get_contents(__DIR__ . '/content.json'), true, 512, JSON_THROW_ON_ERROR);
$author = get_user_by('login', getenv('WP_ADMIN_USER') ?: 'sebastian');
if (!$author) { WP_CLI::error('No se encontró al autor del blog'); }
wp_update_user(['ID' => $author->ID, 'display_name' => 'Sebastian Montemayor Trujillo']);
$ids = [];
foreach ($posts as $post) {
    $existing = get_page_by_path($post['slug'], OBJECT, $post['type']);
    $id = save_blog_post($post['slug'], $post['type'], [
        'post_author' => $author->ID,
        'post_title' => $post['title'],
        'post_content' => strtr($post['html'], $config),
        'post_excerpt' => $post['description'],
        'post_status' => $post['status'] ?? 'publish',
        'comment_status' => 'closed',
        'ping_status' => 'closed',
    ], $existing->ID ?? 0);
    update_post_meta($id, '_yoast_wpseo_metadesc', $post['description']);
    $ids[$post['slug']] = $id;
}
$host = wp_parse_url(home_url(), PHP_URL_HOST);
$options = [
    'blogname' => 'Notas de Sebastian',
    'blogdescription' => 'Hackathons, juegos y aprendizajes de desarrollo de software',
    'timezone_string' => 'America/Monterrey',
    'show_on_front' => 'page',
    'page_on_front' => $ids['proyectos'],
    'page_for_posts' => $ids['blog'],
    'default_comment_status' => 'closed',
    'default_ping_status' => 'closed',
    'blog_public' => in_array($host, ['localhost', '127.0.0.1'], true) ? 0 : 1,
];
foreach ($options as $name => $value) {
    update_option($name, $value);
}
wp_update_term(1, 'category', ['name' => 'Proyectos', 'slug' => 'proyectos']);
$navigation = '';
foreach (['proyectos' => 'Inicio', 'blog' => 'Blog', 'sobre-mi' => 'Sobre mí', 'apoya-mis-proyectos' => 'Apoya mis proyectos'] as $slug => $label) {
    $attrs = ['label' => $label, 'type' => 'page', 'id' => $ids[$slug], 'url' => get_permalink($ids[$slug]), 'kind' => 'post-type'];
    $navigation .= '<!-- wp:navigation-link ' . wp_json_encode($attrs) . ' /-->';
}
$navigation .= '<!-- wp:navigation-link ' . wp_json_encode([
    'label' => 'Volver a proyectos', 'type' => 'custom', 'url' => $projects_url . '#blog', 'kind' => 'custom',
]) . ' /-->';
$nav = get_page_by_path('navegacion-del-blog', OBJECT, 'wp_navigation');
$nav_id = save_blog_post('navegacion-del-blog', 'wp_navigation', [
    'post_title' => 'Navegación del blog',
    'post_content' => $navigation,
], $nav->ID ?? 0);
$header = '<!-- wp:group {"align":"wide","style":{"spacing":{"padding":{"top":"24px","bottom":"24px"}}},"layout":{"type":"flex","justifyContent":"space-between","flexWrap":"wrap"}} -->' .
    '<div class="wp-block-group alignwide" style="padding-top:24px;padding-bottom:24px"><!-- wp:site-title {"level":0} /-->' .
    '<!-- wp:navigation {"ref":' . $nav_id . ',"overlayMenu":"mobile"} /--></div><!-- /wp:group -->';
$footer = '<!-- wp:group {"align":"wide","style":{"spacing":{"padding":{"top":"48px","bottom":"32px"}}},"layout":{"type":"constrained"}} -->' .
    '<div class="wp-block-group alignwide" style="padding-top:48px;padding-bottom:32px"><!-- wp:site-title {"level":0} /-->' .
    '<!-- wp:paragraph --><p>Hackathons, juegos y aprendizajes de desarrollo de software.</p><!-- /wp:paragraph -->' .
    '<!-- wp:paragraph --><p><a href="' . $config['{{PORTFOLIO_URL}}'] . '">Sitio personal de Sebastian</a> · ' .
    '<a href="' . $config['{{PROJECTS_URL}}'] . '#blog">Volver a proyectos</a></p><!-- /wp:paragraph -->' .
    '<!-- wp:paragraph --><p><a href="' . rtrim($config['{{PORTFOLIO_URL}}'], '/') . '/privacidad.html">Privacidad</a></p><!-- /wp:paragraph --></div><!-- /wp:group -->';
foreach (['header' => $header, 'footer' => $footer] as $slug => $content) {
    $existing = get_posts(['post_type' => 'wp_template_part', 'name' => $slug, 'numberposts' => 1,
        'tax_query' => [['taxonomy' => 'wp_theme', 'field' => 'slug', 'terms' => 'twentytwentyfive']]]);
    $id = save_blog_post($slug, 'wp_template_part', [
        'post_title' => $slug,
        'post_content' => $content,
    ], $existing[0]->ID ?? 0);
    wp_set_object_terms($id, 'twentytwentyfive', 'wp_theme');
    wp_set_object_terms($id, $slug, 'wp_template_part_area');
}
WP_CLI::success('Contenido preparado. La bitácora de competencias permanece en borrador hasta tener evidencias.');
