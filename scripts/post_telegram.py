"""
Publica automaticamente en el canal de Telegram los productos NUEVOS
(los que no se hayan publicado ya antes), para no repetir el mismo
producto cada dia.

No depende de librerias externas (usa urllib de la libreria estandar).

Configuracion necesaria (variables de entorno, NUNCA hardcodeadas aqui):
  TELEGRAM_BOT_TOKEN  -> token que te da @BotFather al crear el bot
  TELEGRAM_CHAT_ID    -> usuario publico del canal, ej. "@chollostech"

Configuracion opcional:
  TELEGRAM_MAX_POR_DIA -> cuantas ofertas publicar como maximo en cada
                          ejecucion (por defecto 4). Publicar demasiado
                          es la causa principal de que la gente silencie
                          el canal y se vaya.

Si las variables de entorno no estan definidas, el script no hace nada
y no falla el pipeline (para que funcione igual en local sin Telegram).
"""
import json
import os
import time
import urllib.parse
import urllib.request

from generate_content import generate

POSTED_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "telegram_posted.txt")

DEFAULT_MAX_POR_DIA = 4

# No promocionamos productos mal valorados: una recomendacion mala de
# entrada cuesta la credibilidad del canal entera. Siguen estando en la
# web (en su categoria y en el buscador), solo que no se publican.
MIN_RATING = 3.5


def rating_de(a):
    try:
        return float(a["rating"])
    except (TypeError, ValueError):
        return 0.0

# Hashtag por categoria, para que cada suscriptor pueda filtrar o buscar
# solo lo que le interesa dentro del canal. Sin acentos ni enes: asi son
# mas faciles de buscar desde el buscador de Telegram.
CATEGORY_HASHTAGS = {
    "tecnologia": "#tecnologia",
    "hogar-limpieza": "#hogar",
    "deportes": "#deporte",
    "moda-belleza": "#belleza",
    "bebe-ninos": "#bebe",
    "mascotas": "#mascotas",
    "astronomia": "#eclipse",
}


def max_por_dia():
    try:
        valor = int(os.environ.get("TELEGRAM_MAX_POR_DIA", DEFAULT_MAX_POR_DIA))
    except ValueError:
        return DEFAULT_MAX_POR_DIA
    return valor if valor > 0 else DEFAULT_MAX_POR_DIA


def build_hashtags(a):
    tags = ["#chollos"]
    categoria = CATEGORY_HASHTAGS.get(a["category"])
    if categoria:
        tags.append(categoria)
    if a["discount_pct"] >= 35:
        tags.append("#chollazo")
    return " ".join(tags)


def load_posted():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def mark_posted(slug):
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(slug + "\n")


def build_caption(a):
    savings = a["old_price"] - a["price"]
    return (
        f"🛍️ <b>{a['name']}</b>  🔻 -{a['discount_pct']}%\n\n"
        f"💶 Precio normal: <s>{a['old_price']:.2f}€</s>\n"
        f"✅ Oferta: <b>{a['price']:.2f}€</b>  ✨ Ahorras {savings:.2f}€\n"
        f"⭐ {a['rating']}/5 · {a['category_label']}\n\n"
        f'🛒 <a href="{a["affiliate_link"]}">Cómpralo aquí</a>\n\n'
        f"{build_hashtags(a)}"
    )


def send_photo(token, chat_id, image_url, caption):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "HTML",
    }
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID no definidos, no se publica nada.")
        return

    posted = load_posted()
    articles = generate()
    new_articles = [a for a in articles if a["slug"] not in posted]

    descartados = [a for a in new_articles if rating_de(a) < MIN_RATING]
    if descartados:
        print(f"Descartados por valoracion < {MIN_RATING}: " + ", ".join(a["slug"] for a in descartados))
    new_articles = [a for a in new_articles if rating_de(a) >= MIN_RATING]

    if not new_articles:
        print("No hay productos nuevos que publicar en Telegram.")
        return

    # Primero los de mayor descuento: si hay mas ofertas nuevas que el
    # limite diario, salen antes las mejores y el resto quedan para
    # los dias siguientes (no se pierden, siguen sin estar en posted).
    new_articles.sort(key=lambda a: a["discount_pct"], reverse=True)
    limite = max_por_dia()
    pendientes = len(new_articles)
    new_articles = new_articles[:limite]

    if pendientes > limite:
        print(f"{pendientes} ofertas nuevas; publico las {limite} de mayor descuento.")

    for a in new_articles:
        caption = build_caption(a)
        try:
            result = send_photo(token, chat_id, a["image_url"], caption)
            if result.get("ok"):
                print(f"Publicado en Telegram: {a['slug']}")
                mark_posted(a["slug"])
            else:
                print(f"Error publicando {a['slug']}: {result}")
        except Exception as e:
            print(f"Error publicando {a['slug']}: {e}")
        time.sleep(1.5)


if __name__ == "__main__":
    main()
