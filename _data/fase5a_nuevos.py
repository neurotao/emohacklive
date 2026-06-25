#!/usr/bin/env python3
"""Fase 5a - Detección de duplicados + extracción de texto.

Para los 46 libros nuevos en _fuentes/:
  1. Calcula MD5
  2. Marca duplicados (vs JSON existente y entre los nuevos)
  3. Extrae texto de los únicos (pdftotext o extractor EPUB)
  4. Actualiza _data/libros.json
"""
import json
import hashlib
import subprocess
import re
import unicodedata
import zipfile
from html.parser import HTMLParser
from pathlib import Path

BASE = Path("/Users/maclleida/budismo")
LIBROS_DIR = BASE / "_fuentes"
DATA_DIR = BASE / "_data"
TEXTO_DIR = DATA_DIR / "texto_extraido"
JSON_PATH = DATA_DIR / "libros.json"


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()[:70]


def parsear_nombre(nombre):
    base = nombre.rsplit(".", 1)[0]
    partes = [p.strip() for p in base.split("--") if p.strip()]
    out = {"titulo_archivo": base, "partes": partes}
    if len(partes) >= 2:
        out["autor_candidato"] = partes[1]
    m = re.search(r"(19|20)\d{2}", base)
    if m:
        out["año_candidato"] = int(m.group(0))
    return out


def pdfinfo(path):
    try:
        r = subprocess.run(["pdfinfo", str(path)], capture_output=True,
                           text=True, timeout=30)
        info = {}
        for line in r.stdout.splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                info[k.strip().lower().replace(" ", "_")] = v.strip()
        return info
    except Exception:
        return {}


def extraer_pdf_text(path):
    try:
        r = subprocess.run(["pdftotext", str(path), "-"],
                           capture_output=True, text=True, timeout=180)
        return r.stdout
    except Exception:
        return ""


class TX(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = False
    def handle_starttag(self, t, a):
        if t in ("script", "style"):
            self.skip = True
        if t in ("p", "div", "br", "h1", "h2", "h3", "li", "tr"):
            self.parts.append("\n")
    def handle_endtag(self, t):
        if t in ("script", "style"):
            self.skip = False
        if t in ("p", "div", "h1", "h2", "h3"):
            self.parts.append("\n")
    def handle_data(self, d):
        if not self.skip:
            self.parts.append(d)


def extraer_epub_text(path):
    try:
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist()
                     if n.lower().endswith((".xhtml", ".html", ".htm"))]
            names.sort()
            chunks = []
            for n in names:
                try:
                    raw = z.read(n).decode("utf-8", errors="ignore")
                    p = TX()
                    p.feed(raw)
                    chunks.append("".join(p.parts))
                except Exception:
                    pass
        text = "\n\n".join(chunks)
        return re.sub(r"\n{3,}", "\n\n", text)
    except Exception as e:
        print(f"  ✗ Error EPUB: {e}")
        return ""


# === EJECUCIÓN ===
print("=" * 70)
print("FASE 5a — Detección de duplicados + extracción de texto")
print("=" * 70)

# 1. Cargar JSON existente
inventario = json.loads(JSON_PATH.read_text(encoding="utf-8"))
md5_existentes = {r.get("md5"): r for r in inventario if r.get("md5")}
# Calcular MD5 de los existentes (no los teníamos guardados)
print("\nCalculando MD5 de los 24 libros existentes...")
for r in inventario:
    src = LIBROS_DIR / r["archivo"]
    if src.exists():
        r["md5"] = md5(src)
        md5_existentes[r["md5"]] = r
JSON_PATH.write_text(json.dumps(inventario, indent=2, ensure_ascii=False),
                     encoding="utf-8")

# 2. Listar archivos actuales en carpeta
archivos_actuales = sorted(f for f in LIBROS_DIR.iterdir()
                           if f.suffix.lower() in (".pdf", ".epub", ".mobi"))
nombres_json = {r["archivo"] for r in inventario}

# 3. Procesar archivos nuevos
nuevos = [f for f in archivos_actuales if f.name not in nombres_json]
print(f"\nArchivos nuevos a procesar: {len(nuevos)}\n")

vistos_md5 = {}  # MD5 → archivo (para detectar duplicados entre nuevos)
duplicados_nuevos = []
procesados = []

for i, f in enumerate(nuevos, 1):
    print(f"[{i:2}/{len(nuevos)}] {f.name[:65]}")
    hash_val = md5(f)
    info_nombre = parsear_nombre(f.name)
    registro = {
        "id": len(inventario) + 1,
        "archivo": f.name,
        "slug": slug(f.stem),
        "extension": f.suffix.lower(),
        "md5": hash_val,
        **info_nombre,
    }

    # ¿Es duplicado?
    if hash_val in md5_existentes:
        orig = md5_existentes[hash_val]
        print(f"  ⚠️  DUPLICADO de: {orig['archivo'][:50]}")
        registro["tipo"] = "duplicado"
        registro["duplicado_de"] = orig.get("slug")
        registro["duplicado_de_archivo"] = orig["archivo"]
        duplicados_nuevos.append(registro)
        inventario.append(registro)
        continue
    if hash_val in vistos_md5:
        orig = vistos_md5[hash_val]
        print(f"  ⚠️  DUPLICADO de otro nuevo: {orig.name[:50]}")
        registro["tipo"] = "duplicado"
        registro["duplicado_de"] = slug(orig.stem)
        duplicados_nuevos.append(registro)
        inventario.append(registro)
        continue
    vistos_md5[hash_val] = f

    # No es duplicado → extraer texto
    if f.suffix.lower() == ".pdf":
        info = pdfinfo(f)
        paginas = info.get("pages", "")
        registro["paginas"] = int(paginas) if paginas.isdigit() else None
        registro["titulo_meta"] = info.get("title", "")
        registro["autor_meta"] = info.get("author", "")
        texto = extraer_pdf_text(f)
        registro["tipo"] = ("digital" if len(texto) > 1000
                            else "escaneado_ocr")
        registro["caracteres"] = len(texto)
    elif f.suffix.lower() == ".epub":
        texto = extraer_epub_text(f)
        registro["tipo"] = "ebook-convertido"
        registro["caracteres"] = len(texto)
    elif f.suffix.lower() == ".mobi":
        # Intentar con calibre
        try:
            subprocess.run(["ebook-convert", str(f), "/tmp/_mobi.epub"],
                           capture_output=True, timeout=60)
            texto = extraer_epub_text("/tmp/_mobi.epub")
            registro["tipo"] = "ebook-convertido"
            registro["caracteres"] = len(texto)
        except Exception:
            registro["tipo"] = "ebook-pendiente"
            texto = ""
    else:
        texto = ""

    if texto:
        out = TEXTO_DIR / f"{registro['slug']}.txt"
        out.write_text(texto, encoding="utf-8")
        registro["texto"] = f"_data/texto_extraido/{out.name}"

    inventario.append(registro)
    procesados.append(registro)
    pags = registro.get("paginas", "?")
    print(f"  ✓ {pags} págs | {registro['tipo']:18} | "
          f"{registro.get('caracteres', 0):>7} chars")

# Guardar JSON actualizado
JSON_PATH.write_text(json.dumps(inventario, indent=2, ensure_ascii=False),
                     encoding="utf-8")

# Resumen
total = len(inventario)
unicos = sum(1 for r in inventario if r.get("tipo") not in
             ("duplicado", "duplicado-confirmado"))
duplicados = sum(1 for r in inventario if r.get("tipo") in
                 ("duplicado", "duplicado-confirmado"))
con_texto = sum(1 for r in inventario if r.get("texto"))

print(f"\n{'=' * 70}")
print(f"FASE 5a COMPLETADA")
print(f"{'=' * 70}")
print(f"Total en inventario: {total}")
print(f"  Únicos: {unicos}")
print(f"  Duplicados marcados: {duplicados}")
print(f"  Con texto extraído: {con_texto}")
print(f"\nNuevos únicos procesados: {len(procesados)}")
print(f"Duplicados detectados: {len(duplicados_nuevos)}")
