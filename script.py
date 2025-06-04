import re

def modify_sql_file(input_file, output_file):
    # Read the SQL file
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.readlines()

    # Modify lines starting from line 343
    for i in range(342, len(content)):
        # Split the line into parts
        parts = re.split(r'(\s+)', content[i])
        # If the line has the correct number of fields, update the number_of_points
        if len(parts) > 15 and parts[15] == r'\N':
            parts[15] = parts[13]  # Set number_of_points to the value of level
            content[i] = ''.join(parts)  # Reconstruct the line

    # Write the modified content to a new file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(content)

# Usage
input_file = 'db_dump.sql'
output_file = 'modified_db_dump.sql'
modify_sql_file(input_file, output_file)