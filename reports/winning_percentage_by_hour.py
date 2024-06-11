import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pytz import timezone

def generate_winning_percentage_by_hour(df):
    # Convert EnteredAt to Central Time
    df['EnteredAt'] = pd.to_datetime(df['EnteredAt']).dt.tz_convert(timezone('US/Central'))
    df['EnteredHour'] = df['EnteredAt'].dt.strftime('%I %p')
    
    hour_order = ['12 AM', '01 AM', '02 AM', '03 AM', '04 AM', '05 AM', '06 AM', '07 AM', '08 AM', '09 AM', '10 AM', '11 AM',
                  '12 PM', '01 PM', '02 PM', '03 PM', '04 PM', '05 PM', '06 PM', '07 PM', '08 PM', '09 PM', '10 PM', '11 PM']
    df['EnteredHour'] = pd.Categorical(df['EnteredHour'], categories=hour_order, ordered=True)
    df['TradeOutcome'] = df['NetPnL'].apply(lambda x: 'Win' if x > 0 else 'Loss')
    
    # Group by EnteredHour and TradeOutcome
    hourly_summary = df.groupby(['EnteredHour', 'TradeOutcome']).size().unstack(fill_value=0)
    hourly_summary['TotalTrades'] = hourly_summary.sum(axis=1)
    hourly_summary['WinningPercentage'] = hourly_summary['Win'] / hourly_summary['TotalTrades'] * 100

    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create a color palette based on winning percentage
    norm = plt.Normalize(hourly_summary['WinningPercentage'].min(), hourly_summary['WinningPercentage'].max())
    sm = plt.cm.ScalarMappable(cmap="RdYlGn", norm=norm)
    sm.set_array([])

    colors = [sm.to_rgba(pct) for pct in hourly_summary['WinningPercentage']]

    sns.barplot(x=hourly_summary.index, y=hourly_summary['WinningPercentage'], palette=colors, ax=ax)
    
    # Add annotations for number of trades
    for i, (win_percent, total_trades) in enumerate(zip(hourly_summary['WinningPercentage'], hourly_summary['TotalTrades'])):
        ax.text(i, win_percent + 1, f'{total_trades:.0f}', ha='center', va='bottom', fontsize=10, color='black')

    ax.set_title('Winning Percentage by Hour of Day (CST) with Number of Trades')
    ax.set_xlabel('Hour of Day (CST)')
    ax.set_ylabel('Winning Percentage (%)')
    ax.grid(True)
    ax.set_xticklabels(hour_order, rotation=45)
    
    # Add color bar
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label('Winning Percentage (%)')
    
    return fig
