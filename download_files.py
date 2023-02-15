import json
import requests
import re

start_from = 3419

def replace_special_characters(string):
    return re.sub(r'[^a-zA-Z0-9]', '_', string)

# Load the JSON file
with open('merged_data.json') as json_file:
    data = json.load(json_file)

# Iterate over the list of objects
for obj in data:
    if int(obj['id']) <= start_from:
        continue

    # Get the URL to download the file
    url = obj['value']

    # Download the file
    response = requests.get(url)
    content = response.content

    # Combine the id and name properties to form the new filename
    filename = (str(obj['id']) + "_" + obj['name']).replace(' ', '_') + '.png'

    # Save the downloaded file with the new filename
    try:
        with open(filename, 'wb') as f:
            f.write(content)
    except:
        filename = replace_special_characters(str(obj['id']) + "_" + obj['name']) + '.png'
        with open(filename, 'wb') as f:
            f.write(content)
