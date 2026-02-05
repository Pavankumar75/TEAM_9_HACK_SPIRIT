import pandas as pd
import os
import sys

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_employee_master(csv_path: str) -> pd.DataFrame:
    """Loads Employee Master CSV data."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    # Basic cleaning
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    
    # Date Normalization
    for col in df.columns:
        if "date" in col or "joining" in col:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
            
    return df

def load_leave_data(excel_path: str) -> pd.DataFrame:
    """Loads Leave Intelligence Excel data."""
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"File not found: {excel_path}")
    
    df = pd.read_excel(excel_path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    
    # Date Normalization
    for col in df.columns:
        if "date" in col or "start" in col or "end" in col:
             df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
             
    return df

if __name__ == "__main__":
    # Test loading
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    emp_path = os.path.join(base_dir, "employee_master.csv")
    leave_path = os.path.join(base_dir, "leave_intelligence.xlsx")

    try:
        emp_df = load_employee_master(emp_path)
        print(f"Employee Master Loaded: {emp_df.shape}")
        print(emp_df.head(2))
        
        leave_df = load_leave_data(leave_path)
        print(f"Leave Data Loaded: {leave_df.shape}")
        print(leave_df.head(2))
    except Exception as e:
        print(f"Error: {e}")
