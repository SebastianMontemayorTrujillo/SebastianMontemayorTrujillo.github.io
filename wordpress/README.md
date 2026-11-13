# Blog de hackathons en WordPress

El contenido en español está en `content.json`. La bitácora de competencias permanece como borrador: publicar solo después de añadir capturas y resultados reales. El enlace de aportaciones aparece únicamente al configurar un Payment Link válido.

## Vista previa local

1. Copiar `.env.example` a `.env`; elegir contraseñas distintas y completar los enlaces públicos. No subir `.env`.
2. Ejecutar `docker compose up -d db wordpress`.
3. Cuando la base y WordPress estén listos, ejecutar `docker compose run --rm cli sh /setup/setup.sh`.
4. Abrir <http://localhost:8085> y <http://localhost:8085/wp-admin/>. Las credenciales están en `.env`.

El sitio local está limitado a loopback y excluido de buscadores. El script puede repetirse: actualiza las páginas de estos mismos slugs. No ejecutarlo sobre un blog que ya tenga contenido propio con esos slugs sin copia previa.

La portada, navegación, cabecera y pie se guardan como contenido editable de WordPress. Las dos entradas tienen autor, descripción SEO y capturas reales de los proyectos. El sitio no contiene claves de Stripe.

El portafolio externo usa `PORTFOLIO_URL` como dirección base. El script añade **Portafolio de proyectos** al menú y al pie, con destino `/projects.html`; las entradas enlazan a `#crab-chess` y `#voces-de-la-plaza`. Para devolver el enlace desde el sitio personal al blog, configurar `blog_url` en site.json y reconstruir el portafolio. Publicar ambos destinos antes de considerar comprobados los enlaces externos.

## Vercel

El sitio público está en <https://sebastian-notas.vercel.app> y el panel en <https://sebastian-notas.vercel.app/wp-admin/>. El proyecto `name-da43/sebastian-notas` ejecuta WordPress con ServerlessWP. La base SQLite y los archivos subidos se guardan en el almacén privado de Vercel Blob. Los cambios al tema, los plugins y WordPress se despliegan con el código.

El usuario administrador es `sebastian`. Su contraseña generada está en `.env.vercel-admin`, excluido de Git y con permisos 0600. Las peticiones a Vercel admiten hasta 4.5 MB, por lo que las imágenes subidas deben caber dentro de ese límite junto con los datos de la petición.

Para desplegar una actualización, prepara una carpeta nueva con `sh vercel/prepare.sh RUTA_NUEVA`. Desde esa carpeta, ejecuta `vercel link --project sebastian-notas --scope name-da43` y `vercel deploy --prod --skip-domain --archive=tgz --scope name-da43`. Comprueba la versión con `vercel curl` y promuévela con `vercel promote URL_DEL_DESPLIEGUE --scope name-da43`. El almacén y `WP_AUTH_SECRET` ya están configurados en el proyecto. Conserva la base `wp-sqlite.sqlite` en el almacén al actualizar el código. El script de datos de ejemplo es para la instalación inicial y la vista previa local.

## InfinityFree

Crear una cuenta gratuita y un subdominio con HTTPS en su panel; instalar WordPress mediante Softaculous. Usar la dirección sin `www`. No usar su plan de pago ni comprar dominio.

Activar el tema gratuito Twenty Twenty-Five. Instalar Yoast SEO y WordPress Importer desde el directorio oficial. Importar `backups/contenido.xml` en Herramientas → Importar → WordPress, asignando las entradas a tu usuario. Configurar portada **Proyectos y notas de hackathons** y página de entradas **Blog**; usar enlaces permanentes por nombre. Añadir en el editor una navegación con Inicio, Blog, Sobre mí y Apoya mis proyectos.

Los textos de la exportación contienen los enlaces configurados en `.env`: sustituir cualquier enlace local antes de publicar. Yoast conserva sus metadescripciones como metadatos importados; completar su asistente como sitio personal, sin activar servicios de pago. Revisar manualmente títulos y descripciones, sitemap y opciones de indexación.

InfinityFree bloquea webhooks entrantes. Este blog usa un botón hacia checkout alojado por Stripe y no necesita webhooks ni claves secretas en WordPress. Los comprobantes y registros de pago se gestionan en Stripe.

Para una migración completa, usar la copia SQL y `wp-content.tar.gz` sobre una instalación nueva de WordPress con la misma tabla prefijo `wp_`: importar la base mediante phpMyAdmin y subir el contenido por FTP. Cambiar `siteurl` y `home` en `wp_options` a la URL HTTPS pública y sustituir los enlaces locales en las entradas. La copia SQL contiene el usuario local; cambiar sus credenciales en la instalación pública antes de usarla. Para conservar el usuario creado en el alojamiento, preferir la importación WXR y subir las imágenes incluidas en `media/`, reemplazándolas en las dos entradas (las direcciones de imágenes locales del XML no son descargables desde el alojamiento). No subir SQL, copias, `.env`, `seed.php` o scripts al directorio público.

## Stripe y evidencia

En tu cuenta Stripe, crear un Payment Link de pago único con importe elegido por la persona; concepto **Apoyo a mis proyectos**. Configurar primero el enlace de prueba y verificar éxito y cancelación con los medios de prueba oficiales. No hacer cobros reales para probar. Sustituirlo por el enlace activo después de la comprobación. No afirmar deducibilidad fiscal ni presentar el apoyo personal como una campaña de una organización.

Guardar capturas sin datos privados: editor de una entrada; lista de plugins y configuración de Yoast; previsualización SEO y sitemap; checkout de prueba. Añadirlas al borrador **Cómo mantengo este blog en WordPress**, junto con fechas y resultados, antes de publicarlo.

## Copias y restauración

Desde esta carpeta, después de configurar el sitio:

```sh
mkdir -p backups
docker compose exec -T db sh -c 'mariadb-dump -uwordpress -p"$MARIADB_PASSWORD" wordpress' > backups/database.sql
docker compose exec -T wordpress tar -czf - -C /var/www/html wp-content > backups/wp-content.tar.gz
docker compose run --rm -T cli wp export --stdout > backups/contenido.xml
```

Preferir la copia SQL + contenido para restauración completa; el XML sirve para importar entradas y páginas. Ninguna copia se escribe en el directorio público.

Restaurar solo en una base vacía de una instalación de prueba: importar `database.sql`, extraer `wp-content.tar.gz` al volumen de WordPress y ejecutar `wp search-replace URL_ANTERIOR URL_NUEVA --all-tables-with-prefix --skip-columns=guid`. Comprobar inicio, entrada, imagen y acceso al panel antes de usarlo como procedimiento probado. En InfinityFree descargar archivos por FTP y exportar SQL mediante phpMyAdmin; guardar ambas copias fuera de `htdocs`.

## Rutina semanal

- Exportar SQL y archivos antes de actualizar.
- Actualizar WordPress, plugins y tema; revisar portada, entrada, navegación y botón de Stripe después.
- Comprobar enlaces de demos y errores de rastreo.
- Registrar fecha, mejora, comprobación y siguiente acción. Preparar o revisar una entrada.

La disponibilidad de 1–5 horas semanales debe confirmarla Sebastian personalmente.
