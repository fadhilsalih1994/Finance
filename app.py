
"""
__author__ = 'Fadhil Salih'
__email__ = 'fadhilsalih94@gmail.com'
__date__ = '2021-07-16'
__dataset__ = 'https://finance.yahoo.com/'
__connect__ = 'https://www.linkedin.com/in/fadhilsalih/'
__citation__ = 'https://www.youtube.com/watch?v=X8aNFXJEENs'
"""

# Import necessary packages

import numpy as np
import datetime as dt
import pandas as pd
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.stats import norm

# Get inputs from the user

years = int(input("Enter the number of years to lookback: "))
portfolio_value = int(input("Enter portfolio value: "))
days = int(input("Enter the VaR # of days: "))
confidence_interval = float(
    input("Enter the VaR confidence interval: "))/100
simulations = int(
    input("Enter the the # of Monte Carlo simulations to run (Standard 10,000): "))

tickers = input("Enter tickers (separated by spaces): ").split()

end_date = dt. datetime.now()
start_date = end_date - dt.timedelta(days=365*years)


# Use daily adjusted close prices instead of daily close prices to factor in stock splits and dividends so that the analysis is more accurate
adj_close_df = pd.DataFrame()

# Extract Dataset
for ticker in tickers:
    data = yf.download(ticker, start=start_date, end=end_date)
    adj_close_df[ticker] = data['Adj Close']

# Calculate daily log returns and drop NAs - Logs are time additive. Assuming log returns are normally distributed.
log_returns = np.log(adj_close_df/adj_close_df.shift(1))
log_returns = log_returns.dropna()

# Function to create a covariance matrix for all the securities
cov_matrix = log_returns.cov()

# Equally weighted portfolio creation and total portfolio expected return
weights = np.array([1/len(tickers)]*len(tickers))

# Assuming future returns are based on past returns (Not a good assumption)
# Function to calculate portfolio's expected return using historical mean


def expected_return(weights, log_returns):
    return np.sum(log_returns.mean()*weights)

# Function to calculate portfolio's historical standard deviation


def standard_deviation(weights, cov_matrix):
    # Transposing the weights so that it can be multiplied accurately with the covariance matrix
    variance = weights.T @ cov_matrix @ weights  # ?
    return np.sqrt(variance)


portfolio_expected_return = expected_return(weights, log_returns)
portfolio_std_dev = standard_deviation(weights, cov_matrix)

# Random Z-score based on normal distribution


def random_z_score():
    # return random Z score values between 0 and 1
    return np.random.normal(0, 1)

# Scenario Gain Loss


def scenario_gain_loss(portfolio_value, portfolio_std_dev, z_score, days):
    return portfolio_value * portfolio_expected_return * days + portfolio_value*portfolio_std_dev*z_score*np.sqrt(days)


# Run 10000 simulations
scenario_return = []

for i in range(simulations):
    z_score = random_z_score()
    scenario_return.append(scenario_gain_loss(
        portfolio_value, portfolio_std_dev, z_score, days))

# Value at Risk
VaR = -np.percentile(scenario_return, 100*(1 - confidence_interval))
VaR_clean = "{:,.2f}".format(VaR)
print("-$" + str(VaR_clean))

# Plot to view the results
plt.hist(scenario_return, bins=50, density=True)
plt.xlabel(f'Scenario Gain/Loss ($)')
plt.ylabel('Frequency')
plt.title(f'Distribution of Portfolio Gain/Loss Over {days} Days')
plt.axvline(-VaR, color='r', linestyle='dashed', linewidth=2,
            label=f'VaR at {confidence_interval:.0%} confidence level')
plt.legend()
plt.show()
