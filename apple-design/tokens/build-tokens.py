#!/usr/bin/env python3
"""Genera apple-hig-tokens.css a partir de las páginas de la HIG guardadas en source/.

Cada valor del CSS sale de una tabla de la HIG (no se tipea a mano). Para refrescar:

    cd ~/.claude/skills/apple-design/tokens/source
    for p in typography color accessibility materials; do
      curl -s "https://developer.apple.com/tutorials/data/design/human-interface-guidelines/$p.json" -o $p.json
    done
    python3 ../build-tokens.py > ../apple-hig-tokens.css

y copiar el CSS resultante, idéntico, a los repos que lo usan (ver SKILL.md §18).
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

SRC = Path(__file__).parent / "source"


def load(name):
    return json.loads((SRC / f"{name}.json").read_text())


def cell_text(cell, refs):
    out = []
    for blk in cell:
        for it in blk.get("inlineContent", []) if blk.get("type") == "paragraph" else []:
            t = it.get("type")
            if t == "text":
                out.append(it["text"])
            elif t == "codeVoice":
                out.append(it["code"])
            elif t == "image":
                out.append(refs.get(it["identifier"], {}).get("alt", ""))
            elif t == "reference":
                out.append(refs.get(it["identifier"], {}).get("title", ""))
    return " ".join(out).strip()


def tables(doc):
    """Devuelve [(contexto, filas)] donde contexto es la ruta de encabezados/pestañas."""
    refs = doc.get("references", {})
    found = []

    def walk(blocks, path):
        heading = list(path)
        for b in blocks:
            t = b.get("type")
            if t == "heading":
                level = b.get("level", 2)
                heading = [h for h in heading if h[0] < level] + [(level, b.get("text", ""))]
            elif t == "table":
                rows = [[cell_text(c, refs) for c in row] for row in b.get("rows", [])]
                found.append(([h[1] for h in heading], rows))
            elif t == "tabNavigator":
                for tab in b.get("tabs", []):
                    walk(tab.get("content", []), heading + [(99, tab.get("title", ""))])
            elif "content" in b and isinstance(b["content"], list):
                walk(b["content"], heading)

    for s in doc.get("primaryContentSections", []):
        walk(s.get("content", []), [])
    return found


def find(tabs, *needles, last=None):
    for ctx, rows in tabs:
        joined = " / ".join(ctx)
        if all(n in joined for n in needles) and (last is None or (ctx and ctx[-1] == last)):
            return rows
    raise SystemExit(f"tabla no encontrada: {needles}")


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


WEIGHT = {"Ultralight": 100, "Thin": 200, "Light": 300, "Regular": 400, "Medium": 500,
          "Semibold": 600, "Bold": 700, "Heavy": 800, "Black": 900}


def main():
    typo = tables(load("typography"))
    color = tables(load("color"))
    access = tables(load("accessibility"))

    ios = find(typo, "iOS, iPadOS Dynamic Type sizes", "Large (default)")
    mac = find(typo, "macOS built-in text styles")
    # Primera tabla de SF Pro bajo "Tracking values": la de iOS, iPadOS y visionOS.
    tracking_rows = find(typo, "Tracking values", last="SF Pro")
    def tracking_table(rows):
        return {int(size): int(per_mille.replace("+", ""))
                for size, per_mille, _pts in rows[1:] if size.isdigit()}

    tracking = tracking_table(tracking_rows)
    tracking_mac = tracking_table(find(typo, "Tracking values", last="macOS tracking values"))
    minimums = find(typo, "Ensuring legibility")
    controls = contrast = None
    for ctx, rows in access:
        if rows and rows[0][:3] == ["Platform", "Default control size", "Minimum control size"]:
            controls = rows
        if rows and rows[0][:3] == ["Text size", "Text weight", "Minimum contrast ratio"]:
            contrast = rows
    if controls is None or contrast is None:
        raise SystemExit("tablas de accesibilidad no encontradas")
    sys_colors = find(color, "Specifications", "System colors")
    grays = find(color, "system gray colors")

    def rgb(s):
        m = re.match(r"R-(\d+),G-(\d+),B-(\d+)", s)
        if not m:
            raise SystemExit(f"color sin RGB: {s!r}")
        return " ".join(m.groups())

    out = []
    w = out.append
    w("/* ==========================================================================")
    w("   Apple HIG tokens — generado por ~/.claude/skills/apple-design/tokens/build-tokens.py")
    w(f"   Fuente: Human Interface Guidelines (developer.apple.com/design/human-interface-guidelines),")
    w(f"   páginas typography, color y accessibility, leídas el {date.today().isoformat()}.")
    w("   NO editar a mano: regenerar con el script y copiar el archivo idéntico a cada repo.")
    w("")
    w("   Convenciones:")
    w("   - 1 pt de la HIG = 1 px CSS (decisión nuestra; es la equivalencia de iOS a 1x).")
    w("   - Los colores van como canales RGB (\"255 56 60\") para usarlos con alfa:")
    w("     rgb(var(--hig-red)) o rgb(var(--hig-red) / 0.5). Sirve en Tailwind v3 y v4.")
    w("   - La HIG pide no fijar los valores de color en apps nativas (cambian entre versiones);")
    w("     en la web no hay API del sistema, así que se fijan y se regeneran con el script.")
    w("   - Tracking: tablas de SF Pro (iOS y macOS). Aplican cuando la fuente es la del sistema")
    w("     (system-ui en un dispositivo Apple). Con Inter, Geist u otra fuente no es válido.")
    w("   - Los tokens son opt-in: nada del sistema de diseño existente los usa por defecto.")
    w("   ========================================================================== */")
    w("")
    w(":root {")
    w("  /* Familias: la del sistema es SF en Apple, sin servir el archivo (la licencia de SF")
    w("     prohíbe embeberla). Fuera de Apple cae a la fuente del sistema de cada plataforma. */")
    w('  --hig-font-system: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;')
    w('  --hig-font-rounded: ui-rounded, system-ui, -apple-system, sans-serif;')
    w('  --hig-font-serif: ui-serif, "New York", Georgia, "Times New Roman", serif;')
    w('  --hig-font-mono: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, monospace;')
    w("")
    w("  /* Tamaño por defecto y mínimo de texto (HIG › Typography › Ensuring legibility). */")
    for platform, default, minimum in minimums[1:]:
        p = slug(platform.split(",")[0])
        if p in ("ios", "macos"):
            w(f"  --hig-{p}-text-default: {default.split()[0]}px;")
            w(f"  --hig-{p}-text-min: {minimum.split()[0]}px;")
    w("")
    w("  /* Estilos de texto de iOS/iPadOS, tamaño Large (el de fábrica).")
    w("     HIG › Typography › Specifications › iOS, iPadOS Dynamic Type sizes. */")
    for style, weight, size, leading, emph in ios[1:]:
        s = slug(style)
        size_i = int(size)
        w(f"  --hig-ios-{s}-size: {size_i}px;")
        w(f"  --hig-ios-{s}-leading: {int(leading)}px;")
        w(f"  --hig-ios-{s}-weight: {WEIGHT[weight]};")
        w(f"  --hig-ios-{s}-weight-emphasized: {WEIGHT[emph]};")
        w(f"  --hig-ios-{s}-tracking: {tracking[size_i] / 1000:g}em;")
    w("")
    w("  /* Estilos de texto de macOS (no tiene Dynamic Type): la escala para UI densa de escritorio.")
    w("     HIG › Typography › Specifications › macOS built-in text styles. */")
    for style, weight, size, leading, emph in mac[1:]:
        s = slug(style)
        size_i = int(size)
        w(f"  --hig-macos-{s}-size: {size_i}px;")
        w(f"  --hig-macos-{s}-leading: {int(leading)}px;")
        w(f"  --hig-macos-{s}-weight: {WEIGHT[weight]};")
        w(f"  --hig-macos-{s}-weight-emphasized: {WEIGHT[emph]};")
        w(f"  --hig-macos-{s}-tracking: {tracking_mac[size_i] / 1000:g}em;")
    w("")
    w("  /* Tamaño de controles (HIG › Accessibility › Offer sufficiently sized controls). */")
    for platform, default, minimum in controls[1:]:
        p = slug(platform.split(",")[0])
        if p in ("ios", "macos"):
            w(f"  --hig-{p}-control-default: {default.split('x')[0]}px;")
            w(f"  --hig-{p}-control-min: {minimum.split('x')[0]}px;")
    w("  /* Separación alrededor de un control (misma sección de la HIG): ~12 pt si tiene")
    w("     borde o fondo, ~24 pt si no lo tiene. */")
    w("  --hig-control-padding-bezeled: 12px;")
    w("  --hig-control-padding-plain: 24px;")
    w("")
    w("  /* Contraste mínimo de texto (HIG › Accessibility), como referencia para auditar:")
    for size, weight, ratio in contrast[1:]:
        w(f"     - {size} · {weight}: {ratio}")
    w("     Para colores propios, la HIG (Dark Mode) recomienda apuntar a 7:1 en texto chico. */")
    w("")
    w("  /* Liquid Glass claro sobre contenido brillante: capa oscura del 35 % detrás del control")
    w("     (HIG › Materials › Liquid Glass). */")
    w("  --hig-glass-clear-dim: 0 0 0;")
    w("  --hig-glass-clear-dim-alpha: 0.35;")
    w("}")
    w("")

    modes = [
        ("Colores del sistema, apariencia clara (HIG › Color › Specifications).", ":root", 2),
        ("Apariencia oscura. Cubre las tres formas de modo oscuro de nuestros repos.",
         ':root[data-theme="dark"], .dark, .theme-dark', 3),
    ]
    hc_modes = [
        ("Aumentar contraste (claro).", ":root", 4),
        ("Aumentar contraste (oscuro).", ':root[data-theme="dark"], .dark, .theme-dark', 5),
    ]

    def color_block(comment, selector, col, indent=""):
        w(f"{indent}/* {comment} */")
        w(f"{indent}{selector} {{")
        for row in sys_colors[1:]:
            w(f"{indent}  --hig-{slug(row[0])}: {rgb(row[col])};")
        for row in grays[1:]:
            name = slug(row[0].replace("(", "").replace(")", ""))
            w(f"{indent}  --hig-{name}: {rgb(row[col])};")
        w(f"{indent}}}")

    styles = [("ios", slug(r[0])) for r in ios[1:]] + [("macos", slug(r[0])) for r in mac[1:]]
    color_names = [slug(r[0]) for r in sys_colors[1:]] + \
        [slug(r[0].replace("(", "").replace(")", "")) for r in grays[1:]]
    mode = sys.argv[1] if len(sys.argv) > 1 else "css"
    if mode == "tailwind-v4":
        print(tailwind_v4(styles, color_names))
        return
    if mode == "tailwind-v3":
        print(tailwind_v3(styles, color_names))
        return

    for comment, selector, col in modes:
        color_block(comment, selector, col)
        w("")
    w("@media (prefers-contrast: more) {")
    for comment, selector, col in hc_modes:
        color_block(comment, selector, col, indent="  ")
    w("}")
    print("\n".join(out))


HEADER = ("Generado por ~/.claude/skills/apple-design/tokens/build-tokens.py a partir de la HIG. "
          "Requiere apple-hig-tokens.css cargado antes. No editar a mano.")


def tailwind_v4(styles, colors):
    out = [f"/* {HEADER} */", "@theme inline {"]
    out.append("  --font-hig-system: var(--hig-font-system);")
    out.append("  --font-hig-rounded: var(--hig-font-rounded);")
    out.append("  --font-hig-serif: var(--hig-font-serif);")
    out.append("  --font-hig-mono: var(--hig-font-mono);")
    for platform, s in styles:
        base = f"--hig-{platform}-{s}"
        name = f"--text-hig-{platform}-{s}"
        out.append(f"  {name}: var({base}-size);")
        out.append(f"  {name}--line-height: var({base}-leading);")
        out.append(f"  {name}--letter-spacing: var({base}-tracking);")
        out.append(f"  {name}--font-weight: var({base}-weight);")
    for c in colors:
        out.append(f"  --color-hig-{c}: rgb(var(--hig-{c}));")
    out.append("}")
    return "\n".join(out)


def tailwind_v3(styles, colors):
    out = [f"// {HEADER}", "// Uso: en tailwind.config, theme.extend.fontSize/colors/fontFamily."]
    out.append("export const higFontFamily = {")
    for f in ("system", "rounded", "serif", "mono"):
        out.append(f"  'hig-{f}': 'var(--hig-font-{f})',")
    out.append("};")
    out.append("")
    out.append("export const higFontSize = {")
    for platform, s in styles:
        base = f"--hig-{platform}-{s}"
        out.append(f"  'hig-{platform}-{s}': ['var({base}-size)', {{ lineHeight: 'var({base}-leading)', "
                   f"letterSpacing: 'var({base}-tracking)', fontWeight: 'var({base}-weight)' }}],")
    out.append("};")
    out.append("")
    out.append("export const higColors = {")
    for c in colors:
        out.append(f"  'hig-{c}': 'rgb(var(--hig-{c}) / <alpha-value>)',")
    out.append("};")
    return "\n".join(out)


if __name__ == "__main__":
    main()
