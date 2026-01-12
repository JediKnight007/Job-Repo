#########################################
# DO NOT MODIFY ANYTHING IN THIS FILE
#########################################

import os

# DO NOT CHANGE THE VALUES OF THESE CONSTANTS
EXPECTED_CWDS = {"sol", "test"}
DISK_PATH = "disk"

def _is_safe_path(file_path: os.DirEntry[str] | str):
    try:
        working_path = os.getcwd()
        working_dir = working_path.split(os.sep)[-1]
        if isinstance(file_path, os.DirEntry):
            file_path = file_path.path
        file_path_dir = file_path.split(os.sep)[-2]
        return working_dir in EXPECTED_CWDS and file_path_dir == DISK_PATH
    except:
        return False

def remove_file(file_path: os.DirEntry[str] | str):
    '''
    Removes a file from the disk directory.
    If the file is not in the DISK_PATH subdirectory of the EXPECTED_CWD directory, a FileNotFoundError is raised.

    Parameters:
    file_path (str): The path to the file to be removed
    '''
    if _is_safe_path(file_path):
        os.remove(file_path)
    else:
        raise FileNotFoundError(f"Files cannot be removed outside of disk directory: {file_path}")
    
def rename_file(old_path: os.DirEntry[str] | str, new_path: os.DirEntry[str] | str):
    '''
    Renames a file in the disk directory.
    If the file is not in the DISK_PATH subdirectory of the EXPECTED_CWD directory, a FileNotFoundError is raised.

    Parameters:
    old_path (str): The path to the file to be renamed
    new_path (str): The new path for the file
    '''
    if _is_safe_path(old_path) and _is_safe_path(new_path):
        os.replace(old_path, new_path)
    else:
        raise FileNotFoundError(f"Files cannot be replaced outside of disk directory: {old_path}")
  