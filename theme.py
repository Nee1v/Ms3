# theme.py
import tkinter as tk
from tkinter import ttk

BG_COLOR = "#2b213a"       # main app background
CARD_BG = "#f7f0e9"        # panels / cards
ACCENT = "#00c2c7"         # primary accent (buttons, focus)
ACCENT_LIGHT = "#ff6fb5"   # hover / active accent
OUTLINE_COLOR = "#3b2731"
TEXT_MAIN = "#1b1022"      # almost-black plum for main text
TEXT_MUTED = "#7a6f80"     # soft grey-purple for secondary text
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_SUBTITLE = ("Segoe UI", 12)
FONT_BUTTON = ("Segoe UI", 11, "bold")
FONT_BODY = ("Segoe UI", 11)
INPUT_BG = "#F4E9F3"        # light pastel lavender (soft, readable)
INPUT_FG = "#2B0E34"        # dark plum text


def apply_theme(root: tk.Tk) -> None:
    """
    Apply a pastel retro / vaporwave-inspired theme and ttk styles
    to the given Tk root window.
    """
    root.configure(bg=BG_COLOR)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        # If 'clam' is not available, just use default
        pass

    # ---------- Frames & Labels ----------
    style.configure("TFrame", background=BG_COLOR)
    style.configure("Card.TFrame", background=CARD_BG)

    style.configure(
        "TLabel",
        background=BG_COLOR,
        foreground=TEXT_MAIN,
        font=FONT_BODY
    )
    style.configure(
        "Header.TLabel",
        background=BG_COLOR,
        foreground=TEXT_MAIN,
        font=FONT_TITLE
    )
    style.configure(
        "Muted.TLabel",
        background=BG_COLOR,
        foreground=TEXT_MUTED,
        font=FONT_SUBTITLE
    )

    # Accent Button style
    style.configure(
        "Accent.TButton",
        font=FONT_BUTTON,
        padding=6,
        foreground="#ffffff",
        background=ACCENT,
        bordercolor=OUTLINE_COLOR,
        focusthickness=2,
        focuscolor=ACCENT_LIGHT
    )
    style.map(
        "Accent.TButton",
        foreground=[
            ("disabled", "#d4d4d4"),
            ("!disabled", "#ffffff"),
        ],
        background=[
            ("pressed", ACCENT_LIGHT),
            ("active", ACCENT_LIGHT),
            ("!active", ACCENT),
        ],
        bordercolor=[
            ("focus", OUTLINE_COLOR),
            ("!focus", OUTLINE_COLOR),
        ]
    )

    #Treeview style
    style.configure(
        "Treeview",
        background=CARD_BG,
        fieldbackground=CARD_BG,
        foreground=TEXT_MAIN,
        rowheight=24,
        bordercolor=OUTLINE_COLOR,
        borderwidth=1
    )
    style.configure(
        "Treeview.Heading",
        background="#f0d7e8",   # soft pink-ish header
        foreground=TEXT_MAIN,
        relief="flat"
    )
    style.map(
        "Treeview.Heading",
        background=[
            ("active", "#ffd1f0"),
            ("!active", "#f0d7e8"),
        ]
    )
    style.configure(
        "TButton",
        font=FONT_BUTTON,
        padding=5
    )
