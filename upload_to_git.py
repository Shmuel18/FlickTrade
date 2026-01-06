#!/usr/bin/env python3
"""
Complete Git Push Solution - No Terminal Required
Handles: Add, Commit, and Push to GitHub
"""
import subprocess
import os
import sys
from pathlib import Path

class GitHelper:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.git_exe = self._find_git()
        
    def _find_git(self):
        """Find git executable"""
        possible_paths = [
            r"C:\Program Files\Git\bin\git.exe",
            r"C:\Program Files (x86)\Git\bin\git.exe",
            "git",
        ]
        for path in possible_paths:
            if os.path.exists(path) or path == "git":
                return path
        return "git"
    
    def run(self, cmd, description=""):
        """Run git command"""
        try:
            full_cmd = f'"{self.git_exe}" {cmd}' if self.git_exe != "git" else f"git {cmd}"
            print(f"[GIT] {description}...")
            print(f"      Running: {full_cmd}")
            
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            
            if result.returncode == 0:
                print(f"[OK] {description}")
                if result.stdout and description != "Getting status":
                    print(f"     {result.stdout[:100]}")
                return True, result.stdout
            else:
                print(f"[WARNING] {description}")
                if result.stderr:
                    print(f"     {result.stderr[:200]}")
                return False, result.stderr
        except Exception as e:
            print(f"[ERROR] {description}: {e}")
            return False, str(e)

def main():
    print("\n" + "="*70)
    print("POLYMARKET BOT - AUTOMATED GIT PUSH")
    print("="*70 + "\n")
    
    repo_path = r"C:\Users\shh92\OneDrive\Documenti\BotPolymarket"
    
    if not os.path.isdir(repo_path):
        print(f"[ERROR] Repository not found at: {repo_path}")
        return False
    
    print(f"Repository: {repo_path}\n")
    
    git = GitHelper(repo_path)
    
    # Step 1: Check if git repo
    print("[STEP 1] Checking if this is a git repository...")
    success, output = git.run("status", "Checking git status")
    if not success:
        print("[ERROR] This is not a git repository or git is not installed")
        return False
    
    # Step 2: Configure git
    print("\n[STEP 2] Configuring git user...")
    git.run('config user.name "Polymarket Bot"', "Setting git user name")
    git.run('config user.email "bot@polymarket.local"', "Setting git email")
    
    # Step 3: Check what changed
    print("\n[STEP 3] Checking for changes...")
    success, output = git.run("status --short", "Getting changes")
    
    if not output.strip():
        print("[INFO] No changes to commit")
        return True
    
    print("[INFO] Files changed:")
    for line in output.strip().split('\n')[:20]:  # Show first 20
        print(f"     {line}")
    
    # Step 4: Add all files
    print("\n[STEP 4] Adding all files...")
    git.run("add -A", "Adding all changes")
    
    # Step 5: Commit
    print("\n[STEP 5] Creating commit...")
    msg = "Polymarket Arbitrage Bot - Complete implementation"
    success, output = git.run(f'commit -m "{msg}"', "Committing changes")
    
    if not success and "nothing to commit" not in output.lower():
        print("[WARNING] Commit might have failed, continuing with push...")
    
    # Step 6: Show current branch
    print("\n[STEP 6] Checking current branch...")
    success, branch = git.run("rev-parse --abbrev-ref HEAD", "Getting branch name")
    branch = branch.strip() if success else "main"
    print(f"[INFO] Current branch: {branch}")
    
    # Step 7: Push
    print(f"\n[STEP 7] Pushing to remote ({branch})...")
    success, output = git.run(f"push origin {branch}", "Pushing to remote")
    
    if success:
        print("\n" + "="*70)
        print("[SUCCESS] Code pushed to Git successfully!")
        print("="*70)
        return True
    else:
        # Try with force
        if "rejected" in output.lower() or "non-fast-forward" in output.lower():
            print("\n[INFO] Standard push rejected, attempting pull + push...")
            git.run(f"pull origin {branch}", "Pulling latest changes")
            success, output = git.run(f"push origin {branch}", "Pushing after pull")
            
            if success:
                print("\n" + "="*70)
                print("[SUCCESS] Code pushed to Git successfully!")
                print("="*70)
                return True
        
        print("\n[ERROR] Push failed")
        print("Common solutions:")
        print("1. Check if you're connected to internet")
        print("2. Check if git credentials are configured")
        print("3. Run: git push -u origin main (from terminal)")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[CANCELLED] Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
