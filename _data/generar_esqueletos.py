#!/usr/bin/env python3
"""Genera notas-esqueleto para los 20 libros restantes (Fase 2a).

Para cada libro extrae automáticamente:
  - Metadatos (del JSON libros.json)
  - Índice / estructura de capítulos detectada
  - Citas candidatas (líneas entre comillas)
  - Conceptos candidatos (keywords budistas)
  - Primeras líneas (portada/intro)

Genera una nota Markdown por libro en 01 - Libros/ siguiendo el template.
Las secciones que requieren análisis semántico quedan marcadas [ANÁLISIS].
"""
import json
import re
import unicodedata
from pathlib import Path

BASE = Path("/Users/maclleida/budismo")
DATA = BASE / "_data"
TEXTO_DIR = DATA / "texto_extraido"
LIBROS_DIR = BASE / "01 - Libros"

# Conceptos budistas para detectar (keyword matching)
CONCEPTOS_KEYWORDS = {
    "Cuatro Nobles Verdades": [r"cuatro nobles verdades", r"four noble truths"],
    "Sufrimiento (Dukkha)": [r"dukkha", r"sufrimiento", r"\bsuffering\b"],
    "Mente": [r"\bmente\b", r"\bmind\b"],
    "Karma": [r"\bkarma\b"],
    "Reencarnación": [r"reencarnaci[óo]n", r"rebirth", r"vidas pasadas"],
    "Vacuidad (Shunyata)": [r"vacuidad", r"shunyata", r"emptiness", r"voidness"],
    "Bodhichitta": [r"bodhichitta", r"bodhicitta"],
    "Bodhisattva": [r"bodhisattva", r"bodhisatva", r"bodhisat"],
    "Compasión": [r"compasi[óo]n", r"compassion", r"karuna"],
    "Paciencia": [r"paciencia", r"patience", r"ksanti"],
    "Renuncia": [r"renuncia", r"renunciation"],
    "Sabiduría": [r"sabidur[íi]a", r"wisdom", r"prajna", r"jnana"],
    "Meditación": [r"meditaci[óo]n", r"meditation", r"dhyana"],
    "Iluminación": [r"iluminaci[óo]n", r"enlightenment", r"budeidad", r"buddhahood"],
    "Samsara": [r"samsara", r"s[aá]msara"],
    "Nirvana": [r"nirvana"],
    "Lamrim": [r"lamrim"],
    "Tantra": [r"\btantra\b"],
    "Sutra": [r"\bsutra\b"],
    "Mahamudra": [r"mahamudra"],
    "Madhyamaka": [r"madhyamaka", r"middle way", r"camino medio"],
    "Atisha": [r"atisha", r"at[ií]sha"],
    "Tsongkhapa": [r"tsongkhapa", r"je tsongkhapa"],
    "Shantideva": [r"shantideva", r"santideva", r"shantideva"],
    "Buda": [r"\bbuda\b", r"\bbuddha\b"],
    "Dharma": [r"\bdharma\b"],
    "Sangha": [r"\bsangha\b"],
    "Impermanencia": [r"impermanencia", r"impermanence", r"anitya"],
    "Naturaleza de Buda": [r"naturaleza de buda", r"buddha nature", r"tathagatagarbha"],
    "Mandala": [r"\bmandala\b"],
    "Mantra": [r"\bmantra\b"],
    "Vajrayana": [r"vajrayana"],
    "Mahayana": [r"mahayana"],
    "Hinayana": [r"hinayana", r"theravada"],
    "Las seis perfecciones": [r"seis perfecciones", r"six perfections", r"paramita"],
    "Tonglen": [r"tonglen", r"dar y recibir"],
}


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()[:70]


def detectar_indice(lineas):
    """Detecta entradas de índice (línea corta seguida de número de página)."""
    pat_toc = re.compile(r"(índice|indice|contents|table of contents|contenido)",
                         re.IGNORECASE)
    inicio = None
    for i, l in enumerate(lineas[:400]):
        if pat_toc.search(l) and len(l) < 60:
            inicio = i
            break
    if inicio is None:
        return [], None
    entradas = []
    pat_num = re.compile(r"\.+\s*\d+$|^\d+$|\s\d{1,4}$")
    for i in range(inicio + 1, min(inicio + 200, len(lineas))):
        l = lineas[i].strip()
        if not l or len(l) > 80:
            continue
        if l.isdigit() and len(l) < 5:
            continue
        # línea tipo "Capítulo 1" o "1. Título" o "Título ... 23"
        if re.match(r"^(cap[ií]tulo|chapter|parte|part|ap[eé]ndice|appendix)\b",
                    l, re.IGNORECASE):
            entradas.append(l)
        elif re.match(r"^\d+[\.\)]\s+\S", l):
            entradas.append(l)
        elif pat_num.search(l) and re.search(r"[a-záéíóúñ]{3,}", l, re.IGNORECASE):
            entradas.append(re.sub(r"\s*\.+\s*\d+\s*$", "", l).strip())
        # parar si llegamos a algo que parece cuerpo del texto
        if len(entradas) > 5 and re.search(r"[\.!?]{1}\s*$", l) and len(l) > 100:
            break
    return entradas[:60], inicio


def detectar_citas(texto, max_citas=8):
    """Detecta líneas entre comillas tipográficas o rectas."""
    citas = []
    pat = re.compile(r"[«""]([^»""]{30,300})[»""]")
    for m in pat.finditer(texto):
        c = m.group(1).strip()
        if len(c.split()) >= 5 and c not in [x[0] for x in citas]:
            citas.append((c, None))
        if len(citas) >= max_citas:
            break
    return citas


def detectar_conceptos(texto):
    """Detecta conceptos presentes en el texto."""
    texto_low = texto.lower()
    encontrados = []
    for concepto, pats in CONCEPTOS_KEYWORDS.items():
        for p in pats:
            if re.search(p, texto_low):
                encontrados.append(concepto)
                break
    return encontrados


def detectar_autor_titulo(registro):
    """Saca autor/título de los metadatos o del nombre del archivo."""
    autor = (registro.get("autor_meta") or registro.get("autor_candidato")
             or "").strip()
    titulo = (registro.get("titulo_meta")
              or registro.get("titulo_archivo", "")).strip()
    año = registro.get("año_candidato")
    # Limpiar título
    titulo = re.sub(r"--.*", "", titulo).strip(" -_")
    titulo = re.sub(r"\.(pdf|epub|mobi)$", "", titulo, flags=re.IGNORECASE)
    if len(titulo) > 100:
        titulo = titulo[:97] + "..."
    return autor or "Desconocido", titulo or registro["archivo"], año


# === EJECUCIÓN ===
inventario = json.loads((DATA / "libros.json").read_text(encoding="utf-8"))

# Saltar el del spike (ya hecho manualmente)
SLUG_SPIKE = "como-solucionar-nuestros-problemas-humanos"

generadas = 0
saltadas = 0
for reg in inventario:
    if reg.get("slug") == SLUG_SPIKE:
        saltadas += 1
        continue
    texto_path = BASE / reg.get("texto", "") if reg.get("texto") else None
    if not texto_path or not texto_path.exists():
        print(f"SALTADO (sin texto): {reg['archivo'][:60]}")
        continue

    texto = texto_path.read_text(encoding="utf-8")
    lineas = texto.split("\n")
    autor, titulo, año = detectar_autor_titulo(reg)
    indice, _ = detectar_indice(lineas)
    citas = detectar_citas(texto)
    conceptos = detectar_conceptos(texto)

    slug_name = reg["slug"]
    # Frontmatter
    fm = [
        "---",
        f'id: {reg["id"]}',
        f'titulo: "{titulo}"',
        f'autor: "{autor}"',
    ]
    if año:
        fm.append(f"año: {año}")
    if reg.get("paginas"):
        fm.append(f'paginas: {reg["paginas"]}')
    fm.append(f'idioma: "es"')
    fm.append(f'tipo_archivo: "{reg.get("tipo", "desconocido")}"')
    fm.append(f'archivo: "[[{reg["archivo"]}]]"')
    fm.append(f'palabras: {len(texto.split())}')
    fm.append(f'estado: "esqueleto-automatico"')
    fm.append("conceptos:")
    for c in conceptos[:15]:
        fm.append(f'  - "[[{c}]]"')
    fm.append("tags: [libro, pendiente-revision]")
    fm.append("---")
    fm.append("")

    # Cuerpo
    cuerpo = [f"# {titulo}", ""]
    cuerpo.append(f"**Autor:** {autor}  ")
    if año:
        cuerpo.append(f"**Año:** {año}  ")
    if reg.get("paginas"):
        cuerpo.append(f"**Páginas:** {reg['paginas']}  ")
    cuerpo.append(f"**Palabras:** {len(texto.split()):,}  ")
    cuerpo.append("")

    cuerpo.append("> **[PENDIENTE — Tesis central]** Extraer del texto del libro.")
    cuerpo.append("")

    cuerpo.append("## Resumen ejecutivo")
    cuerpo.append("")
    cuerpo.append("**[ANÁLISIS — 2-3 párrafos]** "
                  "Leer la introducción y la conclusión del texto extraído y "
                  "sintetizar la tesis principal, el contexto del libro y su "
                  "aporte.")
    cuerpo.append("")

    cuerpo.append("## Contexto y tradición")
    cuerpo.append("")
    cuerpo.append("**[ANÁLISIS]** Identificar tradición (Kadampa, Zen, Theravada, "
                  "etc.), linaje, texto raíz si lo hay, marco sistemático.")
    cuerpo.append("")

    cuerpo.append("## Estructura")
    cuerpo.append("")
    if indice:
        cuerpo.append("Índice detectado:")
        cuerpo.append("")
        for e in indice:
            cuerpo.append(f"- {e}")
    else:
        cuerpo.append("**[Índice no detectado automáticamente]** "
                      "Revisar el texto para extraer capítulos.")
    cuerpo.append("")

    cuerpo.append("## Resumen por capítulo")
    cuerpo.append("")
    cuerpo.append("**[ANÁLISIS — un párrafo por capítulo]**")
    cuerpo.append("")

    cuerpo.append("## Conceptos clave")
    cuerpo.append("")
    if conceptos:
        cuerpo.append("Conceptos detectados automáticamente:")
        cuerpo.append("")
        for c in conceptos[:15]:
            cuerpo.append(f"- [[{c}]]")
    else:
        cuerpo.append("**[Sin detección automática]** Revisar manualmente.")
    cuerpo.append("")

    cuerpo.append("## Cómo aplicar esta enseñanza")
    cuerpo.append("")
    cuerpo.append("**[ANÁLISIS]**")
    cuerpo.append("- Práctica diaria sugerida")
    cuerpo.append("- Aplicación en problemas cotidianos")
    cuerpo.append("- Errores comunes al practicar")
    cuerpo.append("")

    cuerpo.append("## Glosario de términos")
    cuerpo.append("")
    cuerpo.append("**[ANÁLISIS]** Términos sánscritos/tibetanos relevantes del libro.")
    cuerpo.append("")

    cuerpo.append("## Citas destacadas")
    cuerpo.append("")
    if citas:
        for c, _ in citas:
            cuerpo.append(f'> {c}')
            cuerpo.append(">")
    else:
        cuerpo.append("**[Sin citas detectadas automáticamente]** "
                      "Revisar manualmente líneas entre comillas.")
    cuerpo.append("")

    cuerpo.append("## Preguntas de reflexión")
    cuerpo.append("")
    cuerpo.append("**[ANÁLISIS — 5 preguntas]**")
    cuerpo.append("")

    cuerpo.append("## Conexiones en la colección")
    cuerpo.append("")
    cuerpo.append("**[ANÁLISIS]** Cruzar con otros libros que toquen los mismos "
                  "conceptos.")
    cuerpo.append("")

    cuerpo.append("## Plan de estudio y práctica")
    cuerpo.append("")
    cuerpo.append("**[ANÁLISIS]** Principiantes / intermedios / enseñanza.")
    cuerpo.append("")

    cuerpo.append("## Notas de extracción")
    cuerpo.append("")
    cuerpo.append(f"- Texto: `{reg.get('texto', '?')}`")
    cuerpo.append(f"- {len(texto):,} caracteres, ~{len(texto.split()):,} palabras")
    cuerpo.append(f"- Tipo: {reg.get('tipo', '?')}")
    cuerpo.append("")

    contenido = "\n".join(fm + cuerpo)
    out = LIBROS_DIR / f"{slug_name}.md"
    if out.exists():
        print(f"SALTADO (ya existe .md): {slug_name[:60]}")
        continue
    out.write_text(contenido, encoding="utf-8")
    generadas += 1
    print(f"OK  {slug_name[:60]:60} | {len(conceptos):2} conceptos | "
          f"{len(citas)} citas | {len(indice):2} entradas índice")

print(f"\n{'='*60}")
print(f"Esqueletos generados: {generadas}")
print(f"Saltadas (ya hechas): {saltadas}")
print(f"Total notas en 01 - Libros/: "
      f"{len(list(LIBROS_DIR.glob('*.md')))}")
