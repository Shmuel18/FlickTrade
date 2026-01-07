#!/usr/bin/env python3
"""
Script to help update Polymarket API keys
Run this after creating new API keys in Polymarket settings
"""
import os
from pathlib import Path

def update_env_file():
    """Update the .env file with new API credentials"""

    print("🔑 Polymarket API Key Updater")
    print("=" * 40)

    # Get the .env file path
    env_path = Path("config/.env")
    if not env_path.exists():
        print("❌ config/.env file not found!")
        return

    print(f"📁 Updating: {env_path.absolute()}")

    # Get new credentials from user
    print("\n📝 Enter your NEW Polymarket API credentials:")
    print("(Get these from: https://polymarket.com/settings)")

    api_key = input("API Key: ").strip()
    api_secret = input("API Secret: ").strip()
    api_passphrase = input("API Passphrase: ").strip()
    private_key = input("Private Key (0x...): ").strip()

    # Validate inputs
    if not all([api_key, api_secret, api_passphrase, private_key]):
        print("❌ All fields are required!")
        return

    if not private_key.startswith("0x"):
        print("❌ Private key must start with '0x'")
        return

    # Create new .env content
    env_content = f"""POLYMARKET_API_KEY={api_key}
POLYMARKET_API_SECRET={api_secret}
POLYMARKET_API_PASSPHRASE={api_passphrase}
POLYMARKET_PRIVATE_KEY={private_key}
"""

    # Backup current file
    backup_path = env_path.with_suffix('.env.backup')
    if env_path.exists():
        env_path.rename(backup_path)
        print(f"💾 Backup created: {backup_path}")

    # Write new .env file
    env_path.write_text(env_content)
    print(f"✅ Updated: {env_path}")

    # Test the configuration
    print("\n🧪 Testing new configuration...")
    try:
        from src.polymarket_bot.config import API_KEY, API_SECRET, API_PASSPHRASE, PRIVATE_KEY
        print(f"🔍 API Key starts with: {API_KEY[:5]}...")
        print("✅ Configuration loaded successfully!")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return

    print("\n🎯 Next steps:")
    print("1. Run: python test_api_keys.py")
    print("2. If successful, run your bot!")
    print("3. Delete the backup file if everything works")

if __name__ == "__main__":
    update_env_file()