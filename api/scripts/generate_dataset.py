#!/usr/bin/env python3
"""
HyperVolt Dataset Generator
Generates synthetic energy consumption dataset with weekday/weekend patterns
and exports graphs matching the website forecast visualization
"""

import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Output directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'generated')
GRAPH_DIR = os.path.join(OUTPUT_DIR, 'graphs')

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GRAPH_DIR, exist_ok=True)

# Peak hour definitions (matching website logic)
WEEKDAY_PEAK_HOURS = {
    'morning': (7, 9),   # 7AM - 9AM
    'evening': (17, 20)  # 5PM - 8PM
}
WEEKEND_PEAK_HOURS = {
    'afternoon': (11, 14),  # 11AM - 2PM
    'evening': (18, 21)     # 6PM - 9PM
}

# Power consumption ranges (in mW to match new units)
NORMAL_POWER_RANGE = (500, 1700)       # 0.5 - 1.7 kW = 500-1700 mW
PEAK_POWER_RANGE = (1700, 2500)        # 1.7 - 2.5 kW = 1700-2500 mW
NIGHT_POWER_RANGE = (300, 500)         # 0.3 - 0.5 kW = 300-500 mW


def is_peak_hour(hour: int, is_weekend: bool) -> bool:
    """Check if given hour is a peak hour based on day type"""
    if is_weekend:
        return (WEEKEND_PEAK_HOURS['afternoon'][0] <= hour <= WEEKEND_PEAK_HOURS['afternoon'][1] or
                WEEKEND_PEAK_HOURS['evening'][0] <= hour <= WEEKEND_PEAK_HOURS['evening'][1])
    else:
        return (WEEKDAY_PEAK_HOURS['morning'][0] <= hour <= WEEKDAY_PEAK_HOURS['morning'][1] or
                WEEKDAY_PEAK_HOURS['evening'][0] <= hour <= WEEKDAY_PEAK_HOURS['evening'][1])


def get_power_consumption(hour: int, is_weekend: bool) -> float:
    """Calculate power consumption for a given hour"""
    if hour <= 6:
        return random.uniform(*NIGHT_POWER_RANGE)
    if is_peak_hour(hour, is_weekend):
        return random.uniform(*PEAK_POWER_RANGE)
    return random.uniform(*NORMAL_POWER_RANGE)


def generate_day_data(date: datetime) -> list:
    """Generate 24 hours of data for a given date"""
    day_of_week = date.weekday()
    is_weekend = day_of_week >= 5
    day_name = date.strftime('%A')
    
    records = []
    for hour in range(24):
        timestamp = date.replace(hour=hour, minute=0, second=0, microsecond=0)
        power_mw = get_power_consumption(hour, is_weekend)
        is_peak = is_peak_hour(hour, is_weekend)
        
        # Additional features
        temperature = 20 + 10 * np.sin((hour - 6) * np.pi / 12) + random.uniform(-2, 2)
        humidity = 50 + 20 * np.cos((hour - 12) * np.pi / 12) + random.uniform(-5, 5)
        solar_irradiance = max(0, 800 * np.sin((hour - 6) * np.pi / 12)) if 6 <= hour <= 18 else 0
        solar_irradiance += random.uniform(-50, 50) if solar_irradiance > 0 else 0
        cloud_cover = random.uniform(0, 100)
        
        battery_soc = 50 + 30 * np.sin((hour - 12) * np.pi / 12) + random.uniform(-5, 5)
        battery_soc = max(10, min(100, battery_soc))
        
        if solar_irradiance > 400 and cloud_cover < 50:
            primary_source = 'solar'
        elif battery_soc > 30:
            primary_source = 'battery'
        else:
            primary_source = 'grid'
        
        records.append({
            'timestamp': timestamp.isoformat(),
            'date': date.strftime('%Y-%m-%d'),
            'day_of_week': day_of_week,
            'day_name': day_name,
            'is_weekend': is_weekend,
            'hour': hour,
            'is_peak_hour': is_peak,
            'power_consumption_mw': round(power_mw, 2),
            'temperature_c': round(temperature, 1),
            'humidity_percent': round(humidity, 1),
            'solar_irradiance_wm2': round(max(0, solar_irradiance), 1),
            'cloud_cover_percent': round(cloud_cover, 1),
            'battery_soc_percent': round(battery_soc, 1),
            'primary_source': primary_source,
            'peak_start_morning': WEEKDAY_PEAK_HOURS['morning'][0] if not is_weekend else None,
            'peak_end_morning': WEEKDAY_PEAK_HOURS['morning'][1] if not is_weekend else None,
            'peak_start_afternoon': WEEKEND_PEAK_HOURS['afternoon'][0] if is_weekend else None,
            'peak_end_afternoon': WEEKEND_PEAK_HOURS['afternoon'][1] if is_weekend else None,
            'peak_start_evening': WEEKEND_PEAK_HOURS['evening'][0] if is_weekend else WEEKDAY_PEAK_HOURS['evening'][0],
            'peak_end_evening': WEEKEND_PEAK_HOURS['evening'][1] if is_weekend else WEEKDAY_PEAK_HOURS['evening'][1],
        })
    
    return records


def generate_week_dataset(start_date: datetime = None) -> pd.DataFrame:
    """Generate a full week of data starting from given date"""
    if start_date is None:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    all_records = []
    for day_offset in range(7):
        current_date = start_date + timedelta(days=day_offset)
        day_data = generate_day_data(current_date)
        all_records.extend(day_data)
    
    return pd.DataFrame(all_records)


def export_day_graph(df: pd.DataFrame, day_name: str, day_offset: int):
    """Export a graph for a specific day matching website style"""
    day_data = df[df['day_name'] == day_name].copy()
    if day_data.empty:
        return
    
    is_weekend = day_data['is_weekend'].iloc[0]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    hours = day_data['hour'].values
    power = day_data['power_consumption_mw'].values
    peak_hours = day_data['is_peak_hour'].values
    
    ax.fill_between(hours, power, alpha=0.3, color='#a855f7')
    ax.plot(hours, power, color='#a855f7', linewidth=2, label='AI Forecast')
    
    for i, (h, p, is_peak) in enumerate(zip(hours, power, peak_hours)):
        if is_peak:
            ax.scatter([h], [p], color='#ef4444', s=50, zorder=5)
    
    ax.set_xlabel('Hour of Day', color='white', fontsize=12)
    ax.set_ylabel('Power Consumption (mW)', color='white', fontsize=12)
    ax.set_title(f'Energy Forecast - {day_name} {"(Weekend)" if is_weekend else "(Weekday)"}', 
                 color='white', fontsize=14, fontweight='bold')
    
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#374151')
    ax.spines['top'].set_color('#374151')
    ax.spines['left'].set_color('#374151')
    ax.spines['right'].set_color('#374151')
    ax.grid(True, alpha=0.2, color='#374151')
    
    ax.set_xlim(0, 23)
    ax.set_xticks(range(0, 24, 3))
    ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 3)])
    
    peak_times = "11AM-2PM, 6PM-9PM" if is_weekend else "7AM-9AM, 5PM-8PM"
    ax.text(0.02, 0.98, f'Peak Hours: {peak_times}', transform=ax.transAxes,
            color='#ef4444', fontsize=10, verticalalignment='top')
    
    plt.tight_layout()
    
    filename = os.path.join(GRAPH_DIR, f'forecast_day{day_offset}_{day_name.lower()}.png')
    plt.savefig(filename, dpi=150, facecolor='#1a1a2e', edgecolor='none')
    plt.close()
    print(f'✓ Exported: {filename}')


def main():
    print("=" * 60)
    print("HyperVolt Dataset Generator")
    print("=" * 60)
    
    print("\n📊 Generating 7-day dataset...")
    df = generate_week_dataset()
    
    csv_path = os.path.join(OUTPUT_DIR, 'energy_forecast_dataset.csv')
    df.to_csv(csv_path, index=False)
    print(f'✓ Dataset saved: {csv_path}')
    print(f'  - Total records: {len(df)}')
    print(f'  - Columns: {list(df.columns)}')
    
    print("\n📈 Exporting graphs for each day...")
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i, day_name in enumerate(day_names):
        export_day_graph(df, day_name, i)
    
    print("\n📋 Dataset Summary:")
    print(f"  - Peak hours (weekday morning): {WEEKDAY_PEAK_HOURS['morning']}")
    print(f"  - Peak hours (weekday evening): {WEEKDAY_PEAK_HOURS['evening']}")
    print(f"  - Peak hours (weekend afternoon): {WEEKEND_PEAK_HOURS['afternoon']}")
    print(f"  - Peak hours (weekend evening): {WEEKEND_PEAK_HOURS['evening']}")
    print(f"\n  - Avg power (peak): {df[df['is_peak_hour']]['power_consumption_mw'].mean():.2f} mW")
    print(f"  - Avg power (normal): {df[~df['is_peak_hour']]['power_consumption_mw'].mean():.2f} mW")
    
    print("\n✅ Dataset generation complete!")
    print(f"   Output directory: {OUTPUT_DIR}")
    return df


if __name__ == '__main__':
    main()
