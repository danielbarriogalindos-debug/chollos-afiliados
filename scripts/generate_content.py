"""
Genera articulos a partir de data/products.csv usando plantillas de texto.
No depende de librerias externas ni de ninguna API de pago: funciona gratis
desde el minuto uno. Si mas adelante quieres mejorar la calidad del texto,
hay un hook opcional para usar la API de Claude (ver enrich_with_claude()).
"""
import csv
import os
import random
from datetime import date

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "products.csv")

INTROS = [
    "Si estas buscando {name} a buen precio, esta semana hemos encontrado una oferta que merece la pena mirar.",
    "Analizamos si {name} es una buena compra ahora que su precio ha bajado.",
    "Te contamos por que {name} esta llamando la atencion en las ultimas horas.",
]

CATEGORY_PROS = {
    "audio": ["Buena calidad de sonido para el precio", "Comoda para uso prolongado", "Bateria de larga duracion"],
    "hogar": ["Facil de usar desde el primer dia", "Ahorra tiempo en tareas domesticas", "Buena relacion calidad-precio"],
    "informatica": ["Buen rendimiento para el precio", "Construccion solida", "Compatible con la mayoria de setups"],
    "accesorios": ["Muy practico para el dia a dia", "Buena relacion calidad-precio", "Facil de transportar"],
    "wearables": ["Buena autonomia de bateria", "App companion sencilla de usar", "Sensores bastante precisos"],
}
CATEGORY_CONS = {
    "audio": ["La app companion es basica", "El estuche de carga es algo grande"],
    "hogar": ["El manual de instrucciones es escueto", "El nivel de ruido podria ser menor"],
    "informatica": ["El software de configuracion es mejorable", "Los cables incluidos son cortos"],
    "accesorios": ["Los colores disponibles son limitados", "El acolchado podria ser mayor"],
    "wearables": ["Las notificaciones a veces se retrasan", "La correa de serie es basica"],
}

DISCLOSURE = (
    "Este articulo contiene enlaces de afiliado. Si compras a traves de ellos, "
    "podemos recibir una pequeña comision sin coste adicional para ti. "
    "Esto nos ayuda a mantener la web."
)


def load_products():
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def enrich_with_claude(product, base_text):
    """
    Hook opcional: si quieres mejorar el texto generado con IA en vez de
    depender solo de plantillas, define la variable de entorno
    ANTHROPIC_API_KEY e instala el paquete 'anthropic' (pip install anthropic).
    El coste es muy bajo (centimos por articulo con un modelo pequeno), pero
    NO es necesario para que el sistema funcione: por defecto esto no se usa.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return base_text
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{
                "role": "user",
                "content": (
                    "Reescribe este borrador de articulo de chollos en espanol de forma mas "
                    "natural y atractiva para SEO, mantén la estructura en HTML y no inventes "
                    "datos del producto que no esten ya en el texto:\n\n" + base_text
                ),
            }],
        )
        return msg.content[0].text
    except Exception:
        return base_text


def generate_article(product, index):
    name = product["name"]
    category = product["category"]
    price = float(product["price"])
    old_price = float(product["old_price"])
    discount_pct = round((old_price - price) / old_price * 100)
    pros = CATEGORY_PROS.get(category, ["Buena relacion calidad-precio"])
    cons = CATEGORY_CONS.get(category, ["Sin pegas relevantes detectadas"])
    intro = INTROS[index % len(INTROS)].format(name=name)

    body_html = f"""
    <p>{intro}</p>
    <p>{product['short_desc']}.</p>
    <div class="price-box">
      <span class="price-old">{old_price:.2f}€</span>
      <span class="price-new">{price:.2f}€</span>
      <span class="discount">-{discount_pct}%</span>
    </div>
    <h2>Puntos fuertes</h2>
    <ul>{''.join(f'<li>{p}</li>' for p in pros)}</ul>
    <h2>A tener en cuenta</h2>
    <ul>{''.join(f'<li>{c}</li>' for c in cons)}</ul>
    <p><a class="cta-button" href="{product['affiliate_link']}" rel="sponsored nofollow" target="_blank">Ver precio actual en Amazon</a></p>
    <p class="disclosure">{DISCLOSURE}</p>
    """
    body_html = enrich_with_claude(product, body_html)

    return {
        "slug": product["slug"],
        "title": f"{name}: oferta con {discount_pct}% de descuento",
        "meta_description": f"{name} rebajado a {price:.2f}€ ({discount_pct}% de descuento). Analizamos si merece la pena.",
        "category": category,
        "price": price,
        "old_price": old_price,
        "discount_pct": discount_pct,
        "rating": product["rating"],
        "image_url": product["image_url"],
        "affiliate_link": product["affiliate_link"],
        "body_html": body_html,
        "published": date.today().isoformat(),
    }


def generate():
    products = load_products()
    return [generate_article(p, i) for i, p in enumerate(products)]


if __name__ == "__main__":
    articles = generate()
    print(f"Generados {len(articles)} articulos de prueba.")
    for a in articles[:2]:
        print("---", a["title"])
