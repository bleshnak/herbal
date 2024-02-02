# -*- coding: utf-8 -*-
"""
Created on Sun May 22 19:26:35 2022

@author: dalda
"""

import curses

#%%

menu = ['Open', 'Close']

def print_menu(stdscr, selected_row_idx):
    curses.curs_set(0)
    stdscr.clear()
    
    h, w = stdscr.getmaxyx()
    
    for idx, row in enumerate(menu):
        x = w//2 - len(row)//2
        y = h//2 - len(menu)//2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)
        
        message = 'The Novice Wayfarer\'s Herbal'
        stdscr.addstr(h-12, w//2 - len(message)//2, message, curses.A_BOLD | curses.A_UNDERLINE)
        message = '-May it serve you better than it served me, fān shǔ'
        stdscr.addstr(h-10, w//2 - len(message)//2, message, curses.A_ITALIC)
        
    stdscr.refresh()
        
def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    current_row_idx = 0
    
    print_menu(stdscr, current_row_idx)
    
    while True:
        key = stdscr.getch()
        
        stdscr.clear()
        
        if (key == curses.KEY_UP or key in [87, 119]) and current_row_idx > 0:
            current_row_idx -= 1
        elif (key == curses.KEY_DOWN or key in [83, 115]) and current_row_idx < len(menu) - 1:
            current_row_idx += 1
        elif key == curses.KEY_ENTER or key in [10, 13, 32]:
            if menu[current_row_idx] == 'Close':
                break
            else:
                stdscr.addstr(0, 0, f"You pressed {menu[current_row_idx]}")
                stdscr.refresh()
                stdscr.getch()
        elif key in [27]:
            break
            
        print_menu(stdscr, current_row_idx)
        stdscr.refresh()

curses.wrapper(main)