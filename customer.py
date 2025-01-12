import yaml
import random
import logging
from faker import Faker
from datetime import datetime
import csv
import json
from collections import defaultdict
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
# Initialize Faker and Logger
fake = Faker()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
def read_yaml(file_path):
    """Read the YAML configuration file."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.error(f"YAML configuration file not found: {file_path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        raise
def generate_primary_key(start, end, used_keys):
    """Generate a unique primary key within a range."""
    key = random.randint(start, end)
    while key in used_keys:
        key = random.randint(start, end)
    used_keys.add(key)
    return key
def generate_weighted_value(values, probabilities):
    """Generate a value based on weighted probabilities."""
    return random.choices(values, probabilities)[0]
def sort_fields_by_dependency(fields):
    """Sort fields to ensure dependencies are resolved before generation."""
    sorted_fields = []
    resolved_fields = set()
    iteration = 0
    while fields:
        iteration += 1
        unresolved = len(fields)
        for field in fields[:]:
            if field['type'] != 'dependency' or field['dependency']['field'] in resolved_fields:
                sorted_fields.append(field)
                resolved_fields.add(field['name'])
                fields.remove(field)
        if unresolved == len(fields):  # No progress, circular dependency detected
            logging.error("Circular dependency detected in fields.")
            raise ValueError("Circular dependency detected in fields.")
        logging.debug(f"Dependency resolution iteration {iteration}: {resolved_fields}")
    return sorted_fields
def generate_data_batch(domain_config, batch_size, reference_data=None, used_primary_keys=None):
    """Generate a batch of mock data for a domain."""
    reference_data = reference_data or {}
    used_primary_keys = used_primary_keys or set()
    sorted_fields = sort_fields_by_dependency(domain_config['fields'])
    batch_data = []
    for _ in range(batch_size):
        record = {}
        try:
            for field in sorted_fields:
                field_name = field['name']
                field_type = field['type']
                if field_type == 'primary_key':
                    record[field_name] = generate_primary_key(field['range']['start'], field['range']['end'], used_primary_keys)
                elif field_type == 'string' and 'faker' in field:
                    record[field_name] = getattr(fake, field['faker'])()
                elif field_type == 'float' and 'range' in field:
                    record[field_name] = random.uniform(field['range']['min'], field['range']['max'])
                elif field_type == 'integer' and 'range' in field:
                    record[field_name] = random.randint(field['range']['min'], field['range']['max'])
                elif field_type == 'datetime' and 'range' in field:
                    start = datetime.fromisoformat(field['range']['start'])
                    end = datetime.fromisoformat(field['range']['end'])
                    record[field_name] = fake.date_time_between(start_date=start, end_date=end).date().isoformat()
                elif field_type == 'relationship':
                    related_domain = field['relation']['domain']
                    related_field = field['relation']['field']
                    record[field_name] = random.choice(reference_data[related_domain])[related_field]
                elif field_type == 'dependency':
                    dependent_field = field['dependency']['field']
                    dependent_value = record[dependent_field]
                    dependency_values = field['dependency']['values'][dependent_value]
                    if isinstance(dependency_values, int):  # Fixed value dependency
                        record[field_name] = dependency_values
                    elif isinstance(dependency_values, list):  # List-based dependency
                        record[field_name] = random.choice(dependency_values)
                    elif isinstance(dependency_values, dict):  # Range-based dependency
                        record[field_name] = random.randint(dependency_values['min'], dependency_values['max'])
                    else:
                        raise ValueError(f"Invalid dependency format for field {field_name}.")
                elif field_type == 'predefined_list' and 'values' in field:
                    probabilities = field.get('probabilities', [1 / len(field['values'])] * len(field['values']))
                    record[field_name] = generate_weighted_value(field['values'], probabilities)
                elif field_type == 'computed':
                    # Compute values dynamically
                    formula = field['formula']
                    try:
                        record[field_name] = eval(formula, {"datetime": datetime}, record)
                    except KeyError as e:
                        raise ValueError(f"Missing field {e.args[0]} for computed formula in field {field_name}")
                else:
                    logging.warning(f"Unsupported field type {field_type} for field {field_name}.")
                    record[field_name] = None
        except Exception as e:
            logging.error(f"Error generating data for field {field_name}: {e}")
            raise
        batch_data.append(record)
    return batch_data
def write_to_csv(file_name, data):
    """Write data to a CSV file."""
    try:
        if data:
            keys = data[0].keys()
            with open(file_name, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            logging.info(f"Data successfully written to CSV file: {file_name}")
    except Exception as e:
        logging.error(f"Error writing to CSV file {file_name}: {e}")
        raise
def write_to_json(file_name, data):
    """Write data to a JSON file."""
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        logging.info(f"Data successfully written to JSON file: {file_name}")
    except Exception as e:
        logging.error(f"Error writing to JSON file {file_name}: {e}")
        raise
def main():
    try:
        config = read_yaml('customer.yaml')
        settings = config['mock_data_generator']['settings']
        record_count = settings['record_count']
        batch_size = min(record_count // 10, 1000)  # Divide records into 10 batches or max 1000 records per batch
        output_format = settings['output_format'].lower()
        reference_data = defaultdict(list)
        for domain in config['mock_data_generator']['domains']:
            domain_name = domain['name']
            logging.info(f"Generating data for domain: {domain_name}")
            used_primary_keys = set()
            domain_data = []
            with tqdm(total=record_count, desc=f"Generating {domain_name} data", unit="record") as pbar:
                with ThreadPoolExecutor() as executor:
                    futures = [
                        executor.submit(
                            generate_data_batch,
                            domain,
                            min(batch_size, record_count - len(domain_data)),
                            reference_data,
                            used_primary_keys
                        )
                        for _ in range(0, record_count, batch_size)
                    ]
                    for future in as_completed(futures):
                        batch_data = future.result()
                        domain_data.extend(batch_data)
                        pbar.update(len(batch_data))
            reference_data[domain_name] = domain_data
            file_name = f"{domain_name}_mock_data"
            if output_format == 'csv':
                write_to_csv(f"{file_name}.csv", domain_data)
            elif output_format == 'json':
                write_to_json(f"{file_name}.json", domain_data)
            else:
                logging.error(f"Unsupported output format: {output_format}")
                raise ValueError(f"Unsupported output format: {output_format}")
    except Exception as e:
        logging.critical(f"Program terminated due to an error: {e}")
if __name__ == "__main__":
    main()