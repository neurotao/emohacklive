#!/usr/bin/env python3
"""Fase 0 (Inventario) + Fase 1 (Extracción) para la bóveda de budismo.

Para cada archivo en _fuentes/:
  - Extrae metadatos (pdfinfo)
  - Extrae texto (pdftotext) y detecta si es digital o escaneado
  - Guarda el texto plano en _data/texto_extraido/<slug>.txt
  - Genera _data/libros.json con el inventario completo
"""
import json
import subprocess
import unicodedata
import re
from pathlib import Path

LIBROS_DIR = Path("/Users/maclleida/budismo/_fuentes")
DATA_DIR = Path("/Users/maclleida/budismo/_data")
TEXTO_DIR = DATA_DIR / "texto_extraido"
DATA_DIR.mkdir(parents=True, exist_ok=True)
TEXTO_DIR.mkdir(parents=True, exist_ok=True)

UMBRAL_DIGITAL = 1000  # caracteres mínimos para considerar "digital"


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
    except Exception as e:
        return {"error": str(e)}


def extraer_texto_pdf(path):
    try:
        r = subprocess.run(["pdftotext", str(path), "-"],
                           capture_output=True, text=True, timeout=180)
        return r.stdout
    except subprocess.TimeoutExpired:
        return ""
    except Exception:
        return ""


def slug(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-")
    return texto.lower()[:70]


def parsear_nombre(nombre):
    """Intenta sacar autor/año/titulo del nombre del archivo."""
    base = nombre.rsplit(".", 1)[0]
    # Patron: "Titulo -- Autor -- Año"
    partes = [p.strip() for p in base.split("--") if p.strip()]
    out = {"titulo_archivo": base, "partes": partes}
    if len(partes) >= 2:
        out["autor_candidato"] = partes[1]
    # Buscar año
    m = re.search(r"(19|20)\d{2}", base)
    if m:
        out["año_candidato"] = int(m.group(0))
    return out


archivos = sorted(f for f in LIBROS_DIR.iterdir()
                  if f.suffix.lower() in (".pdf", ".epub", ".mobi"))

print(f"Procesando {len(archivos)} archivos...\n")
inventario = []

for i, f in enumerate(archivos, 1):
    nombre = f.name
    info_nombre = parsear_nombre(nombre)
    registro = {
        "id": i,
        "archivo": nombre,
        "slug": slug(f.stem),
        "extension": f.suffix.lower(),
        **info_nombre,
    }
    print(f"[{i:2}/{len(archivos)}] {nombre[:72]}")

    if f.suffix.lower() == ".pdf":
        info = pdfinfo(f)
        paginas = info.get("pages", "")
        registro.update({
            "paginas": int(paginas) if paginas.isdigit() else None,
            "titulo_meta": info.get("title", ""),
            "autor_meta": info.get("author", ""),
            "creador": info.get("creator", ""),
            "tamano_pagina": info.get("page_size", ""),
        })
        texto = extraer_texto_pdf(f)
        registro["caracteres"] = len(texto)
        registro["tipo"] = ("digital" if len(texto) > UMBRAL_DIGITAL
                            else "escaneado_ocr")
        if texto:
            out = TEXTO_DIR / f"{registro['slug']}.txt"
            out.write_text(texto, encoding="utf-8")
            registro["texto"] = str(out.relative_to(DATA_DIR.parent))
    else:
        registro["tipo"] = "ebook"
        registro["nota"] = "Requiere ebook-convert (calibre)"

    inventario.append(registro)
    pags = registro.get("paginas") or "?"
    print(f"        → {pags} págs | {registro['tipo']:14} | "
          f"{registro.get('caracteres', 0):>7} chars")

# Guardar JSON
(DATA_DIR / "libros.json").write_text(
    json.dumps(inventario, indent=2, ensure_ascii=False), encoding="utf-8")

# Resumen
digitales = sum(1 for x in inventario if x["tipo"] == "digital")
escaneados = sum(1 for x in inventario if x["tipo"] == "escaneado_ocr")
ebooks = sum(1 for x in inventario if x["tipo"] == "ebook")
total_pags = sum(x.get("paginas") or 0 for x in inventario)
total_chars = sum(x.get("caracteres", 0) or 0 for x in inventario)

print(f"\n{'='*64}")
print(f"FASE 0 + 1 COMPLETADAS")
print(f"{'='*64}")
print(f"Archivos procesados : {len(inventario)}")
print(f"  Digital (texto)   : {digitales}")
print(f"  Escaneado (OCR)   : {escaneados}")
print(f"  Ebook (epub/mobi) : {ebooks}")
print(f"Total páginas       : {total_pags:,}")
print(f"Total texto extraído: {total_chars:,} caracteres "
      f"(~{total_chars//5:,} palabras)")
print(f"\nInventario: {DATA_DIR / 'libros.json'}")
print(f"Textos    : {TEXTO_DIR}/")
