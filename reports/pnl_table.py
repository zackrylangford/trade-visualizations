import datetime
import pandas as pd
import tkinter as tk

def create_pnl_table(frame, df):
    # Ensure CustomTradeDay is datetime
    df['CustomTradeDay'] = pd.to_datetime(df['CustomTradeDay'])

    # Ensure NetPnL is numeric
    df['NetPnL'] = pd.to_numeric(df['NetPnL'], errors='coerce')

    # Create a complete date range from the min to max CustomTradeDay
    all_days = pd.date_range(start=df['CustomTradeDay'].min(), end=df['CustomTradeDay'].max(), freq='D')

    # Merge with the original DataFrame to include all days
    pnl_summary = pd.DataFrame(all_days, columns=['CustomTradeDay']).merge(df, on='CustomTradeDay', how='left')

    # Fill missing NetPnL values with 0
    pnl_summary['NetPnL'] = pnl_summary['NetPnL'].fillna(0)

    # Group by date and sum NetPnL
    pnl_summary = pnl_summary.groupby(pnl_summary['CustomTradeDay'].dt.date).agg({
        'NetPnL': 'sum'
    }).reset_index()

    # Create the calendar
    current_month = datetime.datetime.now().month
    first_day = pnl_summary['CustomTradeDay'].min()
    start_of_week = first_day - datetime.timedelta(days=first_day.weekday())

    # Find the number of weeks to display
    num_weeks = (pnl_summary['CustomTradeDay'].max() - start_of_week).days // 7 + 1

    # Iterate over the calendar days and create labels
    date = start_of_week
    for week in range(num_weeks):
        for day in range(7):
            daily_pnl = pnl_summary[pnl_summary['CustomTradeDay'] == date]['NetPnL'].values
            pnl_value = daily_pnl[0] if daily_pnl else 0
            day_label = tk.Label(frame, text=f"{date.strftime('%Y-%m-%d')}\n{pnl_value:.2f}",
                                 bg="green" if pnl_value > 0 else "red" if pnl_value < 0 else "gray",
                                 fg="white", padx=5, pady=5)
            day_label.grid(row=week, column=day, padx=5, pady=5, sticky="nsew")
            date += datetime.timedelta(days=1)

# Ensure the function is used correctly in your main.py
def update_overview(tab, df):
    for widget in tab.winfo_children():
        widget.destroy()
    
    overview_frame = tk.Frame(tab)
    overview_frame.pack(fill=tk.BOTH, expand=True)

    # Add PnL calendar table
    pnl_table_frame = tk.Frame(overview_frame)
    pnl_table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    create_pnl_table(pnl_table_frame, df)

    # Add line graph for account balance
    balance_graph_frame = tk.Frame(overview_frame)
    balance_graph_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    create_balance_graph(balance_graph_frame, df)
