import pandas as pd
import json

def load_dataset(filepath: str):
    """
    Loads a dataset from a specified CSV or JSON file.

    Args:
        filepath (str): The path to the file.

    Returns:
        A pandas DataFrame for CSV or a list/dict for JSON.
    """
    if filepath.endswith('.csv'):
        return pd.read_csv(filepath)
    elif filepath.endswith('.json'):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise ValueError("Unsupported file format. Please use .csv or .json")