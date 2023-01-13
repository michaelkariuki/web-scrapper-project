#Objectives
# Read the text file ✔
# filter out the info with the book name and link ✔
# get book names ✔
# write book data to a json (txt) file ✔
# store bulk data to a json ✔

# IMPORTS
from file_ops import *
from web_ops import *
from g_drive_ops import *

link_source_file = 'rudolf steiner links.txt'
base_url = 'https://steinerlibrary.org/'
data_file = 'RudolfSteinerData.json'
download_loc = os.path.join(os.getcwd(), 'downloads')
upload_folder = os.path.join(os.getcwd(), 'upload_sandbox')
upload_files = sort_files_n_dirs(download_loc)['files']

def main():
# file operations ************************************************************

    data = filter_(read_file(link_source_file))
    dict_ = convertAllToDict(data)    
    bulk_dict = convert_to_dict('bulk_data', data)
    dict_.update(bulk_dict)

    if openJsonFile(data_file) == dict_:
        print(f"{data_file} up to date...")
    else:
        write_to_json_file(convert_to_json(dict_),'RudolfSteinerData')

# Web operations ************************************************************
    driver = set_up_driver()

    for i, key in enumerate(dict_['PdfLinks'].keys()):
        file_path = os.path.join(download_loc, dict_['Pdf_Filenames'][i])

        if not os.path.exists(file_path):
            download_file(driver, key, dict_['PdfLinks'][key])
            check_file(file_path)
        else:
            print(f"{key} already exists...")
            
    close_driver(driver)

    print("file(s) downloaded successfully")

    os.system('cls')

# Google drive operations ************************************************************
    get_metadata()
    
    # folder = get_item_data('Atest')   
    # file = search_item('testing')['files'].pop()
    # print(file)
    # folder = get_item_data('Books')

    # for file_name in upload_files:
    #         print(f'\n{file_name} is being uploaded...')
    #         file_path = os.path.join(download_loc, file_name)
    #         if not bool(search_item(file_name)):
    #             upload_item(file_name, file_path, folder['id'])
    #         else:
    #             print(f"File : {file_name} already exists in gdrive...")


    # file = get_item_data('Untitled spreadsheet')
    # delete_item(file)

    # file = search_item('testing123')['files'].pop()
    file2 = search_item('IMG_20190809_153812')['files'].pop()
    path = os.path.join(os.getcwd(), file2['name'])

    # print(file, file2)
    read_item(file2, path)

if __name__ == '__main__':
    main() 