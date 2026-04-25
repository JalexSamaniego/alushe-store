"""
Alushe Store - Generador de Puntos de Entrega
==============================================
Este script:
1. Lee los puntos de entrega desde puntos_entrega.json
2. Descarga imágenes de Street View (Referencia) y Maps Static (Croquis)
3. Guarda las imágenes en assets/images/
4. Genera el index.html final con todo integrado

Uso:
    python generate.py

Requisitos:
    pip install requests
"""

import os
import json
import requests

# ============================================================
#  CONFIGURACIÓN — edita solo esta sección
# ============================================================

GOOGLE_API_KEY = "TU_API_KEY_AQUI"

GITHUB_USER    = "JalexSamaniego"
GITHUB_REPO    = "alushe-store"
GITHUB_BRANCH  = "main"

# Base URL para las imágenes en GitHub (raw)
IMG_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/assets/images"

# ============================================================
#  RUTAS
# ============================================================

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR  = os.path.join(BASE_DIR, "assets", "images")
REF_DIR     = os.path.join(ASSETS_DIR, "referencia")
CROQUIS_DIR = os.path.join(ASSETS_DIR, "croquis")
JSON_PATH   = os.path.join(BASE_DIR, "puntos_entrega.json")
HTML_PATH   = os.path.join(BASE_DIR, "index.html")

os.makedirs(REF_DIR, exist_ok=True)
os.makedirs(CROQUIS_DIR, exist_ok=True)

# ============================================================
#  DESCARGA DE IMÁGENES
# ============================================================

def descargar_imagen(url, ruta_destino):
    """Descarga una imagen desde una URL y la guarda en disco."""
    if os.path.exists(ruta_destino):
        print(f"  ✓ Ya existe: {os.path.basename(ruta_destino)}")
        return True
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        with open(ruta_destino, "wb") as f:
            f.write(r.content)
        print(f"  ↓ Descargada: {os.path.basename(ruta_destino)}")
        return True
    except Exception as e:
        print(f"  ✗ Error descargando {os.path.basename(ruta_destino)}: {e}")
        return False


def url_street_view(lat, lng):
    """Genera URL de Street View Static API."""
    return (
        f"https://maps.googleapis.com/maps/api/streetview"
        f"?size=600x400"
        f"&location={lat},{lng}"
        f"&fov=90"
        f"&pitch=0"
        f"&key={GOOGLE_API_KEY}"
    )


def url_maps_static(lat, lng):
    """Genera URL de Maps Static API con pin rojo centrado."""
    return (
        f"https://maps.googleapis.com/maps/api/staticmap"
        f"?center={lat},{lng}"
        f"&zoom=16"
        f"&size=600x400"
        f"&maptype=roadmap"
        f"&markers=color:red%7C{lat},{lng}"
        f"&key={GOOGLE_API_KEY}"
    )


def descargar_imagenes(puntos):
    """Descarga referencia y croquis para todos los puntos."""
    print("\n📥 Descargando imágenes...\n")
    for p in puntos:
        pid  = p["id"]
        lat  = p["lat"]
        lng  = p["lng"]
        print(f"📍 {p['nombre']}")

        # Referencia (Street View)
        ruta_ref = os.path.join(REF_DIR, f"{pid}.jpg")
        descargar_imagen(url_street_view(lat, lng), ruta_ref)

        # Croquis (Maps Static)
        ruta_croquis = os.path.join(CROQUIS_DIR, f"{pid}.png")
        descargar_imagen(url_maps_static(lat, lng), ruta_croquis)

    print("\n✅ Imágenes listas.\n")

# ============================================================
#  GENERACIÓN DE HTML
# ============================================================

def generar_card(p):
    """Genera el HTML de una tarjeta de punto de entrega."""
    pid      = p["id"]
    nombre   = p["nombre"]
    hora     = p["hora"]
    maps_url = p["maps_url"]

    ref_url     = f"{IMG_BASE}/referencia/{pid}.jpg"
    croquis_url = f"{IMG_BASE}/croquis/{pid}.png"

    return f"""
    <div class="card">
      <div class="images-wrap">
        <div>
          <a href="{ref_url}" data-lightbox="entregas" data-title="Referencia - {nombre}">
            <img src="{ref_url}" alt="Referencia {nombre}" loading="lazy">
          </a>
          <div class="img-label">Referencia</div>
        </div>
        <div>
          <a href="{croquis_url}" data-lightbox="entregas" data-title="Croquis - {nombre}">
            <img src="{croquis_url}" alt="Croquis {nombre}" loading="lazy">
          </a>
          <div class="img-label">Croquis</div>
        </div>
      </div>
      <div class="title">{nombre}</div>
      <div class="desc">🕒 {hora}</div>
      <a href="{maps_url}" target="_blank" class="btn-maps">🗺️ Ver en Google Maps</a>
    </div>"""


def generar_html(puntos):
    """Genera el index.html completo."""
    cards = "\n".join(generar_card(p) for p in puntos)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Puntos de Entrega - Alushe Store</title>

  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;800&display=swap" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/css/lightbox.min.css" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/js/lightbox.min.js"></script>

  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: 'Montserrat', sans-serif;
      margin: 0;
      padding: 20px 15px;
      background-color: #F7F6DE;
    }}

    .header-title {{
      text-align: center;
      color: #333;
      margin-bottom: 20px;
      font-weight: 800;
      font-size: 26px;
      text-transform: uppercase;
    }}

    .info-box {{
      background: #fff;
      border-radius: 12px;
      padding: 15px 20px;
      max-width: 1000px;
      margin: 0 auto 25px;
      text-align: center;
      box-shadow: 0 4px 10px rgba(0,0,0,0.05);
      border-left: 5px solid #ff6b6b;
      font-size: 14px;
      color: #444;
      line-height: 1.6;
    }}
    .info-box.delivery {{
      border-left-color: #25D366;
      margin-top: 10px;
      margin-bottom: 40px;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
      max-width: 1000px;
      margin: 0 auto;
    }}

    .card {{
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.08);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      text-align: center;
      padding-bottom: 20px;
      transition: transform 0.2s;
    }}
    .card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }}

    .images-wrap {{ display: flex; border-bottom: 1px solid #eee; background: #fafafa; }}
    .images-wrap > div {{ flex: 1; padding: 10px; }}
    .images-wrap img {{
      width: 100%;
      height: 130px;
      object-fit: cover;
      border-radius: 8px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      background-color: #eaeaea;
      cursor: pointer;
    }}

    .img-label {{
      font-size: 11px;
      color: #777;
      margin-top: 8px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .title {{ font-size: 17px; font-weight: 800; margin: 15px 15px 5px; color: #333; }}
    .desc  {{ font-size: 14px; color: #ff3366; margin: 0 15px 15px; font-weight: 800; }}

    .btn-maps {{
      background: #1A73E8;
      color: white;
      text-decoration: none;
      padding: 10px 15px;
      margin: auto 20px 0;
      border-radius: 8px;
      font-weight: 600;
      font-size: 13px;
      transition: background 0.2s;
    }}
    .btn-maps:hover {{ background: #1557b0; }}

    @media (max-width: 480px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .header-title {{ font-size: 22px; }}
      .images-wrap img {{ height: 120px; }}
    }}
  </style>
</head>
<body>

  <div class="header-title">📍 Puntos de Entrega</div>

  <div class="info-box">
    <strong>⚠️ INFORMACIÓN IMPORTANTE</strong><br>
    💳 Pagos en efectivo o tarjeta. El costo del artículo es el exhibido en la publicación.<br>
    🕒 Todas las entregas de <strong>Lunes a Sábado</strong> son programadas con <strong>1 día de anticipación</strong>.<br>
    🔍 *Haz clic en las fotos para ampliarlas.*
  </div>

  <div class="grid">
{cards}
  </div>

  <div class="info-box delivery">
    🛵 <strong>ENTREGA A DOMICILIO:</strong> Contamos con servicio a domicilio con costo extra dependiendo de la zona. ¡Mándanos mensaje para cotizar tu envío!
  </div>

</body>
</html>"""

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML generado: {HTML_PATH}\n")


# ============================================================
#  MAIN
# ============================================================

if __name__ == "__main__":
    print("🚀 Alushe Store - Generador de Puntos de Entrega")
    print("=" * 50)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        puntos = json.load(f)

    print(f"📋 {len(puntos)} puntos de entrega cargados.")

    descargar_imagenes(puntos)
    generar_html(puntos)

    print("🎉 Todo listo. Sube los archivos a GitHub y pega el HTML en Google Sites.")
    print("\nEstructura generada:")
    print("  assets/images/referencia/  ← fotos Street View")
    print("  assets/images/croquis/     ← mapas estáticos")
    print("  index.html                 ← página final")
