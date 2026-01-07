"""בדיקת לוגיקה ידנית"""

print("🧪 בדיקת לוגיקה של opposite price")
print("="*70)

test_prices = [0.99, 0.995, 0.999, 0.50, 0.20, 0.01]
threshold = 0.20

for price in test_prices:
    opposite = 1.0 - price
    
    direct_match = (0.0001 <= price <= threshold)
    opposite_match = (0.0001 <= opposite <= threshold)
    
    print(f"\nPrice: ${price:.4f}")
    print(f"  Opposite: ${opposite:.4f}")
    print(f"  Direct match (≤${threshold}): {'✅ YES' if direct_match else '❌ NO'}")
    print(f"  Opposite match (≤${threshold}): {'✅ YES' if opposite_match else '❌ NO'}")
    
    if direct_match:
        print(f"  → קונים ישיר @ ${price:.4f}")
    if opposite_match:
        print(f"  → קונים הפוך @ ${opposite:.4f}")

print("\n" + "="*70)
print("המסקנה: אם מחיר 0.99, ההפוך הוא 0.01 - צריך למצוא!")
