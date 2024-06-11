import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pytz import timezone

def generate_grouped_winning_trades(df):
    # Convert EnteredAt to Central Time
    df['EnteredAt'] = pd.to_datetime(df['EnteredAt']).dt.tz_convert(timezone('US/Central'))
    df['EnteredTimeBlock'] = df['EnteredAt'].apply(lambda x: categorize_time_block(x))

    print("After categorizing time blocks:")
    print(df[['EnteredAt', 'EnteredTimeBlock', 'NetPnL']].to_string())  # Print all rows

    df['TradeOutcome'] = df['NetPnL'].apply(lambda x: 'Win' if x > 0 else 'Loss')
    
    # Ensure all time blocks are included by setting categories
    time_blocks = [
        'Early Morning (pre-9:30)', 'Morning (9:30-12:00)', 'Late Morning (12:00-15:00)', 
        'Early Afternoon (15:00-17:00)', 'Evening (17:00-00:00)', 'Night (00:00-06:00)'
    ]
    df['EnteredTimeBlock'] = pd.Categorical(df['EnteredTimeBlock'], categories=time_blocks, ordered=True)

    # Group by EnteredTimeBlock and TradeOutcome
    grouped_summary = df.groupby(['EnteredTimeBlock', 'TradeOutcome']).size().unstack().fillna(0)

    # Add all time blocks to ensure none are missing
    grouped_summary = grouped_summary.reindex(time_blocks).fillna(0)

    # Calculate total trades and winning percentage
    grouped_summary['TotalTrades'] = grouped_summary.sum(axis=1)
    grouped_summary['WinningPercentage'] = grouped_summary['Win'] / grouped_summary['TotalTrades'] * 100

    print("Grouped summary:")
    print(grouped_summary)  # Print the grouped summary

    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Add padding to the bottom of the plot
    plt.subplots_adjust(bottom=0.3)
    
    # Create a color palette based on winning percentage
    norm = plt.Normalize(grouped_summary['WinningPercentage'].min(), grouped_summary['WinningPercentage'].max())
    sm = plt.cm.ScalarMappable(cmap="RdYlGn", norm=norm)
    sm.set_array([])

    colors = sm.to_rgba(grouped_summary['WinningPercentage'])

    sns.barplot(x=grouped_summary.index, y=grouped_summary['WinningPercentage'], palette=colors, ax=ax)
    
    # Add annotations for number of trades
    for i, (win_percent, total_trades) in enumerate(zip(grouped_summary['WinningPercentage'], grouped_summary['TotalTrades'])):
        ax.text(i, win_percent + 1, f'{total_trades:.0f}', ha='center', va='bottom', fontsize=10, color='black')

    ax.set_title('Winning Percentage by Time Block (CST) with Number of Trades')
    ax.set_xlabel('Time Block (CST)')
    ax.set_ylabel('Winning Percentage (%)')
    ax.grid(True)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    
    # Add color bar
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label('Winning Percentage (%)')
    
    return fig

def categorize_time_block(timestamp):
    hour = timestamp.hour
    minute = timestamp.minute
    if hour < 9 or (hour == 9 and minute < 30):
        return 'Early Morning (pre-9:30)'
    elif 9 <= hour < 12:
        return 'Morning (9:30-12:00)'
    elif 12 <= hour < 15:
        return 'Late Morning (12:00-15:00)'
    elif 15 <= hour < 17:
        return 'Early Afternoon (15:00-17:00)'
    elif 17 <= hour < 24:
        return 'Evening (17:00-00:00)'
    else:
        return 'Night (00:00-06:00)'
