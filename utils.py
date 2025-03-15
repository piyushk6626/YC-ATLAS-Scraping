import os
import json
import csv
from collections import defaultdict

def process_json_files(input_folder, output_folder):
    batch_data = defaultdict(list)
    
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Read JSON files and group by Batch
    for file in os.listdir(input_folder):
        if file.endswith(".json"):
            print(f"Processing file: {file}")
            with open(os.path.join(input_folder, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                batch = data.get("batch")
                if not batch:
                    batch = data.get("Batch", "Unknown")
                
                # Remove embedding field if exists
                data.pop("embedding", None)
                data.pop("markdown", None)
                
                # Flatten founder data
                founders = data.get("Active_Founders", [])
                for i in range(7):  # Max 7 founders
                    if i < len(founders):
                        data[f"Founder_{i+1}_Name"] = founders[i].get("Name", "")
                        data[f"Founder_{i+1}_Description"] = founders[i].get("Description", "")
                        data[f"Founder_{i+1}_LinkedIn"] = founders[i].get("LinkedIn", "")
                    else:
                        data[f"Founder_{i+1}_Name"] = ""
                        data[f"Founder_{i+1}_Description"] = ""
                        data[f"Founder_{i+1}_LinkedIn"] = ""
                
                batch_data[batch].append(data)
    
    # Write to CSV files per batch
    for batch, records in batch_data.items():
        output_file = os.path.join(output_folder, f"Batch_{batch}.csv")
        
        # Get all field names dynamically
        fieldnames = set()
        for record in records:
            fieldnames.update(record.keys())
        fieldnames = sorted(fieldnames)  # Ensure consistent column order
        
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
    
    print("CSV files have been created successfully.")

# Example usage
input_folder = "D:\DEV\YC-ATLAS-Scraping\YC-ATLAS-Scraping\data\company_descriptions_json"  # Change to your JSON folder path
output_folder = "D:\DEV\YC-ATLAS-Scraping\YC-ATLAS-Scraping\data\company_descriptions_csv"  # Change to your CSV output path
process_json_files(input_folder, output_folder)
