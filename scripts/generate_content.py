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

CATEGORY_LABELS = {
    "tecnologia": "Tecnología",
    "hogar-limpieza": "Hogar y Limpieza",
    "deportes": "Deportes",
    "moda-belleza": "Moda y Belleza",
    "bebe-ninos": "Bebé y Niños",
    "mascotas": "Mascotas",
    "astronomia": "Astronomía",
}

CATEGORY_PROS = {
    "tecnologia": ["Buen rendimiento para el precio", "Construccion solida", "Compatible con la mayoria de setups"],
    "hogar-limpieza": ["Facil de usar desde el primer dia", "Ahorra tiempo en tareas domesticas", "Buena relacion calidad-precio"],
    "deportes": ["Buena relacion calidad-precio", "Resistente para uso frecuente", "Facil de guardar o transportar"],
    "moda-belleza": ["Buenos resultados para el precio", "Comodo de usar a diario", "Buena relacion calidad-precio"],
    "bebe-ninos": ["Pensado para el uso diario con niños", "Materiales seguros y faciles de limpiar", "Buena relacion calidad-precio"],
    "mascotas": ["Facil de limpiar y mantener", "Comodo para el animal", "Buena relacion calidad-precio"],
    "astronomia": [
        "Certificadas CE y EN ISO 12312-2, la norma obligatoria para mirar al Sol",
        "Bloquean la radiacion ultravioleta e infrarroja, no solo la luz visible",
        "Ligeras y economicas, faciles de compartir entre varias personas",
    ],
}
CATEGORY_CONS = {
    "tecnologia": ["El software de configuracion es mejorable", "Los cables incluidos son cortos"],
    "hogar-limpieza": ["El manual de instrucciones es escueto", "El nivel de ruido podria ser menor"],
    "deportes": ["El tamaño de embalaje es grande", "Alguna pieza se vende por separado"],
    "moda-belleza": ["Los colores disponibles son limitados", "El cable de alimentacion es algo corto"],
    "bebe-ninos": ["El manual viene solo en varios idiomas genericos", "El montaje inicial lleva unos minutos"],
    "mascotas": ["No apto para mascotas muy grandes", "Requiere limpieza periodica para mejor rendimiento"],
    "astronomia": [
        "Solo valen para mirar a simple vista: NUNCA las uses con telescopio, prismaticos o camara",
        "Hay que revisarlas antes de cada uso y descartarlas si tienen aranazos, agujeros o el filtro despegado",
    ],
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
    <img src="{product['image_url']}" alt="{name}">
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
        "name": name,
        "title": f"{name}: oferta con {discount_pct}% de descuento",
        "meta_description": f"{name} rebajado a {price:.2f}€ ({discount_pct}% de descuento). Analizamos si merece la pena.",
        "category": category,
        "category_label": CATEGORY_LABELS.get(category, category.replace("-", " ").title()),
        "price": price,
        "old_price": old_price,
        "discount_pct": discount_pct,
        "rating": product["rating"],
        "image_url": product["image_url"],
        "affiliate_link": product["affiliate_link"],
        "body_html": body_html,
        "featured": product.get("featured", "no").strip().lower() == "si",
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
