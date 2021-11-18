from src.Helper import Helper
import typing
from src.Event import Event
import subprocess


class Executor(object):

    def __init__(self, excluded_tests, logger=None) -> None:
        # Initiate system properties for precondition checks
        self.preconditions = {}
        self.preconditions["os"] = Helper.determine_os()
        self.preconditions["elevation"] =  Helper.determine_privilege()
        self.preconditions["excluded_tests"] = excluded_tests
        supported_executors = [
            "sh",
            "bash",
            "command_prompt",
            "powershell"
        ]
        self.preconditions["supported_executors"] = supported_executors
        self.logger = logger

    def run_atomic(self, atomic) -> None:
        # Runs an atomic test on the system
        atomic_name = atomic["name"]
        atomic_guid = atomic["auto_generated_guid"]
        atomic_description = atomic["description"]
        atomic_platforms = atomic["supported_platforms"]
        atomic_executor = atomic["executor"]
        atomic_dependencies = {}
        try:
            atomic_input_arguments = atomic["input_arguments"]
        except Exception as e:
            atomic_input_arguments = []
        try:
            atomic_dependencies["executor"] = atomic["dependency_executor_name"]
        except Exception as e:
            atomic_dependencies["executor"] = []
        try:
            atomic_dependencies["dependencies"] = atomic["dependencies"]
        except Exception as e:
            atomic_dependencies["dependencies"] = []

        # Check preconditions
        atomic_can_be_executed, status = self.check_preconditions(atomic_guid,
                                                        atomic_platforms,
                                                        atomic_executor,
                                                        atomic_dependencies["executor"])

        # Execute dependencies
        atomic_can_be_executed, status = self.execute_dependencies(atomic_dependencies,
                                                                  atomic_input_arguments)

        # Execute atomic test
        if atomic_can_be_executed:
            # Execute the atomic
            command = self.replace_input_placeholders(atomic_executor["command"],
                                                      atomic_input_arguments)
            success = self.execute_command(command, atomic_executor["name"])

        # Log to Splunk according to execution results
        # TODO
        if not atomic_can_be_executed:
            Event(status, is_error=True)
        else:
            message = "Executed atomic: " + atomic_name + ", GUID: " + atomic_guid
            Event(message, is_success=True)

        # Cleanup with another Splunk log
        # TODO

    def execute_dependencies(self, dependencies, input_args) -> typing.Tuple[bool, str]:
        # Runs and confirms dependencies for a given atomic
        # If no dependencies are listed, we are done
        if dependencies["executor"] == [] or \
           dependencies["dependencies"] == []:
            return True, ""
        status = dependencies["dependencies"]["description"]
        # Otherwise, the prereq get command is executed
        if "get_prereq_command" in dependencies["dependencies"].keys():
            command = dependencies["dependencies"]["get_prereq_command"]
            command = self.replace_input_placeholders(command, input_args)
            success_get =  self.execute_command(command, dependencies["executor"])
        # Confirm successful prereq get command
        if "prereq_command" in dependencies["dependencies"].keys():
            command = dependencies["dependencies"]["prereq_command"]
            command = self.replace_input_placeholders(command, input_args)
            success = self.execute_command(command, dependencies["executor"])
        return success, status

    def replace_input_placeholders(self, command, input_args) -> str:
        # Replaces all placeholders with supplied input arguments
        placeholders = input_args.keys()
        print(placeholders)
        for placeholder in placeholders:
            print(placeholder)
            value = str(input_args[placeholder]["default"])
            print(value)
            placeholder = "#{" + placeholder + "}"
            print(placeholder)
            command = command.replace(placeholder, value)
            command = command.replace("\n", "")
        return command

    def execute_command(self, command, executor) -> bool:
        # Creates a process according to the executor with the supplied command
        if executor == "sh":
            returncode = subprocess.run(["sh", "-c", command])
        elif executor == "bash":
            returncode = subprocess.run(["bash", "-c", command])
        elif executor == "powershell":
            returncode = subprocess.run(["powershell", "-Command", command])
        elif executor == "command_prompt":
            returncode = subprocess.run([command])
        return returncode == 0

    def run_technique(self, technique) -> None:
        # Runs all the atomics for a given technique
        for atomic in technique["atomic_tests"]:
            self.run_atomic(atomic)

    def check_preconditions(self, guid,platforms, executor,
                            dependent_executor) -> typing.Tuple[bool, str]:
        # Checks if preconditions of the atomic are fulfilled
        status = "Yesterday was a good day :)"
        can_be_run = self.preconditions["os"] in platforms
        if not can_be_run:
            status = "Required operating system not present"
            return can_be_run, status
        can_be_run = not (guid in self.preconditions["excluded_tests"])
        if not can_be_run:
            status = "Test is excluded by config"
            return can_be_run, status
        can_be_run = executor["name"] in self.preconditions["supported_executors"]
        if dependent_executor != []:
            can_be_run = dependent_executor in self.preconditions["supported_executors"]
        if not can_be_run: status = "Required executor is not present"
        return can_be_run, status


