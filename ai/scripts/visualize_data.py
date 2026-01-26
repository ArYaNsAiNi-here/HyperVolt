"""
Data Visualization Script for Vesta Energy Orchestrator
Generates quick visualizations of the collected datasets
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

def visualize_datasets():
    """
    Create visualizations for the collected datasets
    """
    # Check if data exists
    data_path = 'data/raw/integrated_dataset.csv'
    if not os.path.exists(data_path):
        print("Error: Dataset not found. Please run 'python module3-ai/collect_all_data.py' first.")
        return
    
    # Load data
    print("Loading integrated dataset...")
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle('Vesta Energy Orchestrator - Dataset Overview', fontsize=16, fontweight='bold')
    
    # 1. Energy Consumption Over Time
    ax = axes[0, 0]
    ax.plot(df['timestamp'], df['total_energy_kwh'], linewidth=0.8, alpha=0.7)
    ax.set_title('Total Energy Consumption (30 Days)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Energy (kWh)')
    ax.grid(True, alpha=0.3)
    
    # 2. Energy Breakdown
    ax = axes[0, 1]
    energy_breakdown = df[['lighting_energy_kwh', 'appliance_energy_kwh', 'hvac_energy_kwh']].mean()
    ax.bar(range(len(energy_breakdown)), energy_breakdown.values)
    ax.set_xticks(range(len(energy_breakdown)))
    ax.set_xticklabels(['Lighting', 'Appliances', 'HVAC'], rotation=15)
    ax.set_title('Average Energy by Category')
    ax.set_ylabel('Energy (kWh)')
    ax.grid(True, alpha=0.3, axis='y')
    
    # 3. Carbon Intensity Pattern
    ax = axes[1, 0]
    # Group by hour and get average carbon intensity
    hourly_carbon = df.groupby('hour')['carbon_intensity'].mean()
    ax.plot(hourly_carbon.index, hourly_carbon.values, marker='o', linewidth=2)
    ax.set_title('Average Carbon Intensity by Hour')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Carbon Intensity (gCO2eq/kWh)')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=df['carbon_intensity'].mean(), color='r', linestyle='--', 
               label=f'Avg: {df["carbon_intensity"].mean():.0f}')
    ax.legend()
    
    # 4. Temperature vs Energy
    ax = axes[1, 1]
    scatter = ax.scatter(df['temperature'], df['total_energy_kwh'], 
                        c=df['hour'], cmap='viridis', alpha=0.5, s=10)
    ax.set_title('Energy vs Temperature')
    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Total Energy (kWh)')
    ax.grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Hour of Day')
    
    # 5. Grid Price Over Time
    ax = axes[2, 0]
    ax.plot(df['timestamp'], df['grid_price_per_kwh'], linewidth=0.8, alpha=0.7, color='green')
    ax.set_title('Grid Electricity Price')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price (₹/kWh)')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=df['grid_price_per_kwh'].mean(), color='r', linestyle='--',
               label=f'Avg: ₹{df["grid_price_per_kwh"].mean():.2f}')
    ax.legend()
    
    # 6. Renewable Percentage
    ax = axes[2, 1]
    hourly_renewable = df.groupby('hour')['renewable_percentage'].mean()
    ax.fill_between(hourly_renewable.index, 0, hourly_renewable.values, alpha=0.6, color='green')
    ax.plot(hourly_renewable.index, hourly_renewable.values, linewidth=2, color='darkgreen')
    ax.set_title('Average Renewable Energy % by Hour')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Renewable %')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 100)
    
    plt.tight_layout()
    
    # Save figure
    output_path = 'data/dataset_visualization.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Visualization saved to: {output_path}")
    
    # Print statistics
    print("\n" + "=" * 70)
    print("DATASET STATISTICS")
    print("=" * 70)
    print(f"\n📊 Dataset Overview:")
    print(f"  Total Records: {len(df):,}")
    print(f"  Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"  Features: {len(df.columns)}")
    
    print(f"\n⚡ Energy Statistics:")
    print(f"  Average Hourly: {df['total_energy_kwh'].mean():.3f} kWh")
    print(f"  Peak Hour: {df['total_energy_kwh'].max():.3f} kWh")
    print(f"  Total (30 days): {df['total_energy_kwh'].sum():.1f} kWh")
    print(f"  Daily Average: {df['total_energy_kwh'].sum() / 30:.1f} kWh")
    
    print(f"\n🌍 Carbon & Cost:")
    print(f"  Avg Carbon Intensity: {df['carbon_intensity'].mean():.0f} gCO2eq/kWh")
    print(f"  Total Carbon (30d): {df['carbon_footprint'].sum():.1f} kg CO2")
    print(f"  Avg Grid Price: ₹{df['grid_price_per_kwh'].mean():.2f}/kWh")
    print(f"  Total Cost (30d): ₹{df['energy_cost'].sum():.2f}")
    
    print(f"\n🌡️ Environmental:")
    print(f"  Avg Temperature: {df['temperature'].mean():.1f}°C")
    print(f"  Avg Humidity: {df['humidity'].mean():.1f}%")
    print(f"  Avg Renewable %: {df['renewable_percentage'].mean():.1f}%")
    
    print(f"\n🔌 Peak Hours (Highest Consumption):")
    top_hours = df.groupby('hour')['total_energy_kwh'].mean().nlargest(5)
    for hour, energy in top_hours.items():
        print(f"  {int(hour):02d}:00 - {energy:.3f} kWh")
    
    print("\n" + "=" * 70)
    
    # Show plot if not in headless mode
    try:
        plt.show()
    except (ImportError, RuntimeError) as e:
        print(f"\nNote: Running in headless mode ({e.__class__.__name__}), plot saved but not displayed.")


def main():
    """
    Main function to run visualizations
    """
    print("=" * 70)
    print("VESTA ENERGY ORCHESTRATOR - DATA VISUALIZATION")
    print("=" * 70)
    
    visualize_datasets()
    
    print("\n✓ Visualization complete!")
    print("  View the chart at: data/dataset_visualization.png")


if __name__ == "__main__":
    main()
