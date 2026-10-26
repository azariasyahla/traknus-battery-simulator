from datetime import datetime, timedelta
from pathlib import Path
import json
import base64
import pandas as pd
import altair as alt
import streamlit as st
from engine import simulate

ROOT = Path(__file__).parent
CATALOG = json.loads((ROOT / "data" / "model_catalog.json").read_text(encoding="utf-8"))
MODELS = {x["model"]: x for x in CATALOG["models"]}
LOGO_PATH = ROOT / "data" / "traknus_lithium_logo.png"
LOGO_B64_PATH = ROOT / "data" / "traknus_lithium_logo.png.b64"
if not LOGO_PATH.exists() and LOGO_B64_PATH.exists():
    LOGO_PATH.write_bytes(base64.b64decode(LOGO_B64_PATH.read_text(encoding="ascii")))
LOGO_DATA = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")

def model_series(model):
    for prefix in ("8FBR(S)", "8FBS(S)", "8FBP", "8FBE", "8FBN", "8FBH", "4CBT", "3TE", "8FB"):
        if model.startswith(prefix):
            return prefix
    return model

SERIES_BY_MODEL = {name: model_series(name) for name in MODELS}
CB_SERIES = {"8FBE", "8FBN", "8FB", "8FBH"}
MODEL_TYPE = {name: ("CB" if series in CB_SERIES else "WH") for name, series in SERIES_BY_MODEL.items()}

st.set_page_config(page_title="Traknus Battery Simulator", page_icon="🔋", layout="wide")

def reset_inputs():
    reset_keys={"sim_result","shift_count","first_start","default_shift_hours","shift_table","break_table","comparison_mode","compare_trucks"}
    for state_key in list(st.session_state):
        if state_key in reset_keys or state_key.startswith("Truck "):
            del st.session_state[state_key]

with st.sidebar:
    st.markdown("### ⚙️ Preferences")
    language = st.selectbox("Language / Bahasa", ["English", "Bahasa Indonesia"], index=0, key="ui_language")
    dark_mode = st.toggle("Dark mode", value=False, key="dark_mode")
    st.button("↺  Mulai simulasi baru / New simulation", use_container_width=True, on_click=reset_inputs)

ID = language == "Bahasa Indonesia"
def tr(en, id):
    return id if ID else en

bg = "#101923" if dark_mode else "#F5F8FB"
panel = "#172431" if dark_mode else "#FFFFFF"
ink = "#E7EEF5" if dark_mode else "#192B3C"
muted = "#A9BAC9" if dark_mode else "#607286"
line = "#334655" if dark_mode else "#D9E3EC"
section = "#C9E3F6" if dark_mode else "#173957"
axis_color = "#D4E0E9" if dark_mode else "#53677B"
grid_color = "#344654" if dark_mode else "#E6EDF3"
st.markdown(f"""
<style>
:root {{--navy:#122B49;--blue:#2869A6;--sky:#EAF3FA;--red:#D92D32;--ink:{ink};--muted:{muted};--line:{line};--panel:{panel};}}
[data-testid="stAppViewContainer"] {{background:linear-gradient(180deg,{bg} 0%,{panel} 80%); color:var(--ink);}}
[data-testid="stAppViewContainer"] p,[data-testid="stAppViewContainer"] label,[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] {{color:{ink};}}
[data-testid="stAppViewContainer"] input,[data-testid="stAppViewContainer"] textarea,[data-testid="stAppViewContainer"] [data-baseweb="select"] > div {{background-color:{panel};color:{ink};}}
.block-container {{max-width:1420px;padding-top:1.25rem;padding-bottom:3rem;}}
[data-testid="stSidebar"] {{background:{bg};}}
[data-testid="stVerticalBlockBorderWrapper"] {{background-color:{panel};border-color:{line};border-radius:14px;}}
.hero {{background:linear-gradient(115deg,#122B49 0%,#1C527A 75%,#2869A6 100%);border-radius:20px;padding:22px 26px;color:#fff;margin-bottom:18px;box-shadow:0 12px 32px rgba(18,43,73,.14);display:flex;align-items:center;gap:24px}}
.hero-logo {{background:#fff;border:1px solid #e4e9ef;border-radius:14px;padding:8px 12px;flex:0 0 auto}}
.hero-logo img {{display:block;width:205px;max-width:24vw;height:auto}}
.hero-copy {{min-width:0}}
@media (max-width:700px) {{.hero {{align-items:flex-start;flex-direction:column;gap:14px;padding:18px}} .hero-logo img {{width:175px;max-width:65vw}}}}
.hero h1 {{color:white;font-size:2rem;margin:0 0 5px 0;letter-spacing:-.03em}}
.hero p {{color:#DBEAF5;margin:0;font-size:1rem}}
.kicker {{color:#B8D7EE;text-transform:uppercase;letter-spacing:.12em;font-weight:700;font-size:.75rem;margin-bottom:8px}}
.section {{font-size:1.08rem;font-weight:750;color:{section};margin:.25rem 0 .4rem}}
.small {{color:{muted};font-size:.86rem}}
.truck-card {{border:1px solid {line};border-radius:16px;background:{panel};padding:16px 18px 4px;box-shadow:0 5px 18px rgba(18,43,73,.04)}}
.truck-title {{font-weight:800;font-size:1.05rem;color:{section};margin-bottom:.2rem}}
.metric-card {{background:{panel};border:1px solid {line};border-radius:14px;padding:14px 16px;height:100%;box-shadow:0 4px 16px rgba(18,43,73,.04)}}
.metric-label {{font-size:.78rem;color:{muted};text-transform:uppercase;letter-spacing:.06em;font-weight:700}}
.metric-value {{font-size:1.55rem;color:{section};font-weight:800;margin-top:5px}}
div.stButton>button[kind="primary"] {{background:#D92D32;border:0;border-radius:10px;color:white;font-weight:750;padding:.62rem 1.2rem}}
hr {{border-color:{line}}}
[data-testid="stDataFrame"] {{border:1px solid {line};border-radius:10px}}
</style>
<div class="hero"><div class="hero-logo"><img src="data:image/png;base64,{LOGO_DATA}" alt="Traknus Lithium Traction Battery"></div><div class="hero-copy"><div class="kicker">TRAKNUS · TRACTION BATTERY</div><h1>{tr('Battery Runtime Simulator','Simulator Waktu Operasional Baterai')}</h1><p>{tr('Explore battery performance across shifts, breaks, charging, and work conditions.','Lihat perkiraan performa baterai berdasarkan shift, istirahat, pengisian daya, dan kondisi kerja.')}</p></div></div>
""", unsafe_allow_html=True)

st.caption(tr("Estimate battery use from the schedule and truck settings below.", "Estimasi pemakaian baterai dari jadwal dan pengaturan truk di bawah."))

# Shared operating schedule
st.markdown(f'<div class="section">1 · {tr("Plan the work schedule","Atur jadwal kerja")}</div>', unsafe_allow_html=True)
with st.container(border=True):
    sc1, sc2, sc3 = st.columns([1,1,1.3])
    shift_count = sc1.number_input(tr("Number of shifts per workday", "Jumlah shift dalam satu hari kerja"), 1, 5, 1, 1, key="shift_count", help=tr("How many operating shifts the truck runs in one workday.", "Berapa shift operasional truk dalam satu hari kerja."))
    start_clock = sc2.time_input(tr("First shift starts at", "Shift pertama mulai"), value=datetime.strptime("07:00", "%H:%M").time(), key="first_start")
    default_hours = sc3.number_input(tr("Workday length (hours per shift)", "Lama kerja (jam per shift)"), 1.0, 24.0, 8.0, 0.5, key="default_shift_hours", help=tr("Working hours for each shift. Each shift can still be adjusted in the table below.", "Jumlah jam kerja untuk setiap shift. Durasi tiap shift tetap bisa diubah di tabel bawah."))
    shift_rows=[]
    start_dt=datetime.combine(datetime.today().date(),start_clock)
    for i in range(int(shift_count)):
        shift_rows.append({"Shift":f"Shift {i+1}","Start": (start_dt+timedelta(hours=i*default_hours)).strftime("%H:%M"),"Length (h)":float(default_hours)})
    shift_df=st.data_editor(pd.DataFrame(shift_rows),hide_index=True,use_container_width=True,
        column_config={"Shift":st.column_config.TextColumn(label=tr("Shift","Shift"),disabled=True),"Start":st.column_config.TextColumn(label=tr("Start","Mulai"),help=tr("24-hour time, e.g. 07:00","Format 24 jam, contoh 07:00")),"Length (h)":st.column_config.NumberColumn(label=tr("Length (h)","Durasi (jam)"),min_value=0.5,max_value=24,step=0.5)},key="shift_table")
    st.markdown(f"**{tr('Breaks and charging','Istirahat dan pengisian daya')}** <span class='small'>{tr('Enter when each break starts and how long it lasts. Mark Charge if the forklift is connected to its charger during the break.','Isi jam mulai dan lamanya istirahat. Centang Isi daya jika forklift di-charge selama waktu istirahat.')}</span>",unsafe_allow_html=True)
    break_df=st.data_editor(pd.DataFrame([{"Start":"10:00","Length (min)":30,"Charge":False}],columns=["Start","Length (min)","Charge"]),num_rows="dynamic",hide_index=True,use_container_width=True,
        column_config={"Start":st.column_config.TextColumn(label=tr("Break starts at","Mulai istirahat"),help=tr("Enter the break start time in 24-hour format, e.g. 10:00.","Masukkan jam mulai istirahat, format 24 jam, contoh 10:00.")),"Length (min)":st.column_config.NumberColumn(label=tr("Break length (min)","Lama istirahat (menit)"),help=tr("How many minutes the break lasts.","Berapa menit lama istirahatnya."),min_value=0,max_value=720,step=5),"Charge":st.column_config.CheckboxColumn(label=tr("Charge forklift?","Forklift di-charge?"),help=tr("Turn on if the forklift is being charged during this break.","Centang jika forklift di-charge selama istirahat ini."))},key="break_table")

st.markdown(f'<div class="section">2 · {tr("Choose truck and battery","Pilih truk dan baterai")}</div>', unsafe_allow_html=True)
comparison_mode=st.radio(
    tr("What do you want to compare?", "Apa yang ingin dibandingkan?"),
    ["battery_options", "multiple_trucks"],
    format_func=lambda x: tr("Battery capacities for one truck", "Beberapa kapasitas baterai untuk satu truk") if x == "battery_options" else tr("Compare multiple trucks", "Bandingkan beberapa truk"),
    horizontal=True,
    key="comparison_mode",
    help=tr("Choose one truck to test its battery options, or compare two different truck setups.", "Pilih satu truk untuk menguji beberapa kapasitas baterai, atau bandingkan dua konfigurasi truk."),
)
compare= comparison_mode == "multiple_trucks"
truck_count = st.number_input(tr("Number of trucks to compare", "Jumlah truk yang dibandingkan"), min_value=2, max_value=6, value=2, step=1, key="compare_trucks") if compare else 1


def truck_panel(slot, accent, default_model):
    with st.container(border=True):
        name=tr("Setup","Konfigurasi") + " " + slot.rsplit(" ", 1)[-1]
        st.markdown(f'<div class="truck-title" style="color:{accent}">🚜 {name}</div><div class="small">{tr("Choose the equipment and how it will be used.","Pilih unit dan kondisi penggunaannya.")}</div>',unsafe_allow_html=True)
        type_key=f"{slot}_type"
        selected_type=st.selectbox(tr("Truck type","Tipe truk"),["CB","WH"],format_func=lambda x: {"CB":tr("CB · Counterbalance","CB · Counterbalance"),"WH":tr("WH · Warehouse","WH · Warehouse")}[x],key=type_key)
        available_series=sorted({SERIES_BY_MODEL[m] for m in MODELS if MODEL_TYPE[m]==selected_type})
        preferred_series=SERIES_BY_MODEL[default_model] if MODEL_TYPE[default_model]==selected_type else available_series[0]
        series_key=f"{slot}_series"
        if st.session_state.get(series_key) not in available_series:
            st.session_state[series_key]=preferred_series
        selected_series=st.selectbox(tr("Truck series","Seri truk"),available_series,key=series_key)
        model_options=sorted([m for m in MODELS if MODEL_TYPE[m]==selected_type and SERIES_BY_MODEL[m]==selected_series])
        model_key=f"{slot}_model"
        preferred_model=default_model if default_model in model_options else model_options[0]
        if st.session_state.get(model_key) not in model_options:
            st.session_state[model_key]=preferred_model
        model_name=st.selectbox(tr("Truck model","Model truk"),model_options,key=model_key)
        st.selectbox(tr("Version","Versi"),["*"],format_func=lambda _:tr("* Generic version","* Versi generik"),key=f"{slot}_version",help=tr("The catalog currently provides the generic version.","Katalog saat ini menyediakan versi generik."))
        spec=MODELS[model_name]
        if not spec["battery_options"]:
            st.error(tr("No battery capacity is listed for this model.","Kapasitas baterai untuk model ini belum tersedia."))
            return None
        battery_options=spec["battery_options"]
        battery_map={f"{int(x['ah'])} Ah":{**x,"source":"Catalog"} for x in battery_options}
        selected_battery_labels=st.multiselect(
            tr("Battery capacities listed for this model", "Kapasitas baterai yang tercatat untuk model ini"),
            list(battery_map),
            default=list(battery_map),
            key=f"{slot}_batteries_{model_name}",
            help=tr("Select one or more. Each selected capacity will appear as a separate result.", "Pilih satu atau lebih. Setiap kapasitas yang dipilih akan muncul sebagai hasil terpisah."),
        )
        batteries=[battery_map[x] for x in selected_battery_labels]
        if len(battery_options) == 1:
            st.info(tr(
                f"{model_name} ({spec['voltage_v']:g} V) has one battery size in the workbook: {int(battery_options[0]['ah'])} Ah. Add a proposed capacity below if you want to test another candidate.",
                f"Di workbook, {model_name} ({spec['voltage_v']:g} V) hanya tercatat dengan satu kapasitas baterai: {int(battery_options[0]['ah'])} Ah. Tambahkan kapasitas usulan di bawah jika ingin menguji kandidat lain."
            ))
        with st.expander(tr("Add proposed battery capacities (optional)", "Tambahkan kapasitas baterai usulan (opsional)")):
            st.caption(tr(
                "Use this for an early estimate only. The proposed capacity keeps this truck's voltage; confirm battery compatibility before recommending or quoting it.",
                "Gunakan untuk estimasi awal. Tegangan mengikuti truk yang dipilih. Pastikan kecocokan baterai sebelum memberi rekomendasi atau penawaran."
            ))
            proposed_editor=st.data_editor(
                pd.DataFrame({"Capacity (Ah)":pd.Series(dtype="float64")}),
                num_rows="dynamic",hide_index=True,use_container_width=True,
                column_config={"Capacity (Ah)":st.column_config.NumberColumn(label=tr("Proposed capacity (Ah)","Kapasitas usulan (Ah)"),min_value=1,max_value=5000,step=1,format="%d")},
                key=f"{slot}_proposed_capacities_{model_name}"
            )
            official_ah={int(x["ah"]) for x in battery_options}
            reserve_default=float(battery_options[0].get("reserve_pct",0.05))
            proposed_options=[]
            duplicate_proposals=[]
            for raw_ah in proposed_editor["Capacity (Ah)"].tolist():
                if pd.isna(raw_ah):
                    continue
                proposed_ah=int(round(float(raw_ah)))
                if proposed_ah in official_ah:
                    duplicate_proposals.append(proposed_ah)
                elif proposed_ah > 0 and proposed_ah not in {x["ah"] for x in proposed_options}:
                    proposed_options.append({"ah":proposed_ah,"reserve_pct":reserve_default,"source":"Proposed"})
            if duplicate_proposals:
                dup_text=", ".join(f"{x} Ah" for x in sorted(set(duplicate_proposals)))
                st.caption(tr(f"{dup_text} is already listed above.",f"{dup_text} sudah tercantum di pilihan katalog di atas."))
            proposed_map={f"{x['ah']} Ah · {tr('proposed','usulan')}":x for x in proposed_options}
            if proposed_map:
                selected_proposed=st.multiselect(
                    tr("Proposed capacities to include", "Kapasitas usulan yang ikut dihitung"),
                    list(proposed_map),default=list(proposed_map),key=f"{slot}_proposed_selected_{model_name}"
                )
                batteries.extend(proposed_map[x] for x in selected_proposed)
            else:
                st.caption(tr("Click the + row to add a capacity to test.","Klik baris + untuk menambahkan kapasitas yang ingin diuji."))
        chargers=spec["charger_options_a"] or [0]
        charger=st.selectbox(tr("Charger current","Arus charger"),chargers,format_func=lambda x:tr("Not specified","Tidak ditentukan") if x==0 else f"{x} A",key=f"{slot}_charger_{model_name}")
        op1,op2=st.columns(2)
        mode=op1.selectbox(tr("Truck mode","Mode truk"),list(spec["power_modes"]),format_func=lambda x: {"Economy":tr("Economy","Hemat"),"Standard":tr("Standard","Standar"),"Power":tr("Power","Daya"),"High Power":tr("High Power","Daya tinggi")}.get(x,x),key=f"{slot}_mode_{model_name}")
        intensity=op2.selectbox(tr("Work intensity","Intensitas kerja"),list(CATALOG["intensity_factors"]),index=3,format_func=lambda x: {"Very Low":"Sangat rendah","Low":"Rendah","Medium":"Sedang","High":"Tinggi","Very High":"Sangat tinggi"}.get(x,x) if ID else x,key=f"{slot}_intensity")
        lift=st.selectbox(tr("Lift height range","Rentang tinggi angkat"),list(CATALOG["lift_factors"]),format_func=lambda x: {"All":tr("All heights","Semua ketinggian"),"4.3–8.0 m":tr("4.3–8.0 m","4,3–8,0 m"),"8.1 m+":tr("8.1 m and above","8,1 m ke atas")}.get(x,x),key=f"{slot}_lift")
        st.caption(f"{spec['voltage_v']:g} V · {tr('EN-cycle baseline','acuan siklus EN')} {spec['en_ah_per_hour']:.2f} Ah/h")
        return {"slot":slot,"model":model_name,"spec":spec,"batteries":batteries,"charger":charger,"mode":mode,"intensity":intensity,"lift":lift}

truck_configs=[]
truck_colors=["#D92D32", "#2869A6", "#159570", "#C77D12", "#7446A8", "#008A9B"]
default_models=sorted(MODELS)
cols=st.columns(2 if compare else 1,gap="medium")
for i in range(int(truck_count)):
    with cols[i % len(cols)]:
        default_model = ("8FBN25" if i == 0 and "8FBN25" in MODELS else "8FBE15" if i == 1 and "8FBE15" in MODELS else default_models[i % len(default_models)])
        truck_configs.append(truck_panel(f"Truck {i+1}", truck_colors[i % len(truck_colors)], default_model))



st.caption(tr("Results update automatically when you change the schedule or truck settings.","Hasil berubah otomatis saat jadwal atau pengaturan truk diubah."))
result=None
result_error=False
try:
    results=[]
    for cfg in truck_configs:
        if cfg is None:
            continue
        if not cfg["batteries"]:
            raise ValueError(tr("Select at least one battery capacity for each setup.","Pilih minimal satu kapasitas baterai untuk setiap konfigurasi."))
        for battery in cfg["batteries"]:
            source_suffix=tr(" · proposed"," · usulan") if battery.get("source")=="Proposed" else ""
            label=(f"{cfg['model']} · {battery['ah']} Ah{source_suffix}" if not compare else f"{cfg['slot']} · {cfg['model']} · {battery['ah']} Ah{source_suffix}")
            variant={**cfg,"battery":battery,"label":label,"slot":label}
            results.append((variant,simulate(variant,shift_df,break_df,CATALOG)))
    result={"results":results,"compare":compare,"mode":comparison_mode,"shifts":shift_df.copy(),"breaks":break_df.copy()}
except Exception as exc:
    result_error=True
    st.error(str(exc))

if result:
    st.markdown(f'<div class="section">3 · {tr("Your battery runtime estimate","Hasil estimasi waktu pakai baterai")}</div>',unsafe_allow_html=True)
    rescols=st.columns(min(3,len(result["results"])))
    chart=pd.DataFrame()
    for i,(cfg,out) in enumerate(result["results"]):
        with rescols[i % len(rescols)]:
            limit_text = tr(f"10% reserve reached at {out['time_to_soft_limit']:.1f} h",f"Cadangan 10% tercapai pada jam ke-{out['time_to_soft_limit']:.1f}") if out["time_to_soft_limit"] is not None else tr("10% reserve not reached in this schedule","Cadangan 10% belum tercapai pada jadwal ini")
            st.markdown(f"<div class='metric-card'><div class='metric-label'>{cfg['label']}</div><div class='metric-value'>{out['end_soc']:.0f}% {tr('remaining','tersisa')}</div><div class='small'>{limit_text}<br>{tr('Usable capacity','Kapasitas pakai')} {out['usable']:.0f} Ah · {tr('estimated use','estimasi pemakaian')} {out['draw']:.1f} Ah/h</div></div>",unsafe_allow_html=True)
            if out["depleted"]: st.error(tr("Battery is depleted during this schedule.","Baterai habis pada jadwal ini."))
            elif out["min_soc"]<10: st.warning(tr("Below 10% reserve — try a larger battery or a charging break.","Di bawah cadangan 10% — coba baterai lebih besar atau tambahkan waktu charging."))
            else: st.success(tr("Suitable for this schedule — stays above 10% reserve.","Cukup untuk jadwal ini — tetap di atas cadangan 10%."))
        series=out["data"].set_index("Elapsed hour")["State of charge (%)"].rename(cfg["slot"])
        chart=pd.concat([chart,series],axis=1)
    st.markdown(f"#### {tr('Battery level throughout the workday','Sisa daya baterai selama jam kerja')}")
    long_chart=pd.concat([out["data"].assign(Truck=cfg["slot"]) for cfg,out in result["results"]],ignore_index=True)
    chart_colors=["#D92D32","#2869A6","#159570","#C77D12","#7446A8","#008A9B","#AD477A","#667788"]
    chart_labels=[cfg["label"] for cfg,_ in result["results"]]
    line=alt.Chart(long_chart).mark_line(point=False,strokeWidth=3).encode(
        x=alt.X("Absolute minute:Q",title=tr("Time of day","Waktu"),axis=alt.Axis(grid=False, labelExpr="('0' + floor((datum.value % 1440) / 60)).slice(-2) + ':00'")),
        y=alt.Y("State of charge (%):Q",title=tr("Battery remaining (%)","Sisa baterai (%)"),scale=alt.Scale(domain=[0,100]),axis=alt.Axis(values=list(range(0,101,5)))),
        color=alt.Color("Truck:N",scale=alt.Scale(domain=chart_labels,range=[chart_colors[i % len(chart_colors)] for i in range(len(chart_labels))]),legend=alt.Legend(orient="top")),
        tooltip=[alt.Tooltip("Truck:N"),alt.Tooltip("Clock time:N"),alt.Tooltip("State of charge (%):Q",format=".1f")]
    ).properties(height=350,background=panel).configure_view(strokeOpacity=0).configure_axis(labelColor=axis_color,titleColor=axis_color,gridColor=grid_color)
    st.altair_chart(line,use_container_width=True)
    st.caption(tr("The chart shows estimated battery charge every 5 minutes. Charging during breaks cannot exceed usable battery capacity.","Grafik menunjukkan estimasi level baterai tiap 5 menit. Pengisian saat istirahat dibatasi kapasitas baterai yang dapat digunakan."))
    comparison_heading=tr("Battery option comparison","Perbandingan pilihan baterai") if result["mode"]=="battery_options" else tr("Truck setup comparison","Perbandingan konfigurasi truk")
    st.markdown(f"#### {comparison_heading}")
    summary=[]
    for cfg,out in result["results"]:
        suitable=out["min_soc"]>=10 and not out["depleted"]
        battery_source=tr("proposed","usulan") if cfg["battery"].get("source")=="Proposed" else tr("catalog","katalog")
        intensity_label={"Very Low":tr("Very low","Sangat rendah"),"Low":tr("Low","Rendah"),"Medium":tr("Medium","Sedang"),"High":tr("High","Tinggi"),"Very High":tr("Very high","Sangat tinggi")}.get(cfg["intensity"],cfg["intensity"])
        mode_label={"Economy":tr("Economy","Hemat"),"Standard":tr("Standard","Standar"),"Power":tr("Power","Daya"),"High Power":tr("High Power","Daya tinggi")}.get(cfg["mode"],cfg["mode"])
        summary.append({tr("Setup","Konfigurasi"):cfg["label"],tr("Model","Model"):cfg["model"],tr("Battery","Baterai"):f"{cfg['battery']['ah']} Ah ({battery_source})",tr("Charger","Charger"):f"{cfg['charger']} A" if cfg['charger'] else tr("Not specified","Tidak ditentukan"),tr("Mode","Mode"):mode_label,tr("Work intensity","Intensitas kerja"):intensity_label,tr("Lift range","Tinggi angkat"):cfg["lift"],tr("Estimated use","Estimasi pemakaian"):f"{out['draw']:.1f} Ah/h",tr("Lowest battery remaining","Sisa baterai terendah"):f"{out['min_soc']:.1f}%",tr("Battery remaining at end","Sisa baterai di akhir"):f"{out['end_soc']:.1f}%",tr("Assessment","Penilaian"):tr("Suitable","Cukup") if suitable else tr("Needs review","Perlu ditinjau")})
    st.dataframe(pd.DataFrame(summary),hide_index=True,use_container_width=True)
    export=pd.concat([out["data"].assign(Truck=cfg["slot"],Model=cfg["model"]) for cfg,out in result["results"]],ignore_index=True)
    controls=st.columns([1,1,1])
    with controls[0]:
        try:
            from pdf_report import build_pdf
            pdf_bytes=build_pdf(result,result["shifts"],result["breaks"],ROOT/"data"/"traknus_lithium_logo.png",ID)
            st.download_button(tr("📄 Export clear PDF","📄 Ekspor PDF rapi"),pdf_bytes,"traknus_battery_simulation.pdf","application/pdf",use_container_width=True)
        except ModuleNotFoundError as exc:
            if exc.name == "reportlab":
                st.error(tr("PDF export is not installed yet. Close the app and launch run_app.bat again to install the missing component.","Fitur PDF belum terpasang. Tutup aplikasi lalu jalankan run_app.bat lagi untuk memasang komponennya."))
            else:
                st.error(tr(f"Could not prepare the PDF: {exc}",f"PDF belum bisa dibuat: {exc}"))
        except Exception as exc:
            st.error(tr(f"Could not prepare the PDF: {exc}",f"PDF belum bisa dibuat: {exc}"))
    with controls[1]:
        st.download_button(tr("⬇ Download data (CSV)","⬇ Unduh data (CSV)"),export.to_csv(index=False).encode("utf-8-sig"),"battery_simulation.csv","text/csv",use_container_width=True)
    with controls[2]:
        st.button(tr("↺ Start over","↺ Kembali ke awal"),use_container_width=True,on_click=reset_inputs)
    st.caption(tr("Prototype calculation based on workbook formulas. Validate against the principal workbook before customer quotations.","Perhitungan prototipe berdasarkan rumus workbook. Validasi dengan workbook principal sebelum digunakan untuk penawaran ke pelanggan."))
else:
    if not result_error:
        st.info(tr("Choose at least one battery capacity for each setup to see the estimate.","Pilih minimal satu kapasitas baterai untuk setiap konfigurasi agar estimasi dapat ditampilkan."))

with st.expander(tr("How the estimate works","Cara kerja estimasi")):
    st.markdown(f"""
{tr('- **Energy use:** workbook EN-cycle consumption × truck mode × work intensity × lift height.\n- **Charging:** only during breaks marked for charging; rate is limited by battery capacity and charger current.\n- **Usable capacity:** nominal Ah less the battery reserve in the model catalog.\n- **Time step:** 5 minutes, matching the workbook.', '- **Pemakaian energi:** konsumsi siklus EN pada workbook × mode truk × intensitas kerja × tinggi angkat.\n- **Pengisian daya:** hanya saat istirahat yang ditandai untuk charging; arus dibatasi kapasitas baterai dan charger.\n- **Kapasitas pakai:** kapasitas nominal dikurangi cadangan baterai pada katalog model.\n- **Interval simulasi:** 5 menit, mengikuti workbook.')}

{tr("This first app version follows the visible workbook calculation chain. Shift boundaries, model-specific lift-height mapping, and principal adjustments still need side-by-side validation before customer use.","Versi awal aplikasi ini mengikuti alur rumus workbook yang terlihat. Batas pergantian shift, pemetaan tinggi angkat tiap model, dan penyesuaian khusus principal masih perlu divalidasi berdampingan sebelum dipakai pelanggan.")}
""")

st.divider()
st.markdown(f"<div style='text-align:center;color:{muted};font-size:.92rem;letter-spacing:.01em;padding:8px 0 4px;'>Developed by <strong style='color:{ink};'>Azaria Syahla Fitan Adibah</strong></div>",unsafe_allow_html=True)
