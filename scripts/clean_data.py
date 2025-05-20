# scripts/clean_data.py

import pandas as pd
import os

def clean_amount(val):
    """
    Convert strings like '$5M', '4.6E+08' into numeric USD amounts.
    """
    try:
        s = str(val).replace(',', '').replace('$', '')
        if s.upper().endswith('M'):
            return float(s[:-1]) * 1e6
        return float(s)
    except:
        return pd.NA

def main():
    # Paths
    raw_csv   = os.path.join('data', 'startup_cleaned.csv')
    clean_csv = os.path.join('scripts', 'output', 'startup_funding.csv')

    # Load raw data
    df = pd.read_csv(raw_csv)

    # Drop any unnamed index columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # Parse dates (mixed formats)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
    # Clean amounts
    df['Amount'] = df['Amount'].apply(clean_amount)
    # Drop rows missing critical data
    df.dropna(subset=['Date', 'Startup', 'Industry', 'Location', 'Amount'], inplace=True)

    # Standardize categories
    df['Industry'] = df['Industry'].str.strip().str.title()
    df['Type']     = df['Type'].replace('Unknown', 'Other').str.title()

    # Add YearMonth for grouping
    df['YearMonth'] = df['Date'].dt.to_period('M')

    # Ensure output folder exists
    os.makedirs(os.path.dirname(clean_csv), exist_ok=True)
    # Save cleaned data
    df.to_csv(clean_csv, index=False)
    print(f"Cleaned data saved to {clean_csv}")

if __name__ == '__main__':
    main()
