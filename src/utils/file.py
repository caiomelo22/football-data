import os
import json
from datetime import datetime as dt


def generate_dir_path(folder, file_name, file_extension):
    # Ensure the directory exists
    directory = f"dist/{folder}"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Create the full file path
    file_path = os.path.join(directory, f"{file_name}.{file_extension}")

    return file_path


def save_df_to_csv(df, folder, file_name):
    file_path = generate_dir_path(folder, file_name, "csv")

    try:
        df.to_csv(file_path)
        print(f"Data successfully written to {file_path}")
    except Exception as e:
        print(f"Failed to write data to CSV: {e}")


def save_json(data, file_name):
    # Ensure the directory exists
    directory = f"dist/output"
    if not os.path.exists(directory):
        os.makedirs(directory)

    now = dt.now().isoformat().split(".")[0].replace(":", "-")

    # Specify the filename
    file_path = f"./{directory}/{file_name}_{now}.json"

    # Save the list of dictionaries to a JSON file
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Data has been saved to {file_path}.")
