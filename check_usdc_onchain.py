#!/usr/bin/env python3
"""
בדיקה פשוטה של יתרת USDC בכתובת הארנק
"""
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv('config/.env')

# Polygon RPC
RPC_URL = "https://polygon-rpc.com"
USDC_CONTRACT = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"  # USDC on Polygon
FUNDER_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS', '0x6f01ab96024b7e4b87e60f18773c2566b7c8cc23')

# USDC ABI (only balanceOf needed)
USDC_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

def check_usdc_balance():
    """בדיקת יתרת USDC ישירות מהבלוקצ'יין"""
    print("\n" + "="*70)
    print("💰 בדיקת יתרת USDC בבלוקצ'יין")
    print("="*70)
    
    try:
        # Connect to Polygon
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        
        if not w3.is_connected():
            print("❌ לא ניתן להתחבר ל-Polygon RPC")
            return
        
        print(f"✅ מחובר ל-Polygon (Block: {w3.eth.block_number})")
        print(f"📍 כתובת: {FUNDER_ADDRESS}")
        print("-"*70)
        
        # Get USDC contract
        usdc = w3.eth.contract(address=Web3.to_checksum_address(USDC_CONTRACT), abi=USDC_ABI)
        
        # Get decimals (USDC has 6 decimals)
        decimals = usdc.functions.decimals().call()
        
        # Get balance
        balance_wei = usdc.functions.balanceOf(Web3.to_checksum_address(FUNDER_ADDRESS)).call()
        balance_usdc = balance_wei / (10 ** decimals)
        
        print(f"\n💵 יתרת USDC: ${balance_usdc:.6f}")
        print(f"   Raw balance: {balance_wei} (wei)")
        print(f"   Decimals: {decimals}")
        print()
        
        if balance_usdc < 0.01:
            print("❌ אין כמעט USDC בארנק!")
            print("   צריך להפקיד USDC דרך polymarket.com")
        elif balance_usdc < 5:
            print("⚠️  יתרה נמוכה (מתחת ל-$5)")
            print("   Polymarket דורש מינימום 5 USDC למסחר")
        else:
            print(f"✅ יתרה מספיקה למסחר!")
            print(f"   ניתן לסחור עד ~{int(balance_usdc/5)} עסקאות של $5")
        
        # Check MATIC balance too (for gas)
        matic_balance = w3.eth.get_balance(Web3.to_checksum_address(FUNDER_ADDRESS))
        matic_balance_eth = matic_balance / 1e18
        
        print(f"\n⛽ יתרת MATIC (גאז): {matic_balance_eth:.6f} MATIC")
        
        if matic_balance_eth < 0.01:
            print("⚠️  יתרת MATIC נמוכה - ייתכן שלא יספיק לגאז")
        else:
            print("✅ יתרת MATIC מספיקה")
        
        print("\n" + "="*70)
        print(f"🔗 צפייה בבלוקצ'יין:")
        print(f"   https://polygonscan.com/address/{FUNDER_ADDRESS}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ שגיאה: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_usdc_balance()
