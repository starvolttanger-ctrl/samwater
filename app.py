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
