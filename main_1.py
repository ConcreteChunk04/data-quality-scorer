import os
import glob
import json
import logging
from pure_utils import DataQualityProcessor
from pure_finalscores_calculator import calculate_source_average_scores

logging.basicConfig(filename="belden.log", level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")

def get_account_file_names(directory):
    """Returns a list of CSV filenames (without extension) in the directory."""
    if not os.path.exists(directory):
        logging.error(f"Directory does not exist: {directory}")
        return []

    return [
        os.path.splitext(os.path.basename(f))[0]
        for f in glob.glob(os.path.join(directory, '*.csv'))
    ]

def main():
    logging.info(f"Current Working Directory: {os.getcwd()}")

    base_root_directory = 'F:/belden'

    source_config = {
        "analysis": "analysis/Scoring",
        "archive": "archive/Scoring",
        "deskpro": "deskpro/Scoring",
        "duns": "duns/Scoring",
        "fuzzy": "fuzzy/Scoring",
        "prospect": "prospect/Scoring",
        "public": "public/Scoring",
        "supplier360": "supplier360/Scoring"
    }

    final_output_data = {}

    logging.info("Starting data quality score consolidation...")

    for source_name, rel_path in source_config.items():
        source_path = os.path.join(base_root_directory, rel_path)
        logging.debug(f"Processing source: {source_name} at {source_path}")

        processor = DataQualityProcessor(source_path)

        accuracy_dir = os.path.join(source_path, 'accuracy scoring')
        account_names = get_account_file_names(accuracy_dir)

        if not account_names:
            logging.warning(f"No CSVs found for source: {source_name}")
            final_output_data[source_name] = {
                "score": {
                    "Score_Acurracy": None,
                    "Score_Completness": None,
                    "Score_Uniqueness": None,
                    "Score_Data_Quality": None,
                    "Score_Data_Format": None
                }
            }
        else:
            account_results = processor.process_all_accounts(account_names)
            avg_scores = calculate_source_average_scores(account_results)
            final_output_data[source_name] = {"score": avg_scores}

    output_file = "output.json"
    try:
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(final_output_data, f, indent=2)
        logging.info(f"Output saved to {output_file} at {os.path.abspath(output_file)}")
    except Exception as e:
        logging.critical(f"Failed to write output file: {e}")

if __name__ == "__main__":
    main()
