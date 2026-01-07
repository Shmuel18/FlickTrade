#!/usr/bin/env python3
"""
Script to update Polymarket API keys after creating new ones
"""
import os
from pathlib import Path

def update_api_keys():
    """Update the .env file with new Polymarket API credentials"""

    print("🔑 Polymarket API Key Updater")
    print("=" * 40)
    print("Go to: https://polymarket.com/settings")
    print("1. Delete all existing API keys")
    print("2. Create a new API key")
    print("3. Copy the credentials below")
    print()

    # Get the .env file path
    env_path = Path("config/.env")
    if not env_path.exists():
        print("❌ config/.env file not found!")
        return

    # Get new credentials from user
    print("📝 Enter your NEW Polymarket API credentials:")

    api_key = input("API Key: ").strip()
    api_secret = input("API Secret: ").strip()
    api_passphrase = input("API Passphrase: ").strip()

    # Validate inputs
    if not all([api_key, api_secret, api_passphrase]):
        print("❌ All fields are required!")
        return

    # Create backup
    backup_path = env_path.with_suffix('.env.backup')
    if env_path.exists():
        env_path.rename(backup_path)
        print(f"💾 Backup created: {backup_path}")

    # Read current .env to preserve private key
    current_env = {}
    if backup_path.exists():
        for line in backup_path.read_text().split('\n'):
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                current_env[key.strip()] = value.strip()

    # Create new .env content
    env_content = f"""POLYMARKET_API_KEY={api_key}
POLYMARKET_API_SECRET={api_secret}
POLYMARKET_API_PASSPHRASE={api_passphrase}
POLYMARKET_PRIVATE_KEY={current_env.get('POLYMARKET_PRIVATE_KEY', 'YOUR_PRIVATE_KEY_HERE')}
"""

    # Write new .env file
    env_path.write_text(env_content)
    print(f"✅ Updated: {env_path}")

    print("\n🧪 Testing new configuration...")
    try:
        # Test import
        import sys
        sys.path.append('src')
        from polymarket_bot.config import API_KEY, API_SECRET, API_PASSPHRASE
        print(f"🔍 API Key starts with: {API_KEY[:5]}...")
        print("✅ Configuration loaded successfully!")
        print("\n🎯 Run: python -m src.polymarket_bot.main")
    except Exception as e:
        print(f"❌ Configuration error: {e}")

if __name__ == "__main__":
    update_api_keys()