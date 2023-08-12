from binance import Client
import pandas as pd
from datetime import datetime, timedelta
import pytz

# This script will automatically fetch your latest Binance futures trades without having to download anything from their website.
# Will save your results as a CSV with specific trade info. 

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

apikey = ''
secretkey = ''

client = Client(apikey, secretkey)
status = client.get_system_status()
print(status)

sol = 'SOLUSDT'
aave = 'AAVEUSDT'
ape = 'APEUSDT'
luna = 'LUNA2BUSD'


# Specify start date when needed
# Create a datetime object for May 1st, 2023, in UTC timezone

def get_trades_df(start_date):
    dfs = []  # List to store DataFrames from each API call

    # Iterate through the dates with a step of 7 days
    current_date = start_date
    while current_date <= datetime.now(pytz.utc):
        # Convert the current date to UTC
        current_date_utc = current_date.replace(tzinfo=pytz.utc)

        # Convert the datetime object to a timestamp in seconds
        timestamp_seconds = current_date_utc.timestamp()

        # Convert the timestamp to milliseconds
        timestamp_milliseconds = int(timestamp_seconds * 1000)

        # Import recent trade history for specific instrument using Binance API
        try:
            trades = client.futures_account_trades(startTime=timestamp_milliseconds)
        except Exception as e:
            print(f"Error fetching trades for {current_date}: {str(e)}")
            current_date += timedelta(days=7)
            continue

        # Make data frame from dictionary of recent futures trades
        try:
            if len(trades) > 0:
                df = pd.DataFrame.from_dict(trades)
                df = df[['time', 'symbol', 'price', 'side', 'realizedPnl']]
                # Convert unix time to datetime format (milliseconds)
                df['time'] = pd.to_datetime(df['time'], unit='ms')
                # Truncate timestamps and remove milliseconds
                df['time'] = df['time'].dt.floor('s')
                # Convert price and P&L to numeric format from object type (float 64)
                df[['price', 'realizedPnl']] = df[['price', 'realizedPnl']].apply(pd.to_numeric)
                dfs.append(df)  # Append the current DataFrame to the list
            else:
                print(f"No trades found for {current_date}")
        except KeyError as e:
            print(f"Error processing trades for {current_date}: {str(e)}")

        # Increment the current date by 7 days
        current_date += timedelta(days=7)

    # Combine all DataFrames into a single DataFrame
    combined_df = pd.concat(dfs, ignore_index=True)

    # Perform further data processing steps as before...
    combined_df = combined_df.groupby(['time', 'symbol', 'side'], as_index=False).agg(
        {'price': 'mean', 'realizedPnl': 'sum'}).sort_values('time')

    combined_df['time'] = pd.to_datetime(combined_df['time']).dt.tz_localize('utc').dt.tz_convert(
        'Asia/Jerusalem').dt.tz_localize(None)

    combined_df['Day of week'] = combined_df['time'].apply(lambda x: x.day_name())
    # week = combined_df.groupby(['Day of week'], as_index=False).agg({'realizedPnl': 'sum'}).sort_values('realizedPnl')
    #
    for x in range(len(combined_df)):
        pnl = combined_df.loc[x, "realizedPnl"]
        side = combined_df.loc[x, "side"]
        price = combined_df.loc[x, 'price']
        if pnl == 0:
            combined_df.loc[x, 'Action'] = f"Open {side} @ {price.round(5)}"
        else:
            combined_df.loc[x, 'Action'] = f"Close {side} @ {price.round(5)}"
    #
    combined_df = combined_df[['time', 'symbol', 'Action', 'side', 'price', 'realizedPnl', 'Day of week']]
    combined_df = combined_df.rename(columns={'realizedPnl': 'P&L'})
    combined_df[['price', 'P&L']] = combined_df[['price', 'P&L']].round(2)
    return combined_df


start_of_history = datetime(2023, 1, 1, tzinfo=pytz.utc)
ok = get_trades_df(start_date=start_of_history)
print(ok)
# ok.to_csv('April2023.csv')

# df2 = df.sort_values(['time'])
# sum = df2['P&L'].cumsum()
# sum_df = sum.to_frame()
# sum_df = sum_df.rename(columns={'P&L': 'Cumulative P&L'})
# final_df = pd.concat([df, sum_df], axis=1)
# print(final_df)


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
# cumulative_chart(final_df['time'], final_df['Cumulative P&L'])
