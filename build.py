#!/usr/bin/env python3
"""Genera index.html (web / iPhone), horario-2B.ics (Calendario) y horario-2B.pdf (imprimir).

Uso:  python3 build.py
Ajusta INICIO_CURSO / FIN_CURSO cuando el colegio publique el calendario escolar.
"""
from datetime import date, timedelta
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).parent
SRC = ROOT / "src" / "horario.html"

# ---- Curso 2026-27 (Comunidad de Madrid, ESO). Cambia estas dos fechas si difieren. ----
INICIO_CURSO = date(2026, 9, 9)
FIN_CURSO = date(2027, 6, 18)

# ---- Horario 2º B (misma fuente que src/horario.html) ----
SUBJECTS = {
    "ING": "Inglés", "LEN": "Lengua Castellana", "GH": "Geografía e Historia",
    "EF": "Educación Física", "EVC": "Ed. en Valores Éticos y Cívicos", "TUT": "Tutoría",
    "FQ": "Física y Química", "TEC": "Tecnología y Digitalización", "PEEX": "PEEX",
    "CMP": "Computación", "ART": "Arte", "MAT": "Matemáticas",
    "REL": "Atención Educativa / Religión", "REC": "Recreo", "COM": "Comedor",
}
SLOTS = [("9:00", "9:55"), ("9:55", "10:50"), ("10:50", "11:45"), ("11:45", "12:15"),
         ("12:15", "13:10"), ("13:10", "14:05"), ("14:05", "15:10"), ("15:10", "16:05"), ("16:05", "17:00")]
WEEK = [
    ["ING", "LEN", "EVC", "REC", "GH", "PEEX", "COM", "CMP", "MAT"],
    ["ING", "EF", "TUT", "REC", "TEC", "PEEX", "COM", "ART", "MAT"],
    ["LEN", "GH", "FQ", "REC", "TEC", "PEEX", "COM", "MAT", "ART"],
    ["LEN", "LEN", "EF", "REC", "FQ", "PEEX", "COM", "CMP", "MAT"],
    ["ING", "REL", "FQ", "REC", "EF", "PEEX", "COM", "TEC", "GH"],
]
BYDAY = ["MO", "TU", "WE", "TH", "FR"]
EXCLUIR_DEL_CALENDARIO = {"REC", "COM"}  # recreo y comedor no hacen falta como eventos


def build_html() -> Path:
    body = SRC.read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", body).group(1)
    body = body.replace(f"<title>{title}</title>\n", "", 1)
    head = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="Horario semanal de 2º B ESO, curso 2026-27.">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Horario 2ºB">
<meta name="theme-color" content="#2b3a8f">
</head>
<body>
"""
    out = ROOT / "index.html"
    out.write_text(head + body + "\n</body>\n</html>\n", encoding="utf-8")
    return out


def _first_on_or_after(d: date, weekday: int) -> date:
    return d + timedelta(days=(weekday - d.weekday()) % 7)


def _hm(t: str) -> str:
    h, m = t.split(":")
    return f"{int(h):02d}{int(m):02d}00"


def build_ics() -> Path:
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Horario escolar//2B ESO 2026-27//ES",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:Horario 2º B", "X-WR-TIMEZONE:Europe/Madrid",
        "BEGIN:VTIMEZONE", "TZID:Europe/Madrid",
        "BEGIN:DAYLIGHT", "TZOFFSETFROM:+0100", "TZOFFSETTO:+0200", "TZNAME:CEST",
        "DTSTART:19700329T020000", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU", "END:DAYLIGHT",
        "BEGIN:STANDARD", "TZOFFSETFROM:+0200", "TZOFFSETTO:+0100", "TZNAME:CET",
        "DTSTART:19701025T030000", "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU", "END:STANDARD",
        "END:VTIMEZONE",
    ]
    until = FIN_CURSO.strftime("%Y%m%dT215959Z")
    stamp = INICIO_CURSO.strftime("%Y%m%dT000000Z")
    for d, keys in enumerate(WEEK):
        first = _first_on_or_after(INICIO_CURSO, d)
        # Une horas consecutivas de la misma asignatura (p. ej. Lengua 9:00-10:50 los jueves).
        merged = []
        for i, key in enumerate(keys):
            if merged and merged[-1][0] == key:
                merged[-1][2] = SLOTS[i][1]
            else:
                merged.append([key, SLOTS[i][0], SLOTS[i][1]])
        for key, start, end in merged:
            if key in EXCLUIR_DEL_CALENDARIO:
                continue
            lines += [
                "BEGIN:VEVENT",
                f"UID:2b-eso-2627-{BYDAY[d].lower()}-{_hm(start)}-{key.lower()}@horario-escolar",
                f"DTSTAMP:{stamp}",
                f"DTSTART;TZID=Europe/Madrid:{first.strftime('%Y%m%d')}T{_hm(start)}",
                f"DTEND;TZID=Europe/Madrid:{first.strftime('%Y%m%d')}T{_hm(end)}",
                f"RRULE:FREQ=WEEKLY;BYDAY={BYDAY[d]};UNTIL={until}",
                f"SUMMARY:{SUBJECTS[key]}",
                "DESCRIPTION:2º B ESO · Educrea El Viso",
                "TRANSP:TRANSPARENT",
                "END:VEVENT",
            ]
    lines.append("END:VCALENDAR")
    out = ROOT / "horario-2B.ics"
    out.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
    return out


def build_pdf(html: Path) -> Path | None:
    chrome = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome") \
        or next((str(p) for p in [Path("/opt/pw-browsers/chromium")] if p.exists()), None)
    if not chrome:
        print("Chromium no encontrado: se omite el PDF (puedes imprimir desde el navegador).")
        return None
    out = ROOT / "horario-2B.pdf"
    subprocess.run([
        chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
        "--virtual-time-budget=4000", f"--print-to-pdf={out}", html.resolve().as_uri(),
    ], check=True, capture_output=True)
    return out


if __name__ == "__main__":
    html = build_html()
    print("✓", html.name)
    print("✓", build_ics().name)
    pdf = build_pdf(html)
    if pdf:
        print("✓", pdf.name)
