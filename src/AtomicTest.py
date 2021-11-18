from src.Helper import Helper
from src.Event import Event
from src.Logger import Logger
from src.Executor import Executor
from src.TestContainer import TestContainer
import argparse
import re
import csv


class AtomicTest(object):

    def __init__(self) -> None:
        # System and execution properties
        self.log_file = "logs/AtomicTest.log"
        self.exclude_tests_file = "config/excluded_tests.csv"
        self.mitre_coverage_tests_file = "config/mitre_coverage.csv"
        self.official_tests_path = "tests/official/"
        self.custom_tests_path = "tests/custom/"
        self.atomic_test_official_repo = "https://github.com/redcanaryco/atomic-red-team/"
        self.test_container = None
        self.executor = None
        self.logger = Logger()

        # Print the header
        Helper.print_header()

        # Parser for commandline arguments
        self.parser = argparse.ArgumentParser(prog="OCD Atomic Test Framework")
        self.populate_parser_arguments()
        self.parse_arguments()
        return

    def populate_parser_arguments(self) -> None:
        # Setup argument for initial setup and configuration
        self.parser.add_argument(
                "--setup",
                help="Setup the OCD Atomic Test Framework",
                action='store_true')

        # Install argument for installing/updating the official Atomic
        # Red Team test suite in the tests/official folder
        self.parser.add_argument(
                "--install",
                help="Installs/updates the official Atomic Tests",
                action='store_true')

        # Runtype argument to determine if provided test list CSV 
        # will include or exclude tests, or if tests are provided 
        # via command line parameter
        self.parser.add_argument(
                "--runtype",
                help="Specify the desired runtype where" +
                " 'manual' stands for running a string of manually " + 
                "supplied tests via the --test_list parameter" + 
                " 'include' stands for including the testlist specified " + 
                "via the --test_list parameter" + 
                " 'exclude' stands for excluding the testlist specified " + 
                "via the --test_list parameter",
                choices=["manual", "exclude", "include"],
                nargs=1)

        # Test_list argument supplies either a path to a CSV file 
        # with techniques to be handeled according to runtype, or 
        # a string with "," delimited test techniques, if runtype 
        # is manual
        self.parser.add_argument(
                "--test_list",
                help="Specify either a string with ',' delimited test techniques" + 
                ", or a CSV file containing techniques in every line",
                type=str,
                nargs=1)
        return

    def parse_arguments(self) -> None:
        args = self.parser.parse_args()
        # Setup argument
        if (args.setup):
            self.setup_framework()
        # Install argument
        elif (args.install):
            self.install_atomics()
        # Run tests
        elif (args.runtype is not None and args.test_list is not None):
            test_list = self.parse_test_list(args)
            self.run_tests()
        else:
            self.parser.print_help()
        return

    def setup_framework(self) -> None:
        # Install atomic tests from Github
        self.install_atomics()

        # Additional setup goes here
        # TODO

        return

    def install_atomics(self) -> None:
        # Download the latest version of the Atomic Test repo to tmp folder
        Event("Initiating download and extraction of atomic tests...")
        message, is_error = Helper.delete_directory(self.official_tests_path)
        if is_error:
            Event(message=message, is_error=is_error, exit=is_error)
        message, is_error = Helper.create_directory(self.official_tests_path)
        if is_error:
            Event(message=message, is_error=is_error, exit=is_error)

        at_repo_zip_url = self.atomic_test_official_repo + \
            "archive/refs/heads/master.zip"
        at_temp_folder = self.official_tests_path + "tmp"
        message, is_error = Helper.download_and_exstract_zip(at_repo_zip_url,
                at_temp_folder)
        Event(message=message, is_error=is_error, is_success=not is_error, exit=is_error)
        
        # Extract tests
        Event("Extracting attack techniques from the repository" + \
                " and deleting leftover files.")
        at_temp_folder_atomics = at_temp_folder + "/atomic-red-team-master/atomics/"
        message, is_error = Helper.replace_content_in_folder(at_temp_folder_atomics,
                self.official_tests_path)
        Event(message=message, is_error=is_error, is_success=not is_error, exit=is_error)
        # Remove tmp folder
        message, is_error = Helper.delete_directory(at_temp_folder)
        Event(message=message, is_error=is_error, is_success=not is_error, exit=is_error)

        # Load tests
        self.test_container = TestContainer(self.official_tests_path,
                                            self.custom_tests_path,
                                            self.exclude_tests_file)
        return

    def run_tests(self) -> None:
        # Load tests
        self.test_container = TestContainer(self.official_tests_path,
                                            self.custom_tests_path,
                                            self.exclude_tests_file)
        techniques = self.test_container.get_techniques()

        # Initiate the Executor
        self.executor = Executor(self.test_container.exclude_guids_list,
                                 self.logger)
        for technique in techniques:
            self.executor.run_technique(techniques[technique])
        return

    def parse_test_list(self, args) -> list:
        arg_test_list = args.test_list[0]
        parsed_test_list = []

        # If a csv file was supplied, load technique IDs from file
        test_list_is_csv = Helper.check_string_is_csv(arg_test_list) 
        if (test_list_is_csv):
            csv_exists = Helper.check_file_existing(arg_test_list)
            if (csv_exists):
                parsed_test_list = Helper.load_technique_ids_from_csv(arg_test_list)
            else:
                message = "supplied CSV file does not exist: " + arg_test_list
                Event(message=message, is_error=True, exit=True)
        # When there is no csv file, parse "," delimited tests from parameter
        else:
            parsed_test_list = Helper.parse_technique_ids_from_string(arg_test_list)
            if parsed_test_list == []: 
                message = "could not parse any technique IDs from input: " + arg_test_list
                event = Event(message=message, is_error=True, exit=True)
        return parsed_test_list


if __name__=='__main__':
    tester = AtomicTest()


