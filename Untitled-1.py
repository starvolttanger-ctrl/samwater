# -*- coding: utf-8 -*-
"""SAMWATER — مولّد نسخة أندرويد (Kivy + Buildozer + GitHub Actions)"""
import os, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
AND = os.path.join(BASE, "android")

# 1) نسخ الحزم النقية (تعمل على أندرويد كما هي)
for pkg in ["core", "modules"]:
    dst = os.path.join(AND, pkg)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(os.path.join(BASE, pkg), dst)
    print("[OK] نسخ", pkg)

# 2) تطبيق Kivy
MAIN = r'''
# -*- coding: utf-8 -*-
import json, os
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from core import i18n, units
from modules.catalog import MODULES

Window.softinput_mode = "below_target"

def T(dic):
    s = i18n.L(dic) if isinstance(dic, dict) else str(dic)
    if i18n.get_lang() == "ar":
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(s))
        except Exception:
            return s
    return s

class HomeScreen(Screen):
    def __init__(self, app, **kw):
        super().__init__(name="home", **kw)
        self.app = app
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        root.add_widget(Label(text=T({"fr": "SAMWATER", "ar": "SAMWATER", "en": "SAMWATER"}),
                              size_hint_y=None, height=50, font_size="24sp", bold=True))
        top = GridLayout(cols=2, size_hint_y=None, height=100, spacing=6)
        top.add_widget(Label(text=T(i18n.S["project"])))
        self.project = TextInput(multiline=False, text=self.app.project)
        top.add_widget(self.project)
        top.add_widget(Label(text=T(i18n.S["customer"])))
        self.customer = TextInput(multiline=False, text=self.app.customer)
        top.add_widget(self.customer)
        root.add_widget(top)
        langs = list(i18n.LANGUAGES.values())
        self.lang = Spinner(text=i18n.LANGUAGES[i18n.get_lang()], values=langs,
                            size_hint_y=None, height=44)
        self.lang.bind(text=self.change_lang)
        root.add_widget(self.lang)
        sc = ScrollView()
        grid = GridLayout(cols=1, spacing=6, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for m in MODULES:
            b = Button(text=T(m["title"]), size_hint_y=None, height=52)
            b.bind(on_release=lambda btn, i=m["id"]: self.app.open_module(i))
            grid.add_widget(b)
        sc.add_widget(grid)
        root.add_widget(sc)
        self.add_widget(root)

    def change_lang(self, spinner, name):
        code = [k for k, v in i18n.LANGUAGES.items() if v == name][0]
        i18n.set_lang(code)
        self.app.project = self.project.text
        self.app.customer = self.customer.text
        self.build()

class ModuleScreen(Screen):
    def __init__(self, app, defn, **kw):
        super().__init__(name=defn["id"], **kw)
        self.app, self.defn = app, defn
        self.inputs, self.unit_spinners = {}, {}
        self.build()

    def build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=10, spacing=6)
        bar = BoxLayout(size_hint_y=None, height=48, spacing=6)
        back = Button(text="<", size_hint_x=None, width=50)
        back.bind(on_release=lambda b: setattr(self.app.sm, "current", "home"))
        bar.add_widget(back)
        bar.add_widget(Label(text=T(self.defn["title"]), font_size="18sp", bold=True))
        root.add_widget(bar)

        sc = ScrollView()
        grid = GridLayout(cols=1, spacing=4, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for f in self.defn["fields"]:
            grid.add_widget(Label(text=T(f["label"]), size_hint_y=None, height=34,
                                  halign="left"))
            row = BoxLayout(size_hint_y=None, height=44, spacing=6)
            ti = TextInput(multiline=False, input_filter="float")
            self.inputs[f["key"]] = ti
            row.add_widget(ti)
            if "ion" in f:
                sp = Spinner(text="mg/L", values=["mg/L", "meq/L"],
                             size_hint_x=None, width=110)
                self.unit_spinners[f["key"]] = (sp, f["ion"])
                row.add_widget(sp)
            grid.add_widget(row)
        sc.add_widget(grid)
        root.add_widget(sc)

        btns = BoxLayout(size_hint_y=None, height=50, spacing=6)
        bc = Button(text=T(i18n.S["calc"]))
        bc.bind(on_release=self.calculate)
        btns.add_widget(bc)
        bx = Button(text=T(i18n.S["clear"]))
        bx.bind(on_release=self.clear)
        btns.add_widget(bx)
        bs = Button(text=T(i18n.S["save"]))
        bs.bind(on_release=self.save)
        btns.add_widget(bs)
        root.add_widget(btns)
        self.result = Label(text="", size_hint_y=None, height=220,
                            halign="left", valign="top")
        root.add_widget(self.result)
        self.add_widget(root)

    def values(self):
        v = {}
        for k, ti in self.inputs.items():
            val = float(ti.text.replace(",", "."))
            if k in self.unit_spinners:
                sp, ion = self.unit_spinners[k]
                val = units.to_mg_l(val, sp.text, ion)
            v[k] = val
        return v

    def calculate(self, *_):
        try:
            res = self.defn["compute"](self.values())
            self.result.text = "\n".join(f"{k} = {val:.6g}" for k, val in res.items())
        except ValueError:
            self.result.text = T(i18n.S["fill"])
        except Exception as ex:
            self.result.text = str(ex)

    def clear(self, *_):
        for ti in self.inputs.values():
            ti.text = ""
        self.result.text = ""

    def save(self, *_):
        data = {"customer": self.app.customer,
                "values": {k: ti.text for k, ti in self.inputs.items()}}
        path = os.path.join(self.app.user_data_dir,
                            (self.app.project or "projet") + "_" + self.defn["id"] + ".json")
        os.makedirs(self.app.user_data_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.result.text = T(i18n.S["saved"]) + "\n" + path

class SamwaterAndroid(App):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.project, self.customer = "", ""

    def build(self):
        self.title = "SAMWATER"
        self.sm = ScreenManager()
        self.home = HomeScreen(self)
        self.sm.add_widget(self.home)
        self.screens = {}
        return self.sm

    def open_module(self, mid):
        if mid not in self.screens:
            defn = next(m for m in MODULES if m["id"] == mid)
            s = ModuleScreen(self, defn)
            self.screens[mid] = s
            self.sm.add_widget(s)
        self.sm.current = mid

SamwaterAndroid().run()
'''

with open(os.path.join(AND, "main.py"), "w", encoding="utf-8") as f:
    f.write(MAIN.lstrip("\n"))
print("[OK] android/main.py")

# 3) ملف Buildozer
SPEC = '''[app]
title = SAMWATER
package.name = samwater
package.domain = org.samwater
source.dir = .
source.include_exts = py,png,jpg,json
version = 1.0
requirements = python3,kivy,fpdf2,arabic-reshaper,python-bidi
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
'''
with open(os.path.join(AND, "buildozer.spec"), "w", encoding="utf-8") as f:
    f.write(SPEC)
print("[OK] android/buildozer.spec")

# 4) GitHub Action لبناء APK سحابيًا
WF = '''name: Build APK
on: [push, workflow_dispatch]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: ArtemSBulgakov/buildozer-action@v1
        id: buildozer
        with:
          workdir: android
          buildozer_version: stable
      - uses: actions/upload-artifact@v4
        with:
          name: samwater-apk
          path: ${{ steps.buildozer.outputs.filename }}
'''
wfd = os.path.join(BASE, ".github", "workflows")
os.makedirs(wfd, exist_ok=True)
with open(os.path.join(wfd, "build-apk.yml"), "w", encoding="utf-8") as f:
    f.write(WF)
print("[OK] .github/workflows/build-apk.yml")
print("=" * 40)
print("Done:", AND)