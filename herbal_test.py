# -*- coding: utf-8 -*-
"""
Created on Fri May  6 22:55:31 2022

@author: Caelynn
"""

import json
import pandas as pd
import os
import glob

#%%

def get_file():
    '''
    Changes directory and obtains herb database location
    '''
    file_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(file_path)
    file_list = glob.glob('*.json')
    json_file = max(file_list, key=os.path.getctime)

    
    return json_file

#==============================================================================

def condition_cleanup():
    '''
    Creates a list of all, unique herbal conditions
    '''
    condition_list = []
    
    for i in range(len(herbs)):
        condition = herbs[i]['Condition']
        condition = condition.split(',')
        
        if len(condition) > 1:
            for j in range(len(condition)):
                condition[j] = condition[j].strip()
            condition_list += condition
        else:
            condition_list.append(condition[0])
            
    condition_list = list(set(condition_list))
    return condition_list

#==============================================================================

def initial_print(df):
    try:
        df = df.drop(columns=['Description',
                              'Climatic Zone','Preparation',
                              'Uses','Ability Check','Lore','Rarity'])
    except:
        df = df.drop(columns=['Description',
                              'Climatic Zone','Preparation',
                              'Uses','Ability Check','Rarity'])
    print(df.to_string(index=False))
    herbs_present = df['Herb'].tolist()
        
    return herbs_present

#==============================================================================

def herb_print(df, input_):
    df = df[df['Herb'] == input_]
    df = df.to_dict('list')
    
    print('='*60)
    print(f"Herb: {df['Herb'][0]}")
    print(f"Available: {df['Availability'][0]}")
    print(f"Climatic Zone: {df['Climatic Zone'][0]}")
    print(f"Locale: {df['Locale'][0]}")
    print(f"Preparation: {df['Preparation'][0]}")
    print(f"Cost: {df['Cost'][0]}")
    print(f"Uses: {df['Uses'][0]}")
    print(f"Ability Check: {df['Ability Check'][0]}")
    print(f"Condition: {df['Condition'][0]}")    
    
    try:
        if type(df['Lore'][0]) == str:
            print(f"\n{df['Lore'][0]}")
    except:
        pass
    
    print(f"\n{df['Description'][0]}")

#==============================================================================

def sort_by_condition():
    '''
    Inputs a desired condition and outputs a dataframe of herbs that fit said
    condition
    '''
    herbs_by_condition = []
    input_loop = True
    condition_list = condition_cleanup()    
    
    while input_loop == True:
        input_ = input('Select Condition: ')
        for condition in condition_list:
            if input_.lower() in condition.lower():
                input_ = condition
                input_loop = False
                break
    
    for i in range(len(herbs)):
        herb_condition = herbs[i]['Condition']
        
        if input_ in herb_condition:
            cost = herbs[i]['Cost']
            
            if 'cj' in cost:
                cost = cost.split()
                cost = float(cost[0])
            elif 'sm' in cost:
                cost = cost.split()
                cost = float(cost[0])
                cost *= 10
            elif 'gt' in cost:
                cost = cost.split()
                cost = float(cost[0])
                cost *= 100
            elif 'pc' in cost:
                cost = cost.split()
                cost = float(cost[0])
                cost *= 1000
                
            herbs[i]['Rarity'] = cost
            herbs_by_condition.append(herbs[i])
                
    herbs_by_condition = pd.DataFrame(herbs_by_condition).sort_values('Rarity')
    herbs_present = initial_print(herbs_by_condition)
    
    loop = True
    while loop == True:
        input_ = input('Select Herb: ')
        
        for herb in herbs_present:
            if input_.lower() in herb.lower():
                loop = False
                input_ = herb
                herb_print(herbs_by_condition, input_)
                break
        if loop == True:
            print('\nHerb not available')
    
#%%

file = get_file()
with open(file,'r') as r:
    herbs = json.load(r)

#%%

df = pd.DataFrame(herbs).sort_values('Herb').reset_index(drop=True)
# herbs = herbs.sort_values('Herb',ascending=False)

autocomplete_dict = {}

for category in df.columns:
    try:
        column = list(set(df[category]))
        refined_column = []
        for item in column:
            if ',' in item:
                split_item = item.split(',')
                
                for item in split_item:
                    refined_column.append(item.strip())
           
            else:
                refined_column.append(item)
        
        refined_column = list(set(refined_column))
        
        autocomplete_dict[category] = refined_column
    except TypeError:
        pass
    
bool_df = df['Herb'].str.contains('Zur')
test_df = df[bool_df].reset_index(drop=True).to_dict('index')[0]

selection_index = df.index[df['Herb'] == test_df['Herb']].tolist()[0]
test = dict(df.iloc[selection_index].fillna(''))

# while True:
#     sort_by_condition()
            
# print(herbs.Herb.to_string(index=False))
# max_length = herbs.Herb.str.len().max()

