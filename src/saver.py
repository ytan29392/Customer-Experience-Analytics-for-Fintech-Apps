import os

def save_raw_data(df, output_dir, file_name):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, file_name)
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    if not os.path.exists(output_path):
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Data saved to: {output_path}")
    else:
        print(f"File already exists: {output_path}. Skipping save.")