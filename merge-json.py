import json

# Load the first JSON file into a dictionary
with open("logo_paths.json", "r") as f:
    first_file = json.load(f)

# Load the second JSON file into a list of dictionaries
with open("network_ids.json", "r") as f:
    second_file = json.load(f)

# Create a new list to store the merged data
merged_data = []

# Iterate over the list of dictionaries from the second JSON file
for obj in second_file:
    id = obj["id"]
    name = obj["name"].lower()

    # Check if the "name" value from the second JSON file exists in the first JSON file
    if name in first_file:
        value = first_file[name]

        # Create a new dictionary with the merged data
        merged_dict = {"id": id, "name": name, "value": "https://image.tmdb.org/t/p/w500" + value}

        # Append the merged dictionary to the list of merged data
        merged_data.append(merged_dict)

# Write the merged data to a new JSON file
with open("merged_data.json", "w") as f:
    json.dump(merged_data, f)
