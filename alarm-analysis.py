import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

def load_and_process_data(data):
    # Convert the data into a proper DataFrame format
    df = pd.DataFrame(data)
    
    # Melt the DataFrame to convert dates from columns to rows
    df_melted = pd.melt(df, 
                        id_vars=['Room_Codes', 'Rooms'],
                        value_vars=[col for col in df.columns if 'Count_' in col],
                        var_name='Date',
                        value_name='Alarms')
    
    # Clean up the date column
    df_melted['Date'] = df_melted['Date'].str.replace('Count_', '')
    df_melted['Date'] = pd.to_datetime(df_melted['Date'], format='%d')
    
    return df_melted

def analyze_alarm_patterns(df):
    # Daily totals
    daily_totals = df.groupby('Date')['Alarms'].sum().reset_index()
    
    # Room rankings
    room_totals = df.groupby('Room_Codes')['Alarms'].agg([
        ('total_alarms', 'sum'),
        ('avg_daily_alarms', 'mean'),
        ('max_daily_alarms', 'max'),
        ('days_with_alarms', lambda x: (x > 0).sum())
    ]).sort_values('total_alarms', ascending=False)
    
    # Identify rooms with unusual patterns
    room_stats = df.groupby('Room_Codes')['Alarms'].agg(['mean', 'std']).reset_index()
    room_stats['cv'] = room_stats['std'] / room_stats['mean']  # Coefficient of variation
    
    return daily_totals, room_totals, room_stats

def create_visualizations(df, daily_totals, room_totals):
    # Set up the visualization style
    plt.style.use('seaborn')
    
    # Create a figure with multiple subplots
    fig = plt.figure(figsize=(20, 15))
    
    # 1. Daily Trend Plot
    plt.subplot(2, 2, 1)
    plt.plot(daily_totals['Date'], daily_totals['Alarms'], marker='o')
    plt.title('Daily Alarm Trends')
    plt.xlabel('Date')
    plt.ylabel('Total Alarms')
    plt.xticks(rotation=45)
    
    # 2. Top 10 Rooms by Total Alarms
    plt.subplot(2, 2, 2)
    top_10_rooms = room_totals.head(10)
    plt.bar(range(10), top_10_rooms['total_alarms'])
    plt.title('Top 10 Rooms by Total Alarms')
    plt.xlabel('Room Code')
    plt.ylabel('Total Alarms')
    plt.xticks(range(10), top_10_rooms.index, rotation=45)
    
    # 3. Heatmap of Alarm Patterns
    plt.subplot(2, 2, 3)
    pivot_data = df.pivot(index='Room_Codes', columns='Date', values='Alarms')
    sns.heatmap(pivot_data.head(20), cmap='YlOrRd', cbar_kws={'label': 'Number of Alarms'})
    plt.title('Alarm Patterns Heatmap (Top 20 Rooms)')
    plt.xlabel('Date')
    plt.ylabel('Room Code')
    
    # 4. Distribution of Daily Alarms
    plt.subplot(2, 2, 4)
    plt.hist(df['Alarms'], bins=50)
    plt.title('Distribution of Daily Alarm Counts')
    plt.xlabel('Number of Alarms')
    plt.ylabel('Frequency')
    
    plt.tight_layout()
    return fig

def generate_insights(daily_totals, room_totals, room_stats):
    insights = {
        'total_alarms': int(room_totals['total_alarms'].sum()),
        'avg_daily_alarms': float(daily_totals['Alarms'].mean()),
        'max_daily_alarms': int(daily_totals['Alarms'].max()),
        'top_rooms': room_totals.head(5).index.tolist(),
        'rooms_with_high_variance': room_stats[room_stats['cv'] > 1]['Room_Codes'].tolist()
    }
    return insights

def main():
    # Load your data here
    df = load_and_process_data(your_data)  # Replace with actual data loading
    
    # Perform analysis
    daily_totals, room_totals, room_stats = analyze_alarm_patterns(df)
    
    # Generate visualizations
    fig = create_visualizations(df, daily_totals, room_totals)
    
    # Generate insights
    insights = generate_insights(daily_totals, room_totals, room_stats)
    
    # Print key findings
    print("\nKey Insights:")
    print(f"Total Alarms: {insights['total_alarms']:,}")
    print(f"Average Daily Alarms: {insights['avg_daily_alarms']:.2f}")
    print(f"Maximum Daily Alarms: {insights['max_daily_alarms']:,}")
    print("\nTop 5 Rooms by Alarm Count:")
    for room in insights['top_rooms']:
        print(f"Room {room}: {int(room_totals.loc[room, 'total_alarms']):,} alarms")
    
    return df, daily_totals, room_totals, room_stats, insights

if __name__ == "__main__":
    df, daily_totals, room_totals, room_stats, insights = main()
