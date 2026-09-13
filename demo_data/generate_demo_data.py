import csv
import random
from datetime import datetime, timedelta

def generate_demo_dataset():
    random.seed(42)
    categories = {
        "Enterprise Software": {"base_price": (1200, 5000), "margin": 0.75, "elasticity": -0.8},
        "Cloud Services": {"base_price": (400, 2500), "margin": 0.65, "elasticity": -1.1},
        "Professional Consulting": {"base_price": (2000, 8000), "margin": 0.45, "elasticity": -1.4},
        "Hardware & Peripherals": {"base_price": (150, 1200), "margin": 0.28, "elasticity": -1.8}
    }
    
    regions = ["North America", "EMEA", "APAC", "LATAM"]
    channels = ["Direct Sales", "Partner / Reseller", "Digital Self-Service", "Inside Sales"]
    
    # 24-month span
    start_date = datetime(2024, 1, 1)
    
    records = []
    order_id_counter = 10001

    for month_idx in range(24):
        month_date = start_date + timedelta(days=month_idx * 30.5)
        # Seasonal multiplier (Q4 spike, Q1 dip)
        month_num = (month_date.month)
        seasonal_mult = 1.0 + (0.25 if month_num in [11, 12] else (-0.15 if month_num in [1, 2] else 0.05))
        # Growth trend (+1.2% per month)
        trend_mult = 1.0 + (month_idx * 0.012)

        # Base orders per month
        orders_in_month = int(80 * seasonal_mult * trend_mult)

        for _ in range(orders_in_month):
            order_id = f"ORD-{order_id_counter}"
            order_id_counter += 1
            
            day_offset = random.randint(0, 29)
            trans_date = (month_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            
            category = random.choices(
                list(categories.keys()),
                weights=[0.40, 0.30, 0.18, 0.12]
            )[0]
            
            cat_info = categories[category]
            price = round(random.uniform(*cat_info["base_price"]), 2)
            quantity = random.choices([1, 2, 3, 5, 10], weights=[0.55, 0.25, 0.12, 0.05, 0.03])[0]
            revenue = round(price * quantity, 2)
            
            # Cost reflects margin with minor material inflation in second year
            inflation_factor = 1.0 + (0.08 if month_idx >= 12 else 0.0)
            cost_ratio = (1.0 - cat_info["margin"]) * inflation_factor
            cogs = round(revenue * cost_ratio, 2)
            profit = round(revenue - cogs, 2)

            cust_id = f"CUST-{random.randint(100, 350)}"
            region = random.choices(regions, weights=[0.45, 0.28, 0.18, 0.09])[0]
            channel = random.choice(channels)
            discount_pct = random.choices([0.0, 5.0, 10.0, 15.0, 25.0], weights=[0.4, 0.3, 0.15, 0.1, 0.05])[0]

            records.append({
                "order_id": order_id,
                "date": trans_date,
                "customer_id": cust_id,
                "region": region,
                "channel": channel,
                "category": category,
                "quantity": quantity,
                "unit_price": price,
                "discount_pct": discount_pct,
                "revenue": revenue,
                "cogs": cogs,
                "gross_profit": profit,
                "is_demo_data": True
            })

    # Inject a few intentional realistic outliers / anomalies for testing
    records.append({
        "order_id": "ORD-ANOM-1",
        "date": "2025-06-15",
        "customer_id": "CUST-GLOBAL-CORP",
        "region": "North America",
        "channel": "Direct Sales",
        "category": "Enterprise Software",
        "quantity": 50,
        "unit_price": 4500.0,
        "discount_pct": 20.0,
        "revenue": 180000.0,
        "cogs": 36000.0,
        "gross_profit": 144000.0,
        "is_demo_data": True
    })

    records.append({
        "order_id": "ORD-ANOM-2",
        "date": "2025-09-22",
        "customer_id": "CUST-MEGA-TECH",
        "region": "EMEA",
        "channel": "Partner / Reseller",
        "category": "Cloud Services",
        "quantity": 100,
        "unit_price": 2200.0,
        "discount_pct": 15.0,
        "revenue": 187000.0,
        "cogs": 65450.0,
        "gross_profit": 121550.0,
        "is_demo_data": True
    })

    # Write CSV
    output_path = "demo_data/enterprise_sales_sample.csv"
    keys = list(records[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {len(records)} realistic enterprise records in {output_path}")

if __name__ == "__main__":
    generate_demo_dataset()
