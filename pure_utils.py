import os
import csv
import logging

logging.basicConfig(filename="belden.log", level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")

class DataQualityProcessor:
    def __init__(self, base_directory):
        self.base_dir = base_directory
        self.metric_config = {
            "accuracy_scoring": {"path": "accuracy scoring", "column": "Record_Score"},
            "completeness": {"path": "completeness", "column": "Complete_Score"},
            "data_formatting": {"path": "data formating", "column": "DF_Score"},
            "data_quality": {"path": "data quality", "column": "DQ_Score"},
            "uniqueness_scoring": {
                "path": "uniqueness scoring", "file": "uniquesness_scores.csv",
                "account_col": "File", "score_col": "Uniqueness Score"
            }
        }

    def _read_csv_column(self, file_path, column_name):
        """Read a specific column from CSV file using proper CSV parsing."""
        values = []
        try:
            with open(file_path, 'r', encoding='utf-8', newline='') as file:
                reader = csv.DictReader(file)
                
                # Check if fieldnames exist and are valid
                if not reader.fieldnames:
                    logging.warning(f"No headers found or empty file: {file_path}")
                    return None
                    
                if column_name not in reader.fieldnames:
                    logging.warning(f"Column '{column_name}' not found in {file_path}")
                    logging.warning(f"Available columns: {reader.fieldnames}")
                    return None

                for row_num, row in enumerate(reader, start=2):
                    try:
                        value_str = row[column_name].strip()
                        if value_str:  # Skip empty values
                            val = float(value_str)
                            values.append(val)
                    except (ValueError, TypeError) as e:
                        logging.warning(f"Non-numeric value '{row[column_name]}' at row {row_num} in {file_path}: {e}")
                        continue
                    except KeyError:
                        logging.warning(f"Missing column data at row {row_num} in {file_path}")
                        continue
                        
        except FileNotFoundError:
            logging.warning(f"File not found: {file_path}")
            return None
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return None

        logging.debug(f"Read {len(values)} values from {file_path} for column '{column_name}'")
        return values if values else None

    def _calculate_mean_metric(self, metric_key, account_name):
        """Calculate mean using proper CSV parsing and pandas-like precision."""
        config = self.metric_config[metric_key]
        file_path = os.path.join(self.base_dir, config["path"], f"{account_name}.csv")
        values = self._read_csv_column(file_path, config["column"])
        
        if values:
            # Use pandas-like mean calculation
            mean_val = sum(values) / len(values)
            # Round to 14 decimal places to match pandas behavior
            mean_val = round(mean_val, 14)
            logging.debug(f"Mean for {metric_key} ({account_name}): {mean_val} from {len(values)} values")
            return mean_val
        else:
            logging.debug(f"No valid values found for {metric_key} ({account_name})")
            return None

    def _get_uniqueness_scores_map(self):
        """Read uniqueness scores using proper CSV parsing."""
        config = self.metric_config["uniqueness_scoring"]
        file_path = os.path.join(self.base_dir, config["path"], config["file"])
        scores = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8', newline='') as file:
                reader = csv.DictReader(file)
                
                # Check if fieldnames exist and are valid
                if not reader.fieldnames:
                    logging.warning(f"No headers found or empty file: {file_path}")
                    return None
                    
                if config["account_col"] not in reader.fieldnames or config["score_col"] not in reader.fieldnames:
                    logging.warning(f"Required columns not found in {file_path}")
                    logging.warning(f"Available columns: {reader.fieldnames}")
                    logging.warning(f"Looking for: '{config['account_col']}' and '{config['score_col']}'")
                    return None
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        account_name = row[config["account_col"]].strip()
                        score_str = row[config["score_col"]].strip()
                        
                        if account_name and score_str:
                            scores[account_name] = float(score_str)
                    except (ValueError, TypeError) as e:
                        logging.warning(f"Invalid uniqueness score at row {row_num}: {e}")
                        continue
                    except KeyError as e:
                        logging.warning(f"Missing required column at row {row_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            logging.warning(f"Uniqueness file not found: {file_path}")
            return None
        except Exception as e:
            logging.error(f"Error reading uniqueness file {file_path}: {e}")
            return None
            
        logging.debug(f"Loaded uniqueness scores for {len(scores)} accounts")
        return scores

    def aggregate_single_account_scores(self, account_name, uniqueness_data_map):
        """Aggregate scores with pandas-like precision and behavior."""
        scores = {"Source": account_name}

        # Map metric keys to output keys
        metric_key_to_output_key = {
            "accuracy_scoring": "Accuracy_Record",
            "completeness": "Completeness",
            "data_formatting": "Data_Formatting",
            "data_quality": "Data_Quality"
        }

        # Calculate mean metrics
        for metric_key, output_key in metric_key_to_output_key.items():
            val = self._calculate_mean_metric(metric_key, account_name)
            if val is not None:
                scores[output_key] = val
            else:
                logging.debug(f"Skipping {output_key} for {account_name} due to missing data")

        # Add uniqueness score
        if uniqueness_data_map and account_name in uniqueness_data_map:
            # Round to 4 decimal places to match pandas behavior
            scores["Uniqueness"] = round(float(uniqueness_data_map[account_name]), 4)
        elif uniqueness_data_map:
            logging.warning(f"Uniqueness score not found for '{account_name}'")

        # Calculate overall score from available numeric scores
        numeric_scores = [v for k, v in scores.items() if k != "Source" and isinstance(v, (int, float))]
        if numeric_scores:
            overall_score = sum(numeric_scores) / len(numeric_scores)
            scores["Overall_Score"] = round(overall_score, 15)
        else:
            scores["Overall_Score"] = None

        logging.debug(f"Final aggregated scores for {account_name}: {scores}")
        return scores

    def process_all_accounts(self, account_names):
        """Process all accounts with proper error handling."""
        all_results = []
        uniqueness_data_map = self._get_uniqueness_scores_map()
        
        for account in account_names:
            logging.info(f"Processing: {account}")
            try:
                scores = self.aggregate_single_account_scores(account, uniqueness_data_map)
                all_results.append(scores)
            except Exception as e:
                logging.error(f"Error processing account {account}: {e}")
                # Add a placeholder result with None values
                all_results.append({
                    "Source": account,
                    "Accuracy_Record": None,
                    "Completeness": None,
                    "Data_Formatting": None,
                    "Data_Quality": None,
                    "Uniqueness": None,
                    "Overall_Score": None
                })
                
        return all_results