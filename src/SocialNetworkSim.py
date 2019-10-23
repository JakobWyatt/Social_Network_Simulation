"""
This file is the top level file to be executed by a user of this program.
It uses the python argparse module to process command line arguments,
and delegates the programs execution to either py:class::SocialNetworkInteractive.interactive
or py:class::SocialNetworkSimRunner.SocialNetworkSimRunner.SimulationInterface

Use of this module has been approved by Ben, my DSA Tutor.
"""


import argparse
import sys

from SocialNetworkInteractive import interactive
from SocialNetworkSimRunner import SocialNetworkSimRunner

def make_parser():
    parser = argparse.ArgumentParser(description="Simulate Social Networks.",
                                     add_help=False, prefix_chars='\0')
    subparsers = parser.add_subparsers(dest="mode")

    simulation_parser = subparsers.add_parser("-s", add_help=False,
                                              help="Run in simulation mode")
    interactive_parser = subparsers.add_parser("-i", add_help=False,
                                               help="Run in interactive mode")

    simulation_parser.add_argument('netfile', type=argparse.FileType('r'),
                                   help='File that describes the initial network')
    simulation_parser.add_argument('eventfile', type=argparse.FileType('r'),
                                   help='File that lists all events on the network')
    simulation_parser.add_argument('prob_like', type=float,
                                   help='Probability of liking a post')
    simulation_parser.add_argument('prob_foll', type=float,
                                   help='Probability of following the original poster of a liked post')
    return parser, interactive_parser, simulation_parser


if __name__ == "__main__":
    parser, interactive_parser, simulation_parser = make_parser()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        interactive_parser.print_help(sys.stderr)
        simulation_parser.print_help(sys.stderr)
    else:
        args = parser.parse_args()
        if args.mode == "-i":
            try:
                interactive().cmdloop()
            except KeyboardInterrupt:
                print("")
        elif args.mode == "-s":
            SocialNetworkSimRunner.SimulationInterface(args.netfile, args.eventfile, args.prob_like, args.prob_foll)
