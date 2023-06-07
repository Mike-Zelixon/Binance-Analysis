import pandas as pd
import numpy as np
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# THIS SCRIPT REQUIRES YOU DONWNLOAD YOUR TRADING HISTORY PRIOR TO RUNNING 

# Import trade history Excel from Binance
# I have included a sample XLSX file from my own trading history (don't judge) 

df = pd.read_excel('/Users/mikezelixon/Downloads/Binance Trading Feb-March 2023.xlsx', engine="openpyxl")

# Rename columns
df = df.rename(columns={'Date(UTC)': 'Date'})

# Make a new dataframe with just the columns you want
df2 = df[['Date', 'Symbol', 'Side', 'Price', 'Realized Profit', 'Fee']]

# 1. Use groupby by to group rows by Date, Symbol, and Side
# 2. Sum up profits/fees and average the price of each row
df2 = df2.groupby(['Date', 'Symbol', 'Side', ], as_index=False).agg(
    {'Price': 'mean', 'Realized Profit': 'sum', 'Fee': 'sum'}).sort_values('Date', ascending=False)

# Convert timestamps to desired format and change timezone from GMT to Israel Time (Or whatever local time you prefer) 
df2['Date'] = pd.to_datetime(df2['Date'], errors='coerce').dt.tz_localize('utc').dt.tz_convert(
    'Asia/Jerusalem').dt.tz_localize(None)


# OPTIONAL - include day of the week if you want to
df2['Day of week'] = df2['Date'].apply(lambda x: x.day_name())
week = df2.groupby(['Day of week'], as_index=False).agg({'Realized Profit':'mean'}).sort_values('Realized Profit', ascending=False)

# print(week)
# print(df2[-14:])

df2['Type'] = np.where(df2['Realized Profit'] == 0, "Entry", "Exit")


print(df2)

# Make variables for trade statistics 
profit = df2['Realized Profit']
wins = df2[df2['Realized Profit'] > 0]
losses = df2[df2['Realized Profit'] < -1]
total_trades = pd.concat([wins, losses])

avg_win = wins['Realized Profit'].mean()
avg_loss = losses['Realized Profit'].mean()

median_win = wins['Realized Profit'].median()
median_loss = losses['Realized Profit'].median()

# Print your stats 
print(f"\nTotal number of trades = {len(total_trades)}")
print(f"Number of winning trades = {len(wins)}")
print(f"Number of losing trades = {len(losses)}")


print(f"\nAverage win = {avg_win.round(2)}")
print(f"Average loss = {avg_loss.round(2)}")

print(f"\nMedian win = {median_win.round(2)}")
print(f"Median loss = {median_loss.round(2)}")

print(f"\nAverage trade = {total_trades['Realized Profit'].mean().round(2)}")


def Trade_History(csv):
    df = pd.read_csv(csv, encoding='latin-1')
    df = df.rename(columns={'Date(UTC)': 'Date'})
    df2 = df[['Date(UTC)', 'Symbol', 'Side', 'Price', 'Realized Profit', 'Fee']]
    df2 = df2.groupby(['Date(UTC)', 'Symbol', 'Side'], as_index=False).agg(
        {'Realized Profit': 'sum', 'Fee': 'sum'}).sort_values('Date(UTC)', ascending=False)
    df2['Date(UTC)'] = pd.to_datetime(df2['Date(UTC)'], errors='coerce').dt.tz_localize('utc').dt.tz_convert(
        'Asia/Jerusalem')
    print(df2)
