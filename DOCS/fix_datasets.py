"""
Quick fix script for MLSUM dataset loading issue
This downgrades the datasets library to a version that supports dataset scripts
"""

import subprocess
import sys

def fix_datasets():
    """Downgrade datasets library to version 3.6.0"""
    print("Fixing datasets library compatibility issue...")
    print("Downgrading datasets to version 3.6.0 (supports dataset scripts)")
    print("-" * 60)
    
    try:
        # Try with pip first
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "datasets==3.6.0"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Successfully downgraded datasets to 3.6.0")
            print("\nNext steps:")
            print("1. Restart your Jupyter kernel")
            print("2. Run the data preparation notebook again")
            return True
        else:
            print("Error with pip, trying alternative method...")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nManual fix:")
        print("Run this command in your terminal:")
        print("  pip install 'datasets==3.6.0'")
        print("\nOr if using UV:")
        print("  uv pip install 'datasets==3.6.0'")
        return False

if __name__ == "__main__":
    success = fix_datasets()
    if success:
        print("\n" + "="*60)
        print("Fix applied successfully!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("Please run the manual commands shown above")
        print("="*60)

