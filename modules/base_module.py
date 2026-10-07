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
