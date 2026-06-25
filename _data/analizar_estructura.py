#!/usr/bin/env python3
"""Analiza la estructura de un libro extraído para preparar el spike.

Detecta:
  - Tabla de contenidos / índice
  - Capítulos (patrones: Capítulo, Chapter, números)
  - Líneas iniciales de cada capítulo (para muestreo)
"""
import re
import sys
from pathlib import Path

TEXTO = Path("/Users/maclleida/budismo/_data/texto_extraido/"
             "como-solucionar-nuestros-problemas-humanos.txt")

texto = TEXTO.read_text(encoding="utf-8")
lineas = texto.split("\n")
total = len(lineas)

print(f"=== ARCHIVO: {TEXTO.name} ===")
print(f"Total líneas: {total}")
print(f"Total caracteres: {len(texto):,}")
print(f"Palabras aprox: {len(texto.split()):,}")

# Buscar índice / tabla de contenidos
print(f"\n{'='*60}\n=== DETECCIÓN DE ÍNDICE / TOC ===")
patrones_toc = re.compile(
    r"(índice|indice|table of contents|contents|contenido)",
    re.IGNORECASE)
toc_start = None
for i, l in enumerate(lineas):
    if patrones_toc.search(l) and len(l) < 60:
        toc_start = i
        print(f"Línea {i}: {l}")
        break

if toc_start:
    print("\n--- 40 líneas desde el índice ---")
    for i in range(toc_start, min(toc_start + 40, total)):
        if lineas[i].strip():
            print(f"{i:5}: {lineas[i][:80]}")

# Buscar capítulos
print(f"\n{'='*60}\n=== DETECCIÓN DE CAPÍTULOS ===")
pat_capitulo = re.compile(
    r"^\s*(cap[ií]tulo|chapter|parte|part)\s+([0-9ivxlcdm]+)",
    re.IGNORECASE)
caps = []
for i, l in enumerate(lineas):
    m = pat_capitulo.match(l)
    if m and len(l) < 80:
        caps.append((i, l.strip()))

print(f"Capítulos detectados: {len(caps)}")
for i, (ln, txt) in enumerate(caps[:30]):
    print(f"  línea {ln:5}: {txt[:70]}")

# Primeras líneas (portada/prólogo)
print(f"\n{'='*60}\n=== PRIMERAS 60 LÍNEAS NO VACÍAS ===")
mostradas = 0
for i, l in enumerate(lineas):
    if l.strip() and len(l.strip()) > 3:
        print(f"{i:5}: {l[:90]}")
        mostradas += 1
        if mostradas >= 60:
            break

# Últimas líneas (conclusión)
print(f"\n{'='*60}\n=== ÚLTIMAS 40 LÍNEAS NO VACÍAS ===")
cola = []
for i in range(total - 1, -1, -1):
    if lineas[i].strip() and len(lineas[i].strip()) > 3:
        cola.append((i, lineas[i]))
        if len(cola) >= 40:
            break
for i, l in reversed(cola):
    print(f"{i:5}: {l[:90]}")
