import json
import copy
from os.path import isdir
import os
from fpdf import FPDF

"""Assistance functions to streamline main GUI program"""

def full_display(path,window):
    """ Load .json file and fully display all fields

        @param path: Path to .json file
        @type path: Str
        @param window: GUI window 
        @type window: Class Window
    """
    try:
        with open(path) as jfile:
            f = json.load(jfile)
            for lac in f.keys():
                for conv in f[lac]:
                    try:
                        del f[lac][conv]['load_identity']
                    except:
                        pass
            window['-FULL OUTPUT-'].print(json.dumps(f, indent = 4).replace('"','').replace('\\',''))
    except Exception as e:
        window['-FULL OUTPUT-'].print(e)

def load_LACs(path,window):
    """ Load all available LACs in the parsed .json

        @param path: Path to .json file
        @type path: Str
        @param window: GUI window 
        @type window: Class Window
    """
    try:
        with open(path) as jfile:
            f = json.load(jfile)
            lacs = []
            for lac in f.keys():
                lacs.append(lac)
            update_values_stuff(['-PARSED LAC SELECT SEARCHABLE-'],lacs,window)
    except Exception as e:
        window['-SEARCHABLE OUTPUT-'].print(e)

def load_conveyors(path,LAC,window):
    """ Load all available conveyors in the selected LAC from the parsed .json

        @param path: Path to .json file
        @type path: Str
        @param LAC: LAC to expand conveyors
        @type LAC: Str
        @param window: GUI window 
        @type window: Class Window
    """
    try:
        with open(path) as jfile:
            f = json.load(jfile)
            convs = []
            for conv in f[LAC].keys():
                convs.append(conv)
            update_values_stuff(['-PARSED CONVEYOR SELECT SEARCHABLE-'],convs,window)
    except Exception as e:
        window['-SEARCHABLE OUTPUT-'].print(e)

def searchable_display(path,LAC,conveyor,window,values):
    """ Display the selected conveyor/all conveyor data in the searchable tab

        @param path: Path to .json file
        @type path: Str
        @param LAC: LAC to expand conveyors
        @type LAC: Str
        @param conveyor: Conveyor to expand information
        @type conveyor: Str
        @param window: GUI window 
        @type window: Class Window
    """
    try:
        with open(path) as jfile:
            if values['-ALL CONV CB-']:
                f = json.load(jfile)[LAC]
                for conv in f.keys():
                    del f[conv]['load_identity']
                    window['-SEARCHABLE OUTPUT-'].print(conv+json.dumps(f[conv], indent = 4).replace('"','').replace('\\',''))
            else:
                f = json.load(jfile)[LAC][conveyor]
                del f['load_identity']
                window['-SEARCHABLE OUTPUT-'].print(conveyor+json.dumps(f, indent = 4).replace('"','').replace('\\',''))
    except Exception as e:
        print(e)


def expandable_display(path,depth,window,expanded_keys,target = [None]):
    """ Display clickable options to explore parsed .json file, returns all keys currently expanded

        @param path: Path to .json file
        @type path: Str
        @param depth: Depth of expansion of the option tree (Can be 0 for LAC lever or 1 for conveyor and parameters)
        @type depth: Int
        @param window: GUI window 
        @type window: Class Window
        @param expanded_keys: Keys currently expanded in the tree
        @type expanded_keys: List[Str]
        @param target: Target to expand on click (defaults to [None])
        @type target: Str
    """
    try:
        if target[0] in expanded_keys and target[0] is not None:
            expanded_keys.remove(target[0])
            expandable_display(path,depth,window,expanded_keys)
            expanded_keys.remove(None)
            return expanded_keys
        with open(path) as jfile:
            expanded_keys.append(target[0])
            f = json.load(jfile)
            if depth == 0:
                update_values_stuff(['-EXPANDABLE OUTPUT-'],[lac for lac in f.keys()],window)       
            elif depth == 1:
                vals = []
                for lac in f.keys():
                    vals.append(lac)
                    if target[0] in f[lac].keys() or lac in expanded_keys:
                        for conv in f[lac].keys():
                            vals.append('       ->' + conv)
                            if '       ->' + conv == target[0] or conv in [key.strip().strip('->') for key in expanded_keys if key is not None]:
                                del f[lac][conv]['load_identity']
                                for key in f[lac][conv].keys():
                                    if 'Conveyor' in key:
                                        vals.append('                ->' + key + ' : ' +str(f[lac][conv][key]))
                                    else:
                                        try:
                                            if str(type(f[lac][conv][key][0])) == "<class 'list'>":
                                                vals.append('                ->' + key + ' : ' +str(f[lac][conv][key][0][0]))
                                                for thing in f[lac][conv][key][0][1:]:
                                                    vals.append('                                               '+ str(thing))
                                                    continue
                                            else:
                                                vals.append('                ->' + key + ' : ' +str(f[lac][conv][key][0]))
                                            for item in f[lac][conv][key][1:]:
                                                if str(type(item)) == "<class 'list'>":
                                                    for thing in item:
                                                        vals.append('                                               '+ str(thing))
                                                else:
                                                    vals.append('                                               '+ str(item))
                                        except Exception as e:
                                            print(e)
                                            vals.append('                ->' + key + ' : ' +str(f[lac][conv][key]))
                               
                update_values_stuff(['-EXPANDABLE OUTPUT-'],vals,window)
        return expanded_keys #TODO add side scrolling for expandable output
    except Exception as e:
        print(e)

def kw_display(path, window,kw_select):
    """ Load .json file and fully display with or without the selected keywords

        @param path: Path to .json file
        @type path: Str
        @param window: GUI window 
        @type window: Class Window
        @param kw_select: True for displaying conveyors containing at least one not empty keyword, 
                          False for displaying conveyors with all empty keywords
        @type kw_select:Bool
    """
    key_flg = False
    try:
        with open(path) as jfile:
            f = json.load(jfile)
            for lac in copy.deepcopy(f).keys():
                for conv in  copy.deepcopy(f)[lac]:
                    del f[lac][conv]['load_identity']
                    copy_for_keys = copy.deepcopy(f)
                    del copy_for_keys[lac][conv]['Conveyor_model']
                    for key in copy_for_keys[lac][conv].keys():
                        if f[lac][conv][key] != '':
                            if kw_select:
                                key_flg = True
                            else:
                                key_flg = False
                            break
                        elif f[lac][conv][key] == '' and not kw_select:
                            key_flg = True
                    if not key_flg:
                        del f[lac][conv]
                    key_flg = False

            window['-FULL OUTPUT-'].print(json.dumps(f, indent = 4).replace('"','').replace('\\',''))
    except Exception as e:
        window['-FULL OUTPUT-'].print(e)

def export_selected(file_path,file_name,save_path):
    """ Export selected file to .txt 

        @param file_path: Path to parsed .json
        @type file_path: Str
        @param file_name: Name for the file to be saved as
        @type file_name: Str
        @param save_path: path to save the .txt file to
        @type save_path: Str
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 12)
    os.makedirs(save_path+'/Exported', exist_ok = True)
    with open(file_path) as jfile:
        with open(save_path+'/Exported/'+file_name+'.txt','w') as w:
            f = json.load(jfile)
            for lac in copy.deepcopy(f).keys():
                for conv in  copy.deepcopy(f)[lac]:
                    del f[lac][conv]['load_identity']
            w.write(json.dumps(f, indent = 4).replace('"','').replace('\\',''))
    os.makedirs(save_path+'/Exported/PDF', exist_ok = True)
    with open(save_path+'/Exported/'+file_name + '.txt','r') as r:
        for line in r:
            pdf.cell(0,5,txt = line, ln = 1, align = 'L')
        pdf.output(save_path + '/Exported/PDF/'+ file_name + '.pdf')


def export_all(audit_path,disp_list,save_path):
    """ Export all parsed files to .txt 

        @param audit_path: All paths to audited files
        @type audit_path: Dict
        @param save_path: ath to save the .txt files to
        @type save_path: Str

    """
    for f in  disp_list:
        export_selected(audit_path[str(f)],f,save_path)


def export_displayed(values,display,save_path):
    """ Export displayed files to .txt 

        @param value: Values to extract title and info from
        @type values: Values dict from PySimpleGUI
        @param display: Which display to take the data to export from
        @type display: Str
        @param save_path: Path to save the .txt files to
        @type save_path: Str
    """

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 12)
    output = values[display]
    if display == '-EXPANDABLE OUTPUT-':
        fselect = values['-PARSED FILE SELECT SEARCHABLE-']
        lacselect = values['-PARSED LAC SELECT SEARCHABLE-']
        convselect = values['-PARSED CONVEYOR SELECT SEARCHABLE-']
        if values['-ALL CONV CB-']:
            convselect = 'All'
        if not values['-MULTI SEARCH CB-']:
            file_name = (fselect+'['+lacselect+']'+'[' + convselect+']').replace(' ','').replace('\n','')
        else:
            file_name = 'MULTIPLE'
    else:
        file_name = values['-PARSED FILE SELECT-']+'_displayed'
    os.makedirs(save_path+'/Exported', exist_ok = True)
    with open(save_path+'/Exported/'+file_name + '.txt','w+') as w:
        w.write(output)
    os.makedirs(save_path+'/Exported/PDF', exist_ok = True)
    with open(save_path+'/Exported/'+file_name + '.txt','r') as r:
        for line in r:
            pdf.cell(0,5,txt = line, ln = 1, align = 'L')
        pdf.output(save_path + '/Exported/PDF/'+ file_name + '.pdf')

def extract_keys_load(path):
    """ Retrieve keys from file path for displaying

        @param path: Path to .json file
        @type path: Str
    """
    crude_keys=[]
    if isdir(path):
        crude_keys = path.split('/')[-1].split('-')
    else:
        crude_keys = path.split('/')[-1].split('[')[1].split(']')[0].split(',')
    if str(type(crude_keys)) == "<class 'str'>":
        keys = [str(crude_keys)]
    else:
        keys = [str(key) for key in crude_keys]
    return keys

def display_keys(keys,window):
    """ Display currently stored keys in full display window

        @param keys: Currently stored keys
        @type keys: List[Str]
        @param window: GUI window
        @type window: Class Window
    """
    for key in keys:
        window['-KEYS DISPLAY-'].print(key)

def clear_stuff(stuff,window):
    """ Clear list of objects from the screen, used to reduce clutter

        @param stuff: Objects to clear
        @type stuff: List[Str]
        @param window: GUI window 
        @type window: Class Window
    """
    for thing in stuff:
        window[thing].update('')

def enable_stuff(stuff, window):
    """ Enable list of objects from the screen, used to reduce clutter

        @param stuff: Objects to enable
        @type stuff: List[Str]
        @param window: GUI window 
        @type window: Class Window
    """
    for thing in stuff:
        window[thing].update(disabled = False)

def disable_stuff(stuff, window):
    """ Disable list of objects from the screen, used to reduce clutter

        @param stuff: Objects to disable
        @type stuff: List[Str]
        @param window: GUI window 
        @type window: Class Window
    """
    for thing in stuff:
        window[thing].update(disabled = True)

def update_values_stuff(stuff,values,window):
    """ Update list of objects from the screen to given values, used to reduce clutter

        @param stuff: Objects to update
        @type stuff: List[Str]
        @param values: Values to update in the objects
        @type values: List[Str]
        @param window: GUI window 
        @type window: Class Window
    """
    for thing in stuff:
        window[thing].update(values = values)

def remove_duplicates(lst):
    """ Remove duplicates from a list and returns it

        @param lst: List to clean
        @type lst: List

    """
    return list(dict.fromkeys(lst))

def set_cursor(stuff, cursor, window):
    """ Set cursor for list of objects, used to reduce clutter

        @param stuff: Objects to set
        @type stuff: List[Str]
        @param cursor: Cursor type 
        @type cursor: Str
        @param window: GUI window 
        @type window: Class Window
    """
    for thing in stuff:
        window[thing].set_cursor(cursor= cursor)
#IX_ResetESM QX_TrspStopped QX_TORdy