import os
import json
import random
import urllib.parse
from datetime import datetime
import google.generativeai as genai

# 1. Configuração da API Gemini
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("A chave GEMINI_API_KEY não foi encontrada nas variáveis de ambiente.")

genai.configure(api_key=API_KEY)

hoje_dt = datetime.now()
data_hoje_iso = hoje_dt.strftime("%Y-%m-%d")
data_curta = hoje_dt.strftime("%m%d")

# 2. Matriz de Caos Histórico
SIGLOS = ["Siglo XVIII", "Siglo XIX", "Principios del Siglo XX", "Edad Media", "Antigüedad Clásica"]
REGIONES = ["Europa Occidental", "Asia", "América Latina", "África", "Europa del Este"]
TEMAS = [
    "Un fraude audaz o estafa financiera insólita",
    "Un invento o descubrimiento médico accidental y bizarro",
    "Un evento militar absurdo o guerra por motivos ridículos",
    "Una ley extraña o impuesto insólito que cambió a la sociedad",
    "Un animal o fenómeno natural que aterrorizó a una ciudad",
    "Un robo famoso o una fuga imposible"
]

random.seed(hoje_dt.strftime("%Y%m%d"))
siglo_hoy = random.choice(SIGLOS)
region_hoy = random.choice(REGIONES)
tema_hoy = random.choice(TEMAS)

# 3. Chamada à IA (Gemini)
model = genai.GenerativeModel("gemini-1.5-flash")

prompt = f"""
Eres un investigador cazador de curiosidades oscuras y reales de la historia mundial.
Tu misión es contar una historia verdadera, documentada, rápida y alucinante.

PARÁMETROS OBLIGATORIOS DEL SORTEO DE HOY:
- Época: {siglo_hoy}
- Localización: {region_hoy}
- Enfoque: {tema_hoy}

REGLAS DE ESCRITURA (PROHIBIDO PARECER IA):
1. INVESTIGACIÓN REAL: Encuentra un hecho histórico real y oscuro que encaje con los parámetros. Si no hay exactitud exacta, busca el más cercano en la historia documentada. No inventes datos falsos.
2. EL GANCHO DE WHATSAPP (CRÍTICO): El campo 'chamada_zap' DEBE ser un gancho narrativo cortado en el clímax. Entrega la premisa bizarra pero esconde el desenlace (MÁXIMO 3 LÍNEAS).
3. TEXTO DIRECTO Y ESCANEABLE: Escribe 3 párrafos envolventes (entre 300 y 400 palabras en total). Usa negritas (<b>texto</b>) en 1 o 2 frases clave por párrafo para facilitar la lectura rápida en el móvil.

Retorna EXCLUSIVAMENTE un JSON puro (sin bloques markdown):
{{
  "slug": "url-corta-del-tema-en-kebab-case",
  "chamada_zap": "Texto corto para WhatsApp con la premisa increíble y el misterio.",
  "titulo": "Título intrigante del artículo (máximo 65 caracteres)",
  "paragrafos": [
    "Párrafo 1: El contexto directo y el inicio del suceso bizarro.",
    "Párrafo 2: El clímax y los detalles más absurdos de cómo ocurrió.",
    "Párrafo 3: El desenlace real y las consecuencias históricas."
  ],
  "fator_uau": "Una curiosidad extra de 1 frase impactante para cerrar el expediente."
}}
"""

try:
    response = model.generate_content(prompt)
    raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
    conteudo = json.loads(raw_text)
except Exception as e:
    print(f"Erro na IA: {e}")
    conteudo = {
        "slug": "la-guerra-de-38-minutos",
        "chamada_zap": "La guerra más corta de la historia duró solo 38 minutos. Un sultán desafió al imperio más poderoso del mundo y el resultado fue fulminante.",
        "titulo": "La Guerra de los 38 Minutos",
        "paragrafos": [
            "El 27 de agosto de 1896, el <b>Imperio Británico y el Sultanato de Zanzíbar</b> entraron en conflicto bélico después de que el sultán Khalid bin Barghash tomara el poder mediante un golpe de Estado sin la aprobación diplomática europea.",
            "A las 09:02 de la mañana, tras el vencimiento del ultimátum, tres cruceros y dos cañoneros británicos <b>abrieron fuego coordinado contra el palacio real de madera</b>. A las 09:40, el palacio estaba en ruinas, la bandera del sultán había sido derribada y el fuego cesó por completo.",
            "El enfrentamiento dejó cerca de 500 bajas en el bando de Zanzíbar y apenas <b>un marinero británico herido</b>, convirtiéndose oficialmente en el conflicto armado más breve jamás registrado en la historia militar."
        ],
        "fator_uau": "El gobierno británico obligó a Zanzíbar a pagar el costo financiero de todos los proyectiles disparados contra su propio palacio."
    }

slug = conteudo["slug"]
caminho_pasta = f"artigos/{slug}"

# 4. Formatação Visual dos Parágrafos (Primeiro parágrafo ganha Drop Cap editorial)
paragrafos_formatados = []
for idx, p in enumerate(conteudo["paragrafos"]):
    if idx == 0:
        paragrafos_formatados.append(f"<p class='drop-cap'>{p}</p>")
    else:
        paragrafos_formatados.append(f"<p>{p}</p>")

reflexao_html = "".join(paragrafos_formatados)
titulo_url = urllib.parse.quote(conteudo["titulo"].upper())

# 5. Carrega a Vitrine de Afiliados (Com Fallback configurado para aquaponiabr05-20)
try:
    with open("produtos.json", "r", encoding="utf-8") as f:
        produtos_afiliados = json.load(f)
    dia_do_ano = hoje_dt.timetuple().tm_yday
    produto_hoje = produtos_afiliados[dia_do_ano % len(produtos_afiliados)]
except:
    produto_hoje = {
        "titulo": "Sapiens: De animales a dioses (Edición en Español)",
        "descricao": "Una breve historia de la humanidad que revela los secretos ocultos de nuestra evolución.",
        "imagem_url": "https://m.media-amazon.com/images/I/713jIoMO3UL._SL1500_.jpg",
        "link_afiliado": "https://www.amazon.com/dp/8499926222?tag=aquaponiabr05-20"
    }

# 6. Monta o HTML Final
with open("template.html", "r", encoding="utf-8") as f:
    template = f.read()

html_subpagina = template \
    .replace("{{TITULO}}", conteudo["titulo"]) \
    .replace("{{TITULO_URL}}", titulo_url) \
    .replace("{{TITULO_JSON}}", json.dumps(conteudo["titulo"])) \
    .replace("{{CHAMADA_ZAP}}", conteudo["chamada_zap"]) \
    .replace("{{CHAMADA_JSON}}", json.dumps(conteudo["chamada_zap"])) \
    .replace("{{EPOCA}}", siglo_hoy) \
    .replace("{{REGIAO}}", region_hoy) \
    .replace("{{DATA_CURTA}}", data_curta) \
    .replace("{{REFLEXAO_HTML}}", reflexao_html) \
    .replace("{{FATOR_UAU}}", conteudo["fator_uau"]) \
    .replace("{{PRODUTO_NOME}}", produto_hoje["titulo"]) \
    .replace("{{PRODUTO_DESC}}", produto_hoje["descricao"]) \
    .replace("{{PRODUTO_IMAGEM}}", produto_hoje["imagem_url"]) \
    .replace("{{PRODUTO_LINK}}", produto_hoje["link_afiliado"]) \
    .replace("{{CANONICAL_URL}}", f"https://archivosocultos.com/artigos/{slug}/")

os.makedirs(caminho_pasta, exist_ok=True)
with open(f"{caminho_pasta}/index.html", "w", encoding="utf-8") as f:
    f.write(html_subpagina)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_subpagina)

# 7. Atualiza Sitemap.xml
sitemap_path = "sitemap.xml"
url_nova = f"  <url>\n    <loc>https://archivosocultos.com/artigos/{slug}/</loc>\n    <lastmod>{data_hoje_iso}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n"

if os.path.exists(sitemap_path):
    with open(sitemap_path, "r", encoding="utf-8") as f:
        conteudo_sitemap = f.read()
        if f"<loc>https://archivosocultos.com/artigos/{slug}/</loc>" not in conteudo_sitemap:
            conteudo_sitemap = conteudo_sitemap.replace("</urlset>", url_nova + "</urlset>")
        sitemap_final = conteudo_sitemap
else:
    sitemap_final = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap-0.9">\n  <url>\n    <loc>https://archivosocultos.com/</loc>\n    <lastmod>{data_hoje_iso}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>\n{url_nova}</urlset>'

with open(sitemap_path, "w", encoding="utf-8") as f:
    f.write(sitemap_final)

# 8. Gera o arquivo de disparo inicial para WhatsApp
msg_zap = f"""🕵️‍♂️ *{conteudo['titulo']}*

{conteudo['chamada_zap']}

👉 *Lee el expediente completo aquí:*
https://archivosocultos.com/artigos/{slug}/"""

with open("mensaje_hoy.txt", "w", encoding="utf-8") as f:
    f.write(msg_zap)

print(f"Sucesso! Expediente gerado em: {caminho_pasta}/index.html")
