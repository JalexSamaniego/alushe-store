"""
Alushe Store - Generador de Puntos de Entrega
==============================================
Este script:
1. Lee los puntos de entrega desde puntos_entrega.json
2. Descarga imágenes de Street View (Referencia) y Maps Static (Croquis)
3. Guarda las imágenes en assets/images/
4. Genera puntos_entrega/index.html final con todo integrado

Uso:
    python generate.py

Requisitos:
    pip install requests
"""

import os
import sys
import json
import html
import urllib.parse
import requests

# Compatibilidad UTF-8 en terminales de Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ============================================================
#  RUTAS BASE
# ============================================================

BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR         = os.path.join(BASE_DIR, "assets", "images")
REF_DIR            = os.path.join(ASSETS_DIR, "referencia")
CROQUIS_DIR        = os.path.join(ASSETS_DIR, "croquis")
JSON_PATH          = os.path.join(BASE_DIR, "puntos_entrega.json")
PUNTOS_ENTREGA_DIR = os.path.join(BASE_DIR, "puntos_entrega")
HTML_PATH          = os.path.join(PUNTOS_ENTREGA_DIR, "index.html")

os.makedirs(REF_DIR, exist_ok=True)
os.makedirs(CROQUIS_DIR, exist_ok=True)
os.makedirs(PUNTOS_ENTREGA_DIR, exist_ok=True)


# ============================================================
#  CARGA DE VARIABLES DE ENTORNO (.env)
# ============================================================

def cargar_env():
    """Carga variables desde .env si existe en el directorio base."""
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

cargar_env()

# Clave de API de Google (se lee de .env o variable de entorno para evitar exposición pública)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "").strip()

GITHUB_USER    = "JalexSamaniego"
GITHUB_REPO    = "alushe-store"
GITHUB_BRANCH  = "master"
WHATSAPP_PHONE = "526183973897"

# Base URL para las imágenes en GitHub (raw)
IMG_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/assets/images"


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
    if not GOOGLE_API_KEY:
        print("\n⚠️ AVISO: GOOGLE_API_KEY no encontrada en .env ni en variables de entorno.")
        print("   Se usarán únicamente las imágenes ya descargadas en assets/images/.\n")

    print("\n📥 Verificando / descargando imágenes...\n")
    for p in puntos:
        pid  = p["id"]
        lat  = p["lat"]
        lng  = p["lng"]
        print(f"📍 {p['nombre']}")

        # Referencia (Street View)
        ruta_ref = os.path.join(REF_DIR, f"{pid}.jpg")
        if os.path.exists(ruta_ref):
            print(f"  ✓ Ya existe: {pid}.jpg")
        elif GOOGLE_API_KEY:
            descargar_imagen(url_street_view(lat, lng), ruta_ref)
        else:
            print(f"  ✗ Falta {pid}.jpg (configura GOOGLE_API_KEY en .env para descargar)")

        # Croquis (Maps Static)
        ruta_croquis = os.path.join(CROQUIS_DIR, f"{pid}.png")
        if os.path.exists(ruta_croquis):
            print(f"  ✓ Ya existe: {pid}.png")
        elif GOOGLE_API_KEY:
            descargar_imagen(url_maps_static(lat, lng), ruta_croquis)
        else:
            print(f"  ✗ Falta {pid}.png (configura GOOGLE_API_KEY en .env para descargar)")

    print("\n✅ Verificación de imágenes lista.\n")


# ============================================================
#  GENERACIÓN DE HTML
# ============================================================

def generar_card(p):
    """Genera el HTML de una tarjeta de punto de entrega."""
    pid      = p["id"]
    nombre   = p["nombre"]
    hora     = p["hora"]
    maps_url = p.get("maps_url", "#")

    nombre_esc = html.escape(nombre, quote=True)
    msg_wa     = urllib.parse.quote(f"Hola, me interesa el punto de entrega: {nombre} ({hora})")
    wa_url     = f"https://wa.me/{WHATSAPP_PHONE}?text={msg_wa}"

    ref_url     = f"{IMG_BASE}/referencia/{pid}.jpg"
    croquis_url = f"{IMG_BASE}/croquis/{pid}.png"

    return f"""    <div class="card">
      <div class="images-wrap">
        <div>
          <a href="{ref_url}" data-lightbox="entregas" data-title="Referencia - {nombre_esc}">
            <img src="{ref_url}" alt="Referencia {nombre_esc}" loading="lazy">
          </a>
          <div class="img-label">Referencia</div>
        </div>
        <div>
          <a href="{croquis_url}" data-lightbox="entregas" data-title="Croquis - {nombre_esc}">
            <img src="{croquis_url}" alt="Croquis {nombre_esc}" loading="lazy">
          </a>
          <div class="img-label">Croquis</div>
        </div>
      </div>
      <div class="title">{nombre_esc}</div>
      <div class="desc">🕒 {hora}</div>
      <a href="{maps_url}" target="_blank" class="btn-maps"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" style="width:16px;height:16px;flex-shrink:0;"><path fill="white" d="M12 0C7.802 0 4 3.403 4 7.602 4 11.8 7.469 16.812 12 24c4.531-7.188 8-12.2 8-16.398C20 3.403 16.199 0 12 0zm0 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"/></svg> Ver en Google Maps</a>
      <a href="{wa_url}" target="_blank" class="btn-wa"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" style="width:16px;height:16px;flex-shrink:0;"><path fill="white" d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg> Apartar lugar</a>
    </div>"""


def generar_html(puntos):
    """Genera puntos_entrega/index.html completo."""
    cards = "\n\n".join(generar_card(p) for p in puntos)

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <link rel="icon" type="image/png" href="/assets/images/favicon.png">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="10 puntos de entrega en Durango. Coordina tu pedido por WhatsApp.">
  <!-- Open Graph / WhatsApp / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://alushe.store/puntos_entrega">
  <meta property="og:title" content="Puntos de Entrega — Alushe Store">
  <meta property="og:description" content="10 puntos de entrega en Durango. Coordina tu pedido por WhatsApp.">
  <meta property="og:image" content="https://alushe.store/assets/images/favicon.png">
  <meta property="og:image:width" content="500">
  <meta property="og:image:height" content="500">
  <meta property="og:locale" content="es_MX">
  <meta property="og:site_name" content="Alushe Store">
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="Puntos de Entrega — Alushe Store">
  <meta name="twitter:description" content="10 puntos de entrega en Durango. Coordina tu pedido por WhatsApp.">
  <meta name="twitter:image" content="https://alushe.store/assets/images/favicon.png">
  <title>Puntos de Entrega - Alushe Store</title>

  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;800&display=swap" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/css/lightbox.min.css" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.3/js/lightbox.min.js"></script>

  <style>
    :root {{
      --cream:   #f6f5ca;
      --cream-d: #e8e7a8;
      --ink:     #1a1a18;
      --ink-mid: #3a3a35;
      --ink-lt:  #7a7a6e;
      --green:   #25D366;
      --green-d: #1ebe57;
      --white:   #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: 'Montserrat', sans-serif;
      margin: 0;
      padding: 76px 15px 30px;
      background-color: #F7F6DE;
    }}

    /* ── NAVBAR ──────────────────────────────────────── */
    nav {{
      position: fixed; top: 0; left: 0; right: 0; z-index: 100;
      display: flex; align-items: center; justify-content: space-between;
      padding: 12px 24px;
      background: rgba(246,245,202,0.92);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(26,26,24,0.08);
      transition: padding 0.3s;
    }}
    .nav-logo {{ display: flex; align-items: center; gap: 10px; text-decoration: none; }}
    .nav-logo img {{ width: 34px; height: 34px; object-fit: contain; border-radius: 8px; }}
    .nav-logo-text {{ font-family: 'Montserrat', sans-serif; font-size: 15px; font-weight: 800; color: var(--ink); letter-spacing: -0.3px; }}
    .nav-links {{ display: flex; gap: 16px; align-items: center; }}
    .nav-links a {{ font-size: 12px; font-weight: 600; color: var(--ink-mid); text-decoration: none; transition: color 0.2s; }}
    .nav-links a:hover {{ color: var(--ink); }}
    .nav-cta {{
      background: var(--ink) !important; color: var(--cream) !important;
      padding: 8px 16px; border-radius: 50px;
      font-weight: 600 !important; font-size: 12px !important;
      transition: background 0.2s, transform 0.15s !important;
    }}
    .nav-cta:hover {{ background: var(--ink-mid) !important; transform: scale(1.03); }}
    @media (max-width: 600px) {{
      nav {{ padding: 10px 12px; }}
      .nav-logo-text {{ font-size: 14px; }}
      .nav-links {{ gap: 8px; }}
      .nav-links a {{ font-size: 11px; }}
      .nav-cta {{ padding: 6px 10px; font-size: 11px !important; }}
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

    /* Botones con iconos SVG */
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
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }}
    .btn-maps:hover {{ background: #1557b0; }}

    .btn-wa {{
      background: #25D366;
      color: white;
      text-decoration: none;
      padding: 10px 15px;
      margin: 10px 20px 0;
      border-radius: 8px;
      font-weight: 600;
      font-size: 13px;
      transition: background 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }}
    .btn-wa:hover {{ background: #1ebe57; }}

    /* FOOTER */
    footer {{
      background: var(--ink); color: rgba(246,245,202,0.55);
      padding: 30px 20px; text-align: center;
      font-size: 12px; font-weight: 400; letter-spacing: 0.3px;
      margin-top: 50px; border-radius: 14px;
    }}
    footer a {{ color: var(--cream); text-decoration: none; font-weight: 600; }}
    footer strong {{ color: var(--cream); font-weight: 700; }}

    @media (max-width: 480px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .header-title {{ font-size: 22px; }}
      .images-wrap img {{ height: 120px; }}
    }}
  </style>
</head>
<body>

  <!-- NAV -->
  <nav>
    <a class="nav-logo" href="/"><img src="/assets/images/favicon.png" alt="Alushe Store logo"><span class="nav-logo-text">Alushe Store</span></a>
    <div class="nav-links">
      <a href="/">Inicio</a>
      <a href="/catalogo">Catálogo</a>
      <a href="https://wa.me/526183973897" target="_blank" class="nav-cta">WhatsApp 💬</a>
    </div>
  </nav>

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
    🛵 <strong>ENTREGA A DOMICILIO:</strong> Contamos con servicio a través de las plataformas digitales como Didi, Uber y Bolt. ¡Mándanos mensaje para cotizar tu envío!
  </div>

  <!-- FOOTER -->
  <footer>
    <p><strong>Alushe Store</strong> &nbsp;·&nbsp; Durango, Dgo. &nbsp;·&nbsp;
    <a href="/">Inicio</a> &nbsp;·&nbsp;
    <a href="/catalogo">Catálogo</a> &nbsp;·&nbsp;
    <a href="/puntos_entrega">Puntos de entrega</a></p>
    <p style="margin-top:8px;">© 2026 Alushe Store. Todos los derechos reservados.</p>
  </footer>

</body>
</html>"""

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ HTML generado correctamente: {HTML_PATH}\n")


# ============================================================
#  MAIN
# ============================================================

if __name__ == "__main__":
    print("🚀 Alushe Store - Generador de Puntos de Entrega")
    print("=" * 50)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        puntos = json.load(f)

    print(f"📋 {len(puntos)} puntos de entrega cargados desde {os.path.basename(JSON_PATH)}.")

    descargar_imagenes(puntos)
    generar_html(puntos)

    print("🎉 Todo listo. Destino:")
    print(f"  Puntos de Entrega HTML: {HTML_PATH}")
    print("  (Tu página principal 'index.html' se mantiene protegida)")
