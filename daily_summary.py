# daily_summary.py
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
        
        # Check if the 'CustomTradeDay' column exists
        if 'CustomTradeDay' in df.columns:
            # Ensure CustomTradeDay column is in datetime format
            df['CustomTradeDay'] = pd.to_datetime(df['CustomTradeDay'])
            
            # Perform analysis if the 'CustomTradeDay' column is present
            daily_summary = df.groupby(df['CustomTradeDay'].dt.date).agg({
                'NetPnL': 'sum',
                'TotalSize': 'mean',
                'id': 'count'  # Number of trades
            }).reset_index()

            print(daily_summary)

            # Plot daily profit/loss
            plt.figure(figsize=(10, 6))
            sns.lineplot(data=daily_summary, x='CustomTradeDay', y='NetPnL')
            plt.title('Daily Profit/Loss')
            plt.xlabel('Date')
            plt.ylabel('Profit/Loss')
            plt.grid(True)
            plt.savefig('reports/daily_profit_loss.png')  # Save the plot as an image file

            # Plot trade size over time
            plt.figure(figsize=(10, 6))
            sns.lineplot(data=daily_summary, x='CustomTradeDay', y='TotalSize')
            plt.title('Average Trade Size Over Time')
            plt.xlabel('Date')
            plt.ylabel('Trade Size')
            plt.grid(True)
            plt.savefig('reports/trade_size_over_time.png')  # Save the plot as an image file
        else:
            print("The 'CustomTradeDay' column is missing from the data.")
    else:
        print("Unexpected data format. Expected a list of dictionaries.")
