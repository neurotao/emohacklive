#!/usr/bin/env python3
"""Fase 6 - Extracción filtrada de imágenes de TODOS los PDFs.

Estrategia:
  - Solo PDFs digitales (no escaneados) tienen ilustraciones útiles
  - Filtrar imágenes por tamaño: 30KB-8MB (ilustraciones reales)
  - Excluir dimensiones de página completa (>1500x2000 suelen ser fotos de página)
  - Renombrar con slug del libro + índice
  - Guardar en 05 - Imágenes/<libro-slug>/
"""
import json
import subprocess
import re
import unicodedata
from pathlib import Path

BASE = Path("/Users/maclleida/budismo")
LIBROS_DIR = BASE / "_fuentes"
IMG_DIR = BASE / "05 - Imágenes"
DATA_DIR = BASE / "_data"
JSON_PATH = DATA_DIR / "libros.json"

IMG_DIR.mkdir(parents=True, exist_ok=True)

# Filtros
MIN_BYTES = 30_000       # 30KB
MAX_BYTES = 8_000_000    # 8MB
MAX_WIDTH = 2000         # descartar imágenes de página completa
MAX_HEIGHT = 2700


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()[:50]


def listar_imagenes(pdf_path):
    """Retorna lista de dicts con metadatos de imágenes del PDF."""
    try:
        r = subprocess.run(["pdfimages", "-list", str(pdf_path)],
                           capture_output=True, text=True, timeout=60)
    except Exception:
        return []
    lineas = r.stdout.splitlines()
    if len(lineas) < 3:
        return []
    # Formato: page num type width height color comp bpc enc interp object ID x-ppi y-ppi size ratio
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
                "color": partes[5],
                "enc": partes[11],
                "size_str": partes[15],
            }
            # parsear size (123K, 1.2M, 456B)
            s = img["size_str"]
            mult = 1
            if s.endswith("K"):
                mult = 1000
                s = s[:-1]
            elif s.endswith("M"):
                mult = 1_000_000
                s = s[:-1]
            elif s.endswith("B"):
                s = s[:-1]
            try:
                img["size"] = int(float(s) * mult)
            except Exception:
                img["size"] = 0
            resultado.append(img)
        except (ValueError, IndexError):
            continue
    return resultado


def filtrar_relevantes(imgs):
    """Filtra imágenes relevantes (ilustraciones, no fotos de página)."""
    out = []
    for img in imgs:
        if img["type"] == "smask":
            continue
        if img["size"] < MIN_BYTES or img["size"] > MAX_BYTES:
            continue
        if img["width"] > MAX_WIDTH or img["height"] > MAX_HEIGHT:
            continue  # foto de página completa
        if img["width"] < 100 or img["height"] < 100:
            continue  # demasiado pequeña
        out.append(img)
    return out


def extraer_imagen(pdf_path, num, out_path, fmt="png"):
    """Extrae una imagen específica del PDF."""
    try:
        subprocess.run(["pdfimages", f"-{fmt}", "-f", str(num), "-l", str(num),
                        str(pdf_path), str(out_path)],
                       capture_output=True, timeout=30)
        # pdfimages añade sufijo -000, -001... buscar el generado
        return True
    except Exception:
        return False


# === EJECUCIÓN ===
print("=" * 70)
print("FASE 6 — Extracción filtrada de imágenes")
print("=" * 70)

inventario = json.loads(JSON_PATH.read_text(encoding="utf-8"))

# Solo procesar PDFs (los EPUB/MOBI tienen imágenes integradas de forma distinta)
pdfs = [r for r in inventario if r["extension"] == ".pdf"
        and r.get("tipo") not in ("duplicado", "duplicado-confirmado")]
print(f"\nProcesando {len(pdfs)} PDFs únicos...\n")

total_extraidas = 0
total_descartadas = 0
resumen = []

for i, r in enumerate(pdfs, 1):
    src = LIBROS_DIR / r["archivo"]
    if not src.exists():
        continue
    slug_libro = r["slug"]
    out_dir = IMG_DIR / slug_libro
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{i:2}/{len(pdfs)}] {r['archivo'][:60]}")

    imgs = listar_imagenes(src)
    relevantes = filtrar_relevantes(imgs)
    descartadas = len(imgs) - len(relevantes)

    if relevantes:
        # Extraer todas las relevantes de una con pdfimages (formato png)
        prefix = out_dir / "img"
        try:
            # Extraer TODAS, luego filtramos por tamaño en disco
            subprocess.run(["pdfimages", "-png", str(src), str(prefix)],
                           capture_output=True, timeout=300)
            # Filtrar por tamaño en disco
            archivos_gen = sorted(out_dir.glob("img-*.png"))
            conservadas = 0
            for f in archivos_gen:
                if MIN_BYTES <= f.stat().st_size <= MAX_BYTES:
                    # Renombrar con índice
                    nuevo = out_dir / f"imagen-{conservadas+1:03d}.png"
                    if nuevo != f:
                        f.rename(nuevo)
                    conservadas += 1
                else:
                    f.unlink()
            total_extraidas += conservadas
            print(f"  ✓ {conservadas} imágenes (de {len(imgs)} totales, "
                  f"{descartadas} descartadas)")
            resumen.append((r["archivo"], conservadas, len(imgs)))
        except subprocess.TimeoutExpired:
            print(f"  ✗ Timeout")
    else:
        # Limpiar directorio vacío
        try:
            out_dir.rmdir()
        except OSError:
            pass
        print(f"  — Sin imágenes relevantes ({len(imgs)} totales descartadas)")
        total_descartadas += len(imgs)

# Limpiar carpetas vacías
for d in sorted(IMG_DIR.iterdir()):
    if d.is_dir() and not any(d.iterdir()):
        d.rmdir()

print(f"\n{'=' * 70}")
print(f"FASE 6 COMPLETADA")
print(f"{'=' * 70}")
print(f"Total imágenes extraídas: {total_extraidas}")
print(f"Total descartadas (fotos página/separadores): {total_descartadas}")
print(f"Libros con imágenes: {sum(1 for r in resumen if r[1] > 0)}")
print(f"\nTop 10 libros con más imágenes:")
for archivo, n, total in sorted(resumen, key=lambda x: -x[1])[:10]:
    print(f"  {n:4} imgs  |  {archivo[:60]}")
