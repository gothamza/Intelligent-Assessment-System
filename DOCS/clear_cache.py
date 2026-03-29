"""
Script to clear Hugging Face dataset cache for MLSUM
Run this if you encounter "Dataset scripts are no longer supported" error
"""

import os
import shutil

def clear_mlsum_cache():
    """Clear MLSUM dataset cache"""
    cache_path = os.path.expanduser("~/.cache/huggingface/datasets")
    mlsum_cache = os.path.join(cache_path, "mlsum")
    
    if os.path.exists(mlsum_cache):
        print(f"Found MLSUM cache at: {mlsum_cache}")
        try:
            shutil.rmtree(mlsum_cache, ignore_errors=True)
            print("✓ MLSUM cache cleared successfully!")
        except Exception as e:
            print(f"Error clearing cache: {e}")
    else:
        print("No MLSUM cache found.")
    
    # Also check for any mlsum.py scripts
    scripts_path = os.path.join(cache_path, "scripts")
    if os.path.exists(scripts_path):
        mlsum_script = os.path.join(scripts_path, "mlsum")
        if os.path.exists(mlsum_script):
            print(f"Found MLSUM script at: {mlsum_script}")
            try:
                shutil.rmtree(mlsum_script, ignore_errors=True)
                print("✓ MLSUM script cache cleared!")
            except Exception as e:
                print(f"Error clearing script cache: {e}")

if __name__ == "__main__":
    print("Clearing Hugging Face dataset cache for MLSUM...")
    clear_mlsum_cache()
    print("\nDone! Now try loading the dataset again in your notebook.")

