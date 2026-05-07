"""Tycron desktop notebook prototype inspired by GoodNotes.

Run with:
    python test.py

The app is intentionally self-contained and uses only Tkinter from the Python
standard library so it can run without installing dependencies.
"""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import colorchooser, filedialog, messagebox, simpledialog
from typing import Callable


APP_TITLE = "Tycron"
SIDEBAR_BG = "#f4f4f4"
SELECTED_BLUE = "#d9ebfc"
PRIMARY_BLUE = "#0877d9"
INK = "#121212"
MUTED = "#707070"
TEAL = "#1b6668"
PAPER = "#fffdf8"
BORDER = "#d7d7d7"


@dataclass
class Notebook:
    """A small in-memory notebook record used by the prototype library."""

    title: str
    kind: str = "Not Defteri"
    pages: int = 1


class TycronApp(tk.Tk):
    """A Tycron notebook UI prototype with library, account drawer, and editor."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1024x680")
        self.minsize(900, 600)
        self.configure(bg="white")

        self.notebooks: list[Notebook] = []
        self.current_notebook: Notebook | None = None
        self.current_section = "Belgeler"
        self.pen_color = "#111111"
        self.pen_width = 4
        self.last_xy: tuple[int, int] | None = None
        self.overlay: tk.Frame | None = None

        self._build_window_chrome()
        self._build_shell()
        self.show_library()

    def _build_window_chrome(self) -> None:
        chrome = tk.Frame(self, bg="white", height=30)
        chrome.pack(fill="x", side="top")
        tk.Label(chrome, text="▱", fg=PRIMARY_BLUE, bg="white", font=("Segoe UI", 14)).pack(
            side="left", padx=(8, 3)
        )
        tk.Label(chrome, text=APP_TITLE, bg="white", fg=INK, font=("Segoe UI", 9)).pack(
            side="left"
        )
        for symbol in ("×", "□", "−", "⋯"):
            tk.Label(chrome, text=symbol, bg="white", fg=INK, font=("Segoe UI", 14)).pack(
                side="right", padx=12
            )

    def _build_shell(self) -> None:
        self.shell = tk.Frame(self, bg="white")
        self.shell.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(self.shell, bg=SIDEBAR_BG, width=238)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self.shell, bg="white")
        self.content.pack(side="left", fill="both", expand=True)

        tk.Label(
            self.sidebar,
            text=APP_TITLE,
            bg=SIDEBAR_BG,
            fg=INK,
            font=("Segoe UI", 32),
            anchor="w",
        ).pack(fill="x", padx=14, pady=(78, 22))

        self.nav_buttons: dict[str, tk.Frame] = {}
        nav_items = [
            ("📁", "Belgeler"),
            ("🔖", "Sık Kullanılanlar"),
            ("♟", "Paylaşılan"),
            ("🏬", "Alışveriş merkezi"),
        ]
        for icon, label in nav_items:
            self._nav_button(icon, label).pack(fill="x", padx=14, pady=2)

        tk.Frame(self.sidebar, bg="#d0d0d0", height=1).pack(fill="x", padx=14, pady=16)
        self._nav_button("🗑", "Çöp").pack(fill="x", padx=14, pady=2)

    def _nav_button(self, icon: str, label: str) -> tk.Frame:
        row = tk.Frame(self.sidebar, bg=SIDEBAR_BG, cursor="hand2")
        icon_label = tk.Label(row, text=icon, bg=SIDEBAR_BG, fg=INK, font=("Segoe UI Emoji", 17), width=2)
        text_label = tk.Label(row, text=label, bg=SIDEBAR_BG, fg=INK, font=("Segoe UI", 12), anchor="w")
        icon_label.pack(side="left", padx=(10, 8), pady=10)
        text_label.pack(side="left", fill="x", expand=True)
        self.nav_buttons[label] = row

        def on_click(_: tk.Event | None = None, target: str = label) -> None:
            self.current_section = target
            self.show_library()

        row.bind("<Button-1>", on_click)
        icon_label.bind("<Button-1>", on_click)
        text_label.bind("<Button-1>", on_click)
        return row

    def _set_active_nav(self) -> None:
        for label, row in self.nav_buttons.items():
            bg = SELECTED_BLUE if label == self.current_section else SIDEBAR_BG
            row.configure(bg=bg)
            for child in row.winfo_children():
                child.configure(bg=bg)

    def _clear_content(self) -> None:
        self._hide_overlay()
        for child in self.content.winfo_children():
            child.destroy()

    def show_library(self) -> None:
        self.current_notebook = None
        self._set_active_nav()
        self._clear_content()

        header = tk.Frame(self.content, bg="white")
        header.pack(fill="x", padx=(26, 16), pady=(70, 0))
        tk.Label(
            header,
            text=self.current_section,
            bg="white",
            fg=INK,
            font=("Segoe UI", 30, "bold"),
            anchor="w",
        ).pack(side="left")
        tk.Button(
            header,
            text="⚙",
            bg="white",
            fg=INK,
            relief="flat",
            font=("Segoe UI", 20),
            cursor="hand2",
            command=self.show_account_drawer,
        ).pack(side="right")
        tk.Frame(self.content, bg=BORDER, height=1).pack(fill="x", padx=(26, 16), pady=(2, 0))

        body = tk.Frame(self.content, bg="white")
        body.pack(fill="both", expand=True)

        if self.current_section == "Belgeler" and self.notebooks:
            self._render_notebook_grid(body)
        else:
            self._render_empty_state(body)

    def _render_empty_state(self, parent: tk.Frame) -> None:
        card = tk.Frame(parent, bg="white")
        card.place(relx=0.54, rely=0.48, anchor="center")
        art = tk.Canvas(card, width=210, height=180, bg="white", highlightthickness=0)
        art.pack()
        self._draw_empty_illustration(art)
        tk.Label(
            card,
            text="Kütüphanenizi canlandırmaya hazır mısınız?",
            bg="white",
            fg=INK,
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(8, 4))
        tk.Label(
            card,
            text="Başlamak için bir not defteri ekleyin, bir belgeyi içeri aktarın veya\nbir klasör oluşturun",
            bg="white",
            fg=MUTED,
            font=("Segoe UI", 11),
            justify="center",
        ).pack()
        tk.Button(
            card,
            text="＋   Yeni   ˅",
            bg=PRIMARY_BLUE,
            fg="white",
            activebackground="#0568bf",
            activeforeground="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 11),
            padx=18,
            pady=12,
            cursor="hand2",
            command=self.show_new_menu,
        ).pack(pady=24)

    def _draw_empty_illustration(self, canvas: tk.Canvas) -> None:
        canvas.create_arc(38, 30, 154, 130, start=20, extent=140, outline=TEAL, width=2, style="arc")
        canvas.create_arc(54, 42, 138, 116, start=20, extent=140, outline=TEAL, width=2, style="arc")
        canvas.create_line(74, 35, 80, 22, 92, 22, 100, 12, 111, 24, 123, 24, 134, 38, fill=TEAL, width=2)
        canvas.create_rectangle(84, 62, 146, 145, outline=TEAL, width=2, fill="#d8e8eb")
        canvas.create_line(95, 96, 101, 104, 110, 96, fill=TEAL, width=2, smooth=True)
        canvas.create_rectangle(126, 62, 137, 78, outline=TEAL, width=2, fill="#bcd6dc")
        canvas.create_polygon(48, 76, 83, 88, 70, 138, 35, 126, fill="#e7f0f2", outline=TEAL, width=2)
        canvas.create_rectangle(52, 112, 74, 137, outline=TEAL, width=2, fill="#d9e9ed")
        canvas.create_oval(59, 116, 66, 123, outline=TEAL, width=2)
        canvas.create_arc(55, 121, 72, 137, start=20, extent=140, outline=TEAL, width=2, style="arc")
        canvas.create_polygon(144, 105, 187, 116, 176, 151, 132, 141, fill="#edf6f6", outline=TEAL, width=2)
        canvas.create_line(147, 104, 174, 68, 187, 76, 158, 111, fill=TEAL, width=7)
        canvas.create_line(177, 70, 190, 78, fill="#f7f1df", width=5)

    def _render_notebook_grid(self, parent: tk.Frame) -> None:
        grid = tk.Frame(parent, bg="white")
        grid.pack(fill="both", expand=True, padx=34, pady=32)
        for index, notebook in enumerate(self.notebooks):
            tile = tk.Frame(grid, bg="white", highlightbackground=BORDER, highlightthickness=1, cursor="hand2")
            tile.grid(row=index // 4, column=index % 4, padx=14, pady=14, sticky="n")
            cover = tk.Canvas(tile, width=132, height=166, bg="white", highlightthickness=0)
            cover.pack(padx=14, pady=(14, 8))
            self._draw_notebook_cover(cover, index)
            tk.Label(tile, text=notebook.title, bg="white", fg=INK, font=("Segoe UI", 11, "bold")).pack()
            tk.Label(tile, text=f"{notebook.pages} sayfa • {notebook.kind}", bg="white", fg=MUTED, font=("Segoe UI", 9)).pack(
                pady=(2, 12)
            )
            tile.bind("<Button-1>", lambda _event, item=notebook: self.open_notebook(item))
            for child in tile.winfo_children():
                child.bind("<Button-1>", lambda _event, item=notebook: self.open_notebook(item))

        tk.Button(
            parent,
            text="＋   Yeni   ˅",
            bg=PRIMARY_BLUE,
            fg="white",
            activebackground="#0568bf",
            activeforeground="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 11),
            padx=18,
            pady=12,
            cursor="hand2",
            command=self.show_new_menu,
        ).place(relx=0.5, rely=0.92, anchor="center")

    def _draw_notebook_cover(self, canvas: tk.Canvas, index: int) -> None:
        colors = ["#d8e8eb", "#f8e7a8", "#e8dff5", "#d8eedf"]
        canvas.create_rectangle(18, 8, 114, 158, fill=colors[index % len(colors)], outline=TEAL, width=2)
        canvas.create_rectangle(28, 24, 104, 54, fill="white", outline=TEAL, width=1)
        for y in (78, 96, 114):
            canvas.create_line(32, y, 100, y, fill=TEAL, width=1)
        canvas.create_line(36, 134, 70, 120, 94, 136, fill=TEAL, width=2, smooth=True)

    def show_new_menu(self) -> None:
        menu = self._overlay_box(width=216, height=275, relx=0.52, rely=0.53)
        actions: list[tuple[str, str, Callable[[], None]]] = [
            ("▣", "Not Defteri", self.create_notebook),
            ("□", "Klasör", lambda: self.create_named_item("Klasör")),
            ("⇩", "İçe Aktar", self.import_document),
            ("▧", "Resim", self.import_image),
            ("✎", "Hızlı not", self.quick_note),
        ]
        for icon, label, command in actions:
            row = tk.Frame(menu, bg="#f7fafb", cursor="hand2")
            row.pack(fill="x", padx=16, pady=(9, 2))
            tk.Label(row, text=icon, bg="#f7fafb", fg=INK, font=("Segoe UI", 16), width=2).pack(side="left")
            tk.Label(row, text=label, bg="#f7fafb", fg=INK, font=("Segoe UI", 10), anchor="w").pack(
                side="left", padx=10
            )
            row.bind("<Button-1>", lambda _event, cmd=command: self._run_overlay_action(cmd))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda _event, cmd=command: self._run_overlay_action(cmd))
        tk.Frame(menu, bg=BORDER, height=1).pack(fill="x", padx=14, pady=(10, 6))
        tk.Label(
            menu,
            text='İpucu: Bir Hızlı not oluşturmak için\n"+ Yeni" düğmesine çift dokunun',
            bg="#f7fafb",
            fg=MUTED,
            font=("Segoe UI", 8),
            justify="left",
        ).pack(anchor="w", padx=18)

    def _overlay_box(self, width: int, height: int, relx: float, rely: float) -> tk.Frame:
        self._hide_overlay()
        self.overlay = tk.Frame(
            self.content,
            bg="#f7fafb",
            highlightbackground="#cfcfcf",
            highlightthickness=1,
        )
        self.overlay.place(relx=relx, rely=rely, anchor="center", width=width, height=height)
        return self.overlay

    def _run_overlay_action(self, command: Callable[[], None]) -> None:
        self._hide_overlay()
        command()

    def _hide_overlay(self) -> None:
        if self.overlay is not None:
            self.overlay.destroy()
            self.overlay = None

    def create_named_item(self, kind: str) -> None:
        title = simpledialog.askstring(kind, f"{kind} adı:", parent=self)
        if not title:
            return
        self.notebooks.append(Notebook(title=title, kind=kind))
        self.current_section = "Belgeler"
        self.show_library()

    def create_notebook(self) -> None:
        title = simpledialog.askstring("Not Defteri", "Not defteri adı:", initialvalue="Yeni Not Defteri", parent=self)
        if not title:
            return
        notebook = Notebook(title=title, kind="Not Defteri")
        self.notebooks.append(notebook)
        self.open_notebook(notebook)

    def quick_note(self) -> None:
        notebook = Notebook(title=f"Hızlı Not {len(self.notebooks) + 1}", kind="Hızlı not")
        self.notebooks.append(notebook)
        self.open_notebook(notebook)

    def import_document(self) -> None:
        path = filedialog.askopenfilename(
            title="Belge içe aktar",
            filetypes=[("Belgeler", "*.pdf *.docx *.txt"), ("Tüm dosyalar", "*.*")],
        )
        if path:
            self.notebooks.append(Notebook(title=path.split("/")[-1], kind="İçe aktarıldı"))
            self.show_library()

    def import_image(self) -> None:
        path = filedialog.askopenfilename(
            title="Resim seç",
            filetypes=[("Resimler", "*.png *.jpg *.jpeg *.gif"), ("Tüm dosyalar", "*.*")],
        )
        if path:
            self.notebooks.append(Notebook(title=path.split("/")[-1], kind="Resim"))
            self.show_library()

    def show_account_drawer(self) -> None:
        self._hide_overlay()
        scrim = tk.Frame(self.content, bg="#eeeeee")
        scrim.place(relx=0, rely=0, relwidth=1, relheight=1)
        drawer = tk.Frame(scrim, bg="#fbfbfb")
        drawer.place(relx=1, rely=0, relheight=1, width=352, anchor="ne")
        self.overlay = scrim

        top = tk.Frame(drawer, bg="#fbfbfb")
        top.pack(fill="x", padx=16, pady=(22, 18))
        tk.Button(top, text="×", bg="#fbfbfb", relief="flat", fg=INK, font=("Segoe UI", 20), command=self._hide_overlay).pack(
            side="right"
        )
        user = tk.Frame(drawer, bg="#fbfbfb")
        user.pack(fill="x", padx=26, pady=(0, 18))
        tk.Label(user, text="◎", bg="#eeeeee", fg=INK, font=("Segoe UI", 20), width=2).pack(side="left", padx=(0, 12))
        names = tk.Frame(user, bg="#fbfbfb")
        names.pack(side="left")
        tk.Label(names, text="Burak Dayan", bg="#fbfbfb", fg=INK, font=("Segoe UI", 12)).pack(anchor="w")
        tk.Label(names, text="burakdayn@gmail.com", bg="#fbfbfb", fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")
        self._subscription_card(drawer)
        drawer_items = [
            ("♙", "Hesabı yönet", self.show_manage_account),
            ("▱", "Not defteri şablonlarınızı yönetin", None),
            ("⌘", "Ayarlar", None),
            ("?", "Yardım", None),
            ("▱", "Hakkında", None),
        ]
        for icon, label, command in drawer_items:
            self._drawer_row(drawer, icon, label, command).pack(fill="x", padx=26, pady=7)
        tk.Label(drawer, text="↪   Çıkış Yap", bg="#fbfbfb", fg=INK, font=("Segoe UI", 11), anchor="w").pack(
            side="bottom", fill="x", padx=32, pady=18
        )

    def _subscription_card(self, parent: tk.Frame) -> None:
        card = tk.Frame(parent, bg="white", highlightbackground="#a9a9a9", highlightthickness=1)
        card.pack(fill="x", padx=16, pady=(0, 22))
        tk.Label(card, text="🔒", bg="white", fg=INK, font=("Segoe UI Emoji", 18)).pack(side="left", padx=(16, 12), pady=18)
        text = tk.Frame(card, bg="white")
        text.pack(side="left", fill="x", expand=True, pady=14)
        tk.Label(text, text="Abone ol ve sınırsız kullan", bg="white", fg=INK, font=("Segoe UI", 11)).pack(anchor="w")
        tk.Label(
            text,
            text="sınırsız not defteri düzenlemesi ve daha\nfazlasına kavuşun!",
            bg="white",
            fg=MUTED,
            font=("Segoe UI", 8),
            justify="left",
        ).pack(anchor="w")

    def _drawer_row(self, parent: tk.Frame, icon: str, label: str, command: Callable[[], None] | None) -> tk.Frame:
        row = tk.Frame(parent, bg="#fbfbfb", cursor="hand2" if command else "")
        tk.Label(row, text=icon, bg="#fbfbfb", fg=INK, font=("Segoe UI", 16), width=2).pack(side="left")
        tk.Label(row, text=label, bg="#fbfbfb", fg=INK, font=("Segoe UI", 11), anchor="w").pack(side="left", padx=14)
        if command:
            row.bind("<Button-1>", lambda _event: command())
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda _event: command())
        return row

    def show_manage_account(self) -> None:
        if self.overlay is not None:
            self.overlay.destroy()
        scrim = tk.Frame(self.content, bg="#eeeeee")
        scrim.place(relx=0, rely=0, relwidth=1, relheight=1)
        drawer = tk.Frame(scrim, bg="#fbfbfb")
        drawer.place(relx=1, rely=0, relheight=1, width=354, anchor="ne")
        self.overlay = scrim
        header = tk.Frame(drawer, bg="#fbfbfb")
        header.pack(fill="x", padx=22, pady=(20, 22))
        tk.Button(header, text="‹", bg="#fbfbfb", relief="flat", fg=INK, font=("Segoe UI", 23), command=self.show_account_drawer).pack(
            side="left"
        )
        tk.Label(header, text="Hesabı yönet", bg="#fbfbfb", fg=INK, font=("Segoe UI", 15, "bold")).pack(side="left", padx=8)
        tk.Button(header, text="×", bg="#fbfbfb", relief="flat", fg=INK, font=("Segoe UI", 20), command=self._hide_overlay).pack(
            side="right"
        )
        self._subscription_card(drawer)
        self._info_section(drawer, "ÜYELİK BİLGİLERİ", [("Üyelik türü", "Ücretsiz"), ("Üyelik başlangıç tarihi", "22 Haz 2025"), ("Kupon kodunu kullan", "")])
        self._info_section(drawer, "HESAP BİLGİLERİ", [("Kullanıcı adı", "Burak Dayan  ›"), ("Kullanıcı kimliği", "cfa04983-827e-40ee-8...  ⧉"), ("E-posta", "burakdayn@gmail.com"), ("Bağlantı Kanalı", "Google")])
        tk.Label(drawer, text="Hesabı sil                                      ›", bg="#fbfbfb", fg="#e92828", font=("Segoe UI", 11), anchor="w").pack(
            fill="x", padx=32, pady=(16, 0)
        )

    def _info_section(self, parent: tk.Frame, title: str, rows: list[tuple[str, str]]) -> None:
        frame = tk.Frame(parent, bg="#fbfbfb")
        frame.pack(fill="x", padx=32, pady=(8, 18))
        tk.Label(frame, text=title, bg="#fbfbfb", fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 8))
        for label, value in rows:
            row = tk.Frame(frame, bg="#fbfbfb")
            row.pack(fill="x", pady=9)
            tk.Label(row, text=label, bg="#fbfbfb", fg=INK, font=("Segoe UI", 10), anchor="w").pack(side="left")
            tk.Label(row, text=value, bg="#fbfbfb", fg=MUTED, font=("Segoe UI", 9), anchor="e").pack(side="right")

    def open_notebook(self, notebook: Notebook) -> None:
        self._set_active_nav()
        self._clear_content()
        self.current_notebook = notebook
        toolbar = tk.Frame(self.content, bg="white", height=66)
        toolbar.pack(fill="x", padx=18, pady=(14, 0))
        tk.Button(toolbar, text="‹ Belgeler", bg="white", fg=INK, relief="flat", font=("Segoe UI", 11), command=self.show_library).pack(
            side="left", padx=(0, 14)
        )
        tk.Label(toolbar, text=notebook.title, bg="white", fg=INK, font=("Segoe UI", 15, "bold")).pack(side="left")
        tools = tk.Frame(toolbar, bg="white")
        tools.pack(side="right")
        for label, command in [
            ("Kalem", self.choose_pen),
            ("Silgi", self.erase_canvas),
            ("Renk", self.choose_color),
            ("Sayfa +", self.add_page),
        ]:
            tk.Button(tools, text=label, bg="#f5f7f9", fg=INK, relief="flat", padx=12, pady=8, command=command).pack(
                side="left", padx=4
            )
        paper_wrap = tk.Frame(self.content, bg="#eeeeee")
        paper_wrap.pack(fill="both", expand=True, padx=18, pady=16)
        self.canvas = tk.Canvas(paper_wrap, bg=PAPER, highlightthickness=1, highlightbackground=BORDER)
        self.canvas.pack(fill="both", expand=True, padx=44, pady=28)
        self._draw_paper_lines()
        self.canvas.bind("<Button-1>", self._start_draw)
        self.canvas.bind("<B1-Motion>", self._draw)
        self.canvas.bind("<ButtonRelease-1>", lambda _event: setattr(self, "last_xy", None))

    def _draw_paper_lines(self) -> None:
        self.canvas.delete("paper-line")
        self.canvas.update_idletasks()
        width = self.canvas.winfo_width() or 700
        for y in range(58, 900, 34):
            self.canvas.create_line(48, y, width - 48, y, fill="#e8ddd0", tags="paper-line")
        self.canvas.create_line(82, 30, 82, 1200, fill="#f1bbb3", tags="paper-line")

    def _start_draw(self, event: tk.Event) -> None:
        self.last_xy = (event.x, event.y)

    def _draw(self, event: tk.Event) -> None:
        if self.last_xy is None:
            self.last_xy = (event.x, event.y)
            return
        x0, y0 = self.last_xy
        self.canvas.create_line(
            x0,
            y0,
            event.x,
            event.y,
            fill=self.pen_color,
            width=self.pen_width,
            capstyle="round",
            joinstyle="round",
            smooth=True,
        )
        self.last_xy = (event.x, event.y)

    def choose_pen(self) -> None:
        width = simpledialog.askinteger("Kalem", "Kalem kalınlığı:", initialvalue=self.pen_width, minvalue=1, maxvalue=20, parent=self)
        if width:
            self.pen_width = width

    def choose_color(self) -> None:
        color = colorchooser.askcolor(title="Kalem rengi", initialcolor=self.pen_color, parent=self)[1]
        if color:
            self.pen_color = color

    def erase_canvas(self) -> None:
        if messagebox.askyesno("Silgi", "Bu sayfadaki çizimleri temizlemek ister misiniz?", parent=self):
            self.canvas.delete("all")
            self._draw_paper_lines()

    def add_page(self) -> None:
        if self.current_notebook:
            self.current_notebook.pages += 1
        self.canvas.delete("all")
        self._draw_paper_lines()
        messagebox.showinfo("Yeni sayfa", "Yeni boş sayfa eklendi.", parent=self)


def main() -> None:
    app = TycronApp()
    app.mainloop()


if __name__ == "__main__":
    main()
