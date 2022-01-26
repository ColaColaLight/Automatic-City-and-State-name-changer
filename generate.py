import os

import pandas as pd
from tqdm import tqdm
from load_write_database import load_dataframe, write_dataframe

states = load_dataframe("states.yaml")
provinces = load_dataframe("provinces.yaml")

languages = set(states.columns)

scripted_effects_folder = "common/scripted_effects"
if not os.path.exists(scripted_effects_folder):
    os.makedirs(scripted_effects_folder)

root_template = """apply_{}_endonyms = {{
    {}
}}
"""

state_template = """
if = {{
		limit = {{
			state = {}
			NOT = {{ has_state_flag = state_name_{} }}
		}}
		set_state_name = "{}"
		
		set_state_flag = state_name_{}
		{}
		
		{}
	}}
"""

clr_template = """
		clr_state_flag = state_name_{}"""

province_template = """
		set_province_name = {{ id = {} name = "{}" }}"""

# TODO handle case where state is same name but province is not

# for each language
for language in tqdm(languages):
    dest_file = os.path.join(scripted_effects_folder, "endonyms_{}.txt".format(language))
    with open(dest_file, 'w') as file:
        # for each state not null in the language column
        non_null_index = states[language].notna()
        states_not_null = states.loc[non_null_index]
        states_not_null = states_not_null[language]
        clear_string = "".join([clr_template.format(lang) for lang in languages.difference(language)])
        state_string = ""
        for index, state in states_not_null.items():
            state_provices = provinces[provinces['StateID'] == index]
            # select column
            state_provices = state_provices[[language]]
            # select rows
            state_provices = state_provices[state_provices[language].notna()]
            province_string = ""
            for provinceID, row in state_provices.iterrows():
                province_string += province_template.format(provinceID, row[0])
            state_string += state_template.format(index, language, state, language, clear_string, province_string)
        file.write(root_template.format(language, state_string))
