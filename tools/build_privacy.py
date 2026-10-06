"""Convierte la politica de privacidad de Markdown a HTML y la mete en su pagina.

El texto vive en `content/privacidad.es.md` y `content/privacy.en.md`. Este script lo
convierte a HTML semantico (titulos con ancla, listas, tablas, enlaces) y lo escribe entre
los marcadores de cada pagina:

    <!-- PRIVACIDAD:VERSION --> ... <!-- /PRIVACIDAD:VERSION -->   la linea de version y fecha
    <!-- PRIVACIDAD:INICIO -->  ...  <!-- PRIVACIDAD:FIN -->        el indice y el cuerpo
    (y PRIVACY:VERSION, PRIVACY:START / PRIVACY:END en ingles)

Todo lo de fuera de los marcadores (cabecera, pie, aviso de como apagar el envio) no se toca.
Para cambiar el texto: edita el .md y corre `python tools/build_privacy.py`. Tambien se puede
editar a mano el HTML entre los marcadores, si no se va a regenerar.

Solo entiende el Markdown que usa la politica: `#` y `###`, parrafos, listas con `-`, tablas,
**negrita**, *cursiva*, `codigo` y URLs sueltas.
"""
from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = [
    (ROOT / "content" / "privacidad.es.md", ROOT / "privacidad" / "index.html",
     "PRIVACIDAD", "INICIO", "FIN", "En esta página"),
    (ROOT / "content" / "privacy.en.md", ROOT / "en" / "privacy" / "index.html",
     "PRIVACY", "START", "END", "On this page"),
]

def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "seccion"


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", out)

    def link(m: re.Match) -> str:
        url = m.group(0)
        trail = ""
        while url and url[-1] in ".,;:)":
            trail = url[-1] + trail
            url = url[:-1]
        return f'<a href="{url}" rel="noopener">{url}</a>{trail}'

    out = re.sub(r"https?://[^\s<]+", link, out)
    return out


def table(rows: list[str]) -> str:
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    head, body = cells[0], cells[2:]
    th = "".join(f'<th scope="col">{inline(c)}</th>' for c in head)
    trs = []
    for r in body:
        tds = "".join(f'<td data-label="{html.escape(head[i])}">{inline(c)}</td>'
                      for i, c in enumerate(r))
        trs.append(f"<tr>{tds}</tr>")
    return (f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead>'
            f"<tbody>{''.join(trs)}</tbody></table></div>")


def convert(md: str) -> tuple[str, str, str, list[tuple[str, str]]]:
    lines = md.splitlines()
    title, version, blocks, toc = "", "", [], []
    i = 0
    para: list[str] = []

    def flush() -> None:
        if para:
            blocks.append(f"<p>{inline(' '.join(s.strip() for s in para))}</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        if line.startswith("# "):
            flush()
            title = line[2:].strip()
        elif line.startswith("### ") or line.startswith("## "):
            flush()
            text = line.lstrip("#").strip()
            anchor = slug(text)
            toc.append((anchor, text))
            blocks.append(f'<h2 id="{anchor}">{inline(text)}</h2>')
        elif line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            blocks.append(table(rows))
            continue
        elif re.match(r"^\s*- ", line):
            flush()
            items = []
            while i < len(lines) and (re.match(r"^\s*- ", lines[i]) or
                                      (lines[i].startswith("  ") and lines[i].strip())):
                if re.match(r"^\s*- ", lines[i]):
                    items.append(re.sub(r"^\s*- ", "", lines[i]))
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            blocks.append("<ul>" + "".join(f"<li>{inline(t)}</li>" for t in items) + "</ul>")
            continue
        elif not line.strip():
            flush()
        elif not version and re.match(r"^\*\*.+\*\*$", line.strip()) and not blocks:
            version = line.strip().strip("*")
        else:
            para.append(line)
        i += 1
    flush()
    return title, version, "\n".join(blocks), toc


def replace_between(text: str, start: str, end: str, block: str, page: Path) -> str:
    pattern = re.compile(rf"<!-- {re.escape(start)} -->.*?<!-- {re.escape(end)} -->", re.S)
    if not pattern.search(text):
        raise SystemExit(f"{page}: no encuentro los marcadores {start} / {end}")
    return pattern.sub(lambda _: f"<!-- {start} -->{block}<!-- {end} -->", text)


def main() -> None:
    for md_path, page, key, start, end, toc_label in PAGES:
        _title, version, body, toc = convert(md_path.read_text(encoding="utf-8"))
        toc_html = "".join(f'<li><a href="#{a}">{inline(t)}</a></li>' for a, t in toc)
        block = (
            '\n<nav class="toc panel" aria-labelledby="toc-titulo"><h2 id="toc-titulo">'
            f"{toc_label}</h2><ol>{toc_html}</ol></nav>\n{body}\n"
        )
        text = page.read_text(encoding="utf-8")
        text = replace_between(text, f"{key}:VERSION", f"/{key}:VERSION", inline(version), page)
        text = replace_between(text, f"{key}:{start}", f"{key}:{end}", block, page)
        page.write_text(text, encoding="utf-8")
        print(f"ok {page.relative_to(ROOT)}  ({len(toc)} secciones)")


if __name__ == "__main__":
    main()
