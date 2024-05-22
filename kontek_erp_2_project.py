import os
import json

def list_folder_structure(root_path):
    """ Recursively list the structure of the given directory. """
    structure = []
    for dirpath, dirnames, _ in os.walk(root_path):
        for dirname in dirnames:
            path = os.path.join(dirpath, dirname)
            structure.append(os.path.relpath(path, root_path))
    return structure

def get_alternate_names(vendor_path):
    """ Scan for shortcut links and assume they are alternate names. """
    alternates = []
    for item in os.listdir(vendor_path):
        item_path = os.path.join(vendor_path, item)
        if os.path.islink(item_path):  # Checks if it's a shortcut/link
            alternates.append(item)
    return alternates

def main():
    template_path = 'P:\\VENDORS\\__TEMPLATE FOLDER (DO NOT DELETE)'
    vendors_path = 'P:\\VENDORS'
    
    print(f"Listing folder structure for template at {template_path}")
    template_structure = set(list_folder_structure(template_path))
    
    errors = {}
    vendors = []

    for letter_folder in os.listdir(vendors_path):
        letter_folder_path = os.path.join(vendors_path, letter_folder)
        if os.path.isdir(letter_folder_path) and letter_folder != '__TEMPLATE FOLDER (DO NOT DELETE)':
            for vendor_folder in os.listdir(letter_folder_path):
                vendor_folder_path = os.path.join(letter_folder_path, vendor_folder)
                if os.path.isdir(vendor_folder_path):
                    print(f"Checking folder structure for vendor: {vendor_folder}")
                    vendor_structure = set(list_folder_structure(vendor_folder_path))
                    missing_folders = template_structure - vendor_structure
                    if missing_folders:
                        print(f"Missing folders for {vendor_folder}: {missing_folders}")
                        errors[vendor_folder] = list(missing_folders)
                    
                    alternates = get_alternate_names(vendor_folder_path)
                    vendors.append({
                        "vendorfullpath": vendor_folder_path,
                        "vendorname": vendor_folder,
                        "vendorpath": os.path.normpath(vendor_folder_path).split(os.sep),
                        "alternatenames": alternates
                    })

    if errors:
        print("Writing errors to errors.json")
        with open('errors.json', 'w') as f:
            json.dump(errors, f, indent=4)
    else:
        print("No errors found.")
        
    print("Writing vendor list to vendor.json")
    with open('vendor.json', 'w') as f:
        json.dump(vendors, f, indent=4)

    print(f"Total vendors logged: {len(vendors)}")
    print(f"Total errors logged: {len(errors)}")

if __name__ == "__main__":
    main()
