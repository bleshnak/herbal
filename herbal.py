# -*- coding: utf-8 -*-
"""
Created on Sun May 22 21:39:14 2022

@author: 
"""

import os
import glob
import json
import pandas as pd
import curses
import copy


#%%

def get_file():
    '''
    Changes directory and obtains herb database location
    '''
    file_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(file_path)
    file_list = glob.glob('*.json')
    json_file = max(file_list, key=os.path.getctime)
    
    with open(json_file,'r') as r:
        herbs = json.load(r)

    return herbs

#%%

def populate_pads(stdscr, df, labels, col_buffer, row_buffer, current_row):
    curses.curs_set(0)
    labels_list = list(labels.keys())
    
    rows, cols = stdscr.getmaxyx() #update rows and columns of terminal if re-adjusted
    pad_width = ((cols-col_buffer*2)//len(labels_list)) #update pad_width if re-adjusted
    
    stdscr.clear() #clear to adjust the column titles when adjusted
    pad_dimensions = [] #initialize pad dimension list
    label_locations = []
    pads = {} #initialize pad dictionary
    
    #iterate through the labels list
    for idx, label in enumerate(labels_list):
        #define the column title locations and place them in stdscr
        label_loc = pad_width*idx + (pad_width//2 - len(label)//2) + col_buffer
        if labels[label] == True:
            stdscr.addstr(row_buffer-3, label_loc, labels_list[idx], curses.A_STANDOUT | curses.A_BOLD | curses.A_UNDERLINE)
        else:
            stdscr.addstr(row_buffer-3, label_loc, labels_list[idx], curses.A_BOLD | curses.A_UNDERLINE)
        #define the start and stop locations for each pad for future use
        pad_dimensions.append([((cols-col_buffer*2)//len(labels_list))*(idx) + col_buffer, ((cols-col_buffer*2)//len(labels))*(idx) + ((cols-col_buffer*2)//len(labels)) + col_buffer])
        #store label locations for future purposes
        label_locations.append(label_loc)
        #populate the pads dictionary
        pads[label] = curses.newpad(len(df[label])*3, ((cols-col_buffer*2)//len(labels_list)))
        #refresh to add pads
        stdscr.refresh()
            
    #iterate through the pads dictionary
    for idx, label in enumerate(pads):
        #iterate through the dataframe rows
        for item in df[label]:
            #if the item length is greater than the pad width, truncate the item
            if len(item) >= pad_width:
                pads[label].addstr(item[:pad_width-1] + '\n\n')
            else:
                pads[label].addstr(item + '\n\n')
        #refresh the pad to its initial state
        pads[label].refresh(current_row, 0, 
                            row_buffer - 1, pad_dimensions[idx][0], 
                            rows-row_buffer, pad_dimensions[idx][1])
    
    return label_locations, rows, cols

#------------------------------------------------------------------------------

def search(stdscr, search_pad, original_df, autocomplete_dict, col_buffer, row_buffer, current_row):
    curses.mousemask(0)
    found = False
    
    rows, cols = stdscr.getmaxyx()

    search_pad.clear()
    search_pad.refresh(0, 0, 
                       rows-row_buffer//2 + 1, col_buffer,
                       rows-row_buffer//2 + 1, (cols-col_buffer*2)//2)
    
    search_container = []
    
    while True:
        key = stdscr.getkey()
        
        try:
            if ord(key) == 27:
                break
            elif key == '\n':
                if found != False:
                    if list(autocomplete_dict.keys())[0] != found[0]:
                        bool_df = original_df[found[0]].str.contains(found[1])
                        original_df = original_df[bool_df]
                        current_row = 0
                    else:
                        bool_df = original_df[found[0]].str.contains(found[1])
                        selection = original_df[bool_df].reset_index(drop=True).to_dict('index')[0]
                        selection_info(stdscr, selection, original_df, col_buffer, row_buffer)
                break
            elif ord(key) == 8:
                if len(search_container) > 0:
                    search_container.pop()
            else:
                search_container.append(key)
                
                if len(search_container) >= (cols-col_buffer*2)//2:
                    break
        except:
            search_container = []
        
        search_text = ''.join(search_container)
        
        search_pad.clear()
        
        found = False
        for key in autocomplete_dict:
            for item in autocomplete_dict[key]:
                if item.upper().startswith(search_text.upper()) and len(search_text) > 0:
                    search_pad.addstr(0, 0, item, curses.color_pair(1))
                    found = (key, item)
                    break
            if found != False:
                break
        
        
        for idx, char in enumerate(search_text):
            search_pad.addstr(0, idx, char)
        
        search_pad.refresh(0, 0, 
                           rows-row_buffer//2 + 1, col_buffer,
                           rows-row_buffer//2 + 1, (cols-col_buffer*2)//2)
    
    return original_df, current_row

#------------------------------------------------------------------------------

def selection_info(stdscr, selection, original_df, col_buffer, row_buffer):
    def assure_continuity(string, starting_row):
        string = string.split()
        
        line = ''
        n = 0
        for idx, word in enumerate(string):
            if len(line) + len(word) + 1 < cols:
                line += word + ' '
            else:
                info_window.addstr(starting_row + n, 0, line)
                n += 1
                line = word + ' '
            
            if idx == len(string)-1:
                info_window.addstr(starting_row + n, 0, line.center(cols, ' '))
        
        return n
    
    while True:
        curses.curs_set(0)
        curses.mousemask(0)
        rows, cols = stdscr.getmaxyx()
        if rows < 13:
            rows = 13
        
        data_rows = 11
        start = ((rows-data_rows)//2) - data_rows//3
        
        
        info_window = curses.newwin(rows, cols, 0, 0)
        info_window.addstr(0, 0, f" {selection['Herb']} ".center(cols,'-'))
        info_window.addstr(rows-2, 0, f" {selection['Herb']} ".center(cols,'-'))
        
        info_window.addstr(start-1, 0, f'{selection["Herb"]}'.center(cols,' '))
        info_window.addstr(start+1, 0, f'{selection["Condition"]}'.center(cols,' '))
        info_window.addstr(start+2, 0, f'{selection["Availability"]}'.center(cols,' '))
        info_window.addstr(start+3, 0, f'{selection["Climatic Zone"]}'.center(cols,' '))
        info_window.addstr(start+4, 0, f'{selection["Locale"]}'.center(cols,' '))
        
        preparation = selection["Preparation"]
        preparation.strip().replace('none','not necessary').replace('None','not necessary')
        info_window.addstr(start+5, 0, f'{preparation} to prepare'.center(cols,' '))
                
        uses = selection["Uses"]
        try:
            if int(uses) == 1:
                info_window.addstr(start+6, 0, f'{selection["Uses"]} use'.center(cols,' '))
            else:
                info_window.addstr(start+6, 0, f'{selection["Uses"]} uses'.center(cols,' '))
        except:
            info_window.addstr(start+6, 0, f'{selection["Uses"]} uses'.center(cols,' '))
    
        info_window.addstr(start+7, 0, f'costs {selection["Cost"]}'.center(cols,' '))
    
        offset_1 = assure_continuity(selection["Description"], start+9)
        
        lore = selection["Lore"]
        if lore != '':
            assure_continuity(lore, start + 11 + offset_1)
        
        info_window.refresh()
        
        key = stdscr.getch()
        
        selection_index = original_df.index[original_df['Herb'] == selection['Herb']].tolist()[0]
        
        try:
            if key == 27:
                break
            elif key == 97 or key == 65 or key == curses.KEY_LEFT:
                selection_index -= 1
                selection = dict(original_df.iloc[selection_index].fillna(''))
            elif key == 100 or key == 68 or key == curses.KEY_RIGHT:
                if selection_index == len(original_df)-1:
                    selection_index = 0
                else:
                    selection_index += 1
                selection = dict(original_df.iloc[selection_index].fillna(''))
            else:
                pass
        except:
            pass

#------------------------------------------------------------------------------

def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(1)
    
    curses.init_color(17, 200, 200, 200)
    curses.init_pair(1, 17, curses.COLOR_BLACK)
    
    labels = ['Herb', 'Condition', 'Availability', 'Locale', 'Cost']
    
    df = pd.DataFrame(get_file()).fillna('')
    df = df.sort_values(labels[0]).reset_index(drop=True)
    original_df = copy.deepcopy(df)
    
    
    autocomplete_dict = {}
    for category in labels:
        if category in ['Herb', 'Condition', 'Locale']:
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
    
    bool_list = [True]
    for i in range(len(labels)-1):
        bool_list.append(False)
    labels = dict(zip(labels, bool_list))
    
    col_buffer = 6
    row_buffer = 6
    current_row = 0
        
    while True:
        curses.mousemask(1)
        
        label_locations, rows, cols = populate_pads(stdscr, df, labels, col_buffer, row_buffer, current_row)
        
        search_pad = curses.newpad(1, (cols-col_buffer*2)//2)
        search_pad.addstr('Click Here to Search')
        search_pad.refresh(0, 0, 
                           rows-row_buffer//2 + 1, col_buffer,
                           rows-row_buffer//2 + 1, (cols-col_buffer*2)//2)
        stdscr.refresh()
        
        key = stdscr.getch()
        
        bool_list = []
        for i in range(len(list(labels.keys()))):
            bool_list.append(False)
        labels = dict(zip(list(labels.keys()), bool_list))
        
        if key == 119 or key == curses.KEY_UP:
            if current_row >= 2:
                current_row -= 2
        elif key == 115 or key == curses.KEY_DOWN:
            if current_row <= int((len(df[list(labels.keys())[0]]))*2 - 75/row_buffer):
                current_row += 2
        elif key == curses.KEY_PPAGE:
            current_row = 0
        elif key == curses.KEY_NPAGE:
            current_row = int((len(df[list(labels.keys())[0]]))*2  - 75/row_buffer)
        elif key == curses.KEY_MOUSE:
            _, x, y, _, _ = curses.getmouse()
            for idx, label in enumerate(list(labels.keys())):
                if y == row_buffer-3 and x in range(label_locations[idx], label_locations[idx]+len(label)):
                    labels[label] = not labels[label]
                    if label == 'Cost':
                        if df.index.is_monotonic_increasing:
                            df = df.sort_values('Rarity', ascending=False)
                        else:
                            df = df.sort_values('Rarity', ascending=True).reset_index(drop=True)
                    else:
                        if df.index.is_monotonic_increasing:
                            df = df.sort_values(label, ascending=False)
                        else:
                            df = df.sort_values(label,ascending=True).reset_index(drop=True)
            if y == rows-row_buffer//2 + 1:
                df, current_row = search(stdscr, search_pad, original_df, autocomplete_dict, col_buffer, row_buffer, current_row)
                    
curses.wrapper(main)
