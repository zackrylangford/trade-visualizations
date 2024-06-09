import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Fetch data from the API
api_endpoint = "https://x6vqzeow7a.execute-api.us-east-1.amazonaws.com/default/get-trade-recaps"

# Request without a specific date to fetch all data
response = requests.get(api_endpoint)
data = response.json()

# Convert the data to a DataFrame
df = pd.DataFrame(data)

# Check if the 'tradeDate' column exists
if 'tradeDate' in df.columns:
    # Ensure tradeDate column is in datetime format
    df['tradeDate'] = pd.to_datetime(df['tradeDate'])
else:
    print("The 'tradeDate' column is missing from the data.")

# Perform analysis if the 'tradeDate' column is present
if 'tradeDate' in df.columns:
    daily_summary = df.groupby(df['tradeDate'].dt.date).agg({
        'profitLoss': 'sum',
        'tradeSize': 'mean',
        'executionTime': 'count'  # Number of trades
    }).reset_index()

    print(daily_summary)

    # Plot daily profit/loss
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=daily_summary, x='tradeDate', y='profitLoss')
    plt.title('Daily Profit/Loss')
    plt.xlabel('Date')
    plt.ylabel('Profit/Loss')
    plt.grid(True)
    plt.show()

    # Plot trade size over time
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=daily_summary, x='tradeDate', y='tradeSize')
    plt.title('Average Trade Size Over Time')
    plt.xlabel('Date')
    plt.ylabel('Trade Size')
    plt.grid(True)
    plt.show()
else:
    print("Data does not contain the 'tradeDate' column.")
