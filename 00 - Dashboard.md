---
tipo: dashboard
titulo: "Dashboard de Lectura"
tags: [dashboard, lectura]
---

# 📊 Dashboard de Lectura

> Panel de control para tu estudio personal. Las tablas se actualizan solas desde el frontmatter de cada libro. Para cambiar el estado de lectura, editá el campo `estado_lectura` en la nota del libro (`pendiente` → `leyendo` → `completado`).

---

## 📈 Resumen

| Métrica | Total |
|---------|-------|
| 🔄 Leyendo ahora | `$= dv.pages('"01 - Libros"').where(p => p.estado_lectura == "leyendo").length` |
| ⬜ Pendientes | `$= dv.pages('"01 - Libros"').where(p => p.estado_lectura == "pendiente").length` |
| ✅ Completados | `$= dv.pages('"01 - Libros"').where(p => p.estado_lectura == "completado").length` |
| 📝 Notas por enriquecer | `$= dv.pages('"01 - Libros"').where(p => p.estado == "esqueleto-automatico" || p.estado == "pendiente-ocr").length` |

---

## 🔄 Leyendo ahora

```dataview
TABLE WITHOUT ID file.link AS "Libro", autor AS "Autor", nivel AS "Nivel", tradicion AS "Tradición"
FROM "01 - Libros"
WHERE estado_lectura = "leyendo"
SORT file.name ASC
```

---

## ⬜ Próximos recomendados — Principiante

```dataview
TABLE WITHOUT ID file.link AS "Libro", tradicion AS "Tradición", idioma AS "Idioma"
FROM "01 - Libros"
WHERE estado_lectura = "pendiente" AND nivel = "principiante" AND !contains(estado, "duplicado") AND !contains(estado, "edicion")
SORT tradicion ASC, file.name ASC
LIMIT 10
```

## ⬜ Próximos recomendados — Intermedio

```dataview
TABLE WITHOUT ID file.link AS "Libro", tradicion AS "Tradición", idioma AS "Idioma"
FROM "01 - Libros"
WHERE estado_lectura = "pendiente" AND nivel = "intermedio" AND !contains(estado, "duplicado") AND !contains(estado, "edicion")
SORT tradicion ASC, file.name ASC
LIMIT 10
```

## ⬜ Próximos recomendados — Avanzado

```dataview
TABLE WITHOUT ID file.link AS "Libro", tradicion AS "Tradición", idioma AS "Idioma"
FROM "01 - Libros"
WHERE estado_lectura = "pendiente" AND nivel = "avanzado" AND !contains(estado, "duplicado") AND !contains(estado, "edicion")
SORT tradicion ASC, file.name ASC
LIMIT 10
```

---

## ✅ Completados

```dataview
TABLE WITHOUT ID file.link AS "Libro", autor AS "Autor", tradicion AS "Tradición"
FROM "01 - Libros"
WHERE estado_lectura = "completado"
SORT file.name ASC
```

---

## 📊 Progreso por tradición

```dataview
TABLE WITHOUT ID 
  tradicion AS "Tradición",
  length(rows) AS "Total",
  length(filter(rows, (p) => p.estado_lectura == "completado")) AS "✅",
  length(filter(rows, (p) => p.estado_lectura == "leyendo")) AS "🔄",
  length(filter(rows, (p) => p.estado_lectura == "pendiente")) AS "⬜"
FROM "01 - Libros"
WHERE tradicion != null AND !contains(estado, "duplicado") AND !contains(estado, "edicion")
GROUP BY tradicion
SORT length(rows) DESC
```

---

## 🔧 Cómo usar este dashboard

1. **Empezar a leer un libro:** abrí la nota del libro y cambiá `estado_lectura: "pendiente"` a `"leyendo"`
2. **Terminar un libro:** cambiá a `"completado"`
3. **El dashboard se actualiza solo** — no hay que editar nada acá manualmente
4. Usá `Cmd+O` (Quick Switcher) y buscá por el título del libro — los aliases hacen que funcione con el título real

---
*Dashboard dinámico con Dataview — se actualiza automáticamente desde el frontmatter de cada nota.*
