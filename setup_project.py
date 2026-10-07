# -*- coding: utf-8 -*-
"""SAMWATER — مولّد المشروع الكامل"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
FILES = {}

FILES["main.py"] = "from app import SamwaterApp\n\nif __name__ == '__main__':\n    SamwaterApp().mainloop()\n"
FILES["requirements.txt"] = "customtkinter>=5.2.2\nfpdf2>=2.7.8\n"
FILES["core/__init__.py"] = ""
FILES["modules/__init__.py"] = ""

FILES["core/engineering.py"] = r'''
import math

def water_chemistry(cations, anions, sio2, ca, mg, ph, tds, temp_c, alk, pca, palk, k):
    """cations/anions: {ion: (mg/L, poids équivalent)}"""
    cat = sum(c / e for c, e in cations.values())
    an = sum(c / e for c, e in anions.values())
    tot = cat + an
    err = 0.0 if tot == 0 else 100 * (cat - an) / tot
    tds_calc = sum(c for c, _ in cations.values()) + sum(c for c, _ in anions.values()) + sio2
    hard = 2.497 * ca + 4.118 * mg
    if min(tds, temp_c + 273.15, alk, ca) <= 0:
        raise ValueError("TDS, T absolue, alcalinité et Ca doivent être > 0")
    A = (math.log10(tds) - 1) / 10
    B = -13.12 * math.log10(temp_c + 273.15) + 34.55
    C = math.log10(ca) - 0.4
    D = math.log10(alk)
    phs = 9.3 + A + B - C - D
    return {"Cations (meq/L)": cat, "Anions (meq/L)": an,
            "Erreur balance (%)": err, "TDS calculé (mg/L)": tds_calc,
            "Dureté totale (mg/L CaCO3)": hard, "LSI": ph - phs,
            "S&DSI": ph - pca - palk - k,
            "Pression osmotique (bar)": 0.0385 * (tds / 1000) * ((temp_c + 273.15) / 298.15)}

def mineral_saturation(ca, so4, ba, sr, f, sio2, ksp_caso4, ksp_baso4, ksp_srso4, ksp_caf2, sio2_sol):
    def pct(iap, ksp):
        return 100 * iap / ksp if ksp > 0 else float("inf")
    mm = {"Ca": 40.08, "SO4": 96.06, "Ba": 137.33, "Sr": 87.62, "F": 19.0}
    iap_caso4 = (ca / mm["Ca"] / 1000) * (so4 / mm["SO4"] / 1000)
    iap_baso4 = (ba / mm["Ba"] / 1000) * (so4 / mm["SO4"] / 1000)
    iap_srso4 = (sr / mm["Sr"] / 1000) * (so4 / mm["SO4"] / 1000)
    iap_caf2 = (ca / mm["Ca"] / 1000) * (f / mm["F"] / 1000) ** 2
    return {"CaSO4 (%)": pct(iap_caso4, ksp_caso4), "BaSO4 (%)": pct(iap_baso4, ksp_baso4),
            "SrSO4 (%)": pct(iap_srso4, ksp_srso4), "CaF2 (%)": pct(iap_caf2, ksp_caf2),
            "SiO2 (%)": 100 * sio2 / sio2_sol if sio2_sol > 0 else float("inf")}

def uf(q_fil, area, p_feed, p_conc, p_fil, v_fil, v_bw, tcf):
    if min(area, tcf, v_fil) <= 0:
        raise ValueError("Surface, TCF et volume filtrat > 0 requis")
    flux = q_fil / area
    tmp = (p_feed + p_conc) / 2 - p_fil
    if tmp <= 0:
        raise ValueError("TMP doit être > 0")
    return {"Flux (LMH)": flux, "TMP (bar)": tmp,
            "Récupération (%)": 100 * (v_fil - v_bw) / v_fil,
            "Perméabilité (LMH/bar)": flux / (tmp * tcf)}

def ro_nf(q_perm, q_feed, c_perm, c_feed, p_feed, dp_stage, p_perm,
          osm_avg, osm_perm, A, B, c_memb, k_mass, y,
          q_act, ndp_init, ndp_act, tcf_init, tcf_act):
    if min(q_feed, c_feed) <= 0:
        raise ValueError("Débit et concentration d'alimentation > 0 requis")
    ndp = (p_feed - dp_stage / 2 - p_perm) - (osm_avg - osm_perm)
    jw = A * ndp
    js = B * (c_memb - c_perm)
    rej = (1 - c_perm / c_feed) * 100
    return {"Récupération (%)": 100 * q_perm / q_feed,
            "Rejet de sel (%)": rej, "Passage de sel (%)": 100 - rej,
            "NDP (bar)": ndp, "Flux d'eau Jw": jw, "Flux de sel Js": js,
            "CPF exp(Jw/k)": math.exp(jw / k_mass) if k_mass > 0 else float("inf"),
            "CPF 1+0.7Y": 1 + 0.7 * y,
            "Q perm. normalisé (ASTM D4516)": q_act * (ndp_init / ndp_act) * (tcf_init / tcf_act)}

def ion_exchange(v_water_m3, v_resin_l, eq_removed, mass_chem_g, dosage_eq_l):
    if v_resin_l <= 0:
        raise ValueError("Volume de résine > 0 requis")
    cap = eq_removed / v_resin_l
    return {"Bed Volumes (BV)": v_water_m3 * 1000 / v_resin_l,
            "Capacité opératoire (eq/L)": cap,
            "Dosage régénérant (g/L)": mass_chem_g / v_resin_l,
            "Efficacité régénération (%)": 100 * cap / dosage_eq_l if dosage_eq_l > 0 else 0}

def blending(q1, c1, q2, c2):
    if q1 + q2 <= 0:
        raise ValueError("Débit total > 0 requis")
    return {"Concentration finale": (q1 * c1 + q2 * c2) / (q1 + q2)}

def sec(power_kw, flow_m3h):
    if flow_m3h <= 0:
        raise ValueError("Débit > 0 requis")
    return {"SEC (kWh/m3)": power_kw / flow_m3h}

def chemical_dosing(q_water, dose, conc_pct, sg, alum_dose, cl_resid, contact_min):
    den = conc_pct * 10 * sg
    if den <= 0:
        raise ValueError("Concentration et densité > 0 requises")
    return {"Pompe doseuse (L/h)": q_water * dose / den,
            "Alcalinité consommée alun (mg/L CaCO3)": alum_dose * 0.5,
            "CT chlore (mg.min/L)": cl_resid * contact_min}

def media_filtration(q, a_filter, h_settled, h_expanded, a_settling):
    if min(a_filter, h_settled, a_settling) <= 0:
        raise ValueError("Surfaces et hauteur > 0 requises")
    return {"Vitesse filtration (m/h)": q / a_filter,
            "Expansion du lit (%)": 100 * (h_expanded - h_settled) / h_settled,
            "SOR (m3/m2.h)": q / a_settling}

def wastewater(q, bod5, v_aer, mlvss, mlss, ssv30, q_w, x_w, q_e, x_e, v_tank):
    if min(q, v_aer, mlvss, mlss) <= 0:
        raise ValueError("Débit, volumes, MLSS/MLVSS > 0 requis")
    out = q_w * x_w + q_e * x_e
    return {"HRT (h)": v_tank / q,
            "SRT (j)": v_aer * mlss / out if out > 0 else float("inf"),
            "F/M (1/j)": q * bod5 / (v_aer * mlvss),
            "SVI (mL/g)": ssv30 * 1000 / mlss}

def pump_hydraulics(q, h_dis_static, h_suc_static, hf, h_minor, p_dis, p_suc, sg,
                    eff_p, eff_m, eff_vfd, f, L, D, vel,
                    h_baro, h_suc_fric, h_vapor):
    if min(sg, eff_p, eff_m, eff_vfd, D) <= 0:
        raise ValueError("SG, rendements et diamètre > 0 requis")
    h_static = h_dis_static - h_suc_static
    tdh = h_static + hf + h_minor + (p_dis - p_suc) * 10.197 / sg
    pw = q * tdh * sg / 367
    return {"H statique (m)": h_static,
            "TDH (m)": tdh,
            "Perte Darcy (m)": f * (L / D) * vel ** 2 / (2 * 9.81),
            "P hydraulique (kW)": pw,
            "P arbre BHP (kW)": pw / eff_p,
            "P électrique (kW)": pw / (eff_p * eff_m * eff_vfd),
            "Rendement système (%)": 100 * eff_p * eff_m * eff_vfd,
            "NPSHA (m)": h_baro + h_suc_static - h_suc_fric - h_vapor}

def ro_pumps(ndp, osm_avg, dp_stages, p_perm_bp, q_feed, q_perm, q_conc,
             p_conc, erd_eff, eff_p, eff_m):
    if min(eff_p, eff_m) <= 0:
        raise ValueError("Rendements > 0 requis")
    p_feed = ndp + osm_avg + dp_stages + p_perm_bp
    p_no = q_feed * p_feed / (36 * eff_p * eff_m)
    p_erd = (q_perm * p_feed + q_conc * (p_feed - p_conc * erd_eff)) / (36 * eff_p * eff_m)
    return {"P alimentation requise (bar)": p_feed,
            "P HPP sans ERD (kW)": p_no,
            "P HPP avec ERD (kW)": p_erd,
            "SEC RO (kWh/m3)": p_erd / q_perm if q_perm > 0 else float("inf")}

def dosing_pumps(q_raw, dose, conc_pct, sg, q_max, stroke_pct, freq_pct,
                 vol_ml, time_s, p_line, dp_valve):
    den = conc_pct * 10 * sg
    if min(den, time_s) <= 0:
        raise ValueError("Concentration, densité et temps > 0 requis")
    return {"Q doseuse (L/h)": q_raw * dose / den,
            "Q réel course/fréq. (L/h)": q_max * stroke_pct / 100 * freq_pct / 100,
            "Q mesuré calibration (L/h)": vol_ml / time_s * 3.6,
            "P nominale min. (bar)": p_line + dp_valve + 1.5}

def instrumentation(i_ma, pv_min, pv_max, cond, k):
    return {"Valeur mesurée (4-20 mA)": pv_min + (i_ma - 4) / 16 * (pv_max - pv_min),
            "TDS depuis conductivité (mg/L)": k * cond}

def affinity(q1, h1, p1, n1, n2, d1, d2):
    if min(n1, d1) <= 0:
        raise ValueError("N1 et D1 > 0 requis")
    rn, rd = n2 / n1, d2 / d1
    return {"Q2 vitesse": q1 * rn, "H2 vitesse": h1 * rn ** 2, "P2 vitesse": p1 * rn ** 3,
            "Q2 diamètre": q1 * rd, "H2 diamètre": h1 * rd ** 2, "P2 diamètre": p1 * rd ** 3}
'''

FILES["core/i18n.py"] = r'''
LANGUAGES = {"fr": "Français", "ar": "العربية", "en": "English"}
_cur = "fr"

S = {
 "app": {"fr": "SAMWATER — Calculs de traitement de l'eau",
         "ar": "SAMWATER — حسابات معالجة المياه",
         "en": "SAMWATER — Water Treatment Calculations"},
 "calc": {"fr": "Calculer", "ar": "احسب", "en": "Calculate"},
 "clear": {"fr": "Effacer", "ar": "مسح", "en": "Clear"},
 "pdf": {"fr": "Rapport PDF", "ar": "تقرير PDF", "en": "PDF Report"},
 "save": {"fr": "Enregistrer", "ar": "حفظ", "en": "Save"},
 "open": {"fr": "Ouvrir", "ar": "فتح", "en": "Open"},
 "project": {"fr": "Projet", "ar": "المشروع", "en": "Project"},
 "customer": {"fr": "Client", "ar": "الزبون", "en": "Customer"},
 "results": {"fr": "Résultats", "ar": "النتائج", "en": "Results"},
 "saved": {"fr": "Projet enregistré.", "ar": "تم حفظ المشروع.", "en": "Project saved."},
 "err": {"fr": "Erreur", "ar": "خطأ", "en": "Error"},
 "fill": {"fr": "Remplissez tous les champs (nombres).",
          "ar": "املأ جميع الحقول بأرقام.", "en": "Fill all fields with numbers."},
}

def set_lang(c):
    global _cur
    if c in LANGUAGES:
        _cur = c

def get_lang():
    return _cur

def t(k):
    return S.get(k, {}).get(_cur, k)

def L(d):
    return d.get(_cur, d.get("fr", ""))
'''

FILES["core/units.py"] = r'''
EQ = {"Ca": 20.04, "Mg": 12.15, "Na": 23.0, "K": 39.1,
      "HCO3": 61.0, "Cl": 35.45, "SO4": 48.03}

def to_mg_l(v, unit, ion):
    return v * EQ[ion] if unit == "meq/L" else v
'''

FILES["core/projects.py"] = r'''
import json, os

DIR = os.path.join(os.path.expanduser("~"), "Documents", "SAMWATER_Projects")
os.makedirs(DIR, exist_ok=True)

def save(name, data):
    p = os.path.join(DIR, name + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return p

def load(name):
    with open(os.path.join(DIR, name + ".json"), encoding="utf-8") as f:
        return json.load(f)

def list_all():
    return sorted(p[:-5] for p in os.listdir(DIR) if p.endswith(".json"))
'''

FILES["core/pdf_report.py"] = r'''
from fpdf import FPDF
from datetime import datetime
import os

def make_report(project, customer, title, inputs, results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "SAMWATER - Calculation Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Date: {datetime.now():%Y-%m-%d %H:%M}", ln=True)
    pdf.cell(0, 8, f"Project: {project}   Customer: {customer}", ln=True)
    pdf.cell(0, 8, f"Module: {title}", ln=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Inputs", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for k, v in inputs.items():
        pdf.cell(0, 6, f"  {k} = {v}", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Results", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for k, v in results.items():
        pdf.cell(0, 6, f"  {k} = {v:.6g}", ln=True)
    out = os.path.join(os.path.expanduser("~"), "Documents",
                       f"SAMWATER_{project or 'report'}.pdf")
    pdf.output(out)
    return out
'''

FILES["modules/base_module.py"] = r'''
import customtkinter as ctk
from tkinter import messagebox
from core import i18n, units, pdf_report

class BaseModule(ctk.CTkFrame):
    def __init__(self, master, defn, app):
        super().__init__(master)
        self.defn, self.app = defn, app
        self.entries, self.unit_menus = {}, {}
        self.last_in, self.last_out = {}, {}
        ctk.CTkLabel(self, text=i18n.L(defn["title"]),
                     font=("Segoe UI", 20, "bold")).pack(pady=10)
        box = ctk.CTkScrollableFrame(self)
        box.pack(fill="both", expand=True, padx=12, pady=6)
        for f in defn["fields"]:
            row = ctk.CTkFrame(box)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=i18n.L(f["label"]), width=300,
                         anchor="w").pack(side="left", padx=6)
            e = ctk.CTkEntry(row, width=130)
            e.pack(side="left", padx=6)
            self.entries[f["key"]] = e
            if "ion" in f:
                m = ctk.CTkOptionMenu(row, values=["mg/L", "meq/L"], width=95)
                m.pack(side="left", padx=4)
                self.unit_menus[f["key"]] = (m, f["ion"])
        bar = ctk.CTkFrame(self)
        bar.pack(fill="x", padx=12, pady=8)
        ctk.CTkButton(bar, text=i18n.t("calc"), command=self.calculate).pack(side="left", padx=6)
        ctk.CTkButton(bar, text=i18n.t("clear"), command=self.clear,
                      fg_color="gray").pack(side="left", padx=6)
        ctk.CTkButton(bar, text=i18n.t("pdf"), command=self.export_pdf).pack(side="left", padx=6)
        self.out = ctk.CTkTextbox(self, height=200)
        self.out.pack(fill="x", padx=12, pady=6)

    def values(self):
        v = {}
        for k, e in self.entries.items():
            val = float(e.get().replace(",", "."))
            if k in self.unit_menus:
                menu, ion = self.unit_menus[k]
                val = units.to_mg_l(val, menu.get(), ion)
            v[k] = val
        return v

    def calculate(self):
        try:
            self.last_in = {k: e.get() for k, e in self.entries.items()}
            self.last_out = self.defn["compute"](self.values())
            self.out.delete("1.0", "end")
            self.out.insert("end", f"--- {i18n.t('results')} ---\n")
            for k, val in self.last_out.items():
                self.out.insert("end", f"{k} = {val:.6g}\n")
        except ValueError:
            messagebox.showwarning(i18n.t("err"), i18n.t("fill"))
        except Exception as ex:
            messagebox.showerror(i18n.t("err"), str(ex))

    def clear(self):
        for e in self.entries.values():
            e.delete(0, "end")
        self.out.delete("1.0", "end")

    def export_pdf(self):
        if not self.last_out:
            self.calculate()
        if self.last_out:
            p = pdf_report.make_report(self.app.project.get(), self.app.customer.get(),
                                       i18n.L(self.defn["title"]),
                                       self.last_in, self.last_out)
            messagebox.showinfo("PDF", p)
'''

FILES["modules/catalog.py"] = r'''
from core import engineering as E

def F(key, fr, ar, en, ion=None):
    d = {"key": key, "label": {"fr": fr, "ar": ar, "en": en}}
    if ion:
        d["ion"] = ion
    return d

def _wc(v):
    cat = {"Ca": (v["ca"], 20.04), "Mg": (v["mg"], 12.15),
           "Na": (v["na"], 23.0), "K": (v["k"], 39.1)}
    an = {"HCO3": (v["hco3"], 61.0), "Cl": (v["cl"], 35.45), "SO4": (v["so4"], 48.03)}
    return E.water_chemistry(cat, an, v["sio2"], v["ca"], v["mg"], v["ph"],
                             v["tds"], v["temp"], v["alk"], v["pca"], v["palk"], v["ksd"])

MODULES = [
 {"id": "water", "title": {"fr": "Chimie de l'eau & équilibre ionique",
                           "ar": "كيمياء المياه والاتزان الأيوني",
                           "en": "Water Chemistry & Ionic Balance"},
  "fields": [F("ca", "Ca²⁺", "الكالسيوم", "Calcium", "Ca"),
             F("mg", "Mg²⁺", "المغنيسيوم", "Magnesium", "Mg"),
             F("na", "Na⁺", "الصوديوم", "Sodium", "Na"),
             F("k", "K⁺", "البوتاسيوم", "Potassium", "K"),
             F("hco3", "HCO₃⁻", "البيكربونات", "Bicarbonate", "HCO3"),
             F("cl", "Cl⁻", "الكلوريد", "Chloride", "Cl"),
             F("so4", "SO₄²⁻", "الكبريتات", "Sulfate", "SO4"),
             F("sio2", "SiO₂ (mg/L)", "السيليكا", "Silica"),
             F("ph", "pH", "pH", "pH"),
             F("tds", "TDS (mg/L)", "الأملاح الذائبة", "TDS"),
             F("temp", "Température (°C)", "الحرارة", "Temperature"),
             F("alk", "Alcalinité (mg/L CaCO₃)", "القلوية", "Alkalinity"),
             F("pca", "pCa", "pCa", "pCa"),
             F("palk", "pAlk", "pAlk", "pAlk"),
             F("ksd", "K (Stiff&Davis)", "ثابت K", "K constant")],
  "compute": _wc},

 {"id": "sat", "title": {"fr": "Saturation minérale (%)", "ar": "تشبع المعادن", "en": "Mineral Saturation"},
  "fields": [F("ca", "Ca (mg/L)", "الكالسيوم", "Ca"),
             F("so4", "SO₄ (mg/L)", "الكبريتات", "SO4"),
             F("ba", "Ba (mg/L)", "الباريوم", "Ba"),
             F("sr", "Sr (mg/L)", "السترونشيوم", "Sr"),
             F("fl", "F (mg/L)", "الفلوريد", "F"),
             F("sio2", "SiO₂ (mg/L)", "السيليكا", "SiO2"),
             F("k1", "Ksp CaSO₄", "Ksp CaSO4", "Ksp CaSO4"),
             F("k2", "Ksp BaSO₄", "Ksp BaSO4", "Ksp BaSO4"),
             F("k3", "Ksp SrSO₄", "Ksp SrSO4", "Ksp SrSO4"),
             F("k4", "Ksp CaF₂", "Ksp CaF2", "Ksp CaF2"),
             F("ss", "Solubilité SiO₂ (mg/L)", "ذوبانية السيليكا", "SiO2 solubility")],
  "compute": lambda v: E.mineral_saturation(v["ca"], v["so4"], v["ba"], v["sr"],
          v["fl"], v["sio2"], v["k1"], v["k2"], v["k3"], v["k4"], v["ss"])},

 {"id": "uf", "title": {"fr": "Ultrafiltration (UF)", "ar": "الترشيح الفائق", "en": "Ultrafiltration"},
  "fields": [F("q", "Débit filtrat (L/h)", "تدفق الراشح", "Filtrate flow"),
             F("a", "Surface (m²)", "المساحة", "Area"),
             F("pf", "P alimentation (bar)", "ضغط التغذية", "Feed P"),
             F("pc", "P concentrat (bar)", "ضغط المركز", "Concentrate P"),
             F("pfi", "P filtrat (bar)", "ضغط الراشح", "Filtrate P"),
             F("vf", "Volume filtrat", "حجم الراشح", "Filtrate vol."),
             F("vbw", "Volume backwash", "حجم الغسيل العكسي", "Backwash vol."),
             F("tcf", "TCF", "معامل الحرارة", "TCF")],
  "compute": lambda v: E.uf(v["q"], v["a"], v["pf"], v["pc"], v["pfi"],
                            v["vf"], v["vbw"], v["tcf"])},

 {"id": "ro", "title": {"fr": "Osmose inverse / Nanofiltration", "ar": "التناضح العكسي/النانوي", "en": "RO / NF"},
  "fields": [F("qp", "Q perméat (m³/h)", "تدفق النفاذ", "Permeate flow"),
             F("qf", "Q alimentation (m³/h)", "تدفق التغذية", "Feed flow"),
             F("cp", "C perméat (mg/L)", "تركيز النفاذ", "Permeate conc."),
             F("cf", "C alimentation (mg/L)", "تركيز التغذية", "Feed conc."),
             F("pf", "P alimentation (bar)", "ضغط التغذية", "Feed P"),
             F("dp", "ΔP étage (bar)", "فقد الضغط بالمرحلة", "Stage ΔP"),
             F("pp", "P perméat (bar)", "ضغط النفاذ", "Permeate P"),
             F("oa", "Osmotique moy. (bar)", "الأسموزي الوسطي", "Avg osmotic"),
             F("op", "Osmotique perméat (bar)", "الأسموزي للنفاذ", "Permeate osmotic"),
             F("A", "Constante A", "ثابت A", "A constant"),
             F("B", "Constante B", "ثابت B", "B constant"),
             F("cm", "C membrane (mg/L)", "تركيز الغشاء", "Membrane conc."),
             F("km", "k transfert", "معامل النقل k", "k mass transfer"),
             F("y", "Y récupération (0-1)", "الاسترجاع Y", "Recovery Y"),
             F("qa", "Q perm. actuel", "النفاذ الفعلي", "Actual Q perm"),
             F("ni", "NDP initial", "NDP الابتدائي", "Initial NDP"),
             F("na", "NDP actuel", "NDP الفعلي", "Actual NDP"),
             F("ti", "TCF initial", "TCF الابتدائي", "Initial TCF"),
             F("ta", "TCF actuel", "TCF الفعلي", "Actual TCF")],
  "compute": lambda v: E.ro_nf(v["qp"], v["qf"], v["cp"], v["cf"], v["pf"], v["dp"],
          v["pp"], v["oa"], v["op"], v["A"], v["B"], v["cm"], v["km"], v["y"],
          v["qa"], v["ni"], v["na"], v["ti"], v["ta"])},

 {"id": "ix", "title": {"fr": "Échange d'ions (IX)", "ar": "التبادل الأيوني", "en": "Ion Exchange"},
  "fields": [F("vw", "Volume eau (m³)", "حجم الماء", "Water volume"),
             F("vr", "Volume résine (L)", "حجم الراتنج", "Resin volume"),
             F("eq", "Équivalents éliminés (eq)", "المكافئات المزالة", "Eq removed"),
             F("mc", "Masse chimique (g)", "كتلة المادة", "Chemical mass"),
             F("deq", "Dosage appliqué (eq/L)", "الجرعة المطبقة", "Applied dosage")],
  "compute": lambda v: E.ion_exchange(v["vw"], v["vr"], v["eq"], v["mc"], v["deq"])},

 {"id": "blend", "title": {"fr": "Mélange & SEC", "ar": "الخلط واستهلاك الطاقة", "en": "Blending & SEC"},
  "fields": [F("q1", "Q1 (m³/h)", "التدفق 1", "Flow 1"),
             F("c1", "C1 (mg/L)", "التركيز 1", "Conc 1"),
             F("q2", "Q2 (m³/h)", "التدفق 2", "Flow 2"),
             F("c2", "C2 (mg/L)", "التركيز 2", "Conc 2"),
             F("p", "Puissance (kW)", "القدرة", "Power"),
             F("qp", "Débit produit (m³/h)", "تدفق المنتج", "Product flow")],
  "compute": lambda v: {**E.blending(v["q1"], v["c1"], v["q2"], v["c2"]),
                        **E.sec(v["p"], v["qp"])}},

 {"id": "dose", "title": {"fr": "Dosage chimique", "ar": "الجرعات الكيميائية", "en": "Chemical Dosing"},
  "fields": [F("q", "Débit eau (m³/h)", "تدفق الماء", "Water flow"),
             F("d", "Dose (mg/L)", "الجرعة", "Dose"),
             F("c", "Concentration (%)", "التركيز %", "Concentration"),
             F("sg", "Densité relative", "الكثافة النسبية", "Spec. gravity"),
             F("al", "Dose alun (mg/L)", "جرعة الشبة", "Alum dose"),
             F("cl", "Chlore résiduel (mg/L)", "الكلور المتبقي", "Cl residual"),
             F("ct", "Temps contact (min)", "زمن التماس", "Contact time")],
  "compute": lambda v: E.chemical_dosing(v["q"], v["d"], v["c"], v["sg"],
                                         v["al"], v["cl"], v["ct"])},

 {"id": "media", "title": {"fr": "Filtration sur média", "ar": "الترشيح بالرمل", "en": "Media Filtration"},
  "fields": [F("q", "Débit (m³/h)", "التدفق", "Flow"),
             F("af", "Surface filtre (m²)", "مساحة المرشح", "Filter area"),
             F("hs", "H lit repos (m)", "ارتفاع المستقر", "Settled bed"),
             F("he", "H lit expansé (m)", "ارتفاع المتمدد", "Expanded bed"),
             F("as", "Surface décanteur (m²)", "مساحة المرسّب", "Settling area")],
  "compute": lambda v: E.media_filtration(v["q"], v["af"], v["hs"], v["he"], v["as"])},

 {"id": "bio", "title": {"fr": "Traitement biologique", "ar": "المعالجة البيولوجية", "en": "Biological Wastewater"},
  "fields": [F("q", "Débit (m³/h)", "التدفق", "Flow"),
             F("bod", "BOD5 (mg/L)", "BOD5", "BOD5"),
             F("va", "Volume aération (m³)", "حجم التهوية", "Aeration vol."),
             F("mlvss", "MLVSS (mg/L)", "MLVSS", "MLVSS"),
             F("mlss", "MLSS (mg/L)", "MLSS", "MLSS"),
             F("ssv", "Vase 30 min (mL/L)", "الحمأة المترسبة", "Settled sludge"),
             F("qw", "Q purge (m³/j)", "تدفق التصريف", "Waste flow"),
             F("xw", "X purge (mg/L)", "تركيز التصريف", "Waste conc."),
             F("qe", "Q effluent (m³/j)", "تدفق المخرج", "Effluent flow"),
             F("xe", "X effluent (mg/L)", "تركيز المخرج", "Effluent conc."),
             F("vt", "Volume bassin (m³)", "حجم الخزان", "Tank volume")],
  "compute": lambda v: E.wastewater(v["q"], v["bod"], v["va"], v["mlvss"], v["mlss"],
          v["ssv"], v["qw"], v["xw"], v["qe"], v["xe"], v["vt"])},

 {"id": "pump", "title": {"fr": "Hydraulique des pompes", "ar": "هيدروليكا المضخات", "en": "Pump Hydraulics"},
  "fields": [F("q", "Débit (m³/h)", "التدفق", "Flow"),
             F("hds", "H refoulement stat. (m)", "شحنة الطرد الساكنة", "Discharge static"),
             F("hss", "H aspiration stat. (m)", "شحنة السحب الساكنة", "Suction static"),
             F("hf", "Perte frottement (m)", "فقد الاحتكاك", "Friction loss"),
             F("hm", "Pertes mineures (m)", "الفقد الثانوي", "Minor losses"),
             F("pd", "P refoulement (bar)", "ضغط الطرد", "Discharge P"),
             F("ps", "P aspiration (bar)", "ضغط السحب", "Suction P"),
             F("sg", "Densité relative", "الكثافة النسبية", "Spec. gravity"),
             F("ep", "Rend. pompe (0-1)", "كفاءة المضخة", "Pump eff."),
             F("em", "Rend. moteur (0-1)", "كفاءة المحرك", "Motor eff."),
             F("ev", "Rend. VFD (0-1)", "كفاءة VFD", "VFD eff."),
             F("f", "Facteur frottement f", "معامل الاحتكاك", "Friction factor"),
             F("L", "Longueur tuyau (m)", "طول الأنبوب", "Pipe length"),
             F("D", "Diamètre (m)", "القطر", "Diameter"),
             F("vel", "Vitesse (m/s)", "السرعة", "Velocity"),
             F("hb", "H barométrique (m)", "الشحنة البارومترية", "Barometric H"),
             F("hsf", "Perte aspiration (m)", "فقد السحب", "Suction friction"),
             F("hv", "H vapeur (m)", "ضغط البخار", "Vapor head")],
  "compute": lambda v: E.pump_hydraulics(v["q"], v["hds"], v["hss"], v["hf"], v["hm"],
          v["pd"], v["ps"], v["sg"], v["ep"], v["em"], v["ev"], v["f"],
          v["L"], v["D"], v["vel"], v["hb"], v["hsf"], v["hv"])},

 {"id": "ropump", "title": {"fr": "Pompes HP & récupération d'énergie", "ar": "مضخات الضغط العالي وERD", "en": "RO HP Pumps & ERD"},
  "fields": [F("ndp", "NDP (bar)", "NDP", "NDP"),
             F("oa", "Osmotique moy. (bar)", "الأسموزي الوسطي", "Avg osmotic"),
             F("dp", "ΔP étages (bar)", "فقد المراحل", "Stages ΔP"),
             F("pb", "Contre-pression perméat (bar)", "ضغط النفاذ العكسي", "Permeate back-P"),
             F("qf", "Q alimentation (m³/h)", "تدفق التغذية", "Feed flow"),
             F("qp", "Q perméat (m³/h)", "تدفق النفاذ", "Permeate flow"),
             F("qc", "Q concentrat (m³/h)", "تدفق المركز", "Concentrate flow"),
             F("pc", "P concentrat (bar)", "ضغط المركز", "Concentrate P"),
             F("erd", "Rend. ERD (0-1)", "كفاءة ERD", "ERD eff."),
             F("ep", "Rend. pompe (0-1)", "كفاءة المضخة", "Pump eff."),
             F("em", "Rend. moteur (0-1)", "كفاءة المحرك", "Motor eff.")],
  "compute": lambda v: E.ro_pumps(v["ndp"], v["oa"], v["dp"], v["pb"], v["qf"],
          v["qp"], v["qc"], v["pc"], v["erd"], v["ep"], v["em"])},

 {"id": "dosepump", "title": {"fr": "Pompes doseuses", "ar": "مضخات الجرعات", "en": "Dosing Pumps"},
  "fields": [F("q", "Débit eau brute (m³/h)", "تدفق الماء الخام", "Raw water flow"),
             F("d", "Dose cible (mg/L)", "الجرعة المستهدفة", "Target dose"),
             F("c", "Concentration (%)", "التركيز %", "Concentration"),
             F("sg", "Densité relative", "الكثافة النسبية", "Spec. gravity"),
             F("qm", "Q max nominale (L/h)", "التدفق الأقصى", "Max rated Q"),
             F("st", "Course (%)", "الشوط %", "Stroke %"),
             F("fr", "Fréquence (%)", "التردد %", "Frequency %"),
             F("vm", "Volume tiré (mL)", "الحجم المسحوب", "Volume drawn"),
             F("ts", "Temps (s)", "الزمن (ث)", "Time (s)"),
             F("pl", "P ligne max (bar)", "ضغط الخط الأقصى", "Max line P"),
             F("dv", "ΔP vanne injection (bar)", "فقد صمام الحقن", "Valve ΔP")],
  "compute": lambda v: E.dosing_pumps(v["q"], v["d"], v["c"], v["sg"], v["qm"],
          v["st"], v["fr"], v["vm"], v["ts"], v["pl"], v["dv"])},

 {"id": "inst", "title": {"fr": "Instrumentation (4-20 mA)", "ar": "الأتمتة والتحويل", "en": "Instrumentation"},
  "fields": [F("i", "Courant (mA)", "التيار", "Current"),
             F("pmin", "PV min", "الحد الأدنى", "PV min"),
             F("pmax", "PV max", "الحد الأقصى", "PV max"),
             F("cond", "Conductivité (µS/cm)", "التوصيلية", "Conductivity"),
             F("k", "Facteur k (0.55-0.70)", "المعامل k", "k factor")],
  "compute": lambda v: E.instrumentation(v["i"], v["pmin"], v["pmax"], v["cond"], v["k"])},

 {"id": "aff", "title": {"fr": "Lois d'affinité", "ar": "قوانين التناظر", "en": "Affinity Laws"},
  "fields": [F("q1", "Q1 (m³/h)", "التدفق 1", "Flow 1"),
             F("h1", "H1 (m)", "الشحنة 1", "Head 1"),
             F("p1", "P1 (kW)", "القدرة 1", "Power 1"),
             F("n1", "N1 (tr/min)", "السرعة 1", "Speed 1"),
             F("n2", "N2 (tr/min)", "السرعة 2", "Speed 2"),
             F("d1", "D1 (mm)", "القطر 1", "Diameter 1"),
             F("d2", "D2 (mm)", "القطر 2", "Diameter 2")],
  "compute": lambda v: E.affinity(v["q1"], v["h1"], v["p1"], v["n1"],
                                  v["n2"], v["d1"], v["d2"])},
]
'''

FILES["app.py"] = r'''
import customtkinter as ctk
from tkinter import messagebox
from core import i18n, projects
from modules.catalog import MODULES
from modules.base_module import BaseModule

ctk.set_appearance_mode("dark")

class SamwaterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1150x720")
        self.project = ctk.StringVar()
        self.customer = ctk.StringVar()
        self.frames = {}
        self._build()
        self.show(MODULES[0]["id"])

    def _build(self):
        self.title(i18n.t("app"))
        top = ctk.CTkFrame(self, height=48)
        top.pack(fill="x")
        ctk.CTkLabel(top, text=i18n.t("project")).pack(side="left", padx=4)
        ctk.CTkEntry(top, textvariable=self.project, width=120).pack(side="left")
        ctk.CTkLabel(top, text=i18n.t("customer")).pack(side="left", padx=4)
        ctk.CTkEntry(top, textvariable=self.customer, width=120).pack(side="left")
        ctk.CTkButton(top, text=i18n.t("save"), width=90,
                      command=self.save_project).pack(side="left", padx=6)
        ctk.CTkButton(top, text=i18n.t("open"), width=90,
                      command=self.open_project).pack(side="left")
        menu = ctk.CTkOptionMenu(top, values=list(i18n.LANGUAGES.values()),
                                 command=self.change_lang, width=110)
        menu.set(i18n.LANGUAGES[i18n.get_lang()])
        menu.pack(side="right", padx=8)
        side = ctk.CTkScrollableFrame(self, width=280)
        side.pack(side="left", fill="y")
        self.content = ctk.CTkFrame(self)
        self.content.pack(side="right", fill="both", expand=True)
        for m in MODULES:
            ctk.CTkButton(side, text=i18n.L(m["title"]), anchor="w",
                          command=lambda i=m["id"]: self.show(i)).pack(fill="x", padx=8, pady=3)

    def show(self, mid):
        for f in self.frames.values():
            f.pack_forget()
        if mid not in self.frames:
            defn = next(m for m in MODULES if m["id"] == mid)
            self.frames[mid] = BaseModule(self.content, defn, self)
        self.frames[mid].pack(fill="both", expand=True)

    def change_lang(self, name):
        code = [k for k, v in i18n.LANGUAGES.items() if v == name][0]
        i18n.set_lang(code)
        for w in self.winfo_children():
            w.destroy()
        self.frames = {}
        self._build()
        self.show(MODULES[0]["id"])

    def save_project(self):
        name = self.project.get().strip()
        if not name:
            messagebox.showwarning(i18n.t("err"), i18n.t("project"))
            return
        data = {"customer": self.customer.get(), "modules": {}}
        for mid, fr in self.frames.items():
            data["modules"][mid] = {k: e.get() for k, e in fr.entries.items()}
        projects.save(name, data)
        messagebox.showinfo("SAMWATER", i18n.t("saved"))

    def open_project(self):
        names = projects.list_all()
        if not names:
            return
        win = ctk.CTkToplevel(self)
        win.title(i18n.t("open"))
        for n in names:
            ctk.CTkButton(win, text=n,
                          command=lambda x=n: self._load(x, win)).pack(pady=3)

    def _load(self, name, win):
        data = projects.load(name)
        self.project.set(name)
        self.customer.set(data.get("customer", ""))
        for mid, vals in data.get("modules", {}).items():
            self.show(mid)
            for k, val in vals.items():
                e = self.frames[mid].entries.get(k)
                if e:
                    e.delete(0, "end")
                    e.insert(0, val)
        win.destroy()
'''

FILES["build.bat"] = r'''@echo off
cd /d "%~dp0"
pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed --name SAMWATER --collect-all customtkinter main.py
echo Done: dist\SAMWATER.exe
pause
'''

FILES["installer/SAMWATER.iss"] = r'''[Setup]
AppName=SAMWATER
AppVersion=1.0
DefaultDirName={pf}\SAMWATER
OutputBaseFilename=SAMWATER_Setup

[Files]
Source: "..\dist\SAMWATER.exe"; DestDir: "{app}"

[Icons]
Name: "{commondesktop}\SAMWATER"; Filename: "{app}\SAMWATER.exe"
'''

for path, content in FILES.items():
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
    print("[OK]", path)
print("=" * 40)
print("Done:", BASE)