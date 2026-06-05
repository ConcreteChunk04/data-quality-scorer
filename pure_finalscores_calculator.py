import logging

logging.basicConfig(filename="belden.log", level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")


def calculate_source_average_scores(account_results_list):
    """
    Calculates average data quality scores from a list of account result dictionaries.
    Mimics pandas behavior for consistency with the original implementation."""

  
    if not account_results_list:
        logging.info("No account results provided. Returning None scores.")
        return {
            "Score_Acurracy": None,
            "Score_Completness": None,
            "Score_Uniqueness": None,
            "Score_Data_Quality": None,
            "Score_Data_Format": None
        }

    # Prepare buckets to collect scores - using exact key names from pandas version
    scores_bucket = {
        "Accuracy_Record": [],
        "Completeness": [],
        "Uniqueness": [],
        "Data_Quality": [],
        "Data_Formatting": []
    }

    # Collect scores with better validation
    for i, entry in enumerate(account_results_list):
        if not isinstance(entry, dict):
            logging.warning(f"Entry {i} is not a dictionary. Skipping: {type(entry)}")
            continue

        for key in scores_bucket:
            if key in entry:
                value = entry[key]
                # Handle both None and numeric values properly
                if value is not None and isinstance(value, (int, float)):
                    # Check for NaN values (though unlikely in this context)
                    if str(value).lower() != 'nan':
                        scores_bucket[key].append(float(value))
                elif value is not None:
                    logging.warning(f"Ignoring non-numeric value for {key} in entry {i}: {value} (type: {type(value)})")

    # Compute averages with pandas-like behavior
    def safe_average(values):
        if not values:
            return None
        # Use sum/len for consistency with pandas mean calculation
        avg = sum(values) / len(values)
        # Round to 2 decimal places as in original code
        return round(avg, 2)

    result = {
        "Score_Acurracy": safe_average(scores_bucket["Accuracy_Record"]),
        "Score_Completness": safe_average(scores_bucket["Completeness"]),
        "Score_Uniqueness": safe_average(scores_bucket["Uniqueness"]),
        "Score_Data_Quality": safe_average(scores_bucket["Data_Quality"]),
        "Score_Data_Format": safe_average(scores_bucket["Data_Formatting"]),
    }
    
    # Log the calculation details for debugging
    for key, values in scores_bucket.items():
        output_key = f"Score_{key.replace('_Record', '').replace('_', '_')}"
        if key == "Accuracy_Record":
            output_key = "Score_Acurracy"
        elif key == "Completeness":
            output_key = "Score_Completness"
        elif key == "Data_Formatting":
            output_key = "Score_Data_Format"
        elif key == "Data_Quality":
            output_key = "Score_Data_Quality"
        elif key == "Uniqueness":
            output_key = "Score_Uniqueness"
            
        logging.debug(f"{output_key}: {len(values)} values, average: {result.get(output_key)}")
    
    return result