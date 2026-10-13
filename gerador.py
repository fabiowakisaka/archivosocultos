import os
import json
import random
from datetime import datetime
import google.generativeai as genai

# 1. Configuração da API Gemini
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("A chave GEMINI_API_KEY não foi encontrada nas variáveis de ambiente do GitHub.")

genai.configure(api_key=API_KEY)

hoje_dt = datetime.now()
data_hoje_iso = hoje_dt.strftime("%Y-%m-%d")

# 2. Matriz de Caos Histórico (Garante conteúdo inédito em espanhol)
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

# Semeia o gerador com a data de hoje para consistência diária
random.seed(hoje_dt.strftime("%Y%m%d"))
siglo_hoy = random.choice(SIGLOS)
region_hoy = random.choice(REGIONES)
tema_hoy = random.choice(TEMAS)

# 3. Chamada à IA - Engenharia de Curiosidade (Em Espanhol)
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
2. EL GANCHAL DE WHATSAPP (CRÍTICO): El campo 'llamada_zap' DEBE ser un gancho narrativo cortado en el clímax. Entrega la premisa bizarra pero esconde el desenlace.
   Ejemplo: "En 1925, un hombre logró VENDER la Torre Eiffel a un grupo de chatarreros. Lo más loco: ¡intentó repetir la estafa meses después! Descubre cómo lo hizo."
3. TEXTO DIRECTO: Sin introducciones largas ni adornos poéticos. Estilo periodístico intrigante y dinámico.

Retorna EXCLUSIVAMENTE un JSON puro (sin bloques de código markdown extras, solo el JSON):
{{
  "slug": "url-corta-del-tema-en-kebab-case",
  "chamada_zap": "Texto corto para WhatsApp con la premisa increíble y la promesa de la respuesta en el enlace (MÁXIMO 4 LÍNEAS).",
  "titulo": "Título intrigante del artículo",
  "paragrafos": [
    "Párrafo 1: La introducción directa al hecho bizarro.",
    "Párrafo 2: El desarrollo y la explicación de cómo ocurrió.",
    "Párrafo 3: El desenlace y cómo impactó o terminó."
  ],
  "fator_uau": "Una curiosidad extra de 1 frase (bullet point) relacionada con el tema para cerrar el artículo."
}}
"""

try:
    response = model.generate_content(prompt)
    raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
    conteudo = json.loads(raw_text)
except Exception as e:
    print(f"Erro na IA: {e}")
    # Fallback de segurança (em espanhol)
    conteudo = {
        "slug": "la-guerra-de-38-minutos",
        "chamada_zap": "La guerra más corta de la historia duró solo 38 minutos. Un sultán desafió al imperio más poderoso del mundo y el resultado fue fulminante. Mira lo que pasó.",
        "titulo": "La Guerra de los 38 Minutos",
        "paragrafos": [
            "El 27 de agosto de 1896, el Imperio Británico y el Sultanato de Zanzíbar entraron en conflicto bélico después de que el sultán Khalid bin Barghash se negará a ceder el poder.",
            "A las 09:02 horas, los buques de guerra británicos abrieron fuego coordinado contra el palacio real de madera. A las 09:40, el palacio estaba en ruinas y el fuego cesó por completo.",
            "El enfrentamiento dejó cerca de 500 bajas en el bando de Zanzíbar y apenas un marinero británico herido, convirtiéndose en la guerra relámpago más breve de la historia."
        ],
        "fator_uau": "El sultán Khalid logró asilarse en el consulado alemán y vivió en el exilio hasta 1927."
    }

slug = conteudo["slug"]
caminho_pasta = f"artigos/{slug}"

# 4. Carrega o Molde HTML
with open("template.html", "r", encoding="utf-8") as f:
    template = f.read()

reflexao_html = "".join([f"<p class='mb-4 text-stone-300'>{p}</p>" for p in conteudo["paragrafos"]])

# 5. Vitrine de Afiliados Globais (Amazon EUA / Afiliados)
try:
    with open("produtos.json", "r", encoding="utf-8") as f:
        produtos_afiliados = json.load(f)
    dia_do_ano = hoje_dt.timetuple().tm_yday
    produto_hoje = produtos_afiliados[dia_do_ano % len(produtos_afiliados)]
except:
    produto_hoje = {
        "titulo": "Libro: Sapiens - De animales a dioses",
        "descricao": "Descubre la fascinante historia de cómo nuestra especie logró dominar el planeta.",
        "imagem_url": "https://m.media-amazon.com/images/I/414Wp0sqzoL._SY445_SX342_.jpg",
        "link_afiliado": "https://www.amazon.com"
    }

# 6. Monta a Página Específica do Artigo
html_subpagina = template \
    .replace("{{TITULO}}", conteudo["titulo"]) \
    .replace("{{CHAMADA_ZAP}}", conteudo["chamada_zap"]) \
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

# 7. Atualiza o Índice da Raiz (index.html principal aponta sempre para o mais recente)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_subpagina)

# 8. Atualiza o Sitemap.xml para SEO do Google
sitemap_path = "sitemap.xml"
url_nova = f"  <url>\n    <loc>https://archivosocultos.com/artigos/{slug}/</loc>\n    <lastmod>{data_hoje_iso}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n"

urls_existentes = []
if os.path.exists(sitemap_path):
    with open(sitemap_path, "r", encoding="utf-8") as f:
        conteudo_sitemap = f.read()
        if f"<loc>https://archivosocultos.com/artigos/{slug}/</loc>" not in conteudo_sitemap:
            # Insere antes do fechamento do urlset
            conteudo_sitemap = conteudo_sitemap.replace("</urlset>", url_nova + "</urlset>")
        sitemap_final = conteudo_sitemap
else:
    sitemap_final = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap-0.9">\n  <url>\n    <loc>https://archivosocultos.com/</loc>\n    <lastmod>{data_hoje_iso}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>\n{url_nova}</urlset>'

with open(sitemap_path, "w", encoding="utf-8") as f:
    f.write(sitemap_final)

# 9. Gera o arquivo de texto pronto para o WhatsApp
msg_zap = f"""🕵️‍♂️ *Archivo Oculto del Día* 🕵️‍♂️

{conteudo['chamada_zap']}

👉 Descubre cómo terminó esta historia aquí:
https://archivosocultos.com/artigos/{slug}/"""

with open("mensaje_hoy.txt", "w", encoding="utf-8") as f:
    f.write(msg_zap)

print(f"Sucesso! Artigo gerado em: {caminho_pasta}/index.html")
