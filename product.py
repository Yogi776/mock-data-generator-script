import yaml
import random
import logging
from faker import Faker
from datetime import datetime
import csv
import json
from tqdm import tqdm

# Initialize Faker and Logger
fake = Faker()
logging.basicConfig(
    level=logging.INFO,  # Set INFO level for general logs
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
    while True:
        key = random.randint(start, end)
        if key not in used_keys:
            used_keys.add(key)
            return key


def generate_weighted_value(values, probabilities):
    """Generate a value based on weighted probabilities."""
    return random.choices(values, probabilities)[0]


def sort_fields_by_dependency(fields):
    """Sort fields to ensure dependencies are resolved before generation."""
    sorted_fields = []
    resolved_fields = set()

    while fields:
        unresolved = len(fields)
        for field in fields[:]:
            if field['type'] != 'dependency' or field['dependency']['field'] in resolved_fields:
                sorted_fields.append(field)
                resolved_fields.add(field['name'])
                fields.remove(field)
        if unresolved == len(fields):  # No progress, circular dependency detected
            logging.error("Circular dependency detected in fields.")
            raise ValueError("Circular dependency detected in fields.")
    return sorted_fields


def generate_field_value(field, record, used_keys):
    """Generate a value for a field based on its type."""
    try:
        field_type = field.get('type')
        field_name = field.get('name')
        logging.debug(f"Generating value for field: {field_name} (type: {field_type})")

        if field_type == 'primary_key':
            return generate_primary_key(field['range']['start'], field['range']['end'], used_keys)
        elif field_type == 'predefined_list':
            probabilities = field.get('probabilities', [1 / len(field['values'])] * len(field['values']))
            return generate_weighted_value(field['values'], probabilities)
        elif field_type == 'dependency':
            dependency = field['dependency']
            dependent_field = dependency['field']
            if dependent_field not in record:
                raise ValueError(f"Dependency field '{dependent_field}' not found in the record.")
            dependent_value = record[dependent_field]
            dependency_values = dependency['values'][dependent_value]
            if isinstance(dependency_values, list):  # List-based dependency
                return random.choice(dependency_values)
            elif isinstance(dependency_values, dict):  # Range-based dependency
                return round(random.uniform(dependency_values['min'], dependency_values['max']), 2)
        elif field_type == 'computed':
            formula = field['formula']
            return eval(formula, {"random": random, "datetime": datetime}, record)
        elif field_type == 'datetime' and 'range' in field:
            start = datetime.fromisoformat(field['range']['start'])
            end = datetime.fromisoformat(field['range']['end'])
            return fake.date_time_between(start_date=start, end_date=end).isoformat()
        elif field_type == 'string' and 'faker' in field:
            return getattr(fake, field['faker'])()
        else:
            logging.warning(f"Unsupported or missing type for field: {field.get('name')}")
            return None
    except Exception as e:
        logging.error(f"Error generating value for field '{field_name}': {e}")
        raise


def generate_record(domain_config, used_keys):
    """Generate a single record for a domain."""
    record = {}
    fields = sort_fields_by_dependency(domain_config['fields'])

    for field in fields:
        try:
            value = generate_field_value(field, record, used_keys)
            if value is None:
                logging.error(f"Field '{field['name']}' generated a None value. Skipping record.")
                return None  # Skip record if any field is invalid
            record[field['name']] = value
        except Exception as e:
            logging.error(f"Error in field '{field['name']}' of domain '{domain_config['name']}': {e}")
            return None  # Skip record if any error occurs
    return record


def generate_data_batch(domain_config, record_count):
    """Generate records for a domain based on record_count."""
    records = []
    used_keys = set()

    for _ in tqdm(range(record_count), desc=f"Generating {domain_config['name']} records", unit="record"):
        record = generate_record(domain_config, used_keys)
        if record:
            records.append(record)

    if len(records) != record_count:
        logging.warning(
            f"Expected {record_count} records but generated {len(records)} for domain '{domain_config['name']}'")
    else:
        logging.info(f"Successfully generated {len(records)} records for domain '{domain_config['name']}'")

    return records


def generate_unique_combinations(domain_config):
    """Generate all unique combinations for a domain."""
    fields = domain_config['fields']
    primary_key_field = next((f for f in fields if f['type'] == 'primary_key'), None)
    category_field = next((f for f in fields if f['name'] == 'category_name'), None)
    subcategory_field = next((f for f in fields if f['name'] == 'subcategory_name'), None)
    color_field = next((f for f in fields if f['name'] == 'product_color'), None)

    if not (primary_key_field and category_field and subcategory_field and color_field):
        raise ValueError("Required fields for unique combinations are missing.")

    combinations = []
    product_id = primary_key_field['range']['start']

    for category in category_field['values']:
        subcategories = subcategory_field['dependency']['values'][category]
        for subcategory in subcategories:
            for color in color_field['values']:
                record = {}
                record['product_id'] = product_id
                record['category_name'] = category
                record['subcategory_name'] = subcategory
                record['product_color'] = color

                # Generate other fields based on dependencies
                for field in fields:
                    if field['name'] not in record:
                        record[field['name']] = generate_field_value(field, record, set())

                combinations.append(record)
                product_id += 1

    logging.info(f"Generated {len(combinations)} unique combinations for domain '{domain_config['name']}'.")
    return combinations


def write_output(file_name, data, output_format):
    """Write data to a file in the specified format (JSON or CSV)."""
    try:
        if output_format == 'json':
            with open(file_name, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
        elif output_format == 'csv':
            with open(file_name, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        logging.info(f"Data successfully written to {file_name}")
    except Exception as e:
        logging.error(f"Error writing to file {file_name}: {e}")
        raise


def main():
    try:
        config = read_yaml('product.yaml')
        settings = config['mock_data_generator']['settings']
        output_format = settings['output_format']
        record_count = settings['record_count']

        for domain in config['mock_data_generator']['domains']:
            domain_name = domain['name']
            logging.info(f"Generating data for domain: {domain_name}")

            if domain.get('unique_combinations', False):
                domain_data = generate_unique_combinations(domain)
            else:
                domain_data = generate_data_batch(domain, record_count)

            if not domain_data:
                logging.error(f"No records generated for domain '{domain_name}'")
                continue

            file_name = f"{domain_name}_mock_data.{output_format}"
            write_output(file_name, domain_data, output_format)

    except Exception as e:
        logging.critical(f"Program terminated due to an error: {e}")


if __name__ == "__main__":
    main()