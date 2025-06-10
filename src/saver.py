import os

def save_raw_data(df, output_dir, file_name):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, file_name)
    df.to_csv(output_path, index=False, encoding='utf-8')
    