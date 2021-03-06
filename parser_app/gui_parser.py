import PySimpleGUI as sg
from .layout_elements import make_window
import os
from os.path import isdir
from .parse_s7 import *
from .display_file import *
import webbrowser

""" GUI for Siemens S7 FC parser

    Created by Gianluca Traversa (RME Intern), Joe Rush and Jessica Lucas © 2021.
    https://github.com/gtraversa/AmazonRME
    gianlu.traversa@gmail.com
    
    Amazon EMA1, Derbishire, UK.
"""

window = make_window()
set_cursor(stuff = ['-ADD FILE-','-ADD KEY-','-REMOVE KEY-','-FILE LIST-','-REMOVE FILE-','-CLEAR FILES-',
                '-CLEAR KEYS-','-PARSED FILE SELECT-','-ALL KW-','-ALL NO KW-','-CLEAR FULL OUTPUT-','-EXTRACT KEYS-',
                '-PARSED FILE SELECT EXPANDABLE-','-CLEAR EXPANDABLE OUTPUT-','-COLLAPSE EXPANDABLE OUTPUT-',
                '-PARSED FILE SELECT SEARCHABLE-','-PARSED LAC SELECT SEARCHABLE-','-ALL CONV CB-','-PARSE-',
                '-PARSED CONVEYOR SELECT SEARCHABLE-','-SEARCH SEARCHABLE OUTPUT-','-MULTI SEARCH CB-','-CLEAR SEARCHABLE OUTPUT-',
                '-FB PARSED-','-FOB PARSED-','-FILE LIST LOAD-','-LOAD-','-REMOVE FILE LOAD-','-CLEAR FILES LOAD-','-COPYRIGHT-'],cursor='hand2', window =window)

#TODO add support for 302-303-403-404 (sorters have different syntax)
file_list = []
file_list_load = []
disp_list = []
disp_list_load = []
audit_path ={}
keys = []
expanded_keys = []
while True:
    try:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event == "-ADD FILE-":
            if values['-FILE-'] == '':
                continue
            f = values["-FILE-"]
            if isdir(f):
                for fname in os.listdir(f):
                    if fname.endswith('.txt'):
                        if len(keys) <1:
                            disp_list.append(fname.strip('.txt'))
                        else:
                            fname_disp = fname.strip('.txt')
                            fname_disp+= '['
                            for key in keys:
                                fname_disp+= str(key)+','
                            disp_list.append(fname_disp.strip(',')+ ']')
                        fpath = f+'/'+ fname
                        file_list.append(fpath)
            else:
                if len(keys) <1:
                    disp_list.append(f.split('/')[-1].strip('.txt'))
                else:
                    fname = f.split('/')[-1].strip('.txt')
                    fname+= '['
                    for key in keys:
                        fname+= str(key)+','
                    disp_list.append(fname.strip(',')+ ']')
                file_list.append(f)
            disp_list = remove_duplicates(disp_list)
            file_list = remove_duplicates(file_list)
            window["-FILE LIST-"].update(disp_list+disp_list_load)
            window['-FILE-'].update('')

        elif event == "-REMOVE FILE-":
            try:
                f_remove = values['-FILE LIST-'][0]
                disp_list.remove(f_remove)
                file_list = [f for f in file_list if f_remove not in f]
            except:
                pass
            window["-FILE LIST-"].update(disp_list+disp_list_load)

        elif event == "-ADD PARSED-":
            f = values["-JSON FILE-"]
            keys = extract_keys_load(f)
            if f.endswith('.json'):
                identifier =f.split('/')[-1].split('parsed')[0].strip('_')
                disp_list_load.append(identifier)
                file_list_load.append(f)
                audit_path[identifier] = f
            elif isdir(f):
                for fname in os.listdir(f):
                    if fname.endswith('.json'):
                        identifier =fname.split('/')[-1].split('parsed')[0].strip('_') 
                        fpath = f+'/'+fname
                        disp_list_load.append(identifier)
                        file_list_load.append(fpath)
                        audit_path[identifier] = fpath
            window["-FILE LIST LOAD-"].update(disp_list_load)
            window['-JSON FILE-'].update('')

        elif event == '-LOAD-':
            for key,value in audit_path.items():
                    if value == 'Error':
                        del audit_path[key]
                        continue
            update_values_stuff(['-PARSED FILE SELECT-','-PARSED FILE SELECT SEARCHABLE-',
                                    '-PARSED FILE SELECT EXPANDABLE-'], disp_list+disp_list_load, window)
            enable_stuff(['-PARSED FILE SELECT-','-PARSED FILE SELECT EXPANDABLE-',
                            '-PARSED FILE SELECT SEARCHABLE-', '-PARSED LAC SELECT SEARCHABLE-',
                            '-PARSED CONVEYOR SELECT SEARCHABLE-'],window)

        elif event == "-REMOVE FILE LOAD-":
            try:
                f_remove = values['-FILE LIST LOAD-'][0]
                disp_list_load.remove(f_remove)
                file_list_load = [f for f in file_list if f_remove not in f]
            except:
                pass
            window["-FILE LIST LOAD-"].update(disp_list_load)

        elif event == '-CLEAR FILES LOAD-':
            file_list_load, disp_list_load = [],[]
            clear_stuff(["-JSON FILE-",'-FILE LIST LOAD-'],window)
        
        elif event == '-EXTRACT KEYS-':
            keys = extract_keys_load(values['-PARSED FILE SELECT-'])
            window['-KEYS DISPLAY-'].update('')
            display_keys(keys,window)

        elif event == "-ADD KEY-":
            if values["-KEY-"].strip() != '':
                keys.append(values["-KEY-"].strip())
            else:
                continue
            keys = remove_duplicates(keys)
            window["-KEY-"]('')
            window["-KEY LIST-"].update(keys)
            for i,f in enumerate(disp_list):
                f= f.split('[')[0]
                f+= '['
                for key in keys:
                    f+= str(key)+','
                disp_list[i]=f.strip(',')+ ']'
            window['-FILE LIST-'].update(values = disp_list+disp_list_load)

        elif event == "-REMOVE KEY-":
            try:
                key_remove = values["-KEY LIST-"][0]
                keys.remove(key_remove)
            except:
                pass
            keys = remove_duplicates(keys)
            for i,f in enumerate(disp_list):
                f= f.split('[')[0]
                f+= '['
                for key in keys:
                    f+= str(key)+','
                disp_list[i]=f.strip(',')+ ']'
            window['-FILE LIST-'].update(values = disp_list+disp_list_load)
            window["-KEY LIST-"].update(keys)

        elif event == "-CLEAR FILES-":
            file_list, disp_list = [],[]
            clear_stuff(["-FILE-",'-FILE LIST-'],window)

        elif event == "-CLEAR KEYS-":
            keys = []
            clear_stuff(["-KEY-",'-KEY LIST-'],window)

        elif event == '-PARSE-':
            exact = False
            if values['-EXACT CB-']:
                exact = True
            if len(keys)>0:
                for i,f in enumerate(file_list):
                    parsed_file = begin_audit(f,keys,disp_list[i],exact)
                    if parsed_file != 'Error':
                        audit_path[str(disp_list[i])] = parsed_file
                update_values_stuff(['-PARSED FILE SELECT-','-PARSED FILE SELECT SEARCHABLE-',
                                    '-PARSED FILE SELECT EXPANDABLE-'], disp_list+disp_list_load, window)
                enable_stuff(['-PARSED FILE SELECT-','-PARSED FILE SELECT EXPANDABLE-',
                            '-PARSED FILE SELECT SEARCHABLE-', '-PARSED LAC SELECT SEARCHABLE-',
                            '-PARSED CONVEYOR SELECT SEARCHABLE-'],window)

        elif event == '-PARSED FILE SELECT-':
            path = audit_path[values['-PARSED FILE SELECT-']]
            window['-FULL OUTPUT-'].update('')
            full_display(path,window)
        
        elif event == '-ALL KW-':
            path = audit_path[values['-PARSED FILE SELECT-']]
            window['-FULL OUTPUT-'].update('')
            kw_display(path, window, kw_select = True)

        elif event == '-ALL NO KW-':
            path = audit_path[values['-PARSED FILE SELECT-']]
            window['-FULL OUTPUT-'].update('')
            kw_display(path, window, kw_select = False)

        elif event == '-CLEAR FULL OUTPUT-':
            clear_stuff(['-FULL OUTPUT-','-PARSED FILE SELECT-', '-KEYS DISPLAY-'],window)

        elif event == '-PARSED FILE SELECT SEARCHABLE-':
            path = audit_path[values['-PARSED FILE SELECT SEARCHABLE-']]
            load_LACs(path, window)

        elif event =='-PARSED LAC SELECT SEARCHABLE-':
            if values['-ALL CONV CB-']:
                if not values['-MULTI SEARCH CB-']:
                    clear_stuff(['-SEARCHABLE OUTPUT-'],window)
                path = audit_path[values['-PARSED FILE SELECT SEARCHABLE-']]
                LAC = values['-PARSED LAC SELECT SEARCHABLE-']
                conveyor = values['-PARSED CONVEYOR SELECT SEARCHABLE-']
                searchable_display(path,LAC, conveyor,window, values)
            else:
                path = audit_path[values['-PARSED FILE SELECT SEARCHABLE-']]
                LAC = values['-PARSED LAC SELECT SEARCHABLE-']
                load_conveyors(path, LAC, window)

        elif event == '-SEARCH SEARCHABLE OUTPUT-' or event == '-ALL CONV CB-':
            if not values['-MULTI SEARCH CB-']:
                clear_stuff(['-SEARCHABLE OUTPUT-'],window)
            path = audit_path[values['-PARSED FILE SELECT SEARCHABLE-']]
            LAC = values['-PARSED LAC SELECT SEARCHABLE-']
            conveyor = values['-PARSED CONVEYOR SELECT SEARCHABLE-']
            searchable_display(path,LAC, conveyor,window, values)

        elif event == '-CLEAR SEARCHABLE OUTPUT-':
            clear_stuff(['-SEARCHABLE OUTPUT-','-PARSED LAC SELECT SEARCHABLE-',
                        '-PARSED LAC SELECT SEARCHABLE-','-PARSED CONVEYOR SELECT SEARCHABLE-',
                        '-PARSED FILE SELECT SEARCHABLE-'],window)
        
        elif event == '-PARSED FILE SELECT EXPANDABLE-':
            depth = 0
            expanded_keys = []
            path = audit_path[values['-PARSED FILE SELECT EXPANDABLE-']]
            expandable_display(path,depth,window,expanded_keys)

        elif event == '-EXPANDABLE OUTPUT-':
            if 'LAC' or 'Conveyor' in str(values['-EXPANDABLE OUTPUT-'][0]):
                path = audit_path[values['-PARSED FILE SELECT EXPANDABLE-']]
                depth = 1
                target = values['-EXPANDABLE OUTPUT-']
                expanded_keys = expandable_display(path, depth,window,expanded_keys,target)
        
        elif event == '-COLLAPSE EXPANDABLE OUTPUT-':
            depth = 0
            expanded_keys = []
            path = audit_path[values['-PARSED FILE SELECT EXPANDABLE-']]
            expandable_display(path,depth,window,expanded_keys)

        elif event == '-CLEAR EXPANDABLE OUTPUT-':
            clear_stuff(['-EXPANDABLE OUTPUT-'], window)

        elif event == '-DISPLAY TAB-':
            stuff = ['-SEARCHABLE OUTPUT-','-FULL OUTPUT-','-PARSED LAC SELECT SEARCHABLE-',
                    '-PARSED LAC SELECT SEARCHABLE-', '-PARSED CONVEYOR SELECT SEARCHABLE-',
                    '-EXPANDABLE OUTPUT-','-PARSED FILE SELECT SEARCHABLE-','-PARSED FILE SELECT-',
                    '-PARSED FILE SELECT EXPANDABLE-']
            clear_stuff(stuff,window)

        elif event == '-FULL EXPORT-':
            path = sg.popup_get_folder('Select folder for saving:', keep_on_top=True)
            file_to_save = audit_path[values['-PARSED FILE SELECT-']]
            file_name = values['-PARSED FILE SELECT-']
            export_selected(file_to_save,file_name,path)

        elif event == '-FULL EXPORT ALL-':
            path = sg.popup_get_folder('Select folder for saving:', keep_on_top=True)
            export_all(audit_path,save_path = path, disp_list = disp_list+disp_list_load)

        elif event == '-SEARCHABLE EXPORT-':
            path = sg.popup_get_folder('Select folder for saving:', keep_on_top=True)
            export_displayed(values,'-EXPANDABLE OUTPUT-', path)
        
        elif event == '-FULL EXPORT DISPLAYED-':
            path = path = sg.popup_get_folder('Select folder for saving:', keep_on_top=True)
            export_displayed(values,'-FULL OUTPUT-',path)

        elif event == '-COPYRIGHT-':
            url = 'https://github.com/gtraversa/AmazonRME'
            webbrowser.open(url, new=0, autoraise=True)
    except Exception as e:
        print(e)
        
    
window.close()