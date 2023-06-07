from binance import Client
import pandas as pd
from datetime import datetime
import pytz

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Enter your API keys to use with python-binance client 
apikey = ''
secretkey = ''

client = Client(apikey, secretkey)
status = client.get_system_status()

# Make sure API keys are working 
print(status)

# Specify a pair if you want, this is optional. 
sol = 'SOLUSDT'
aave = 'AAVEUSDT'
ape = 'APEUSDT'
luna = 'LUNA2BUSD'

# Specify start date when needed
# Create a datetime object for May 1st, 2023, in UTC timezone
date = datetime(2023, 4, 1, tzinfo=pytz.utc)

# Convert the datetime object to a timestamp in seconds
timestamp_seconds = date.timestamp()

# Convert the timestamp to milliseconds
timestamp_milliseconds = timestamp_seconds * 1000

# Import recent trade history for specific instrument using Binance API
trades = client.futures_account_trades()

# Make data frame from dictionary of recent futures trades
df = pd.DataFrame.from_dict(trades)
# Organize into columns
df = df[['time', 'symbol', 'price', 'side', 'realizedPnl']]

# Convert unix time to datetime format (milliseconds)
df['time'] = pd.to_datetime(df['time'], unit='ms')

# Truncate timestamps and remove milliseconds
df['time'] = df['time'].dt.floor('s')

# Convert price and P&L to numeric format from object type (float 64)
df[['price', 'realizedPnl']] = df[['price', 'realizedPnl']].apply(pd.to_numeric)

'''
    Final steps: 
    1. Group data frame rows by time, symbol, side 
    2. Aggregate the other two columns - average price, sum of P&L
    3. Sort the data frame by descending order in price 
'''

df = df.groupby(['time', 'symbol', 'side'], as_index=False).agg({'price': 'mean', 'realizedPnl': 'sum'}).sort_values(
    'time')

df['time'] = pd.to_datetime(df['time']).dt.tz_localize('utc').dt.tz_convert('Asia/Jerusalem').dt.tz_localize(None)

df['Day of week'] = df['time'].apply(lambda x: x.day_name())
week = df.groupby(['Day of week'], as_index=False).agg({'realizedPnl': 'sum'}).sort_values('realizedPnl')

for x in range(len(df)):
    pnl = df.loc[x, "realizedPnl"]
    side = df.loc[x, "side"]
    price = df.loc[x, 'price']
    if pnl == 0:
        df.loc[x, 'Action'] = f"Open {side} @ {price.round(5)}"

    else:
        df.loc[x, 'Action'] = f"Close {side} @ {price.round(5)}"

df = df[['time', 'symbol', 'Action', 'side', 'price', 'realizedPnl', 'Day of week']]
df = df.rename(columns={'realizedPnl': 'P&L'})
df[['price', 'P&L']] = df[['price', 'P&L']].round(2)
print(df)


df2 = df.sort_values(['time'])
sum = df2['P&L'].cumsum()

sum_df = sum.to_frame()
sum_df = sum_df.rename(columns={'P&L': 'Cumulative P&L'})

# Final DF contains certain metrics 
final_df = pd.concat([df, sum_df], axis=1)


def cumulative_chart(date_column, data):
    import matplotlib.pyplot as plt
    from matplotlib import dates

    # Set up an axis
    ax = plt.gca()

    # start by your date and then your data
    ax.plot(date_column, data)

    # You can change the step of range() as you prefer (now, it selects each third month)
    ax.xaxis.set_major_locator(dates.MonthLocator(bymonth=range(1, 13)))

    # you can change the format of the label (now it is 2016-Jan)
    ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%b'))

    plt.setp(ax.get_xticklabels(), rotation=20)
    plt.grid()
    plt.show()
    
    

# Print a cumulative chart of your P&L with matplotlib
cumulative_chart(final_df['time'], final_df['Cumulative P&L'])
