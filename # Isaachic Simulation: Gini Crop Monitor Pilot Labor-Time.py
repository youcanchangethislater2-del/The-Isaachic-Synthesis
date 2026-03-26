import random
import math
import time
import serial
import serial.tools.list_ports

# --- HARDWARE INITIALIZATION ---
def find_microbit_port():
    """Automatically finds the micro:bit port on a Mac."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "usbmodem" in port.device or "BBC micro:bit" in port.description:
            print(f">>> METABOLIC UMBILICAL FOUND: {port.device}")
            return port.device
    return None

port_address = find_microbit_port()
try:
    ser = serial.Serial(port_address, 115200, timeout=1) if port_address else None
except Exception as e:
    print(f"[ERROR] Could not open serial port: {e}")
    ser = None

if not ser:
    print("[WARNING] Hardware not found. Running in MOCK MODE.")

# --- RESOURCE BANK: THE METABOLIC BASIN ---
class ResourceBank:
    def __init__(self):
        self.waste_bin = {k: 0 for k in ["Steel", "Plastic", "Wood", "Bread", "Medicine", "Water", "Electricity", "Healthcare", "Electronics", "Nutrients"]}
        
        self.plots = {
            "Plot_A": {"moisture": 300, "nutrients": 500, "biomass": 850, "capacity": 1000},
            "Plot_B": {"moisture": 100, "nutrients": 200, "biomass": 400, "capacity": 1000} 
        }

        self.registry = {
            "Nutrient_Solution": {"capacity": 1000, "current": 800, "regrow_rate": 0.02}, # NPK levels
            "Total_Water_Tank": {"capacity": 5000, "current": 4800, "regrow_rate": 0.10}, 
            "Electricity": {"capacity": 2000, "current": 1800}
        }

        self.nutrient_input, self.biomass_output, self.soil_damage_ticks = 0.0, 0.0, 0
        self.environmental_entropy = {"temperature": 25.0, "humidity": 0.50}
        self.minimum_survival = {"Water": 1500.0, "Nutrients": 600.0}

    def sync_sensors(self):
        if ser and ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                if "," in line:
                    raw_moisture, temp = line.split(",")
                    # Convert raw 0-1023 to 0-100%
                    clean_moisture = self.map_moisture(float(raw_moisture))
                    
                    self.plots["Plot_A"]["moisture"] = clean_moisture
                    self.environmental_entropy["temperature"] = float(temp)
                    
                    print(f">>> METABOLIC DATA: Moisture={clean_moisture:.1f}%, Temp={temp}°C")
            except: pass


    def apply_entropy(self):
        temp = self.environmental_entropy["temperature"]
        heatwave_factor = 2.0 if temp >= 32 else 1.0
        decay_rates = {"Water": 0.02 * heatwave_factor, "Nutrients": 0.01}
        
        for name, rate in decay_rates.items():
            if name in self.registry:
                self.registry[name]["current"] -= (self.registry[name]["current"] * rate)

    def get_enlt_multiplier(self, resource_name):
        res = self.registry.get("Total_Water_Tank") if resource_name == "Water" else None
        if res:
            raw_mult = res["capacity"] / max(res["current"], 0.01)
            return 1 + (raw_mult - 1) * 0.3
        return 1.0

    def get_resilience(self, resource_name, usage_rate):
        res = self.registry.get("Total_Water_Tank") if resource_name == "Water" else None
        if not res or usage_rate <= 0: return 99.0
        return (max(res["current"] - self.minimum_survival.get("Water"), 0) / usage_rate)

    def map_moisture(self, raw_value):
        """Maps raw 0-1023 analog data to 0-100% moisture."""
        # Calibration: 200 is bone dry, 850 is fully saturated
        dry = 200 # Change these later to reflect real sensor calibration
        wet = 850 # Change these later to reflect real sensor calibration
        
        # Clamp and scale
        percentage = ((raw_value - dry) / (wet - dry)) * 100
        return max(0, min(100, percentage))


# --- CENTRAL PLAN: THE CYBERNETIC BRAIN ---
class CentralPlan:
    def __init__(self, resource_bank):
        self.bank = resource_bank
        self.products = {
        "NPK_Intake": {"planned_labor": 10, "base_enlt": 5}, # Nutrients for crops
        "Irrigation": {"planned_labor": 15, "base_enlt": 3}, # Water for crops
        "Stability": {"planned_labor": 13, "base_enlt": 5}   # Ecological stability (e.g. pest control, soil health)
        }
    def calculate_gini(self, values):
        n = len(values)
        if n < 2 or sum(values) == 0: return 0
        mean_v = sum(values) / n
        diff_sum = sum(abs(i - j) for i in values for j in values)
        return diff_sum / (2 * n**2 * mean_v)

    def calculate_theil(self, values):
        n = len(values)
        if n < 2: return 0
        mu = sum(values) / n
        return sum((x/mu) * math.log(x/mu) for x in values if x > 0) / n

    def execute_metabolic_rebalancing(self, plots):
            print("\n[CYBER-BRAIN] INEQUALITY DETECTED. Sounding Alarm...")
            if ser:
                ser.write(b"BEEP\n") # The Alarm
                time.sleep(0.1)
                ser.write(b"PUMP_ON\n") # The Action
            
            avg_moisture = sum(p['moisture'] for p in plots.values()) / len(plots)
            for name in plots: plots[name]['moisture'] = avg_moisture

    def calculate_suv(self, plot_data):
        print("\n" + "="*40 + "\n--- ISAACHIC FEEDBACK ---")
        gini = self.calculate_gini(plot_data)
        theil = self.calculate_theil(plot_data)
        total_satisfaction = 0
        
        for name, data in self.products.items():
            mult = self.bank.get_enlt_multiplier(name)
            res = self.bank.get_resilience(name, data["planned_labor"] * 0.1)
            ps = (data["planned_labor"] * 1.0) / (data["base_enlt"] * mult)

            action = "PROCEED"
            if res < 3.0: action = "VETOED (RESILIENCE)"
            elif ps < 1.0 or (gini > 0.5 and name == "Water"): action = "VETOED (STRANGLED)"
            else: total_satisfaction += 1.0
            print(f"{name:10} | PS: {ps:.2f} | {action} | Res: {res:.1f}d")
        
        stability = (total_satisfaction / len(self.products)) * 100
        print(f"STABILITY: {stability:.1f}% | Gini: {gini:.2f} | Theil: {theil:.3f}")
        return stability, gini

# --- EXECUTION ---
if __name__ == "__main__":
    earth = ResourceBank(); plan = CentralPlan(earth)
    with open("metabolic_log.csv", "w") as f: f.write("Cycle,Stability,Gini\n")

    for cycle in range(1, 41):
        print(f"\n### CYCLE {cycle} ###")
        earth.sync_sensors()
        earth.apply_entropy()
        
        moisture_levels = [p['moisture'] for p in earth.plots.values()]
        
        if plan.calculate_gini(moisture_levels) > 0.3:
            plan.execute_metabolic_rebalancing(earth.plots)
            moisture_levels = [p['moisture'] for p in earth.plots.values()]
            
        stability, gini = plan.calculate_suv(moisture_levels)
        with open("metabolic_log.csv", "a") as f: f.write(f"{cycle},{stability},{gini}\n")
        time.sleep(1)
