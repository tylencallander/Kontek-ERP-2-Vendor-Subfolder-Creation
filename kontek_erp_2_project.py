# I was going to use pylnk, but I had some issues resolving .lnk files with it to find the alt names, so I used subprocess instead so I could use powershell

import os
import json
import subprocess

# Returns a list of relative paths to all the directories within the given root path.

def list_folder_structure(root_path):
    structure = []
    for dirpath, dirnames, _ in os.walk(root_path):
        for dirname in dirnames:
            path = os.path.join(dirpath, dirname)
            structure.append(os.path.relpath(path, start=root_path))
    return structure

# Resolves .lnk files in a vendor directory to collect and report unique alternate names recursively.

def get_alternate_names(vendor_path, vendor_name, visited=None):
    if visited is None:
        visited = set()  

    alternates = set()  
    for item in os.listdir(vendor_path):
        item_path = os.path.join(vendor_path, item)
        if item_path.lower().endswith('.lnk') and item_path not in visited:
            visited.add(item_path)
            target_path = resolve_lnk(item_path)
            if target_path:
                alternate_name = os.path.basename(os.path.normpath(target_path))
                alternates.add(alternate_name)
                print(f"Resolved .lnk for vendor '{vendor_name}': links to '{alternate_name}' at '{target_path}'")
                if os.path.isdir(target_path):
                    alternates.update(get_alternate_names(target_path, alternate_name, visited))
            else:
                print(f"Failed to resolve .lnk file '{item}' in vendor '{vendor_name}' directory")
    return list(alternates) 

def resolve_lnk(lnk_path):
    command = f'powershell "$link = (New-Object -COM WScript.Shell).CreateShortcut(\'{lnk_path}\'); $link.TargetPath"'
    try:
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        return output.strip()
    except subprocess.CalledProcessError as e:
        print(f"Failed to resolve .lnk file: {e.output}")
        return None

def main():
    template_path = 'P:\\VENDORS\\__TEMPLATE FOLDER (DO NOT DELETE)'
    vendors_path = 'P:\\VENDORS'
    
    template_structure = set(list_folder_structure(template_path))
    errors = {}
    vendors = {}

# Logging all missing directories and alternate names

    for letter_folder in os.listdir(vendors_path):
        letter_folder_path = os.path.join(vendors_path, letter_folder)
        if os.path.isdir(letter_folder_path) and letter_folder != '__TEMPLATE FOLDER (DO NOT DELETE)':
            for vendor_folder in os.listdir(letter_folder_path):
                vendor_folder_path = os.path.join(letter_folder_path, vendor_folder)
                if os.path.isdir(vendor_folder_path):
                    vendor_structure = set(list_folder_structure(vendor_folder_path))
                    missing_folders = template_structure - vendor_structure
                    alternates = get_alternate_names(vendor_folder_path, vendor_folder)

                    vendor_info = {
                        "vendorfullpath": vendor_folder_path,
                        "vendorname": vendor_folder,
                        "vendorpath": vendor_folder_path.split(os.sep),
                        "alternatenames": alternates
                    }

                    if missing_folders:
                        errors[vendor_folder] = list(missing_folders)
                    
                    vendors[vendor_folder] = vendor_info

# Filling the Json files with the collected vendor data and errors, and a print statement so I can count them.

    if errors:
        with open('errors.json', 'w') as f:
            json.dump(errors, f, indent=4)

    with open('vendor.json', 'w') as f:
        json.dump(vendors, f, indent=4)

    print(f"Total vendors logged: {len(vendors)}")
    print(f"Total errors logged: {len(errors)}")

if __name__ == "__main__":
    main()
