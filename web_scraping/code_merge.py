# import pandas as pd

# # Load each CSV file
# df1 = pd.read_csv('/Users/thiradatiamklang/Desktop/iLab/cover_final.csv')
# df2 = pd.read_csv('/Users/thiradatiamklang/Desktop/iLab/merged_file.csv')

# # Concatenate all dataframes
# merged_df = pd.concat([df1, df2], ignore_index=True)

# # Save the merged dataframe to a new CSV file
# merged_df.to_csv('/Users/thiradatiamklang/Desktop/iLab/merged_file_final.csv', index=False)


import pandas as pd
import csv
import json
df = pd.read_csv("/Users/thiradatiamklang/Desktop/iLab/merged_file_final.csv")
data = {}
# Create a list to store intents
intents = []

# Iterate through each row of the dataframe
for index, row in df.iterrows():
    answer = row["Answer"]
    label = row["Labels"]
    
    # Check if the intent already exists
    intent_exists = False
    for intent in intents:
        if intent["tag"] == label:
            intent["responses"].append(answer)
            intent_exists = True
            break
    
    # If the intent doesn't exist, create a new one
    if not intent_exists:
        intents.append({"tag": label, "responses": [answer]})

# Create a dictionary with the intents list
data = {"intents": intents}

# Write the dictionary to a JSON file
with open("/Users/thiradatiamklang/Desktop/iLab/intents_last_final.json", "w") as f:
    json.dump(data, f, indent=4)

print("JSON file created successfully!")
