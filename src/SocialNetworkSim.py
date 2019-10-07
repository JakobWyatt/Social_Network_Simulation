import argparse
import sys

def interactive():
    print("Interactive")

def simulation():
    print("Simulation")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate Social Networks.",
                                     add_help=False, prefix_chars='\0')
    subparsers = parser.add_subparsers()

    simulation_parser = subparsers.add_parser("-s", help="Run in simulation mode", add_help=False)
    interactive_parser = subparsers.add_parser("-i", help="Run in interactive mode", add_help=False)

    simulation_parser.add_argument('netfile', type=argparse.FileType('r'),
                                   help='File that describes the initial network')
    simulation_parser.add_argument('eventfile', type=argparse.FileType('r'),
                                   help='File that lists all events on the network')
    simulation_parser.add_argument('prob_like', type=float, help='Probability of liking a post')
    simulation_parser.add_argument('prob_foll', type=float,
                                   help='Probability of following the original poster of a liked post')

    parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        interactive_parser.print_help(sys.stderr)
        simulation_parser.print_help(sys.stderr)
