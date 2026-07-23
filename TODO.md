# Checklist rapido — que hacer cuando te despiertes

Orden recomendado. Los 3 primeros son los unicos bloqueantes para tener el sitio online (gratis):

- [ ] 1. Crear cuenta en GitHub (gratis) si no tienes.
- [ ] 2. Crear un repo nuevo llamado `chollos-afiliados` (publico) y hacer push de esta carpeta
      (comandos exactos en el README, seccion "Lo que TU tienes que hacer").
- [ ] 3. Activar GitHub Pages en el repo: Settings → Pages → rama `main`, carpeta `/docs`.
      → En unos minutos el sitio esta online gratis.

Estos dos son los que desbloquean que el sitio empiece a generar dinero de verdad:

- [ ] 4. Solicitar cuenta de Amazon Afiliados en afiliados.amazon.es (hazlo con el sitio ya online y con contenido).
- [ ] 5. Cuando te acepten, cambia `TU-ID-AFILIADO-20` en `data/products.csv` por tu Tracking ID real,
      y sustituye los productos de ejemplo por ofertas reales que tu elijas.

Estos son importantes pero no bloquean el lanzamiento:

- [ ] 6. Rellenar tus datos reales en las paginas legales (`scripts/build_site.py`, variable `LEGAL_PAGES`):
      nombre/razon social, NIF, direccion, email de contacto.
- [ ] 7. (Opcional) Comprar un dominio propio (~10€/año) y apuntarlo a GitHub Pages.

## Lo que ya esta hecho y probado

- Pipeline completo (`scripts/run_pipeline.py`) probado en local, genera 8 articulos de ejemplo sin errores.
- Sitio estatico completo en `docs/` con portada, articulos, sitemap, robots.txt, paginas legales y banner de cookies.
- Automatizacion diaria configurada en `.github/workflows/build-deploy.yml` (gratis, GitHub Actions).
- Todo commiteado en git local, listo para hacer push en cuanto crees el repo remoto.
- Proyeccion de ingresos realista a 6 meses en `PROYECCION.md`.

## Importante

El pipeline automatiza la publicacion, no la busqueda de ofertas nuevas. Para que el
sitio crezca de verdad necesitas seguir anadiendo productos reales a `data/products.csv`
de vez en cuando (o pedirme a mi que lo haga si me pasas los datos de las ofertas).
