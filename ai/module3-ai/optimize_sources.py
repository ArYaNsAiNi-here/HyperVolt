"""
Energy Source Optimization Algorithm for Vesta Energy Orchestrator
Decides which energy source to use: Grid, Solar, or Battery
Optimizes for both cost and carbon footprint
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Tuple, List
from enum import Enum
import json
import os


class EnergySource(Enum):
    """Available energy sources"""
    GRID = "grid"
    SOLAR = "solar"
    BATTERY = "battery"


class SourceOptimizer:
    """
    Optimization algorithm for energy source selection
    Uses a weighted cost function to minimize both monetary cost and carbon footprint
    """
    
    def __init__(self, 
                 carbon_weight: float = 0.5,
                 cost_weight: float = 0.5,
                 solar_capacity: float = 3.0,  # kW
                 battery_capacity: float = 10.0,  # kWh
                 battery_max_discharge: float = 2.0):  # kW
        """
        Initialize the optimizer
        
        Args:
            carbon_weight: Weight for carbon in optimization (0-1)
            cost_weight: Weight for cost in optimization (0-1)
            solar_capacity: Maximum solar panel output (kW)
            battery_capacity: Battery storage capacity (kWh)
            battery_max_discharge: Maximum battery discharge rate (kW)
        """
        self.carbon_weight = carbon_weight
        self.cost_weight = cost_weight
        self.solar_capacity = solar_capacity
        self.battery_capacity = battery_capacity
        self.battery_max_discharge = battery_max_discharge
        self.battery_current_charge = battery_capacity * 0.8  # Start at 80%
        
        # Cost parameters
        self.battery_cycle_cost = 0.10  # ₹/kWh (battery degradation)
        self.solar_maintenance_cost = 0.05  # ₹/kWh (negligible)
        
    def calculate_solar_available(self, 
                                   solar_radiation: float, 
                                   cloud_cover: float,
                                   hour: int) -> float:
        """
        Calculate available solar power based on conditions
        
        Args:
            solar_radiation: Solar radiation proxy (0-1)
            cloud_cover: Cloud cover percentage (0-100)
            hour: Hour of day (0-23)
            
        Returns:
            Available solar power in kW
        """
        # Only generate during daylight hours (6 AM - 6 PM)
        if hour < 6 or hour >= 18:
            return 0.0
        
        # Reduce by cloud cover
        cloud_factor = (100 - cloud_cover) / 100
        
        # Calculate available power
        solar_power = self.solar_capacity * solar_radiation * cloud_factor
        
        return max(0, solar_power)
    
    def calculate_cost_score(self,
                            source: EnergySource,
                            power_needed: float,
                            grid_price: float) -> float:
        """
        Calculate cost score for using a particular source
        Lower is better
        
        Args:
            source: Energy source to evaluate
            power_needed: Power required (kW)
            grid_price: Current grid electricity price (₹/kWh)
            
        Returns:
            Cost score (₹)
        """
        if source == EnergySource.GRID:
            return power_needed * grid_price
        elif source == EnergySource.SOLAR:
            return power_needed * self.solar_maintenance_cost
        elif source == EnergySource.BATTERY:
            return power_needed * self.battery_cycle_cost
        
        return 0.0
    
    def calculate_carbon_score(self,
                               source: EnergySource,
                               power_needed: float,
                               carbon_intensity: float) -> float:
        """
        Calculate carbon score for using a particular source
        Lower is better
        
        Args:
            source: Energy source to evaluate
            power_needed: Power required (kW)
            carbon_intensity: Grid carbon intensity (gCO2eq/kWh)
            
        Returns:
            Carbon score (gCO2eq)
        """
        if source == EnergySource.GRID:
            return power_needed * carbon_intensity
        elif source == EnergySource.SOLAR:
            # Solar has minimal carbon footprint (manufacturing amortized)
            return power_needed * 50  # 50 gCO2eq/kWh lifecycle emissions
        elif source == EnergySource.BATTERY:
            # Battery depends on how it was charged
            # Assume average grid carbon (conservative estimate)
            return power_needed * carbon_intensity * 0.8  # 80% of grid
        
        return 0.0
    
    def calculate_combined_score(self,
                                 cost_score: float,
                                 carbon_score: float) -> float:
        """
        Calculate weighted combined score
        Normalizes carbon to cost equivalent for comparison
        
        Args:
            cost_score: Cost in ₹
            carbon_score: Carbon in gCO2eq
            
        Returns:
            Combined score (lower is better)
        """
        # Normalize carbon to cost (1 kg CO2 = ₹10 penalty)
        carbon_cost_equivalent = (carbon_score / 1000) * 10
        
        combined = (self.cost_weight * cost_score + 
                   self.carbon_weight * carbon_cost_equivalent)
        
        return combined
    
    def optimize_source(self,
                       power_needed: float,
                       conditions: Dict) -> Tuple[List[Tuple[EnergySource, float]], Dict]:
        """
        Optimize energy source selection for given power requirement
        
        Args:
            power_needed: Power required (kW)
            conditions: Dictionary with current conditions:
                - solar_radiation: 0-1
                - cloud_cover: 0-100
                - hour: 0-23
                - carbon_intensity: gCO2eq/kWh
                - grid_price: ₹/kWh
                
        Returns:
            Tuple of (source allocation list, decision metrics)
            Source allocation: [(EnergySource, kW), ...]
        """
        # Calculate available power from each source
        solar_available = self.calculate_solar_available(
            conditions['solar_radiation'],
            conditions['cloud_cover'],
            conditions['hour']
        )
        
        battery_available = min(
            self.battery_max_discharge,
            self.battery_current_charge  # Can't discharge more than stored
        )
        
        # Calculate scores for each source
        scores = {}
        for source in EnergySource:
            cost_score = self.calculate_cost_score(
                source, power_needed, conditions['grid_price']
            )
            carbon_score = self.calculate_carbon_score(
                source, power_needed, conditions['carbon_intensity']
            )
            combined_score = self.calculate_combined_score(cost_score, carbon_score)
            
            scores[source] = {
                'cost': cost_score,
                'carbon': carbon_score,
                'combined': combined_score
            }
        
        # Decision logic: prioritize based on availability and scores
        allocation = []
        remaining_power = power_needed
        
        # 1. Use solar first if available (always best)
        if solar_available > 0 and remaining_power > 0:
            solar_used = min(solar_available, remaining_power)
            allocation.append((EnergySource.SOLAR, solar_used))
            remaining_power -= solar_used
        
        # 2. Decide between battery and grid based on scores
        if remaining_power > 0:
            # Check if battery is better than grid
            if (battery_available > 0 and 
                scores[EnergySource.BATTERY]['combined'] < scores[EnergySource.GRID]['combined']):
                # Use battery
                battery_used = min(battery_available, remaining_power)
                allocation.append((EnergySource.BATTERY, battery_used))
                remaining_power -= battery_used
                self.battery_current_charge -= battery_used
        
        # 3. Use grid for any remaining power
        if remaining_power > 0:
            allocation.append((EnergySource.GRID, remaining_power))
        
        # Calculate actual costs and carbon
        actual_cost = sum([
            self.calculate_cost_score(source, power, conditions['grid_price'])
            for source, power in allocation
        ])
        
        actual_carbon = sum([
            self.calculate_carbon_score(source, power, conditions['carbon_intensity'])
            for source, power in allocation
        ])
        
        metrics = {
            'total_power': power_needed,
            'solar_available': solar_available,
            'battery_available': battery_available,
            'allocation': [(s.value, f"{p:.3f}") for s, p in allocation],
            'cost': actual_cost,
            'carbon': actual_carbon,
            'battery_charge': self.battery_current_charge,
            'scores': {k.value: v for k, v in scores.items()}
        }
        
        return allocation, metrics
    
    def charge_battery_from_solar(self, solar_excess: float):
        """
        Charge battery from excess solar power
        
        Args:
            solar_excess: Excess solar power available (kW)
        """
        charge_amount = min(
            solar_excess,
            self.battery_capacity - self.battery_current_charge
        )
        self.battery_current_charge += charge_amount
        return charge_amount
    
    def simulate_day(self, df_day: pd.DataFrame) -> pd.DataFrame:
        """
        Simulate optimal source selection for a full day
        
        Args:
            df_day: DataFrame with hourly data for one day
            
        Returns:
            DataFrame with optimization results for each hour
        """
        results = []
        
        for idx, row in df_day.iterrows():
            # Power needed (convert kWh to kW for 1-hour period)
            power_needed = row['total_energy_kwh']
            
            # Current conditions
            conditions = {
                'solar_radiation': row['solar_radiation_proxy'],
                'cloud_cover': row['cloud_cover'],
                'hour': row['hour'],
                'carbon_intensity': row['carbon_intensity'],
                'grid_price': row['grid_price_per_kwh']
            }
            
            # Optimize source selection
            allocation, metrics = self.optimize_source(power_needed, conditions)
            
            # Check if there's excess solar for battery charging
            solar_available = metrics['solar_available']
            solar_used = sum([p for s, p in allocation if s == EnergySource.SOLAR])
            solar_excess = solar_available - solar_used
            
            if solar_excess > 0:
                charged = self.charge_battery_from_solar(solar_excess)
                metrics['battery_charged'] = charged
            else:
                metrics['battery_charged'] = 0
            
            results.append({
                'timestamp': row['timestamp'],
                'hour': row['hour'],
                'power_needed': power_needed,
                'allocation': metrics['allocation'],
                'cost': metrics['cost'],
                'carbon': metrics['carbon'],
                'battery_charge': metrics['battery_charge'],
                'battery_charged': metrics['battery_charged']
            })
        
        return pd.DataFrame(results)


def main():
    """
    Main function to demonstrate source optimization
    """
    print("=" * 70)
    print("ENERGY SOURCE OPTIMIZATION - DEMONSTRATION")
    print("=" * 70)
    
    # Load data
    data_path = 'data/raw/integrated_dataset.csv'
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        return
    
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Initialize optimizer
    # Balanced between cost and carbon (50-50)
    optimizer = SourceOptimizer(
        carbon_weight=0.5,
        cost_weight=0.5,
        solar_capacity=3.0,  # 3 kW solar panels
        battery_capacity=10.0,  # 10 kWh battery
        battery_max_discharge=2.0  # Max 2 kW discharge
    )
    
    # Simulate one day
    print("\nSimulating optimal source selection for one day...")
    df_day = df.head(24)  # First 24 hours
    results = optimizer.simulate_day(df_day)
    
    # Print results
    print("\n" + "=" * 70)
    print("HOURLY OPTIMIZATION RESULTS")
    print("=" * 70)
    
    for idx, row in results.iterrows():
        print(f"\nHour {row['hour']:02d}:00")
        print(f"  Power needed: {row['power_needed']:.3f} kW")
        print(f"  Sources: {row['allocation']}")
        print(f"  Cost: ₹{row['cost']:.2f}")
        print(f"  Carbon: {row['carbon']:.0f} gCO2eq")
        print(f"  Battery: {row['battery_charge']:.2f} kWh", end="")
        if row['battery_charged'] > 0:
            print(f" (+{row['battery_charged']:.2f} kWh charged)")
        else:
            print()
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("DAILY SUMMARY")
    print("=" * 70)
    
    total_cost = results['cost'].sum()
    total_carbon = results['carbon'].sum()
    
    # Calculate what it would cost using only grid
    grid_only_cost = (df_day['total_energy_kwh'] * df_day['grid_price_per_kwh']).sum()
    grid_only_carbon = (df_day['total_energy_kwh'] * df_day['carbon_intensity']).sum()
    
    print(f"\nWith Optimization:")
    print(f"  Total Cost:   ₹{total_cost:.2f}")
    print(f"  Total Carbon: {total_carbon/1000:.2f} kg CO2")
    
    print(f"\nGrid Only (No Optimization):")
    print(f"  Total Cost:   ₹{grid_only_cost:.2f}")
    print(f"  Total Carbon: {grid_only_carbon/1000:.2f} kg CO2")
    
    print(f"\nSavings:")
    print(f"  Cost Saved:   ₹{grid_only_cost - total_cost:.2f} ({(1 - total_cost/grid_only_cost)*100:.1f}%)")
    print(f"  Carbon Saved: {(grid_only_carbon - total_carbon)/1000:.2f} kg CO2 ({(1 - total_carbon/grid_only_carbon)*100:.1f}%)")
    
    # Save results
    output_path = 'data/optimization_results.csv'
    results.to_csv(output_path, index=False)
    print(f"\n✓ Results saved to: {output_path}")
    
    # Save optimizer configuration
    config = {
        'carbon_weight': optimizer.carbon_weight,
        'cost_weight': optimizer.cost_weight,
        'solar_capacity': optimizer.solar_capacity,
        'battery_capacity': optimizer.battery_capacity,
        'battery_max_discharge': optimizer.battery_max_discharge,
        'simulation_date': datetime.now().isoformat()
    }
    
    config_path = 'models/optimizer_config.json'
    os.makedirs('models', exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to: {config_path}")
    
    print("\n" + "=" * 70)
    print("✓ OPTIMIZATION DEMONSTRATION COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()
