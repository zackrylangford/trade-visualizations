import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def generate_daily_profit_loss(df):
    df['CustomTradeDay'] = pd.to_datetime(df['CustomTradeDay'])
    daily_summary = df.groupby(df['CustomTradeDay'].dt.date).agg({
        'NetPnL': 'sum',
        'TotalSize': 'mean',
        'id': 'count'
    }).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=daily_summary, x='CustomTradeDay', y='NetPnL', ax=ax)
    ax.set_title('Daily Profit/Loss')
    ax.set_xlabel('Date')
    ax.set_ylabel('Profit/Loss')
    ax.grid(True)
    return fig
