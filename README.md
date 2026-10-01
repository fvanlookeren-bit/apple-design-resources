# Apple Design Resources

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Works with](https://img.shields.io/badge/works%20with-Claude%20Code-8a2be2)

Una **skill para Claude Code** que le enseña a tu IA a diseñar interfaces con los criterios de Apple,
traducidos a la web, más la lista de los **recursos oficiales de Apple** para diseñar.

La skill sale de las charlas de diseño de la WWDC (sobre todo *Designing Fluid Interfaces*, 2018) y de la
Human Interface Guidelines. Trae los números de la HIG como tokens de CSS y Tailwind, generados desde la
HIG con un script, sin valores tipeados a mano.

## Qué trae

| Archivo | Qué es |
| --- | --- |
| [`apple-design/SKILL.md`](apple-design/SKILL.md) | La skill: 20 secciones. Respuesta inmediata, arrastre 1:1, animaciones que se pueden interrumpir, resortes (damping y response, con los valores que usa Apple), traspaso de velocidad, proyección de momentum, rubber-banding, materiales y profundidad, sonido y hápticos, movimiento reducido y accesibilidad, tipografía, los ocho principios de diseño de Apple, color semántico y Liquid Glass. |
| [`apple-design/tokens/apple-hig-tokens.css`](apple-design/tokens/apple-hig-tokens.css) | 144 variables `--hig-*`: los 11 estilos de texto de iOS y los 11 de macOS (tamaño, interlineado, peso y tracking de SF), los 12 colores del sistema y los 6 grises en claro, oscuro y alto contraste, y los mínimos de texto y de controles. |
| [`apple-design/tokens/apple-hig-theme.v4.css`](apple-design/tokens/apple-hig-theme.v4.css) | Los mismos tokens para Tailwind v4: `text-hig-ios-body`, `bg-hig-gray-6`, `text-hig-red`… |
| [`apple-design/tokens/apple-hig-tailwind.v3.ts`](apple-design/tokens/apple-hig-tailwind.v3.ts) | Los mismos tokens para Tailwind v3. |
| [`apple-design/tokens/build-tokens.py`](apple-design/tokens/build-tokens.py) | El script que lee las tablas de la HIG y genera los tres archivos. |

## Instalar

```bash
git clone https://github.com/fvanlookeren-bit/apple-design-resources.git
mkdir -p ~/.claude/skills
cp -R apple-design-resources/apple-design ~/.claude/skills/
```

Claude Code la carga sola cuando trabajas en una interfaz, o la llamas con `/apple-design`.

## Usar los tokens

```css
@import "./apple-hig-tokens.css";

.titulo {
  font: var(--hig-ios-title-1-weight) var(--hig-ios-title-1-size) / var(--hig-ios-title-1-leading) var(--hig-font-system);
  letter-spacing: var(--hig-ios-title-1-tracking);
}
.boton { min-height: var(--hig-ios-control-default); background: rgb(var(--hig-blue)); }
```

Los colores van como canales RGB para poder usarlos con transparencia: `rgb(var(--hig-red) / .5)`. El modo
oscuro responde a `:root[data-theme="dark"]`, `.dark` y `.theme-dark`, y el alto contraste a
`@media (prefers-contrast: more)`. Son opcionales: no tocan nada hasta que los usas.

El tracking es el de SF Pro: vale cuando la fuente es la del sistema (`system-ui` en un dispositivo Apple),
no con Inter, Geist u otra fuente.

## Actualizar desde la HIG

El repo no trae el texto de la HIG (es contenido de Apple): el script lo baja de las páginas oficiales.

```bash
cd apple-design/tokens/source
for p in typography color accessibility materials; do
  curl -s "https://developer.apple.com/tutorials/data/design/human-interface-guidelines/$p.json" -o $p.json
done
cd ..
python3 build-tokens.py > apple-hig-tokens.css
python3 build-tokens.py tailwind-v4 > apple-hig-theme.v4.css
python3 build-tokens.py tailwind-v3 > apple-hig-tailwind.v3.ts
```

## Recursos oficiales de Apple

Revisados el 1 de octubre de 2026.

**Guías**
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/): las reglas de diseño de todas las plataformas de Apple.
- [Apple Design](https://developer.apple.com/design/): la portada de diseño para desarrolladores.

**[Apple Design Resources](https://developer.apple.com/design/resources/)**
- **Kits de interfaz:** iOS 27 y iPadOS 27, macOS 27, watchOS 26 y visionOS 26 en Figma y Sketch; tvOS 18 en Sketch.
- **Plantilla de íconos de app:** Figma, Sketch, Photoshop e Illustrator.
- **Fuentes:** SF Pro, SF Compact, SF Mono, New York, SF Arabic, SF Armenian, SF Georgian y SF Hebrew.
- **SF Symbols 27:** más de 7.000 símbolos en nueve pesos y tres escalas.
- **Icon Composer:** íconos por capas con Liquid Glass para iPhone, iPad, Mac y Apple Watch.
- **Marcos de dispositivos:** iPhone 16, 17 y 18, iPhone Duo, iPad, MacBook Air y Pro M5, iMac, Studio Display, Apple Watch y Apple TV.
- **Plantillas de tecnologías:** Apple Pay, Sign in with Apple, Live Activities, Wallet, TipKit, App Clips y más.

Las fuentes y los marcos de dispositivos tienen su propia licencia: léela antes de usarlos. Por ejemplo, SF
no se puede servir como fuente web (ver §15 de la skill).

**Charlas de la WWDC en las que se basa la skill**
- [Designing Fluid Interfaces](https://developer.apple.com/videos/play/wwdc2018/803/) (2018)
- [Designing Audio-Haptic Experiences](https://developer.apple.com/videos/play/wwdc2019/810/) (2019)
- [The details of UI typography](https://developer.apple.com/videos/play/wwdc2020/10175/) (2020)
- [Get to know the new design system](https://developer.apple.com/videos/play/wwdc2025/356/) (2025)
- [Meet Liquid Glass](https://developer.apple.com/videos/play/wwdc2025/219/) (2025)
- [Design foundations from idea to interface](https://developer.apple.com/videos/play/wwdc2025/359/) (2025)
- [Principles of great design](https://developer.apple.com/videos/play/wwdc2026/250/) (2026)
- [Discover the Apple Design Resources](https://developer.apple.com/videos/play/tech-talks/111427/) (tech talk)

## Licencia

El código y el texto de este repo van con licencia [MIT](LICENSE). No es un proyecto de Apple ni está
afiliado a Apple; Apple, SF Pro, SF Symbols, Liquid Glass y los nombres de sus productos son marcas de
Apple Inc.

Hecho por Francisco Van Lookeren · [vanlookstudio.com](https://vanlookstudio.com)
