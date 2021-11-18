import platform 
import ctypes
import re
import csv
import os
import typing
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import shutil
from src.Event import Event
import yaml

class Helper(object):

    @staticmethod
    def determine_os() -> str:
        return platform.system().lower()

    @staticmethod
    def print_header() -> None:
        print(r"------------------------------------------------")
        print(r"|    / _ \ / ___|  _ \                         |")  
        print(r"|   | | | | |   | | | |     Atomic Testing     |")
        print(r"|   | |_| | |___| |_| |     Framework          |")
        print(r"|    \___/ \____|____/                         |") 
        print(r"------------------------------------------------")

    @staticmethod
    def check_file_existing(filename) -> bool:
        file_existing = os.path.isfile(filename)
        return file_existing

    @staticmethod
    def check_string_is_csv(arg) -> bool:
        string_is_csv = bool(re.match(r".*\.csv", arg))
        return string_is_csv

    @staticmethod
    def load_technique_ids_from_csv(filename) -> list:
        test_list = []
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            first_line = True
            for row in csv_reader:
                if first_line:
                    if (len(row) > 1):
                        # Wrong format, return empty
                        return []
                    first_line = False 
                else:
                    technique = row[0]
                    if (Helper.check_technique_convention(technique)):
                        test_list.append(technique)
        return test_list 

    @staticmethod
    def check_technique_convention(string) -> bool:
        return bool(re.match(r"T\d{4}(\.\d{3})?", string))

    @staticmethod
    def check_guid_convention(string) -> bool:
        return bool(re.match(r"[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-" + \
                "[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}", string))

    @staticmethod
    def load_guids_from_csv(filename) -> list:
        guid_list = []
        first_line = True
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            for row in csv_reader:
                if first_line:
                    if (len(row) > 2):
                        # Wrong format, return empty
                        return []
                    first_line = False 
                else:
                    try:
                        guid = row[0]
                        comment = row[1]
                    except Exception as e:
                        return []
                    if (Helper.check_guid_convention(guid)):
                        guid_list.append([guid, comment])
        return guid_list

    @staticmethod
    def parse_technique_ids_from_string(arg) -> list:
        split_list = arg.replace(" ", "").split(",")
        for technique in split_list:
            if (not Helper.check_technique_convention(technique)) \
                    or len(technique) > 9:
                # Wrong format, return empty
                return []
        return split_list

    @staticmethod
    def delete_directory(path) -> typing.Tuple[str, bool]:
        if os.path.isdir(path):
            # Try to delete a directory
            try:
                shutil.rmtree(path, ignore_errors=True)
            except Exception as e:
                return "Deletion of directory " + path + " failed: " + str(e), True
            else:
                return "Successfully deleted directory", False

    @staticmethod
    def create_directory(path, empty_if_exists=False) -> typing.Tuple[str, bool]:
        # Check if is already exists
        if os.path.isdir(path):
            if empty_if_exists:
                message, is_error = Helper.delete_directory(path)
                if is_error:
                    return message, is_error
            else:
                return "Directory already exists", False
        # Try to create a directory
        try:
            os.mkdir(path)
        except OSError:
            return "Creation of directory " + path + " failed.", True
        else:
            return "Successfully created directory", False

    @staticmethod
    def download_and_exstract_zip(url, path) -> typing.Tuple[str, bool]:
        # Create destination directory
        message, is_error = Helper.create_directory(path, empty_if_exists=True)
        if is_error:
            return message, is_error

        # Download and exstract zip to path
        try:
            with urlopen(url) as zipresp:
                with ZipFile(BytesIO(zipresp.read())) as zfile:
                    zfile.extractall(path)
        except Exception as e:        
            return "Download and exstraction went wrong: " + str(e), True
        else: 
            return "Download and exstraction successful!", False

    @staticmethod
    def replace_content_in_folder(src_folder, dst_folder) -> typing.Tuple[str, bool]:
        # Get all files in source folder
        files = Helper.get_files_in_folder(src_folder) 
        try: 
            for f in files:
                shutil.move(os.path.join(src_folder, f),
                            os.path.join(dst_folder, f))
        except Exception as e:
            return "Replacing content in folder went wrong: " + str(e), True
        else:
            return "Replacing content in folder was sucessful!", False

    @staticmethod
    def get_files_in_folder(path) -> list:
        # Get all files in path
        try: 
            files = os.listdir(path)
        except Exception as e:
            message = "Getting files from folder went wrong: " + path
            Event(message=message, is_error=True, exit=True)
        else:
            return files

    @staticmethod
    def create_technique_yaml_paths(path, technique_list) -> dict:
        yaml_file_paths = {}
        for technique in technique_list:
            yaml_file_paths[technique] = os.path.join(path, technique, technique + ".yaml")
        return yaml_file_paths

    @staticmethod
    def load_yaml_test(filename) -> dict:
        test = {}
        try:
            with open(filename) as yaml_test:
                test = yaml.load(yaml_test, Loader=yaml.FullLoader)
        except Exception as e:
            message = "Loading test from YAML file went wrong: " + filename + \
                    "\n" + str(e)
            Event(message=message, is_error=True, exit=True)
        return test

    @staticmethod
    def determine_privilege() -> bool:
        system = Helper.determine_os()
        if (system == "linux" or system == "mac"):
            return os.getuid() == 0
        else:
            return ctypes.windll.shell32.IsUserAnAdmin()
            



