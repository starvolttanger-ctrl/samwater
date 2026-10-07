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
