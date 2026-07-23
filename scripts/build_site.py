"""
Construye el sitio estatico final en /docs a partir de la lista de articulos.
Se sirve directamente con GitHub Pages (gratis) apuntando a la carpeta /docs
de la rama main, sin necesidad de servidor propio.
"""
import os
import shutil

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
SITE_NAME = "ChollosTech"
SITE_URL = "https://TU-DOMINIO-AQUI.com"  # cambia esto cuando tengas dominio

BASE_CSS = """
* { box-sizing: border-box; }
body { font-family: -apple-system, Arial, sans-serif; margin: 0; background: #f7f7f9; color: #222; }
header { background: #1a1a2e; color: white; padding: 1.2rem 1rem; }
header a { color: white; text-decoration: none; font-weight: bold; font-size: 1.3rem; }
main { max-width: 900px; margin: 0 auto; padding: 1.5rem 1rem; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
.card { background: white; border-radius: 10px; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,.1); }
.card img { max-width: 100%; border-radius: 6px; }
.card h3 { font-size: 1.05rem; margin: .5rem 0; }
.price-box { display: flex; align-items: center; gap: .6rem; margin: 1rem 0; }
.price-old { text-decoration: line-through; color: #888; }
.price-new { font-size: 1.4rem; font-weight: bold; color: #d10000; }
.discount { background: #d10000; color: white; padding: .15rem .5rem; border-radius: 6px; font-size: .85rem; }
.cta-button { display: inline-block; background: #ff9900; color: #111; padding: .7rem 1.2rem; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: .5rem; }
.disclosure { font-size: .8rem; color: #666; margin-top: 1.5rem; border-top: 1px solid #ddd; padding-top: .8rem; }
footer { text-align: center; padding: 2rem 1rem; font-size: .85rem; color: #666; }
footer a { color: #666; }
#cookie-banner { position: fixed; bottom: 0; left: 0; right: 0; background: #1a1a2e; color: white; padding: 1rem; display: none; z-index: 999; }
#cookie-banner button { background: #ff9900; border: none; padding: .5rem 1rem; border-radius: 6px; margin-left: 1rem; cursor: pointer; font-weight: bold; }
"""

COOKIE_JS = """
document.addEventListener('DOMContentLoaded', function () {
  if (!localStorage.getItem('cookie_ok')) {
    document.getElementById('cookie-banner').style.display = 'block';
  }
  document.getElementById('cookie-accept').addEventListener('click', function () {
    localStorage.setItem('cookie_ok', '1');
    document.getElementById('cookie-banner').style.display = 'none';
  });
});
"""

COOKIE_BANNER_HTML = """
<div id="cookie-banner">
  Usamos cookies propias y de terceros (enlaces de afiliado) para el funcionamiento de la web.
  Mas info en nuestra <a href="/legal/cookies.html" style="color:#ff9900">politica de cookies</a>.
  <button id="cookie-accept">Vale</button>
</div>
"""


def page_shell(title, body, description=""):
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | {SITE_NAME}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header><a href="/">{SITE_NAME}</a></header>
<main>
{body}
</main>
<footer>
  &copy; {SITE_NAME}. <a href="/legal/aviso-legal.html">Aviso legal</a> ·
  <a href="/legal/privacidad.html">Privacidad</a> ·
  <a href="/legal/cookies.html">Cookies</a>
</footer>
{COOKIE_BANNER_HTML}
<script src="/static/cookie-consent.js"></script>
</body>
</html>"""


def build_index(articles):
    cards = ""
    for a in articles:
        cards += f"""
        <a class="card" href="/articulos/{a['slug']}.html" style="text-decoration:none;color:inherit;">
          <img src="{a['image_url']}" alt="{a['title']}" loading="lazy">
          <h3>{a['title']}</h3>
          <div class="price-box">
            <span class="price-old">{a['old_price']:.2f}€</span>
            <span class="price-new">{a['price']:.2f}€</span>
            <span class="discount">-{a['discount_pct']}%</span>
          </div>
        </a>"""
    body = f"<h1>Ultimas ofertas</h1><div class='card-grid'>{cards}</div>"
    return page_shell("Inicio", body, "Las mejores ofertas y chollos de tecnologia seleccionados cada dia.")


def build_article(a):
    body = f"<h1>{a['title']}</h1><p><em>Publicado el {a['published']}</em></p>{a['body_html']}"
    return page_shell(a["title"], body, a["meta_description"])


LEGAL_PAGES = {
    "aviso-legal.html": """
<h1>Aviso legal</h1>
<p><strong>[PLACEHOLDER: rellena con tus datos reales antes de publicar]</strong></p>
<p>Titular del sitio: [Tu nombre o razon social]<br>
NIF/DNI: [Tu NIF]<br>
Domicilio: [Tu direccion]<br>
Email de contacto: [tu email]</p>
<p>Este sitio participa en el Programa de Afiliados de Amazon EU, un programa de
publicidad para afiliados diseñado para ofrecer a sitios web un medio para obtener
comisiones por publicidad, publicitando e incluyendo enlaces a Amazon.es.</p>
""",
    "privacidad.html": """
<h1>Politica de privacidad</h1>
<p><strong>[PLACEHOLDER: revisa y completa antes de publicar]</strong></p>
<p>Este sitio no recopila datos personales mas alla de los estrictamente necesarios
para su funcionamiento tecnico. Si en el futuro se anaden formularios, analitica o
publicidad personalizada, esta politica debera actualizarse en consecuencia y,
si corresponde, solicitarse consentimiento explicito conforme al RGPD.</p>
""",
    "cookies.html": """
<h1>Politica de cookies</h1>
<p>Este sitio usa cookies propias tecnicas (para recordar tu eleccion sobre este aviso)
y cookies de terceros derivadas de los enlaces de afiliado a Amazon u otras tiendas,
que pueden usarse para atribuir correctamente las comisiones. Puedes deshabilitar las
cookies desde la configuracion de tu navegador.</p>
""",
}


def build(articles):
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(os.path.join(OUT_DIR, "static"))
    os.makedirs(os.path.join(OUT_DIR, "articulos"))
    os.makedirs(os.path.join(OUT_DIR, "legal"))

    with open(os.path.join(OUT_DIR, "static", "style.css"), "w", encoding="utf-8") as f:
        f.write(BASE_CSS)
    with open(os.path.join(OUT_DIR, "static", "cookie-consent.js"), "w", encoding="utf-8") as f:
        f.write(COOKIE_JS)

    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_index(articles))

    for a in articles:
        with open(os.path.join(OUT_DIR, "articulos", f"{a['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(build_article(a))

    for name, content in LEGAL_PAGES.items():
        with open(os.path.join(OUT_DIR, "legal", name), "w", encoding="utf-8") as f:
            f.write(page_shell(name.replace(".html", "").replace("-", " ").title(), content))

    urls = [SITE_URL + "/"] + [f"{SITE_URL}/articulos/{a['slug']}.html" for a in articles]
    sitemap = "<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"
    sitemap += "".join(f"<url><loc>{u}</loc></url>" for u in urls)
    sitemap += "</urlset>"
    with open(os.path.join(OUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    with open(os.path.join(OUT_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")

    with open(os.path.join(OUT_DIR, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")

    print(f"Sitio generado en {OUT_DIR} con {len(articles)} articulos.")


if __name__ == "__main__":
    from generate_content import generate
    build(generate())
