#!/usr/bin/env python3
"""
MSME AI Cashflow Estimator - Starter Script
==========================================

A practical demo tool for Indian MSMEs to estimate working capital needs
and forecast cash flow gaps using sample GST, UPI, and invoice data.

This starter uses pure Python (no external deps) with realistic sample data.
Extend it with real APIs, ML models, or LLM insights.

Author: ShihaiSuru
Date: 2026-10-31
"""

from datetime import datetime, timedelta
from collections import defaultdict
import random


def generate_sample_data(num_days=90):
    """
    Generate realistic sample transaction data for an Indian MSME.
    Includes invoices (receivables), UPI/bank payments (outflows), and GST.
    """
    today = datetime.now().date()
    transactions = []

    # Sample inflows: customer invoices / UPI collections (delayed sometimes)
    for i in range(15):
        invoice_date = today - timedelta(days=random.randint(1, 60))
        due_date = invoice_date + timedelta(days=random.choice([15, 30, 45, 60]))
        amount = random.randint(25000, 250000)  # ₹25k to ₹2.5L
        paid = random.random() > 0.35  # 65% chance already collected
        transactions.append({
            "type": "inflow",
            "category": "invoice_collection",
            "date": due_date if not paid else invoice_date + timedelta(days=random.randint(5, 25)),
            "amount": amount,
            "description": f"Invoice #{1000+i} from Customer",
            "status": "collected" if paid else "pending",
            "gst_rate": 0.18
        })

    # Sample outflows: vendor payments, GST, salaries, UPI
    categories = ["vendor_payment", "gst_payment", "salary", "rent", "utilities", "upi_expense"]
    for i in range(25):
        txn_date = today - timedelta(days=random.randint(0, 89))
        amount = random.randint(5000, 80000)
        category = random.choice(categories)
        transactions.append({
            "type": "outflow",
            "category": category,
            "date": txn_date,
            "amount": amount,
            "description": f"{category.replace('_', ' ').title()} payment",
            "status": "paid",
            "gst_rate": 0.18 if category in ["vendor_payment", "utilities"] else 0
        })

    return sorted(transactions, key=lambda x: x["date"])


def calculate_cashflow(transactions, starting_cash=500000):
    """
    Project cash position day-by-day and identify gaps.
    Returns daily balances and key metrics.
    """
    daily = defaultdict(lambda: {"in": 0, "out": 0})
    for txn in transactions:
        day = txn["date"]
        if txn["type"] == "inflow":
            daily[day]["in"] += txn["amount"]
        else:
            daily[day]["out"] += txn["amount"]

    # Project forward 90 days from today
    today = datetime.now().date()
    balance = starting_cash
    projections = []
    min_balance = starting_cash
    gap_days = []

    for offset in range(90):
        day = today + timedelta(days=offset)
        inflow = daily[day]["in"]
        outflow = daily[day]["out"]
        balance += inflow - outflow
        projections.append({
            "date": day,
            "inflow": inflow,
            "outflow": outflow,
            "balance": balance
        })
        if balance < min_balance:
            min_balance = balance
        if balance < 100000:  # Flag if below ₹1L buffer
            gap_days.append(day)

    return projections, min_balance, gap_days


def estimate_working_capital(transactions, min_balance, starting_cash):
    """
    Simple working capital estimation based on receivables and gaps.
    """
    pending_receivables = sum(
        t["amount"] for t in transactions
        if t["type"] == "inflow" and t["status"] == "pending"
    )
    avg_daily_outflow = sum(t["amount"] for t in transactions if t["type"] == "outflow") / 90

    # Recommended buffer: 45 days of outflows + gap coverage
    recommended_wc = int(avg_daily_outflow * 45)
    shortfall = max(0, recommended_wc - (starting_cash + pending_receivables))

    return {
        "pending_receivables": pending_receivables,
        "avg_daily_outflow": int(avg_daily_outflow),
        "recommended_working_capital": recommended_wc,
        "estimated_shortfall": shortfall,
        "min_projected_balance": min_balance
    }


def main():
    print("=" * 60)
    print("  MSME AI Cashflow Estimator - Demo")
    print("  For Indian MSMEs | Starter Tool | 2026-10-31")
    print("=" * 60)

    # Generate sample data (in real use, load from CSV/GST/UPI export)
    transactions = generate_sample_data()
    print(f"\nLoaded {len(transactions)} sample transactions (invoices + UPI + GST).")

    starting_cash = 450000  # Example current bank balance
    projections, min_balance, gap_days = calculate_cashflow(transactions, starting_cash)
    wc = estimate_working_capital(transactions, min_balance, starting_cash)

    print(f"\nStarting Cash: ₹{starting_cash:,}")
    print(f"Pending Receivables: ₹{wc['pending_receivables']:,}")
    print(f"Average Daily Outflow: ₹{wc['avg_daily_outflow']:,}")
    print(f"\nRecommended Working Capital Buffer: ₹{wc['recommended_working_capital']:,}")
    print(f"Estimated Shortfall: ₹{wc['estimated_shortfall']:,}")
    print(f"Lowest Projected Balance (90 days): ₹{min_balance:,}")

    if gap_days:
        print(f"\n⚠ Cash Gap Alerts: Balance expected below ₹1L on {len(gap_days)} day(s).")
        print("   Earliest: " + gap_days[0].strftime("%d %b %Y"))
    else:
        print("\n✓ No major cash gaps detected in next 90 days.")

    print("\n" + "-" * 60)
    print("Next 7 days snapshot:")
    for p in projections[:7]:
        print(f"  {p['date'].strftime('%d %b')}: In ₹{p['inflow']:>8,} | Out ₹{p['outflow']:>8,} | Bal ₹{p['balance']:>10,}")

    print("\n" + "=" * 60)
    print("Extend this script with:")
    print("  - Real GST JSON / UPI CSV import")
    print("  - ML forecasting models")
    print("  - LLM-powered explanations for founders")
    print("  - Account Aggregator or bank API integration")
    print("=" * 60)


if __name__ == "__main__":
    main()
