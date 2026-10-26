from datetime import datetime
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


PALETTE = ["#D92D32", "#2869A6", "#159570", "#C77D12", "#7446A8", "#008A9B", "#AD477A", "#667788"]


def _text(c, x, y, value, size=8, color="#23384C", font="Helvetica"):
    c.setFillColor(colors.HexColor(color))
    c.setFont(font, size)
    c.drawString(x, y, str(value))


def _fit(value, length):
    value = str(value)
    return value if len(value) <= length else value[: max(1, length - 1)] + "…"


def build_pdf(result, shifts, breaks, logo_path, indonesian=True):
    """Create a printable two-page maximum simulation summary."""
    out = BytesIO()
    page_w, page_h = landscape(A4)
    c = canvas.Canvas(out, pagesize=(page_w, page_h))
    rows = result["results"]
    if not rows:
        raise ValueError("No simulation results to export.")

    title = "Laporan Simulasi Waktu Pakai Baterai" if indonesian else "Battery Runtime Simulation Report"
    subtitle = "Perbandingan kapasitas untuk kondisi kerja terpilih" if indonesian else "Battery comparison for the selected operating schedule"
    schedule = "; ".join(
        f"{row['Start']} ({float(row['Length (h)']):g} h)" for _, row in shifts.iterrows()
    )
    break_text = []
    for _, row in breaks.iterrows():
        try:
            mins = int(float(row.get("Length (min)", 0) or 0))
        except (ValueError, TypeError):
            mins = 0
        if mins > 0:
            charged = bool(row.get("Charge", False))
            break_text.append(f"{row.get('Start', '')} + {mins} min" + (" (charge)" if charged else " (rest)"))

    # Branded title band and operating context.
    c.setFillColor(colors.HexColor("#122B49"))
    c.rect(0, page_h - 83, page_w, 83, fill=1, stroke=0)
    _text(c, 34, page_h - 35, title, 18, "#FFFFFF", "Helvetica-Bold")
    _text(c, 34, page_h - 55, subtitle, 9, "#DDEAF4")
    _text(c, 34, page_h - 73, f"Generated {datetime.now().strftime('%d %b %Y, %H:%M')}", 8, "#DDEAF4")
    if Path(logo_path).is_file():
        c.setFillColor(colors.white)
        c.roundRect(page_w - 222, page_h - 70, 190, 54, 8, fill=1, stroke=0)
        c.drawImage(ImageReader(str(logo_path)), page_w - 211, page_h - 64, width=168, height=42, preserveAspectRatio=True, anchor="c", mask="auto")

    first_cfg = rows[0][0]
    shift_label = "Jadwal shift" if indonesian else "Shift schedule"
    break_label = "Istirahat" if indonesian else "Breaks"
    model_label = "Model" if indonesian else "Model"
    _text(c, 38, page_h - 105, f"{model_label}: {first_cfg['model']}    |    {shift_label}: {schedule or '-'}", 9, "#23384C", "Helvetica-Bold")
    _text(c, 38, page_h - 121, f"{break_label}: {'; '.join(break_text) if break_text else ('Tidak ada' if indonesian else 'None')}", 8, "#52677A")
    operating = f"{first_cfg['mode']} | {first_cfg['intensity']} | {first_cfg['lift']}"
    _text(c, 38, page_h - 137, f"{'Kondisi kerja' if indonesian else 'Work conditions'}: {operating}", 8, "#52677A")

    # SOC chart with a shaded 10% reserve zone.
    chart_left, chart_bottom, chart_w, chart_h = 58, 170, page_w - 90, 245
    _text(c, chart_left, chart_bottom + chart_h + 10, "Perubahan level baterai (SOC)" if indonesian else "Battery level over time (SOC)", 11, "#122B49", "Helvetica-Bold")
    max_hour = max(float(df["Elapsed hour"].max()) for _, df in ((cfg, out["data"]) for cfg, out in rows))
    max_hour = max(max_hour, 1.0)
    plot_left, plot_bottom = chart_left + 34, chart_bottom + 22
    plot_w, plot_h = chart_w - 48, chart_h - 38
    reserve_y = plot_bottom + plot_h * 0.10
    c.setFillColor(colors.HexColor("#FCE7E7"))
    c.rect(plot_left, plot_bottom, plot_w, reserve_y - plot_bottom, fill=1, stroke=0)
    for pct in range(0, 101, 20):
        y = plot_bottom + plot_h * pct / 100
        c.setStrokeColor(colors.HexColor("#D7E0E8"))
        c.setLineWidth(0.5)
        c.line(plot_left, y, plot_left + plot_w, y)
        _text(c, chart_left, y - 3, f"{pct}%", 7, "#53677B")
    ticks = 5
    for i in range(ticks + 1):
        hour = max_hour * i / ticks
        x = plot_left + plot_w * i / ticks
        c.setStrokeColor(colors.HexColor("#E3E9EF"))
        c.line(x, plot_bottom, x, plot_bottom + plot_h)
        _text(c, x - 7, plot_bottom - 13, f"{hour:g}h", 7, "#53677B")
    _text(c, plot_left + 5, plot_bottom + 3, "10% reserve", 6.5, "#A52C32")

    for i, (cfg, sim) in enumerate(rows):
        df = sim["data"]
        color = colors.HexColor(PALETTE[i % len(PALETTE)])
        c.setStrokeColor(color)
        c.setLineWidth(2)
        points = [
            (plot_left + plot_w * float(r["Elapsed hour"]) / max_hour,
             plot_bottom + plot_h * float(r["State of charge (%)"]) / 100)
            for _, r in df.iterrows()
        ]
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            c.line(x1, y1, x2, y2)
        legend_x = plot_left + (i % 3) * (plot_w / 3)
        legend_y = chart_bottom + chart_h - 3 - (i // 3) * 13
        c.setStrokeColor(color)
        c.line(legend_x, legend_y, legend_x + 17, legend_y)
        _text(c, legend_x + 22, legend_y - 3, _fit(cfg["label"], 32), 7, "#31485E")

    # Compact comparison table on page one, or a dedicated page for larger comparisons.
    headers = ["Setup", "Battery", "Charger", "Mode", "Intensity", "Lift", "End SOC", "Min SOC", "Assessment"]
    if indonesian:
        headers = ["Konfigurasi", "Baterai", "Charger", "Mode", "Intensitas", "Angkat", "SOC akhir", "SOC min.", "Penilaian"]
    widths = [130, 56, 55, 68, 72, 65, 52, 52, 118]
    table_x = 34
    table_y = 145
    row_h = 16
    if len(rows) > 4:
        c.showPage()
        c.setFillColor(colors.HexColor("#122B49"))
        c.rect(0, page_h - 68, page_w, 68, fill=1, stroke=0)
        _text(c, 34, page_h - 40, "Rincian perbandingan" if indonesian else "Detailed comparison", 17, "#FFFFFF", "Helvetica-Bold")
        _text(c, 34, page_h - 56, subtitle, 8, "#DDEAF4")
        table_y = page_h - 96

    def draw_table_header(y):
        x = table_x
        c.setFillColor(colors.HexColor("#EAF1F6"))
        c.rect(table_x, y - 4, sum(widths), row_h + 5, fill=1, stroke=0)
        for head, width in zip(headers, widths):
            _text(c, x + 3, y + 2, head, 8, "#173957", "Helvetica-Bold")
            x += width

    draw_table_header(table_y)
    for i, (cfg, sim) in enumerate(rows):
        y = table_y - (i + 1) * row_h
        if y < 28:
            c.showPage()
            table_y = page_h - 55
            draw_table_header(table_y)
            y = table_y - row_h
        enough = sim["min_soc"] >= 10 and not sim["depleted"]
        assessment = ("Cukup untuk jadwal ini" if indonesian else "Suitable for this schedule") if enough else (("Baterai habis" if indonesian else "Battery depleted") if sim["depleted"] else ("Di bawah cadangan 10%" if indonesian else "Below 10% reserve"))
        proposed_tag = " (usulan)" if indonesian else " (proposed)"
        battery_label = f"{cfg['battery']['ah']} Ah" + (proposed_tag if cfg["battery"].get("source") == "Proposed" else "")
        values = [cfg["label"], battery_label, f"{cfg['charger']} A" if cfg["charger"] else "-", cfg["mode"], cfg["intensity"], cfg["lift"], f"{sim['end_soc']:.1f}%", f"{sim['min_soc']:.1f}%", assessment]
        x = table_x
        for value, width in zip(values, widths):
            _text(c, x + 3, y + 2, _fit(value, max(8, int(width / 4))), 7.5, "#23384C")
            x += width
        c.setStrokeColor(colors.HexColor("#E1E7ED"))
        c.line(table_x, y - 4, table_x + sum(widths), y - 4)

    note = "Estimasi berdasarkan model perhitungan prototipe; validasi terhadap workbook principal sebelum penawaran pelanggan." if indonesian else "Prototype estimate; validate against the principal workbook before using for customer quotations."
    _text(c, 34, 17, note, 7.5, "#66798A")
    c.save()
    return out.getvalue()
