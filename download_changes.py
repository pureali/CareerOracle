#!/usr/bin/env python3
"""
Script to help sync changes with GitHub
This script creates a summary of all changes made to the project
"""

import os
import json
from datetime import datetime

def get_file_info(filepath):
    """Get file information"""
    if os.path.exists(filepath):
        stat = os.stat(filepath)
        return {
            "exists": True,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    return {"exists": False}

def main():
    """Generate change summary"""
    
    # Files that have been modified
    modified_files = [
        "interview.py",
        "role_playing.py"
    ]
    
    # All project files
    all_files = [
        "app.py",
        "interview.py", 
        "role_playing.py",
        "linkscraper.py",
        "google_speech.py",
        "requirements.txt",
        "README.md",
        "setup.py",
        "env_example.txt"
    ]
    
    print("🔄 CareerOracle - GitHub Sync Helper")
    print("=" * 50)
    
    print("\n📝 MODIFIED FILES:")
    for file in modified_files:
        info = get_file_info(file)
        if info["exists"]:
            print(f"✅ {file} - {info['size']} bytes - Modified: {info['modified']}")
        else:
            print(f"❌ {file} - File not found")
    
    print("\n📁 ALL PROJECT FILES:")
    for file in all_files:
        info = get_file_info(file)
        if info["exists"]:
            status = "🔄 MODIFIED" if file in modified_files else "✅ UNCHANGED"
            print(f"{status} {file} - {info['size']} bytes")
        else:
            print(f"❌ {file} - File not found")
    
    print("\n🚀 SYNC INSTRUCTIONS:")
    print("1. Download the modified files from this environment")
    print("2. Replace the corresponding files in your GitHub repository")
    print("3. Commit and push the changes to GitHub")
    print("\nModified files to sync:")
    for file in modified_files:
        print(f"   - {file}")
    
    print("\n💡 CHANGES SUMMARY:")
    print("- interview.py: Updated styling (dark to light blue theme)")
    print("- role_playing.py: Complete rewrite with immersive experience functionality")
    print("  * Added scenario-based role-playing")
    print("  * Added interactive choices and outcomes")
    print("  * Added role-specific puzzles")
    print("  * Added comprehensive performance assessment")

if __name__ == "__main__":
    main()