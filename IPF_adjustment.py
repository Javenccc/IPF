import pandas as pd
import numpy

# Load raw sales data and target growth rates by channel and segment
raw_df = pd.read_csv("Raw data.csv")
channel_target_df = pd.read_excel("Targets.xlsx", sheet_name="Channel")
segment_target_df = pd.read_excel("Targets.xlsx", sheet_name="Segment")

# Pivot data to get sales values by Channel, Type, Segment, and Segment_detail over different time periods
pivot_df = raw_df.pivot_table(
    index=['Channel', 'Type', 'Segment', 'Segment_detail'],
    columns='Time Series',
    values=['TL Sales','TL Sales YA'],
    aggfunc='sum',
    fill_value=0
)

# Define weights to blend different time periods, adjusted for length of each period
weights = {
    'FY 2024': 0.3 * (12/12),
    'Last 52': 0.4 * (12/12),
    'Last 12': 0.1 * (12/3),  # 3 months
    'YTD': 0.2 * (12/5)       # 5 months YTD
}

# Calculate weighted baseline sales using these blended weights
pivot_df['Weighted_baseline'] = sum(
    pivot_df[('TL Sales', period)] * w  
    for period, w in weights.items()
    if ('TL Sales', period) in pivot_df.columns
)

# Start the 2025 projection with the weighted baseline
pivot_df['2025_projection'] = pivot_df['Weighted_baseline']

# Flatten multi-level columns
pivot_df = pivot_df.reset_index()
flat_columns = []
for col in pivot_df.columns:
    if isinstance(col, tuple):
        flat_columns.append('_'.join([str(c) for c in col if c]))
    else:
        flat_columns.append(col)
pivot_df.columns = flat_columns

# Prepare target totals by Channel and Segment
channel_targets = channel_target_df.set_index('Channel')['2025 - Target']
segment_targets = segment_target_df.set_index('Segment')['2025 - Target']

# Define function to iteratively adjust projections to fit channel and segment targets
def ipf_adjustment(df, channel_targets, segment_targets, max_iter=10000, tol=1e-4):
    df = df.copy()
    for i in range(max_iter):
        # Adjust to meet channel targets
        current_channel_totals = df.groupby('Channel')['2025_projection'].sum()
        for channel, target in channel_targets.items():
            current = current_channel_totals.get(channel, 0)
            if current > 0:
                df.loc[df['Channel'] == channel,'2025_projection'] *= target / current

        # Adjust to meet segment targets
        current_segment_totals = df.groupby('Segment')['2025_projection'].sum()
        for segment, target in segment_targets.items():
            current = current_segment_totals.get(segment, 0)
            if current > 0:
                df.loc[df['Segment'] == segment,'2025_projection'] *= target / current

        # Check if adjustments have converged within tolerance
        max_channel_diff = (df.groupby('Channel')['2025_projection'].sum() - channel_targets).abs().max()
        max_segment_diff = (df.groupby('Segment')['2025_projection'].sum() - segment_targets).abs().max()

        if max_channel_diff < tol and max_segment_diff < tol:
            print(f"Converged after {i+1} iterations")
            break
    else:
        print("IPF did not converge within iteration limit.")
    return df

# Run the IPF adjustment to reconcile projections with targets
adjusted_df = ipf_adjustment(pivot_df, channel_targets, segment_targets)

# Select final columns and export to Excel for reporting
final_output = adjusted_df[
    ['Channel', 'Type', 'Segment', 'Segment_detail',
     'TL Sales_FY 2024', 'Weighted_baseline', '2025_projection']
]
final_output.head()
final_output.to_excel("2025_forecast_IPF_adjusted.xlsx", index=False)
