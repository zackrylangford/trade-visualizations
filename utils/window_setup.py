import tkinter as tk
from tkinter import ttk, Canvas

def create_scrollable_window(root):
    # Create a canvas and a scrollbar
    canvas = Canvas(root)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    notebook = ttk.Notebook(scrollable_frame)
    tab_overview = ttk.Frame(notebook)
    tab_winning_percentage = ttk.Frame(notebook)
    tab_daily_profit_loss = ttk.Frame(notebook)
    tab_trade_size = ttk.Frame(notebook)
    notebook.add(tab_overview, text="Overview")
    notebook.add(tab_winning_percentage, text="Winning % by Time of Day")
    notebook.add(tab_daily_profit_loss, text="Daily Profit/Loss")
    notebook.add(tab_trade_size, text="Trade Size Over Time")
    notebook.pack(expand=1, fill="both")

    refresh_button = tk.Button(scrollable_frame, text="Refresh Data")
    refresh_button.pack(pady=10)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return notebook, tab_overview, tab_winning_percentage, tab_daily_profit_loss, tab_trade_size, refresh_button
