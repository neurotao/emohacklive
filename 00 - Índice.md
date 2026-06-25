---
tipo: moc
titulo: "Índice — Bóveda de Budismo"
estado: "completo"
tags: [moc, indice]
---

# 🪷 Bóveda de Budismo — Índice maestro

> Base de conocimiento personal sobre budismo, organizada por **libros**, **conceptos** y **autores**. Los conceptos unifican perspectivas entre tradiciones (Kadampa, Madhyamaka, Zen, neurociencia).

---

## 📊 Estado del proyecto

| Métrica | Valor |
|---------|-------|
| Libros procesados | `$= dv.pages('"01 - Libros"').where(p => !p.estado?.includes("duplicado") && !p.estado?.includes("edicion")).length` |
| Notas enriquecidas | `$= dv.pages('"01 - Libros"').where(p => p.estado == "enriquecido" || p.estado == "completo" || p.estado == "revisado").length` |
| Conceptos | `= dv.pages('"02 - Conceptos"').length` |
| Autores | `= dv.pages('"03 - Autores"').length` |
| Archivos de citas | `= dv.pages('"04 - Citas"').length` |

---

## 📚 Libros por tradición

### Kadampa — Lamrim, Sutra + Tantra unificados

```dataview
TABLE WITHOUT ID file.link AS "Libro", nivel AS "Nivel", estado AS "Nota", estado_lectura AS "📖"
FROM "01 - Libros"
WHERE tradicion = "Kadampa" AND !contains(estado, "duplicado") AND !contains(estado, "edicion")
SORT nivel ASC, file.name ASC
```

### Madhyamaka — Vacuidad y camino medio

```dataview
TABLE WITHOUT ID file.link AS "Libro", nivel AS "Nivel", estado AS "Nota", estado_lectura AS "📖"
FROM "01 - Libros"
WHERE tradicion = "Madhyamaka" AND !contains(estado, "duplicado") AND !contains(estado, "edicion")
SORT nivel ASC, file.name ASC
```

### Mahayana (general)

```dataview
TABLE WITHOUT ID file.link AS "Libro", nivel AS "Nivel", estado AS "Nota", estado_lectura AS "📖"
FROM "01 - Libros"
WHERE tradicion = "Mahayana" AND !contains(estado, "duplicado") AND !contains(estado, "edicion")
SORT nivel ASC, file.name ASC
```

### Vajrayana — Tantra y prácticas avanzadas

```dataview
TABLE WITHOUT ID file.link AS "Libro", nivel AS "Nivel", estado AS "Nota", estado_lectura AS "📖"
FROM "01 - Libros"
WHERE tradicion = "Vajrayana" AND !contains(estado, "duplicado") AND !contains(estado, "edicion")
SORT nivel ASC, file.name ASC
```

### Zen / Chan

```dataview
TABLE WITHOUT ID file.link AS "Libro", nivel AS "Nivel", estado AS "Nota", estado_lectura AS "📖"
FROM "01 - Libros"
WHERE tradicion = "Zen" AND !contains(estado, "duplicado")
SORT file.name ASC
```

### Tierra Pura

```dataview
TABLE WITHOUT ID file.link AS "Libro", nivel AS "Nivel", estado AS "Nota", estado_lectura AS "📖"
FROM "01 - Libros"
WHERE tradicion = "Tierra Pura" AND !contains(estado, "duplicado")
SORT file.name ASC
```

### Académica — Estudios críticos

```dataview
TABLE WITHOUT ID file.link AS "Libro", nivel AS "Nivel", estado AS "Nota", estado_lectura AS "📖"
FROM "01 - Libros"
WHERE tradicion = "Académica" AND !contains(estado, "duplicado") AND !contains(estado, "edicion")
SORT file.name ASC
```

### Secular — Espiritualidad y divulgación

```dataview
TABLE WITHOUT ID file.link AS "Libro", nivel AS "Nivel", estado AS "Nota", estado_lectura AS "📖"
FROM "01 - Libros"
WHERE tradicion = "Secular" AND !contains(estado, "duplicado")
SORT file.name ASC
```

---

## 🧠 Conceptos unificados

```dataview
TABLE WITHOUT ID file.link AS "Concepto", length(file.outlinks) AS "Conexiones"
FROM "02 - Conceptos"
SORT length(file.outlinks) DESC
```

---

## ✍️ Autores

```dataview
TABLE WITHOUT ID file.link AS "Autor"
FROM "03 - Autores"
SORT file.name ASC
```

---

## 💬 Citas destacadas

| Tema | Archivo |
|------|---------|
| 🕳️ Vacuidad y Sabiduría | [[Citas — Vacuidad y Sabiduría]] |
| ❤️ Compasión y Bodhichitta | [[Citas — Compasión y Bodhichitta]] |
| 🧠 Mente y Meditación | [[Citas — Mente y Meditación]] |
| 😣 Sufrimiento y Renuncia | [[Citas — Sufrimiento y Renuncia]] |
| 🔥 Tantra y Práctica Avanzada | [[Citas — Tantra y Práctica Avanzada]] |
| ⏳ Impermanencia y Muerte | [[Citas — Impermanencia y Muerte]] |

---

## 🗺️ Caminos de lectura

### 🔰 Principiante
1. [[dharma-hoy-budismo-fresquito-para-calmar-la-sed-badillo-salv|Dharma hoy]] — introducción accesible
2. [[como-solucionar-nuestros-problemas-humanos|Cómo solucionar nuestros problemas humanos]]
3. [[ocho-pasos-hacia-la-felicidad-el-modo-budista-de-amar|Ocho pasos hacia la felicidad]]

### 📖 Profundizar Kadampa
1. [[como-solucionar-nuestros-problemas-humanos|Cómo solucionar nuestros problemas humanos]]
2. [[el-camino-gozoso-de-buena-fortuna-gueshe-kelsang-gyatso-2016|El camino gozoso de buena fortuna]] (Lamrim completo)
3. [[guia-de-las-obras-del-bodhisatva|Guía del Bodhisatva]] (sobre Shantideva)
4. [[how-to-understand-the-mind-the-nature-and-power-of-the-gyats|How to understand the mind]]

### 🌀 Filosofía Madhyamaka (vacuidad)
1. [[corazon-de-la-sabiduria-un-comentario-al-sutra-del-corazon|Corazón de la sabiduría]] (introducción)
2. [[entering-the-middle-way-madhyamakavatara-candrakirti-thupten|Entering the Middle Way]] (Chandrakirti, Jinpa)
3. [[introduction-to-the-middle-way-chandrakirti-s-jamgon-mipham|Introduction to the Middle Way]] (comentario Mipham)

### 🔬 Puente neurociencia
1. [[el-cerebro-de-buda-la-neurociencia-de-la-felicidad-el-hanson|El cerebro de Buda]]
2. Cruzar con [[Mente]] y [[Meditación]]

### 🔥 Tantra / Mahamudra
1. Cubrir Lamrim completo primero (requisito)
2. [[tantric-grounds-and-paths-how-to-enter-progress-on-and-geshe-kelsang-g|Tantric Grounds and Paths]]
3. [[clear-light-of-bliss-mahamudra-in-vajrayana-buddhism-a-kelsang-gyatso-|Clear Light of Bliss]]
4. [[the-oral-instructions-of-mahumudra-the-very-essence-of-geshe|Oral Instructions of Mahamudra]]

---

## 🔗 Estructura de la bóveda

```
budismo/
├── 00 - Índice.md           ← este MOC (tablas dinámicas con Dataview)
├── 00 - Dashboard.md        ← panel de lectura
├── 01 - Libros/             ← una nota por libro
├── 02 - Conceptos/          ← conceptos transversales unificados
├── 03 - Autores/            ← notas por autor
├── 04 - Citas/              ← citas destacadas por tema
├── 05 - Imágenes/           ← portadas e imágenes
├── 05 - Caminos de estudio.canvas  ← mapa visual de lectura
├── _fuentes/                ← PDFs/EPUB/MOBI originales
└── _data/                   ← datos, scripts y texto extraído
```

---
*Índice dinámico con Dataview — las tablas se generan automáticamente del frontmatter.*
