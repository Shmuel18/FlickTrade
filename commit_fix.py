"""Git commit script to document the WebSocket fix."""
import subprocess
import sys

try:
    # Add all changes
    subprocess.run(["git", "add", "-A"], check=True, cwd=r"c:\Users\shh92\OneDrive\Documenti\BotPolymarket")
    
    # Commit with detailed message
    msg = """Fix: WebSocket subscription payload format

- Changed from incorrect format: {type: "subscriptions", product_ids: [...]}
- To correct Polymarket CLOB format: {type: "market", assets_ids: [...]}
- Fixes INVALID_OPERATION errors on all 636 token subscriptions
- Server now accepts subscriptions and responds with initial []
- Price updates should flow once streaming begins

This aligns with official Polymarket CLOB WebSocket API specification."""
    
    subprocess.run(
        ["git", "commit", "-m", msg],
        check=True,
        cwd=r"c:\Users\shh92\OneDrive\Documenti\BotPolymarket"
    )
    
    # Show last commits
    result = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        capture_output=True,
        text=True,
        cwd=r"c:\Users\shh92\OneDrive\Documenti\BotPolymarket"
    )
    
    print("✓ Commit successful!")
    print("\nLast 5 commits:")
    print(result.stdout)
    
except subprocess.CalledProcessError as e:
    print(f"✗ Git error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
