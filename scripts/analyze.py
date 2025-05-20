# scripts/analyze.py

import pandas as pd
import os


def main():
    cleaned_csv = os.path.join('scripts', 'output', 'startup_funding.csv')
    output_dir  = os.path.join('scripts', 'output')

    # Load cleaned data
    df = pd.read_csv(cleaned_csv, parse_dates=['Date'])
    df['YearMonth'] = df['YearMonth'].astype(str)

    # 1. Total funding by YearMonth
    by_ym = df.groupby('YearMonth')['Amount'].sum().reset_index()
    by_ym.to_csv(os.path.join(output_dir, 'funding_by_yearmonth.csv'), index=False)

    # 2. Total funding by Industry (top 10)
    by_ind = df.groupby('Industry')['Amount'].sum().nlargest(10).reset_index()
    by_ind.to_csv(os.path.join(output_dir, 'top_industries.csv'), index=False)

    # 3. Top 10 Startups by total funding
    top_startups = df.groupby('Startup')['Amount'].sum().nlargest(10).reset_index()
    top_startups.to_csv(os.path.join(output_dir, 'top_startups.csv'), index=False)

    # 4. Funding count by Type
    by_type = df['Type'].value_counts().reset_index()
    by_type.columns = ['Type', 'Count']
    by_type.to_csv(os.path.join(output_dir, 'funding_counts_by_type.csv'), index=False)

    # 5. Funding by Location (top 10 cities)
    by_loc = df['Location'].value_counts().nlargest(10).reset_index()
    by_loc.columns = ['Location', 'Count']
    by_loc.to_csv(os.path.join(output_dir, 'top_locations.csv'), index=False)

    # 6. Investor Analysis
    # Assumes a column 'Investor' in the cleaned CSV, with comma-separated names
    if 'Investor' in df.columns:
        # Explode comma-separated list into individual rows
        df_in = (
            df.assign(
                InvestorName=df['Investor'].str.split(',')
            ).explode('InvestorName')
        )
        df_in['InvestorName'] = df_in['InvestorName'].str.strip()

        # 6a. Top investors by total funding
        inv_funding = (
            df_in.groupby('InvestorName')['Amount']
            .sum()
            .nlargest(10)
            .reset_index()
            .rename(columns={'InvestorName':'Investor'})
        )
        inv_funding.to_csv(os.path.join(output_dir, 'top_investors_by_funding.csv'), index=False)

        # 6b. Top investors by count of rounds
        inv_rounds = (
            df_in['InvestorName']
            .value_counts()
            .nlargest(10)
            .reset_index()
        )
        inv_rounds.columns = ['Investor', 'Rounds']
        inv_rounds.to_csv(os.path.join(output_dir, 'top_investors_by_rounds.csv'), index=False)
    else:
        print("Warning: 'Investor' column not found in cleaned CSV; skipping investor analysis.")

    print(f"Analysis outputs saved to {output_dir}")


if __name__ == '__main__':
    os.makedirs(os.path.join('scripts', 'output'), exist_ok=True)
    main()
