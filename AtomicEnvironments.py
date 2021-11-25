import argparse
import re
import csv
from src.Helper import Helper


class AtomicEnvironments(object):

    def __init__(self) -> None:
        # System and execution properties
        self.log_file = "logs/AtomicEnvironments.log"
        self.atomic_envs_path = "atomic_envs/"
        self.envs_container = None
        self.executor = None

        # Print the header
        Helper.print_header()

        # Parser for commandline arguments
        self.parser = argparse.ArgumentParser(prog="AtomicEnvironments.py")
        self.populate_parser_arguments()
        self.parse_arguments()
        return

    def populate_parser_arguments(self) -> None:
        # Setup argument for initial setup and configuration
        # May be replaced by a setup bash script
        self.parser.add_argument(
                "--setup",
                help="Setup the Atomic Environments Framework",
                action='store_true')

        # The agent argument will determine which agent class to 
        # choose from
        self.parser.add_argument(
                "--agent",
                help="Specify the desired agent where" +
                " 'classic' stands for the tensorfoce Q-Learning " + 
                "agent." + 
                " 'dql' stands for the tensorfoce Deep-Q-Learning " + 
                "agent." + 
                " 'ddql' stands for the tensorfoce Double-Deep-Q-Learning " + 
                "agent." + 
                " 'random' stands for the reference " + 
                "agent, which chooses actions at random",
                choices=["classic", "dql", "ddql", "random"],
                nargs=1)
        
        # The technique argument will determine the technique ID
        # for which an environment will be created
        self.parser.add_argument(
                "--technique",
                help="Specify a technique ID" + 
                ", which has to be defined in a JSON file in the " + 
                self.atomic_envs_path + " folder, for defining" +
                "the desired reinforcement learning environment",
                type=str,
                nargs=1)

    def parse_arguments(self) -> None:
        args = self.parser.parse_args()
        # Setup argument
        if (args.setup):
            self.setup_framework()
        # Install argument
        elif (args.agent is not None and args.technique is not None):
            # TODO
            pass
        else:
            self.parser.print_help()

    def setup_framework(self) -> None:
        # TODO
        return


if __name__=='__main__':
    atomic_environments = AtomicEnvironments()


