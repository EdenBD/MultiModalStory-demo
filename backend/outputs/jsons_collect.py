import pandas as pd
import os
import re
import json

# Get all json files that end with txt and are not the default (defaults have only one \w).
files = [f for f in os.listdir('.') if os.path.isfile(
    f) and re.search(r'\w{2,}\.txt', f)]
dfs = []
# Create a df from each json
for f in files:
    with open(f) as json_file:
        data = json.load(json_file)
        df = pd.json_normalize(data)
        # Insert id as first column
        df.insert(0, 'id', f[:f.rfind('.')])
        dfs.append(df)

# Concatenae all json dfs to one csv, indexed by id
final_df = pd.concat(dfs, ignore_index=True)
final_df.to_csv("jsons_collection.csv", index=False)
