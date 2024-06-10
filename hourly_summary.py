# hourly_summary.py
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pytz import timezone

# Fetch data from the new API endpoint
api_endpoint = "https://adhp0jlvy5.execute-api.us-east-1.amazonaws.com/default/visualize-trade-data"

# Request without a specific date to fetch all data
response = requests.get(api_endpoint)
data = response.json()

# Debug: Print the fetched data structure
print("Fetched data structure:", type(data))
print(data)

# Check if the response contains an error message
if 'error' in data or 'message' in data:
    print("Error fetching data from API:", data.get('error', data.get('message')))
else:
    # Convert the data to a DataFrame if it is a list
    if isinstance(data, list):
        df = pd.DataFrame(data)
        
        # Ensure EnteredAt column is in datetime format and convert to EST
        df['EnteredAt'] = pd.to_datetime(df['EnteredAt']).dt.tz_convert(timezone('US/Eastern'))
        
        # Extract the hour from EnteredAt in 12-hour format with AM/PM
        df['EnteredHour'] = df['EnteredAt'].dt.strftime('%I %p')
        
        # Define the correct order for hours in 12-hour format with AM/PM
        hour_order = ['12 AM', '01 AM', '02 AM', '03 AM', '04 AM', '05 AM', '06 AM', '07 AM', '08 AM', '09 AM', '10 AM', '11 AM',
                      '12 PM', '01 PM', '02 PM', '03 PM', '04 PM', '05 PM', '06 PM', '07 PM', '08 PM', '09 PM', '10 PM', '11 PM']
        
        # Convert EnteredHour to a categorical type with the specified order
        df['EnteredHour'] = pd.Categorical(df['EnteredHour'], categories=hour_order, ordered=True)
        
        # Classify trades as win (NetPnL > 0) or loss (NetPnL <= 0)
        df['TradeOutcome'] = df['NetPnL'].apply(lambda x: 'Win' if x > 0 else 'Loss')
        
        # Aggregate the number of winning and losing trades for each hour
        hourly_summary = df.groupby(['EnteredHour', 'TradeOutcome']).size().unstack().fillna(0)
        
        # Calculate the total number of trades and winning percentage
        hourly_summary['TotalTrades'] = hourly_summary.sum(axis=1)
        hourly_summary['WinningPercentage'] = hourly_summary['Win'] / hourly_summary['TotalTrades'] * 100
        
        # Debug: Print the summary data
        print(hourly_summary)
        
        # Plot the data
        plt.figure(figsize=(12, 8))
        sns.barplot(x=hourly_summary.index, y=hourly_summary['WinningPercentage'], color='blue', alpha=0.7)
        plt.title('Winning Percentage by Hour of Day (EST)')
        plt.xlabel('Hour of Day (EST)')
        plt.ylabel('Winning Percentage (%)')
        plt.grid(True)
        plt.xticks(rotation=45)  # Rotate the x-axis labels for better readability
        plt.savefig('reports/winning_percentage_by_hour.png')  # Save the plot as an image file
    else:
        print("Unexpected data format. Expected a list of dictionaries.")
