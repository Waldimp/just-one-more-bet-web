"""Comprueba que no haya enlaces internos rotos.

Recorre todas las paginas .html y el CSS, y verifica que cada ruta interna exista en disco
(con las reglas de `cleanUrls` de Vercel: `/privacidad` sirve `privacidad/index.html`) y que
cada ancla `#id` exista en su pagina. Los marcadores pendientes (`#ITCH_URL`) y los videos del
trailer cuando todavia no estaban, se listaban aparte como avisos (`PENDING_FILES`).

Uso: python tools/check_links.py   (sale con 1 si hay algo roto)
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
PENDING = {"#ITCH_URL"}
# Archivos que llegan despues del resto del sitio. Vacio desde que estan los trailers.
PENDING_FILES: set[str] = set()
ATTRS = {"href", "src", "poster", "data-full", "data-shot"}  # <source src> incluido


class Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value is None:
                continue
            if name == "id":
                self.ids.add(value)
            elif name in ATTRS:
                self.refs.append(value)
            elif name == "srcset":
                self.refs += [part.strip().split(" ")[0] for part in value.split(",")]


def resolve(path: str) -> Path | None:
    p = ROOT / path.lstrip("/")
    candidates = [p, p / "index.html", p.with_suffix(".html")] if path != "/" else [ROOT / "index.html"]
    for c in candidates:
        if c.is_file():
            return c
    return None


def main() -> int:
    errors, warnings = [], []
    pages = {}
    for html in sorted(ROOT.rglob("*.html")):
        if "node_modules" in html.parts or "tools" in html.parts:
            continue
        c = Collector()
        c.feed(html.read_text(encoding="utf-8"))
        pages[html] = c
    for html, c in pages.items():
        rel = html.relative_to(ROOT)
        for ref in c.refs:
            if ref in PENDING:
                warnings.append(f"{rel}: marcador pendiente {ref}")
                continue
            u = urlparse(ref)
            if u.scheme in ("http", "https", "mailto", "data"):
                continue
            if ref.startswith("#"):
                if ref[1:] and ref[1:] not in c.ids:
                    errors.append(f"{rel}: ancla rota {ref}")
                continue
            if u.path in PENDING_FILES:
                warnings.append(f"{rel}: video pendiente {u.path}")
                continue
            target = resolve(u.path)
            if target is None:
                errors.append(f"{rel}: no existe {ref}")
            elif u.fragment and target in pages and u.fragment not in pages[target].ids:
                errors.append(f"{rel}: ancla rota {ref}")
    css = (ROOT / "assets/css/site.css").read_text(encoding="utf-8")
    for ref in re.findall(r'url\("?(/[^")]+)"?\)', css):
        if resolve(ref) is None:
            errors.append(f"site.css: no existe {ref}")
    for w in sorted(set(warnings)):
        print("aviso:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"{len(pages)} paginas, {sum(len(c.refs) for c in pages.values())} referencias, "
          f"{len(errors)} rotas")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
