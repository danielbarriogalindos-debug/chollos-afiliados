"""
Punto de entrada unico del pipeline: genera contenido a partir de data/products.csv
y construye el sitio estatico en /docs. Esto es lo que ejecuta GitHub Actions cada dia,
y lo que puedes correr tu mismo en local con: python scripts/run_pipeline.py
"""
from generate_content import generate
from build_site import build

if __name__ == "__main__":
    articles = generate()
    build(articles)
    print(f"Pipeline completado: {len(articles)} articulos publicados en /docs")
