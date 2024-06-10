import os
import sys
import psutil
import tkinter as tk
from tkinter import ttk, messagebox, Label
from PIL import Image, ImageTk
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pytz import timezone

data_fetched = False

def check_if_running():
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'python3' and 'main.py' in proc.info['cmdline'] and proc.info['pid'] != current_pid:
            print(f"Found another instance of main.py running with PID {proc.info['pid']}. Exiting.")
            sys.exit()

def fetch_and_process_data():
    global data_fetched
    try:
        api_endpoint = "https://adhp0jlvy5.execute-api.us-east-1.amazonaws.com/default/visualize-trade-data"
        response = requests.get(api_endpoint)
        data = response.json()

        if 'error' in data or 'message' in data:
            messagebox.showerror("Error", f"Error fetching data from API: {data.get('error', data.get('message'))}")
            return

        if isinstance(data, list):
            df = pd.DataFrame(data)

            # Daily Summary Processing
            if 'CustomTradeDay' in df.columns:
                df['CustomTradeDay'] = pd.to_datetime(df['CustomTradeDay'])
                daily_summary = df.groupby(df['CustomTradeDay'].dt.date).agg({
                    'NetPnL': 'sum',
                    'TotalSize': 'mean',
                    'id': 'count'
                }).reset_index()

                plt.figure(figsize=(10, 6))
                sns.lineplot(data=daily_summary, x='CustomTradeDay', y='NetPnL')
                plt.title('Daily Profit/Loss')
                plt.xlabel('Date')
                plt.ylabel('Profit/Loss')
                plt.grid(True)
                plt.savefig('reports/daily_profit_loss.png')

                plt.figure(figsize=(10, 6))
                sns.lineplot(data=daily_summary, x='CustomTradeDay', y='TotalSize')
                plt.title('Average Trade Size Over Time')
                plt.xlabel('Date')
                plt.ylabel('Trade Size')
                plt.grid(True)
                plt.savefig('reports/trade_size_over_time.png')
            else:
                messagebox.showerror("Error", "The 'CustomTradeDay' column is missing from the data.")

            # Hourly Summary Processing
            df['EnteredAt'] = pd.to_datetime(df['EnteredAt']).dt.tz_convert(timezone('US/Eastern'))
            df['EnteredHour'] = df['EnteredAt'].dt.strftime('%I %p')
            hour_order = ['12 AM', '01 AM', '02 AM', '03 AM', '04 AM', '05 AM', '06 AM', '07 AM', '08 AM', '09 AM', '10 AM', '11 AM',
                          '12 PM', '01 PM', '02 PM', '03 PM', '04 PM', '05 PM', '06 PM', '07 PM', '08 PM', '09 PM', '10 PM', '11 PM']
            df['EnteredHour'] = pd.Categorical(df['EnteredHour'], categories=hour_order, ordered=True)
            df['TradeOutcome'] = df['NetPnL'].apply(lambda x: 'Win' if x > 0 else 'Loss')
            hourly_summary = df.groupby(['EnteredHour', 'TradeOutcome']).size().unstack().fillna(0)
            hourly_summary['TotalTrades'] = hourly_summary.sum(axis=1)
            hourly_summary['WinningPercentage'] = hourly_summary['Win'] / hourly_summary['TotalTrades'] * 100

            plt.figure(figsize=(12, 8))
            sns.barplot(x=hourly_summary.index, y=hourly_summary['WinningPercentage'], color='blue', alpha=0.7)
            plt.title('Winning Percentage by Hour of Day (EST)')
            plt.xlabel('Hour of Day (EST)')
            plt.ylabel('Winning Percentage (%)')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.savefig('reports/winning_percentage_by_hour.png')

            data_fetched = True
            messagebox.showinfo("Success", "Data fetched and reports generated successfully.")
            update_images()
        else:
            messagebox.showerror("Error", "Unexpected data format. Expected a list of dictionaries.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while fetching data: {str(e)}")

def display_image(tab, image_path):
    img = Image.open(image_path)
    img = img.resize((600, 400), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)
    panel = Label(tab, image=img)
    panel.image = img  # Keep a reference to avoid garbage collection
    panel.pack(padx=10, pady=10)

def update_images():
    # Clear the tabs before updating images
    for widget in tab_daily.winfo_children():
        widget.destroy()
    for widget in tab_hourly.winfo_children():
        widget.destroy()

    # Display updated images
    display_image(tab_daily, 'reports/daily_profit_loss.png')
    display_image(tab_daily, 'reports/trade_size_over_time.png')
    display_image(tab_hourly, 'reports/winning_percentage_by_hour.png')

def on_closing(root):
    root.destroy()
    sys.exit()

def create_gui():
    global tab_daily, tab_hourly
    root = tk.Tk()
    root.title("Trading Data Analysis")
    root.geometry("1300x800")  # Set window size to be larger

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

    notebook = ttk.Notebook(root)
    tab_daily = ttk.Frame(notebook)
    tab_hourly = ttk.Frame(notebook)
    notebook.add(tab_daily, text="Daily Summary")
    notebook.add(tab_hourly, text="Hourly Summary")
    notebook.pack(expand=1, fill="both")

    refresh_button = tk.Button(root, text="Refresh Data", command=fetch_and_process_data)
    refresh_button.pack(pady=10)

    if data_fetched:
        update_images()

    root.mainloop()

if __name__ == "__main__":
    check_if_running()
    create_gui()
