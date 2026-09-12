# Horario escolar · 2º B ESO · curso 2026‑27

Horario semanal de 2º B (Educrea El Viso) en tres formatos, generados desde una única fuente (`src/horario.html`).

| Archivo | Para qué |
|---|---|
| `index.html` | Web para el iPhone. Muestra el día actual con la clase de **ahora** resaltada, pestañas por día y la semana completa en pantallas grandes. Funciona sin conexión una vez guardada. |
| `horario-2B.ics` | Calendario para importar en el **Calendario del iPhone** (o Google Calendar): un evento semanal por asignatura hasta el final de curso. |
| `horario-2B.pdf` | Una hoja A4 apaisada para imprimir y colgar en la nevera. |

## En el iPhone

**Opción A · como app (recomendada).** Abre `index.html` (o el enlace publicado) en Safari → botón *Compartir* → **Añadir a pantalla de inicio**. Aparece un icono "2ºB" que abre el horario a pantalla completa.

**Opción B · en el Calendario.** Envía `horario-2B.ics` por AirDrop, Mail o WhatsApp al iPhone y ábrelo: Calendario pregunta en qué calendario añadir los eventos. Conviene crear antes un calendario nuevo llamado "Cole" para poder ocultarlo o borrarlo de golpe. Si lo compartes desde iCloud, tu mujer y tu hijo lo verán en sus iPhones sin importar nada.

## Regenerar

```
python3 build.py
```

Edita el horario en `src/horario.html` (constantes `WEEK`, `SLOTS`, `SUBJECTS`) y en `build.py` (misma tabla, más `INICIO_CURSO` / `FIN_CURSO`). El PDF se genera con Chromium si está instalado; si no, imprime `index.html` desde el navegador (ya sale en A4 apaisado).

## Supuestos

- Curso del 9 sept 2026 al 18 jun 2027. El `.ics` no incluye festivos ni vacaciones: esos días los eventos aparecen igualmente.
- Recreo y comedor no se añaden al calendario (sí se ven en la web y el PDF).
- Fuente: pizarra de la reunión de familias del 9 de septiembre de 2026.
