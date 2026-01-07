#!/usr/bin/env python3
"""
בדיקת פוזיציות פתוחות ויתרות
"""
import sys
import os
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from dotenv import load_dotenv

# Load environment
load_dotenv()

def check_wallet_status():
    """בדיקת סטטוס הארנק - יתרה ופוזיציות."""
    print("\n" + "="*70)
    print("🔍 בדיקת סטטוס ארנק")
    print("="*70)
    
    try:
        # Initialize client
        creds = ApiCreds(
            api_key=os.getenv('POLY_API_KEY', '').strip(),
            api_secret=os.getenv('POLY_API_SECRET', '').strip(),
            api_passphrase=os.getenv('POLY_PASSPHRASE', '').strip()
        )
        
        client = ClobClient(
            host=os.getenv('CLOB_URL', 'https://clob.polymarket.com'),
            key=os.getenv('PK', ''),
            chain_id=int(os.getenv('CHAIN_ID', '137')),
            creds=creds,
            signature_type=1,
            funder=os.getenv('POLY_PROXY_ADDRESS', '')
        )
        
        print(f"\n📍 כתובת Signer: {client.get_address()}")
        print(f"📍 כתובת Funder (Proxy): {os.getenv('POLY_PROXY_ADDRESS', 'N/A')}")
        print("-"*70)
        
        # 1. Check balance and allowance
        print("\n💰 בדיקת יתרה:")
        try:
            balance_info = client.get_balance_allowance()
            if balance_info and isinstance(balance_info, dict):
                balance = float(balance_info.get('balance', 0))
                allowance = float(balance_info.get('allowance', 0))
                print(f"   יתרה זמינה: ${balance:.2f} USDC")
                print(f"   Allowance: ${allowance:.2f} USDC")
                
                if balance < 5:
                    print("   ⚠️  יתרה נמוכה מדי למסחר (מינימום $5)")
                if allowance < balance:
                    print("   ⚠️  Allowance נמוך מהיתרה - ייתכן שצריך לאשר")
            else:
                print("   ❌ לא ניתן לקבל מידע על יתרה")
        except Exception as e:
            print(f"   ❌ שגיאה בבדיקת יתרה: {type(e).__name__}")
        
        # 2. Check open orders
        print("\n📋 בדיקת פקודות פתוחות:")
        try:
            open_orders = client.get_orders()
            if open_orders and isinstance(open_orders, list):
                active_orders = [o for o in open_orders if o.get('status') in ['LIVE', 'PENDING']]
                print(f"   פקודות פתוחות: {len(active_orders)}")
                
                if active_orders:
                    print("\n   📜 פירוט:")
                    for i, order in enumerate(active_orders[:5], 1):  # Show first 5
                        token_id = order.get('asset_id', 'N/A')[:8]
                        side = order.get('side', 'N/A')
                        size = order.get('original_size', 0)
                        price = order.get('price', 0)
                        status = order.get('status', 'N/A')
                        print(f"      {i}. {side} {size} @ ${price:.3f} | Token: {token_id}... | Status: {status}")
            else:
                print("   אין פקודות פתוחות")
        except Exception as e:
            print(f"   ❌ שגיאה בבדיקת פקודות: {type(e).__name__}")
        
        # 3. Check positions
        print("\n🎯 בדיקת פוזיציות:")
        try:
            # Get positions from API
            positions = client.get_positions()
            if positions and isinstance(positions, list):
                active_positions = [p for p in positions if float(p.get('size', 0)) > 0]
                print(f"   פוזיציות פתוחות: {len(active_positions)}")
                
                if active_positions:
                    total_value = 0
                    print("\n   📊 פירוט:")
                    for i, pos in enumerate(active_positions[:10], 1):  # Show first 10
                        token_id = pos.get('asset_id', 'N/A')[:8]
                        size = float(pos.get('size', 0))
                        value = float(pos.get('value', 0))
                        total_value += value
                        print(f"      {i}. Token: {token_id}... | Size: {size:.2f} | Value: ${value:.2f}")
                    
                    print(f"\n   💵 סה״כ ערך פוזיציות: ${total_value:.2f}")
                    
                    if total_value > 5:
                        print("   ℹ️  יש לך כסף קשור בפוזיציות פתוחות")
                        print("   ℹ️  כדי לשחרר אותו צריך לסגור את הפוזיציות")
            else:
                print("   אין פוזיציות פתוחות")
        except Exception as e:
            print(f"   ❌ שגיאה בבדיקת פוזיציות: {type(e).__name__}")
        
        print("\n" + "="*70)
        print("✅ בדיקה הושלמה")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ שגיאה כללית: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_wallet_status()
