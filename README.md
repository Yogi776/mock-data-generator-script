# Mock Data Generator Configuration Guide

This guide provides a detailed overview of the **Mock Data Generator** configuration file, explaining the various features and field types. The YAML configuration enables users to easily define the structure and behavior of generated datasets across multiple domains.

---

## Features of the YAML Configuration

### 1. **Output Format**
   - Specify the desired output format for the generated data.
   - Supported formats: **JSON**, **CSV**.
   - Example:
     ```yaml
     output_format: json  # Options: json or csv
     ```

### 2. **Record Count**
   - Define the number of records to generate for each domain.
   - Example:
     ```yaml
     record_count: 10000  # Number of records to generate
     ```

### 3. **Seed for Reproducibility**
   - A seed ensures the data generation process is deterministic and reproducible.
   - Example:
     ```yaml
     seed: 42  # Seed for reproducibility
     ```

### 4. **Domains**
   - Domains are logical groups of data (e.g., `customers`, `products`) with specific fields.
   - Each domain can have a unique structure and set of rules.
   - Example:
     ```yaml
     domains:
       - name: customers
       - name: products
     ```

---

## Field Types

### 1. **Primary Key**
   - Generates unique identifiers for each record.
   - Configurable with a range to define the starting and ending values.
   - Example:
     ```yaml
     - name: customer_id
       type: primary_key
       range:
         start: 1
         end: 10001
     ```

### 2. **String with Faker**
   - Uses the `Faker` library to generate realistic string data (e.g., names, email addresses).
   - Example:
     ```yaml
     - name: first_name
       type: string
       faker: first_name
     ```

### 3. **Predefined List**
   - Selects a value from a predefined list with optional weighted probabilities.
   - Example:
     ```yaml
     - name: gender
       type: predefined_list
       values: ["Male", "Female"]
       probabilities: [0.6, 0.4]
     ```

### 4. **Dependency**
   - Generates values based on another field's value.
   - Supports:
     - **Range-based dependencies** (e.g., `list_price` depends on `category_name`).
     - **List-based dependencies** (e.g., `brand_name` depends on `category_name`).
   - Example:
     ```yaml
     - name: annual_income
       type: dependency
       dependency:
         field: social_class
         values:
           Lower:
             min: 20000
             max: 30000
           Middle:
             min: 35000
             max: 50000
           Upper:
             min: 55000
             max: 850000
     ```

### 5. **Computed Fields**
   - Dynamically computes field values based on a formula or calculation.
   - Example:
     ```yaml
     - name: sale_price
       type: computed
       formula: list_price * random.uniform(0.8, 0.95)
     ```

### 6. **Datetime Fields**
   - Generates dates or timestamps within a specified range and format.
   - Example:
     ```yaml
     - name: register_date
       type: datetime
       format: YYYY-MM-DD
       range:
         start: "2010-01-01"
         end: "2023-12-31"
     ```

---

## Unique Features in the YAML

### 1. **Unique Combinations**
   - Ensures that records within a domain (e.g., `products`) are unique.
   - Example:
     ```yaml
     - name: products
       unique_combinations: true
     ```

### 2. **Domain-Specific Customizations**
   - Each domain has its own set of fields, dependencies, and rules.
   - Example:
     - `customers`: Focus on personal and demographic information.
     - `products`: Focus on product attributes, pricing, and relationships.

### 3. **Hierarchical Dependencies**
   - Fields can depend on other fields for their values (e.g., `subcategory_name` depends on `category_name`).
   - Example:
     ```yaml
     - name: subcategory_name
       type: dependency
       dependency:
         field: category_name
         values:
           Electronic: ["Home Appliance", "Laptop"]
     ```

### 4. **Dynamic Lookup Values**
   - Use `dependency` to map values dynamically based on other fields.
   - Example:
     ```yaml
     - name: brand_name
       type: dependency
       dependency:
         field: category_name
         values:
           Electronic: ["Samsung", "Apple"]
     ```

### 5. **Support for Multiple Domains**
   - Generate data for multiple domains within a single configuration file.

---

## Example Use Cases

### Customers Domain
Generate customer data with attributes like `social_class`, `annual_income`, and `degree_of_loyalty`:
```yaml
- name: customers
  fields:
    - name: customer_id
      type: primary_key
      range:
        start: 1
        end: 10000

    - name: social_class
      type: predefined_list
      values: ["Lower", "Middle", "Upper"]
      
    - name: annual_income
      type: dependency
      dependency:
        field: social_class
        values:
          Lower: {"min": 20000, "max": 30000}
```

### Products Domain
Generate unique product combinations with attributes like `category_name`, `brand_name`, and `list_price`:
```yaml
- name: products
  unique_combinations: true
  fields:
    - name: product_id
      type: primary_key
      range:
        start: 1000
        end: 9000

    - name: category_name
      type: predefined_list
      values: ["Electronic", "Kitchen"]

    - name: brand_name
      type: dependency
      dependency:
        field: category_name
        values:
          Electronic: ["Samsung", "Apple"]
```

---

## Running the Mock Data Generator

### 1. Install Dependencies
Install the required Python libraries:
```bash
pip install faker tqdm pyyaml
```

### 2. Configure YAML
Update the `mock_config.yaml` file to define your desired domains and fields.

### 3. Execute the Script
Run the script to generate the data:
```bash
python mock_data_generator.py
```

### 4. View Generated Files
Generated data will be saved in the specified format (`json` or `csv`) with names like `customers_mock_data.json`.

---

## Error Handling

- **Missing Dependencies**:
  Ensure all `dependency` fields reference existing fields.
- **Unsupported Types**:
  Check for typos or unsupported field types.
- **Invalid Output Format**:
  Set `output_format` to either `json` or `csv`.

---

## Future Enhancements

- Support for hierarchical or nested data structures.
- Additional field types like `geolocation` or `boolean`.
- Integration with external APIs for dynamic data lookups.
  