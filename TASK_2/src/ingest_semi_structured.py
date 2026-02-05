import json
import pandas as pd
import os
import sys

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_attendance_logs(json_path: str) -> pd.DataFrame:
    """
    Loads the large attendance JSON logs.
    Since the structure is nested (EMP_ID -> records), we might need to flatten it
    to make it useful for DataFrame operations.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"File not found: {json_path}")

    with open(json_path, 'r') as f:
        data = json.load(f)

    # Flatten logic
    # Expected structure: { "EMP1001": { "records": [ ... ] }, ... }
    flattened_data = []
    
    for emp_id, content in data.items():
        records = content.get("records", [])
        for record in records:
            # Flatten metadata if needed or keep as dict
            # record is like: { "date": "...", "metadata": {...} }
            entry = {
                "emp_id": emp_id,
                "date": record.get("date"),
                "check_in": record.get("check_in"),
                "check_out": record.get("check_out"),
                "location": record.get("location_logged"),
                # We can extract useful metadata fields
                "ip": record.get("metadata", {}).get("ip"),
                "device": record.get("metadata", {}).get("device")
            }
            flattened_data.append(entry)

    df = pd.DataFrame(flattened_data)
    
    # Date Normalization
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors='coerce').dt.strftime('%Y-%m-%d')
        
    return df

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_file = "attendance_logs_detailed.json"
    json_path = os.path.join(base_dir, json_file)

    try:
        print("Loading JSON (this might take a moment)...")
        df = load_attendance_logs(json_path)
        print(f"Attendance Logs Loaded: {df.shape}")
        print(df.head(2))
    except Exception as e:
        print(f"Error: {e}")
