#!/usr/bin/env python3
"""Fase 6 v2 - Extracción inteligente de imágenes.

Estrategia nueva:
  - PDF digital: extraer imágenes >50KB (son ilustraciones reales)
  - PDF escaneado: NO extraer (todo es foto de página)
  - Excluir smasks, imágenes muy chicas (<50KB) y fotos de página extremas
"""
import json
import subprocess
import re
import unicodedata
from pathlib import Path

BASE = Path("/Users/maclleida/budismo")
LIBROS_DIR = BASE / "_fuentes"
IMG_DIR = BASE / "05 - Imágenes"
JSON_PATH = BASE / "_data/libros.json"
IMG_DIR.mkdir(parents=True, exist_ok=True)

MIN_BYTES = 50_000       # 50KB - descarta iconos/separadores
MAX_BYTES = 15_000_000   # 15MB


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()[:50]


def es_foto_pagina(img_info):
    """Detecta si una imagen es foto de página completa (proporción página)."""
    w, h = img_info["width"], img_info["height"]
    # Una página A4 es 595x842 pts → ratio 0.71. Foto de página = ratio similar
    # Y dimensiones grandes (>1500x2000 típicamente)
    ratio = w / h if h else 0
    return (w > 1500 and h > 2000 and 0.55 < ratio < 0.85)


def listar_imagenes(pdf_path):
    try:
        r = subprocess.run(["pdfimages", "-list", str(pdf_path)],
                           capture_output=True, text=True, timeout=60)
    except Exception:
        return []
    lineas = r.stdout.splitlines()
    if len(lineas) < 3:
        return []
    resultado = []
    for line in lineas[2:]:
        partes = line.split()
        if len(partes) < 16:
            continue
        try:
            img = {
                "page": int(partes[0]),
                "num": int(partes[1]),
                "type": partes[2],
                "width": int(partes[3]),
                "height": int(partes[4]),
                "size_str": partes[15],
            }
            s = img["size_str"]
            mult = 1
            if s.endswith("K"): mult = 1000; s = s[:-1]
            elif s.endswith("M"): mult = 1_000_000; s = s[:-1]
            elif s.endswith("B"): s = s[:-1]
            try:
                img["size"] = int(float(s) * mult)
            except Exception:
                img["size"] = 0
            resultado.append(img)
        except (ValueError, IndexError):
            continue
    return resultado


# === EJECUCIÓN ===
print("=" * 70)
print("FASE 6 v2 — Extracción inteligente de imágenes")
print("=" * 70)

inventario = json.loads(JSON_PATH.read_text(encoding="utf-8"))
pdfs = [r for r in inventario if r["extension"] == ".pdf"
        and r.get("tipo") not in ("duplicado", "duplicado-confirmado",
                                  "escaneado_ocr")]  # NO escaneados
print(f"\nProcesando {len(pdfs)} PDFs digitales (saltando escaneados)...\n")

total_extraidas = 0
resumen = []

for i, r in enumerate(pdfs, 1):
    src = LIBROS_DIR / r["archivo"]
    if not src.exists():
        continue
    slug_libro = r["slug"]
    out_dir = IMG_DIR / slug_libro
    
    print(f"[{i:2}/{len(pdfs)}] {r['archivo'][:60]}")
    
    imgs = listar_imagenes(src)
    # Filtrar: NO smask, NO foto de página, tamaño razonable
    candidatas = [img for img in imgs
                  if img["type"] != "smask"
                  and not es_foto_pagina(img)
                  and MIN_BYTES <= img["size"] <= MAX_BYTES
                  and img["width"] >= 200 and img["height"] >= 200]
    
    if not candidatas:
        print(f"  — {len(imgs)} imgs totales, 0 relevantes")
        continue
    
    # Extraer a directorio temporal, luego filtrar por tamaño en disco
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / "img"
    try:
        subprocess.run(["pdfimages", "-png", str(src), str(prefix)],
                       capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout")
        continue
    
    # Filtrar por tamaño en disco
    conservadas = 0
    for f in sorted(out_dir.glob("img-*.png")):
        size = f.stat().st_size
        if MIN_BYTES <= size <= MAX_BYTES:
            # Renombrar
            conservadas += 1
            nuevo = out_dir / f"imagen-{conservadas:03d}.png"
            if nuevo != f:
                f.rename(nuevo)
        else:
            f.unlink()
    
    if conservadas == 0:
        try:
            out_dir.rmdir()
        except OSError:
            pass
        print(f"  — {len(candidatas)} candidatas pero 0 pasaron filtro disco")
    else:
        total_extraidas += conservadas
        print(f"  ✓ {conservadas} imágenes extraídas (de {len(imgs)} totales)")
        resumen.append((r["archivo"], conservadas))

# Limpiar carpetas vacías
for d in list(IMG_DIR.iterdir()):
    if d.is_dir() and not any(d.iterdir()):
        d.rmdir()

print(f"\n{'=' * 70}")
print(f"FASE 6 v2 COMPLETADA")
print(f"{'=' * 70}")
print(f"Total imágenes extraídas: {total_extraidas}")
print(f"Libros con imágenes: {len(resumen)}")
print(f"\nTop 15 libros con más imágenes:")
for archivo, n in sorted(resumen, key=lambda x: -x[1])[:15]:
    print(f"  {n:4} imgs  |  {archivo[:60]}")
