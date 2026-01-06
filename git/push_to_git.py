#!/usr/bin/env python3
"""
Git push script for Polymarket Bot
"""
import subprocess
import os
import sys

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n[GIT] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print(f"[OK] {description} successful")
            if result.stdout:
                print(result.stdout[:200])
            return True
        else:
            print(f"[ERROR] {description} failed")
            if result.stderr:
                print(result.stderr[:200])
            return False
    except Exception as e:
        print(f"[EXCEPTION] {e}")
        return False

def main():
    print("="*70)
    print("POLYMARKET BOT - GIT PUSH")
    print("="*70)
    
    repo_dir = "C:\\Users\\shh92\\OneDrive\\Documenti\\BotPolymarket"
    os.chdir(repo_dir)
    print(f"Repository: {os.getcwd()}\n")
    
    # Check git status
    print("[GIT] Checking repository status...")
    result = subprocess.run("git status --short", shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("[ERROR] Not a git repository!")
        return
    
    if not result.stdout.strip():
        print("[INFO] Repository is up to date - no changes")
        return
    
    print("[INFO] Changes detected:")
    print(result.stdout)
    
    # Configure git
    print("\n[GIT] Configuring git...")
    subprocess.run("git config user.name \"Polymarket Bot\"", shell=True, capture_output=True)
    subprocess.run("git config user.email \"bot@polymarket.local\"", shell=True, capture_output=True)
    
    # Add all files
    if not run_command("git add -A", "Adding files"):
        return
    
    # Commit
    commit_msg = "Polymarket Arbitrage Bot - Complete implementation with all features"
    if not run_command(f'git commit -m "{commit_msg}"', "Committing changes"):
        return
    
    # Push
    print("\n[GIT] Attempting to push to remote...")
    result = subprocess.run("git push origin main", shell=True, capture_output=True, text=True)
    
    if "rejected" in result.stderr.lower():
        print("[WARNING] Push rejected - trying pull first...")
        run_command("git pull origin main", "Pulling latest changes")
        run_command("git push origin main", "Pushing changes")
    elif result.returncode == 0:
        print("[OK] Successfully pushed to Git!")
    else:
        print("[INFO] Push status:")
        print(result.stderr)
    
    print("\n" + "="*70)
    print("[DONE] Git operation complete!")
    print("="*70)

if __name__ == "__main__":
    main()
