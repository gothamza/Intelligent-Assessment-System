# Quick Fix for MLSUM Dataset Loading Error

## Problem
```
RuntimeError: Dataset scripts are no longer supported, but found mlsum.py
```

## Solution

The MLSUM dataset uses deprecated dataset scripts. You need to downgrade the `datasets` library to a version that supports them.

### Option 1: Automatic Fix (Recommended)

Run the fix script:
```bash
python fix_datasets.py
```

Then restart your Jupyter kernel and run the notebook again.

### Option 2: Manual Fix

**If using pip:**
```bash
pip install 'datasets==3.6.0'
```

**If using UV:**
```bash
uv pip install 'datasets==3.6.0'
```

**If using conda:**
```bash
conda install -c conda-forge datasets=3.6.0
```

### Option 3: Update requirements.txt

Edit `requirements.txt` and change:
```
datasets>=2.12.0
```

To:
```
datasets==3.6.0
```

Then reinstall:
```bash
pip install -r requirements.txt
```

## After Fixing

1. **Restart your Jupyter kernel** (Kernel → Restart)
2. **Clear the output** of the failed cell
3. **Run the data preparation notebook again**

## Why This Happens

- Hugging Face `datasets` library version 4.0.0+ removed support for dataset scripts
- MLSUM dataset still uses the old script-based format (`mlsum.py`)
- Version 3.6.0 is the last version that supports dataset scripts

## Alternative Solutions

If you cannot downgrade, you can:

1. **Manually download the dataset** from [Hugging Face](https://huggingface.co/datasets/mlsum)
2. **Convert it to Parquet format** and load locally
3. **Use a different dataset** that's already in Parquet format

## Verify Installation

After downgrading, verify:
```python
import datasets
print(datasets.__version__)  # Should show 3.6.0
```

