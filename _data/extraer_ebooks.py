#!/usr/bin/env python3
"""Extrae texto de EPUB/MOBI sin calibre.

EPUB = ZIP con archivos XHTML. Strip tags simple.
MOBI: si hay kindleunpack lo usa, sino lo marca pendiente.
"""
import zipfile
import re
import sys
from pathlib import Path
from html.parser import HTMLParser

LIBROS = Path("/Users/maclleida/budismo/_fuentes")
OUT = Path("/Users/maclleida/budismo/_data/texto_extraido")


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip = True
        if tag in ("p", "div", "br", "h1", "h2", "h3", "li", "tr"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = False
        if tag in ("p", "div", "h1", "h2", "h3"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def epub_to_text(path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist()
                 if n.lower().endswith((".xhtml", ".html", ".htm"))]
        names.sort()
        chunks = []
        for n in names:
            try:
                raw = z.read(n).decode("utf-8", errors="ignore")
                p = TextExtractor()
                p.feed(raw)
                chunks.append("".join(p.parts))
            except Exception:
                pass
    text = "\n\n".join(chunks)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def slug(texto):
    import unicodedata
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-")
    return texto.lower()[:70]


for f in sorted(LIBROS.iterdir()):
    ext = f.suffix.lower()
    if ext == ".epub":
        print(f"EPUB: {f.name[:60]}")
        try:
            text = epub_to_text(f)
            slug_name = slug(f.stem)
            out = OUT / f"{slug_name}.txt"
            out.write_text(text, encoding="utf-8")
            print(f"  → {len(text):,} chars → {out.name}")
        except Exception as e:
            print(f"  ✗ {e}")
    elif ext == ".mobi":
        print(f"MOBI: {f.name[:60]} (requiere kindleunpack o calibre GUI)")
        print("  → marcado como pendiente")
