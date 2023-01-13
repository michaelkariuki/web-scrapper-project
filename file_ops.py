# IMPORTS
import re
import json
import os
import time
import traceback
import io

link_source_file = 'rudolf steiner links.txt'

def read_file(file_name):
    with open(file_name) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

    return lines


def openJsonFile(file) -> any:
    with open(file) as json_file:
        data = json.load(json_file)

    return data

def filter_(list):
    result = []
    filtered = [item for item in list if '[' in item and ']' in item]
    
    for item in filtered:
        result.append(convert_(re.sub(',$', '', item)))

    return result

def convert_(str) -> list:
    return json.loads(str)
   
def convert_to_dict(key: str, value: any) -> dict:
    return {key: value}

def filterPdfs(list) -> list:
    return [item[0] for item in list if '.pdf' in item[-1]]

def filterPdfLinks(list) -> dict:
    return {item[0]: item[-1] for item in list if '.pdf' in item[-1]}

def filterBooks(list) -> list:
    return [item[0] for item in list if 'books' in item[-1].lower()]

def filterWorks(list) -> list:
    return [item[0] for item in list]

def filterLectures(list) -> list:
    return [item[0] for item in list if 'lectures' in item[-1].lower()]

def filterFilenames(data) -> list:
    pdf_dict = filterPdfLinks(data)
    pdf_links_list = list(pdf_dict.values())
    res = [extract_filename(url_link) for url_link in pdf_links_list]

    return res

def convert_to_json(obj: dict) -> json:
    return json.dumps(obj, indent= 3)

def convertAllToDict(data: list) -> dict:
    result = {}
    struct = {
        'Books' : filterBooks,
        'Letures' : filterLectures,
        'Pdfs' : filterPdfs,
        'PdfLinks' : filterPdfLinks,
        'Pdf_Filenames' : filterFilenames,
        'All' : filterWorks
    }

    for key in struct.keys():
        result[key] = struct[key](data)

    return result

def write_to_json_file(json_Obj: json, filename: str):
    try:
        with open(filename+'.json', 'w') as outfile:
            outfile.write(json_Obj)
    except IOError as e:
        print("Error : ", e.message, e.args)
    except:
        print("Error Occured")
        print(traceback.format_exc())
    else:
        # print('File created successfully!')
        print(f'File : {filename} created successfully!')



def check_file(file_path: str):
    while not os.path.exists(file_path):
        time.sleep(1)

    if not os.path.isfile(file_path):
        raise ValueError("file does not exist" % file_path)

def extract_filename(str):
    pattern = r'([\w\s\']+\.pdf)'
    match = re.search(pattern, str)

    return match.group(0) if match else None

def get_files_n_dirs(folder_path: str) -> list:
    files_and_directories = []

    if os.path.exists(folder_path) and not os.path.isfile(folder_path):
        # Use the os.listdir() function to get a list of the names of the files and directories in the folder
        files_and_directories = os.listdir(folder_path)

    return files_and_directories

def sort_files_n_dirs(folder_path: str) -> dict:
    res_list = get_files_n_dirs(folder_path)
    res_dict = {
        'files' : [],
        'folders' : []
    }

    for item in res_list:
        if os.path.isfile(os.path.join(folder_path, item)):
            res_dict['files'].append(item)
        else:
            res_dict['folders'].append(item)

    return res_dict

def write_str_to_file(content: str, file_path: str):
    obj = io.StringIO(content)
    try:
        with open(file_path, 'w') as f:
            f.write(obj.read())
    except IOError:
        traceback.format_exc()

def write_bin_to_file(content: any, file_path: str):
    try:
        with open(file_path, 'wb') as f:
            f.write(content.read())
    except IOError:
        traceback.format_exc()