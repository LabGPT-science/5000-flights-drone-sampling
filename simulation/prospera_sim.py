"""
LabGPT — Próspera (Roatán) sampling-mission simulation.
Lite Monte Carlo of out-and-back drone sampling flights over the 184.6-acre Próspera polygon.

Every input is either (a) sourced, or (b) a MODEL CHOICE / SCENARIO, labelled as such in CONFIG.
Run:  python simulation/prospera_sim.py  -> writes data/raw/prospera_sim/{flights.csv, summary.json, charts/*.png}
"""
import json, math, csv, os
import numpy as np

CONFIG = {
  "seed": 51,
  "n_flights": 5000,
  # --- SITE: study polygon (184.6 acres) at Próspera, Roatán, Honduras, as local east/north metres
  # from the mean of its five vertices. Exact coordinates are not published.
  "site_polygon_en_m": [(-779.8920235134933, -214.6853204052541), (-576.9064283533206, -380.679124841909),
                        (502.1222617140837, -270.01658855067467), (502.1222617140837, 172.63355661347637),
                        (352.5539284371282, 692.7474771820025)],
  # MODEL CHOICE: where the edge lab / launch base sits ("centroid" of the polygon).
  "base": "centroid",
  # --- PLATFORM: reference airframe DJI Matrice 350 RTK (sourced: enterprise.dji.com/matrice-350-rtk/specs) ---
  "drone": {"name": "DJI Matrice 350 RTK (reference platform)",
            "mass_with_batteries_kg": 6.47, "mtow_kg": 9.2,
            "battery_Wh": 2*263.2, "rated_endurance_min": 55, "rated_speed_ms": 8.0,
            "max_wind_ms": 12.0, "ascent_ms": 6.0, "descent_ms": 5.0,
            "hover_acc_rtk_m": 0.1, "hover_acc_gnss_m": 1.5},
  # MODEL CHOICES for flight profile 
  "cruise_airspeed_ms": 10.0,
  "wind_margin_ms": 4.0,        # MODEL CHOICE: in strong wind, airspeed = max(cruise, wind + margin), capped at max speed
  "max_speed_ms": 23.0,         # sourced: M350 max horizontal speed
  "cruise_alt_m": 30.0, "on_station_s": 120.0,
  "reserve_frac": 0.20,         # MODEL CHOICE: land with >=20% battery
  "power_mass_exponent": 1.5,   # MODEL CHOICE: ideal induced power ~ m^1.5 (momentum theory)
  # --- WIND (sourced: Windfinder, Roatán Intl Airport, obs 2008-2026: mean 11 kt ENE, gusts 26 kt) ---
  "wind_mean_kt": 11.0, "wind_gust_kt": 26.0, "wind_dir_deg": 67.5,
  "wind_weibull_k": 2.0,        # MODEL CHOICE: Weibull shape (Rayleigh); swap if station data obtained
  "wind_dir_spread_deg": 30.0,  # MODEL CHOICE
  # --- PAYLOAD SCENARIOS ---
  # water sampler: sourced USGS Halema'uma'u deployment (0.8 kg empty incl. ballast, 1.8 kg with 1 L)
  # soil grab tool mass: NOT KNOWN for LabGPT's arm -> scenario range
  "payloads": {
    "water_1L":  {"out_kg": 0.8, "back_kg": 1.8},
    "eDNA_2L":   {"out_kg": 0.8, "back_kg": 2.8},
    "soil_200g_tool0.5": {"out_kg": 0.5, "back_kg": 0.7},
    "soil_200g_tool1.0": {"out_kg": 1.0, "back_kg": 1.2},
  },
  # --- POSITION ERROR BASELINES (sourced: USGS 'Where in the world are my field plots?') ---
  "human_gps_open_m": [1, 5], "human_gps_canopy_m": [20, 30],
}

R = 6371000.0
def poly_area_centroid(P):
    A=cx=cy=0.0
    for i in range(len(P)):
        x1,y1=P[i]; x2,y2=P[(i+1)%len(P)]; c=x1*y2-x2*y1
        A+=c; cx+=(x1+x2)*c; cy+=(y1+y2)*c
    A*=0.5; return abs(A), (cx/(6*A), cy/(6*A))

def inside(pt, P):
    x,y=pt; c=False
    for i in range(len(P)):
        x1,y1=P[i]; x2,y2=P[(i+1)%len(P)]
        if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c

def convex_order(pts):
    cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
    return sorted(pts, key=lambda p: math.atan2(p[1]-cy, p[0]-cx))

def leg(dist, heading, payload_kg, wind_e, wind_n, C):
    """time (s) and energy (Wh) for a straight leg at constant airspeed, drift-corrected."""
    d=C["drone"]; ws=math.hypot(wind_e,wind_n)
    va=min(max(C["cruise_airspeed_ms"], ws+C["wind_margin_ms"]), C["max_speed_ms"])
    ue, un = math.sin(heading), math.cos(heading)
    w_along = wind_e*ue + wind_n*un
    w_cross = -wind_e*un + wind_n*ue
    if abs(w_cross) >= va: return float('inf'), float('inf')
    gs = math.sqrt(va*va - w_cross*w_cross) + w_along   # crab to hold track
    if gs <= 0.5: return float('inf'), float('inf')
    t = dist/gs
    return t, power_W(payload_kg, C)*t/3600

def power_W(payload_kg, C):
    d=C["drone"]
    P0 = d["battery_Wh"]/(d["rated_endurance_min"]/60)  # W at rated mass, 8 m/s, no wind
    return P0*((d["mass_with_batteries_kg"]+payload_kg)/d["mass_with_batteries_kg"])**C["power_mass_exponent"]

def main():
    C=CONFIG; rng=np.random.default_rng(C["seed"]); d=C["drone"]
    poly=[tuple(p) for p in C["site_polygon_en_m"]]
    area, cen = poly_area_centroid(poly)
    base = cen
    xs=[p[0] for p in poly]; ys=[p[1] for p in poly]
    # wind: Weibull with given mean
    k=C["wind_weibull_k"]; mean_ms=C["wind_mean_kt"]*0.514444
    lam = mean_ms/math.gamma(1+1/k)
    gust_factor = C["wind_gust_kt"]/C["wind_mean_kt"]
    rows=[]
    for i in range(C["n_flights"]):
        while True:
            p=(rng.uniform(min(xs),max(xs)), rng.uniform(min(ys),max(ys)))
            if inside(p,poly): break
        ws = lam*rng.weibull(k)
        wdir = math.radians(C["wind_dir_deg"] + rng.normal(0, C["wind_dir_spread_deg"]))
        # wind blowing FROM wdir -> vector points to wdir+180
        we, wn = -ws*math.sin(wdir), -ws*math.cos(wdir)
        dx,dy=p[0]-base[0], p[1]-base[1]; dist=math.hypot(dx,dy); hdg=math.atan2(dx,dy)
        sorties={}
        for name,pl in C["payloads"].items():
            t1,e1=leg(dist,hdg,pl["out_kg"],we,wn,C)
            t2,e2=leg(dist,hdg+math.pi,pl["back_kg"],we,wn,C)
            tv = 2*C["cruise_alt_m"]/d["ascent_ms"] + 2*C["cruise_alt_m"]/d["descent_ms"]
            ev = power_W(pl["out_kg"],C)*(C["cruise_alt_m"]/d["ascent_ms"]+C["cruise_alt_m"]/d["descent_ms"])/3600 \
               + power_W(pl["back_kg"],C)*(C["cruise_alt_m"]/d["ascent_ms"]+C["cruise_alt_m"]/d["descent_ms"])/3600
            es = power_W(pl["back_kg"],C)*C["on_station_s"]/3600   # conservative: loaded hover
            T=t1+t2+tv+C["on_station_s"]; E=e1+e2+ev+es
            within_mtow = d["mass_with_batteries_kg"]+max(pl["out_kg"],pl["back_kg"]) <= d["mtow_kg"]
            sorties[name]=(T,E,within_mtow)
        rows.append({
          "flight": i+1, "east_m": round(p[0],1), "north_m": round(p[1],1),
          "one_way_m": round(dist,1), "wind_ms": round(ws,2), "gust_ms_est": round(ws*gust_factor,2),
          "wind_from_deg": round(math.degrees(wdir)%360,1),
          "go_sustained_rule": ws < d["max_wind_ms"], "go_gust_rule": ws*gust_factor < d["max_wind_ms"],
          **{f"{n}_time_s": round(v[0],1) for n,v in sorties.items()},
          **{f"{n}_energy_Wh": round(v[1],2) for n,v in sorties.items()},
          **{f"{n}_batt_pct": round(100*v[1]/d["battery_Wh"],2) for n,v in sorties.items()},
          **{f"{n}_within_mtow": v[2] for n,v in sorties.items()},
          "rtk_sample_offset_m": round(abs(rng.normal(0, d["hover_acc_rtk_m"]/2)),3),
          "gnss_sample_offset_m": round(abs(rng.normal(0, d["hover_acc_gnss_m"]/2)),3),
        })
    with open("flights.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    A=lambda k: np.array([r[k] for r in rows],dtype=float)
    usable=d["battery_Wh"]*(1-C["reserve_frac"])
    summ={"site_area_acres": round(area/4046.8564,1), "site_area_m2": round(area),
          "base_choice": C["base"], "one_way_m": {"mean":round(A("one_way_m").mean()),"p95":round(np.percentile(A("one_way_m"),95)),"max":round(A("one_way_m").max())},
          "wind_ms": {"mean":round(A("wind_ms").mean(),2),"p95":round(np.percentile(A("wind_ms"),95),2)},
          "pct_flights_go_sustained_rule": round(100*A("go_sustained_rule").mean(),1),
          "pct_flights_go_gust_rule": round(100*A("go_gust_rule").mean(),1),
          "power_W_empty": round(power_W(0,C)), "usable_Wh_after_reserve": round(usable,1),
          "payloads":{}}
    for n,pl in C["payloads"].items():
        T0=A(f"{n}_time_s"); E0=A(f"{n}_energy_Wh"); ok=A(f"{n}_within_mtow").astype(bool)
        go=A("go_sustained_rule").astype(bool) & np.isfinite(T0)
        T=T0[go]; E=E0[go]
        summ["payloads"][n]={"within_MTOW": bool(ok.all()), "payload_out_kg":pl["out_kg"],"payload_back_kg":pl["back_kg"],
           "flights_flown_of_5000": int(go.sum()), "time_min_mean": round(T.mean()/60,2), "time_min_p95": round(np.percentile(T,95)/60,2),
           "batt_pct_mean": round(100*E.mean()/d["battery_Wh"],1), "batt_pct_p95": round(100*np.percentile(E,95)/d["battery_Wh"],1),
           "sorties_per_battery_pair_mean": round(usable/E.mean(),1),
           "total_hours_5000": round(T.sum()/3600,1), "total_km_flown": round(2*A("one_way_m")[go].sum()/1000,1)}
    summ["sample_offset_m"]={"drone_RTK_p95": round(np.percentile(A("rtk_sample_offset_m"),95),3),
        "drone_GNSS_only_p95": round(np.percentile(A("gnss_sample_offset_m"),95),2),
        "human_handheld_open_range": C["human_gps_open_m"], "human_handheld_canopy_range": C["human_gps_canopy_m"]}
    json.dump({"config":C,"summary":summ}, open("summary.json","w"), indent=2, default=str)
    # charts
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    os.makedirs("charts",exist_ok=True)
    fig,ax=plt.subplots(figsize=(6,5)); px=[p[0] for p in poly]+[poly[0][0]]; py=[p[1] for p in poly]+[poly[0][1]]
    ax.plot(px,py,'-',color='#1B5C35'); ax.scatter(A("east_m"),A("north_m"),s=2,c='#00A859',alpha=.35)
    ax.plot(*base,'k^',ms=10,label='edge lab / base ('+C["base"]+')')
    ax.set_aspect('equal'); ax.set_xlabel('east (m)'); ax.set_ylabel('north (m)'); ax.legend(fontsize=7)
    ax.set_title(f'Próspera polygon {summ["site_area_acres"]} acres, {C["n_flights"]} simulated sample points',fontsize=9)
    fig.tight_layout(); fig.savefig('charts/site_samples.png',dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(6,3.6))
    for n in C["payloads"]:
        v=A(f"{n}_batt_pct"); v=v[np.isfinite(v)&A("go_sustained_rule").astype(bool)]; ax.hist(v,bins=40,alpha=.55,label=n)
    ax.axvline(100*(1-C["reserve_frac"]),color='r',ls='--',label='usable (20% reserve)')
    ax.set_xlabel('battery used per sortie (% of 2×TB65)'); ax.set_ylabel('flights'); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig('charts/battery_per_sortie.png',dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(6,3.4))
    labels=['Drone RTK\n(DJI spec ±0.1 m)','Drone GNSS only\n(DJI spec ±1.5 m)','Human handheld GPS\nopen sky (USGS 1–5 m)','Human handheld GPS\nunder canopy (USGS 20–30 m)']
    lo=[0,0,1,20]; hi=[0.1,1.5,5,30]
    ax.barh(labels,[h-l for l,h in zip(lo,hi)],left=lo,color=['#00A859','#7FD3A8','#C9CFCC','#9AA3A0'])
    ax.set_xscale('symlog',linthresh=0.1); ax.set_xlabel('sample-location error (m, log scale)')
    fig.tight_layout(); fig.savefig('charts/location_error.png',dpi=160); plt.close(fig)
    print(json.dumps(summ,indent=1))
if __name__=="__main__":
    from pathlib import Path
    out = Path(__file__).resolve().parents[1] / "data" / "raw" / "prospera_sim"
    out.mkdir(parents=True, exist_ok=True)
    os.chdir(out)
    main()
