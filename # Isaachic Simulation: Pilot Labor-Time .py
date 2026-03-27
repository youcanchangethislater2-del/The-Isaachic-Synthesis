import random

# --- RESOURCE BANK: THE METABOLIC BASIN ---
class ResourceBank:
    def __init__(self):
        self.waste_bin = {"Steel": 0, "Plastic": 0, "Wood": 0, "Bread": 0, "Medicine": 0, "Water": 0, "Electricity": 0, "Healthcare": 0, "Electronics": 0} 
        self.registry = {
            # SET 'current' EQUAL TO 'capacity'
            "Bread": {"capacity": 1000, "current": 1000, "regrow_rate": 0.05}, 
            "Medicine": {"capacity": 500, "current": 500, "regrow_rate": 0.0}, 
            "Water": {"capacity": 5000, "current": 5000, "regrow_rate": 0.10}, 
            "Steel": {"capacity": 1000, "current": 1000, "regrow_rate": 0.0}, 
            "Wood": {"capacity": 1200, "current": 1200, "regrow_rate": 0.08}, 
            "Electricity": {"capacity": 2000, "current": 2000, "regrow_rate": 0.20}, 
            "Plastic": {"capacity": 1500, "current": 1500, "regrow_rate": 0.0}, 
            "Healthcare": {"capacity": 1000, "current": 1000, "regrow_rate": 0.0},
            "Electronics": {"capacity": 500, "current": 0, "regrow_rate": 0.0} # Keep at 0 until unlocked
        }

        

    # --- ADDED THIS METHOD ---
    def produce(self, product_name, labor_units):
        if product_name in self.registry:
            res = self.registry[product_name]
            if res["regrow_rate"] == 0:
                production = labor_units * 15 
                res["current"] = min(res["capacity"], res["current"] + production)
                print(f"  [PROD] {product_name} stock increased...")

    def apply_entropy(self):
        decay_rates = {"Bread": 0.03, "Steel": 0.02, "Electricity": 0.02, "Electronics": 0.05}
        print(">>> ENTROPY: Natural decay applied to stocks.")
        for name, rate in decay_rates.items():
            if name in self.registry:
                self.registry[name]["current"] -= (self.registry[name]["current"] * rate)

    def tick(self, drought=False): 
        print("\n>>> METABOLIC TICK <<<")
        for name, res in self.registry.items():
            rate = res["regrow_rate"]
            if drought and name in ["Water", "Wood"]: rate *= 0.5
            if rate > 0:
                growth = res["capacity"] * rate
                res["current"] = min(res["capacity"], res["current"] + growth)
                # COMMENT OUT THIS LINE:
                # print(f"  * {name} regenerated...")

                
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
            
            # Check for Democratic Subsidy (Temporary Damping Override)
            damping = res.get("temp_damping", 0.3)
            # Reset for next year so it's not a permanent cheat
            if "temp_damping" in res: del res["temp_damping"] 
            
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
        self.in_emergency = False  # Track if we are in War-Economy mode
        self.original_plan = {}    # Store the snapshot for recovery
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
        if self.unlocked_luxury and "Electronics" in self.products and self.products["Electronics"]["spent_vouchers"] == 0:
            target = "Electronics" if random.random() < 0.6 else random.choice(list(self.products.keys()))
        else:
            target = random.choice(list(self.products.keys()))
        self.products[target]["base_enlt"] *= 0.85
        print(f"[TECH] Research focused on {target}. Cost reduced by 15%.")
    
    def dynamic_reallocation(self):
        """The Cybernetic Governor: Shifts labor weights based on scarcity squared."""
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
            """Allows agents to collectively override the algorithm."""
            # Safety check: Can't vote on a product the Plan hasn't unlocked yet
            if target_product not in self.products:
                print(f"\n[VOTE] Motion for {target_product} BLOCKED: Technology not yet unlocked.")
                return

            print(f"\n[VOTE] The Cyber-Demos has convened for: {target_product}")
            
            if motion_type == "SUBSIDIZE":
                self.bank.registry[target_product]["temp_damping"] = 0.05
                print(f"  * Motion PASSED: {target_product} Eco-Penalty reduced.")
                
            elif motion_type == "FORCE_LABOR":
                if not self.in_emergency:
                    self.in_emergency = True
                    self.original_plan = {prod: data["planned_labor"] for prod, data in self.products.items()}
                    print(f"  * EMERGENCY MEASURE: War-Economy controls activated for {target_product}.")
                print(f"  * Motion PASSED: Massive Labor Mobilization for {target_product}.")
                print(f"  * Motion PASSED: Massive Labor Mobilization for {target_product}.")
                
                # --- THE JUMPSTART: Reset the multiplier so agents can actually 'buy' the resource again ---
                if self.bank.registry[target_product]["current"] <= 1.0:
                    self.bank.registry[target_product]["current"] = 10.0 
                    print(f"  [EMERGENCY] Stock jumpstarted to 10 units to break the scarcity loop.")

                for prod in self.products:
                    if prod != target_product:
                        # 0.8 (80%) tax
                        tax = self.products[prod]["planned_labor"] * 0.8
                        self.products[prod]["planned_labor"] -= tax
                        self.products[target_product]["planned_labor"] += tax
    
    def calculate_suv(self):
        print("\n" + "="*80 + "\n--- ISAACHIC-CYBERNETIC FEEDBACK ---")
        total_satisfaction = 0
        ps_scores = {}
        for name, data in self.products.items():
            suv = data["spent_vouchers"] / max(data["planned_labor"], 1)
            mult = self.bank.get_enlt_multiplier(name)
            ps_scores[name] = (data["planned_labor"] * suv) / (data["base_enlt"] * mult)

        for name, ps in ps_scores.items():
            action = "PROCEED"
            if ps < 1.0:
                action = "VETOED"
                if name in self.substitutes:
                    for alt in self.substitutes[name]:
                        if ps_scores.get(alt, 0) > 1.2:
                            action = f"REDIRECT -> {alt}"; total_satisfaction += 0.5; break
            else:
                total_satisfaction += 1.0
            print(f"{name:12} | PS: {ps:.2f} | {action}")
        
        # --- STABILITY CALCULATION (Moved back here to fix the Error) ---
        raw_stability = (total_satisfaction / len(self.products)) * 100
        essentials = ["Bread", "Water", "Medicine", "Electricity", "Healthcare"]
        lowest_essential = min([(self.bank.registry[res]["current"] / self.bank.registry[res]["capacity"]) * 100 
                                for res in essentials if res in self.bank.registry])
        
        self.social_stability = min(raw_stability, lowest_essential)
        print(f"SOCIAL STABILITY: {self.social_stability:.1f}% (Capped by Essentials)")
        
        for name in self.products: self.products[name]["spent_vouchers"] = 0
        return self.social_stability

    def normalize_economy(self):
        """Restores the snapshot plan when essentials are stable (>50%)."""
        essentials = ["Bread", "Water", "Medicine", "Electricity", "Healthcare"]
        lowest_essential = min([(self.bank.registry[res]["current"] / self.bank.registry[res]["capacity"]) * 100 
                                for res in essentials if res in self.bank.registry])
        
        if self.in_emergency and lowest_essential >= 75.0:
            print(f"\n>>> NORMALIZATION: {lowest_essential:.1f}% Integrity achieved. Restoring Snapshot Plan.")
            for prod, labor_val in self.original_plan.items():
                if prod in self.products:
                    self.products[prod]["planned_labor"] = labor_val
            self.in_emergency = False 

# --- AGENT & EXECUTION ---
class IsaachicAgent:
    def __init__(self, training): self.v_hour = 1 + (training / 40000); self.vouchers = 0
    def work(self, hrs): self.vouchers += hrs * self.v_hour; return hrs

earth = ResourceBank(); plan = CentralPlan(earth)
surgeon = IsaachicAgent(20000); laborer = IsaachicAgent(0)
for year in range(1, 41):
    # Only print details for the start, the Wood crisis, and the Great Fire
    show_logs = (year <= 5 or 12 <= year <= 15 or 20 <= year <= 26 or year == 40)
    
    if show_logs:
        print(f"\n### YEAR {year} ###")
    # 1. Labor Input
    h1 = surgeon.work(40); h2 = laborer.work(40)
    total_hours = h1 + h2
    if show_logs:
        plan.dynamic_reallocation()
    if 20 <= year <= 25:
        print("!!! The Great Fire !!! BLOCKADE: Labor efficiency dropped by 70% !!!")
        total_hours *= 0.3
    # During a blockade, productivity drops, and so do the vouchers earned
    surgeon.vouchers *= 0.3; laborer.vouchers *= 0.3

    plan.dynamic_reallocation() 
    for prod_name, data in plan.products.items():
        earth.produce(prod_name, total_hours * data["labor_weight"])

    # 2. Consumption
    share = (surgeon.vouchers + laborer.vouchers) / len(plan.products)
    for prod in plan.products: 
        plan.products[prod]["spent_vouchers"] += share
        earth.deplete(prod, share)
    surgeon.vouchers = 0; laborer.vouchers = 0 
    
    # 3. Feedback Loops
    stability = plan.calculate_suv() # This calculates the stability
    plan.normalize_economy()         # This checks if we can end the emergency
    
    earth.apply_entropy()
    earth.tick(drought=(year == 5))
    if year == 12: earth.registry["Wood"]["current"] *= 0.3
    
    earth.recycle(); plan.innovate(); plan.check_luxury_unlock(stability)
    
    if stability < 40:
        active_products = list(plan.products.keys())
        worst_res = min(active_products, key=lambda k: earth.registry[k]["current"])
        plan.democratic_vote(worst_res, "FORCE_LABOR")
        plan.democratic_vote(worst_res, "SUBSIDIZE")
