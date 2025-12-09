# theme.py
import tkinter as tk
from tkinter import ttk

# Color scheme
BG_COLOR = "#0b1120"      # main background (very dark blue)
CARD_BG = "#111827"       # panel/card background
ACCENT = "#2563eb"        # primary blue
ACCENT_LIGHT = "#3b82f6"  # lighter blue for hover/active
TEXT_MAIN = "#f9fafb"     # main text color
TEXT_MUTED = "#9ca3af"    # secondary/muted text

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_SUBTITLE = ("Segoe UI", 12)
FONT_BUTTON = ("Segoe UI", 11, "bold")
FONT_BODY = ("Segoe UI", 11)


def apply_theme(root: tk.Tk) -> None:
    """
    Apply a consistent dark theme and ttk styles to the given Tk root window.
    """
    root.configure(bg=BG_COLOR)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        # If 'clam' is not available, silently fall back to default
        pass

    # General frames and labels
    style.configure("TFrame", background=BG_COLOR)
    style.configure("Card.TFrame", background=CARD_BG)
    style.configure("TLabel", background=BG_COLOR, foreground=TEXT_MAIN, font=FONT_BODY)
    style.configure("Header.TLabel", background=BG_COLOR, foreground=TEXT_MAIN, font=FONT_TITLE)
    style.configure("Muted.TLabel", background=BG_COLOR, foreground=TEXT_MUTED, font=FONT_SUBTITLE)

    # Accent buttons
    style.configure(
        "Accent.TButton",
        font=FONT_BUTTON,
        padding=6
    )
    style.map(
        "Accent.TButton",
        foreground=[("disabled", "#9ca3af"), ("!disabled", "#ffffff")],
        background=[("pressed", ACCENT_LIGHT), ("active", ACCENT_LIGHT), ("!active", ACCENT)],
    )

    # Treeview styling
    style.configure(
        "Treeview",
        background=CARD_BG,
        fieldbackground=CARD_BG,
        foreground=TEXT_MAIN,
        rowheight=24
    )
    style.configure(
        "Treeview.Heading",
        background="#1f2937",
        foreground=TEXT_MAIN
    )
