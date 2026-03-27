import random

# --- RESOURCE BANK: THE METABOLIC BASIN ---
class ResourceBank:
    def __init__(self):
        self.waste_bin = {k: 0 for k in ["Steel", "Plastic", "Wood", "Bread", "Medicine", "Water", "Electricity", "Healthcare", "Electronics"]} 
        self.registry = {
            "Bread": {"capacity": 1000, "current": 1000, "regrow_rate": 0.05}, 
            "Medicine": {"capacity": 500, "current": 500, "regrow_rate": 0.0}, 
            "Water": {"capacity": 5000, "current": 5000, "regrow_rate": 0.10}, 
            "Steel": {"capacity": 1000, "current": 1000, "regrow_rate": 0.0}, 
            "Wood": {"capacity": 1200, "current": 1200, "regrow_rate": 0.08}, 
            "Electricity": {"capacity": 2000, "current": 2000, "regrow_rate": 0.20}, 
            "Plastic": {"capacity": 1500, "current": 1500, "regrow_rate": 0.0}, 
            "Healthcare": {"capacity": 1000, "current": 1000, "regrow_rate": 0.0},
            "Electronics": {"capacity": 500, "current": 0, "regrow_rate": 0.0} 
        }
        self.carbon_debt = 0

    def produce(self, product_name, labor_units, unlocked_luxury):
        if product_name in self.registry:
            res = self.registry[product_name]
            # Industrial pollution increases Carbon Debt
            if product_name in ["Steel", "Plastic"]:
                self.carbon_debt += (labor_units * 0.05)
            
            if res["regrow_rate"] == 0:
                # Automation Bonus: Scaled up to 3x productivity based on Electronics stock
                elec_integrity = self.registry["Electronics"]["current"] / 500 if unlocked_luxury else 0
                automation_bonus = 1.0 + (elec_integrity * 2.0)
                production = labor_units * 15 * automation_bonus
                res["current"] = min(res["capacity"], res["current"] + production)

    def apply_entropy(self):
        decay_rates = {"Bread": 0.03, "Steel": 0.02, "Electricity": 0.02, "Electronics": 0.05}
        for name, rate in decay_rates.items():
            if name in self.registry:
                self.registry[name]["current"] -= (self.registry[name]["current"] * rate)

    def tick(self, drought=False): 
        for name, res in self.registry.items():
            rate = res["regrow_rate"]
            if drought and name in ["Water", "Wood"]: rate *= 0.5
            if rate > 0:
                growth = res["capacity"] * rate
                res["current"] = min(res["capacity"], res["current"] + growth)
                
    def recycle(self):
        for name, amount in self.waste_bin.items():
            recovered = amount * 0.8 
            if name in self.registry:
                self.registry[name]["current"] = min(self.registry[name]["capacity"], self.registry[name]["current"] + recovered)
            self.waste_bin[name] = 0

    def get_enlt_multiplier(self, resource_name):
        res = self.registry.get(resource_name)
        if res:
            raw_multiplier = res["capacity"] / max(res["current"], 0.01)
            damping = res.get("temp_damping", 0.3)
            return 1 + (raw_multiplier - 1) * damping
        return 1.0

    def deplete(self, resource_name, amount):
        if resource_name in self.registry:
            usage = (amount * 0.1)
            self.registry[resource_name]["current"] = max(0, self.registry[resource_name]["current"] - usage)
            if resource_name in self.waste_bin: self.waste_bin[resource_name] += usage

# --- CENTRAL PLAN: THE CYBERNETIC BRAIN ---
class CentralPlan:
    def __init__(self, resource_bank):
        self.bank = resource_bank
        self.in_emergency = False
        self.original_plan = {}
        self.substitutes = {
            "Steel": ["Wood", "Plastic", "Electricity"],
            "Wood": ["Plastic", "Steel"],
            "Plastic": ["Wood", "Bread"],
            "Electricity": ["Wood", "Water", "Steel"],
        }
        self.unlocked_luxury = False
        self.happiness_streak = 0
        self.products = {
            "Bread": {"planned_labor": 12, "spent_vouchers": 0, "base_enlt": 4, "labor_weight": 0.125},
            "Medicine": {"planned_labor": 8, "spent_vouchers": 0, "base_enlt": 6, "labor_weight": 0.125},
            "Water": {"planned_labor": 15, "spent_vouchers": 0, "base_enlt": 3, "labor_weight": 0.125},
            "Wood": {"planned_labor": 12, "spent_vouchers": 0, "base_enlt": 8, "labor_weight": 0.125},
            "Steel": {"planned_labor": 15, "spent_vouchers": 0, "base_enlt": 12, "labor_weight": 0.125},
            "Electricity": {"planned_labor": 15, "spent_vouchers": 0, "base_enlt": 8, "labor_weight": 0.125},
            "Plastic": {"planned_labor": 10, "spent_vouchers": 0, "base_enlt": 10, "labor_weight": 0.125},
            "Healthcare": {"planned_labor": 13, "spent_vouchers": 0, "base_enlt": 5, "labor_weight": 0.125},
        }

    def check_luxury_unlock(self, stability):
        if not self.unlocked_luxury and stability >= 85:
            self.happiness_streak += 1
            if self.happiness_streak >= 3:
                self.unlocked_luxury = True
                self.products["Electronics"] = {"planned_labor": 50, "spent_vouchers": 0, "base_enlt": 15, "labor_weight": 0.1}
                self.bank.registry["Electronics"]["current"] = 100
                print("\n!!! ACHIEVEMENT UNLOCKED: HIGH-TECH LUXURY !!!")

    def innovate(self):
        target = random.choice(list(self.products.keys()))
        self.products[target]["base_enlt"] *= 0.85
    
    def dynamic_reallocation(self):
        scarcity_map = {}
        total_scarcity = 0
        for name in self.products:
            res = self.bank.registry[name]
            s = res["capacity"] / max(res["current"], 1.0)
            scarcity_map[name] = s ** 2 
            total_scarcity += scarcity_map[name]
        for name in self.products:
            self.products[name]["labor_weight"] = (scarcity_map[name] / total_scarcity) if total_scarcity > 0 else 1 / len(self.products)

    def democratic_vote(self, target_product, motion_type):
        if target_product not in self.products: return
        if motion_type == "FORCE_LABOR":
            if not self.in_emergency:
                self.in_emergency = True
                self.original_plan = {prod: data["planned_labor"] for prod, data in self.products.items()}
                print(f"  * EMERGENCY MEASURE: War-Economy controls activated for {target_product}.")
            if self.bank.registry[target_product]["current"] <= 1.0:
                self.bank.registry[target_product]["current"] = 10.0 
            for prod in self.products:
                if prod != target_product:
                    tax = self.products[prod]["planned_labor"] * 0.8
                    self.products[prod]["planned_labor"] -= tax
                    self.products[target_product]["planned_labor"] += tax

    def calculate_suv(self):
        total_satisfaction = 0
        for name, data in self.products.items():
            suv = data["spent_vouchers"] / max(data["planned_labor"], 1)
            mult = self.bank.get_enlt_multiplier(name)
            ps = (data["planned_labor"] * suv) / (data["base_enlt"] * mult)
            if ps < 1.0:
                for alt in self.substitutes.get(name, []):
                    if alt in self.products: total_satisfaction += 0.5; break
            else: total_satisfaction += 1.0
        
        raw_stability = (total_satisfaction / len(self.products)) * 100
        essentials = ["Bread", "Water", "Medicine", "Electricity", "Healthcare"]
        lowest_essential = min([(self.bank.registry[res]["current"] / self.bank.registry[res]["capacity"]) * 100 for res in essentials])
        self.social_stability = min(raw_stability, lowest_essential)
        for name in self.products: self.products[name]["spent_vouchers"] = 0
        return self.social_stability

    def normalize_economy(self):
        essentials = ["Bread", "Water", "Medicine", "Electricity", "Healthcare"]
        lowest_essential = min([(self.bank.registry[res]["current"] / self.bank.registry[res]["capacity"]) * 100 for res in essentials])
        if self.in_emergency and lowest_essential >= 75.0:
            print(f"\n>>> NORMALIZATION: {lowest_essential:.1f}% Integrity achieved. Restoring Snapshot Plan.")
            for prod, labor_val in self.original_plan.items():
                if prod in self.products: self.products[prod]["planned_labor"] = labor_val
            self.in_emergency = False

# --- AGENT & EXECUTION ---
class IsaachicAgent:
    def __init__(self, training): self.v_hour = 1 + (training / 40000); self.vouchers = 0
    def work(self, hrs): self.vouchers += hrs * self.v_hour; return hrs

earth = ResourceBank(); plan = CentralPlan(earth)
surgeon = IsaachicAgent(20000); laborer = IsaachicAgent(0)

for year in range(1, 81):
    h1 = surgeon.work(40); h2 = laborer.work(40)
    total_hours = h1 + h2
    
    # Calculate Efficiency Bonus based on Electronics stock
    elec_integrity = earth.registry["Electronics"]["current"] / 500 if plan.unlocked_luxury else 0
    current_eff = 1.0 + (elec_integrity * 2.0)
    
    # High-Tech Automation drains electricity
    if plan.unlocked_luxury and earth.registry["Electronics"]["current"] > 100:
        earth.registry["Electricity"]["current"] -= 50 
    
    # Historical Crises
    if 20 <= year <= 25: total_hours *= 0.3; surgeon.vouchers *= 0.3; laborer.vouchers *= 0.3 # Great Fire
    if 60 <= year <= 65: earth.registry["Electricity"]["current"] *= 0.5 # Energy Crisis

    plan.dynamic_reallocation() 
    for prod_name, data in plan.products.items():
        earth.produce(prod_name, total_hours * data["labor_weight"], plan.unlocked_luxury)

    consumption_surge = 1.0 + (year * 0.01) 
    share = ((surgeon.vouchers + laborer.vouchers) / len(plan.products)) * consumption_surge
    for prod in plan.products: 
        plan.products[prod]["spent_vouchers"] += share
        earth.deplete(prod, share)
    
    surgeon.vouchers = 0; laborer.vouchers = 0 
    stability = plan.calculate_suv()
    plan.normalize_economy()
    
    # Climate Feedback based on industrial debt
    drought_roll = random.random()
    is_drought = drought_roll < (earth.carbon_debt / 1000)
    
    earth.apply_entropy()
    earth.tick(drought=is_drought)
    if year == 12: earth.registry["Wood"]["current"] *= 0.3 # Initial Wood Shock
    earth.recycle(); plan.innovate(); plan.check_luxury_unlock(stability)
    
    if stability < 40:
        active_products = list(plan.products.keys())
        worst_res = min(active_products, key=lambda k: earth.registry[k]["current"])
        plan.democratic_vote(worst_res, "FORCE_LABOR")

    # Audit Print for milestones
    if year == 1 or year % 10 == 0 or year == 80:
        print(f"\n" + "="*30 + f"\n   AUDIT: YEAR {year}\n" + "="*30)
        for name, res in earth.registry.items():
            health = (res["current"] / res["capacity"]) * 100
            print(f"{name:12} | Integrity: {health:.1f}%")
        print(f"\n[SYSTEM DATA]\nEFFICIENCY: {current_eff:.2f}x | CARBON: {earth.carbon_debt:.1f} | STABILITY: {plan.social_stability:.1f}%\n" + "="*30)

print("\nSYSTEM TERMINATED: 80-Year Historical Cycle Complete.")
