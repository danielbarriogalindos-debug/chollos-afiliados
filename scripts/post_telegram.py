"""
Publica automaticamente en el canal de Telegram los productos NUEVOS
(los que no se hayan publicado ya antes), para no repetir el mismo
producto cada dia.

No depende de librerias externas (usa urllib de la libreria estandar).

Configuracion necesaria (variables de entorno, NUNCA hardcodeadas aqui):
  TELEGRAM_BOT_TOKEN  -> token que te da @BotFather al crear el bot
  TELEGRAM_CHAT_ID    -> usuario publico del canal, ej. "@chollostech"

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
        f'🛒 <a href="{a["affiliate_link"]}">Cómpralo aquí</a>'
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

    if not new_articles:
        print("No hay productos nuevos que publicar en Telegram.")
        return

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
