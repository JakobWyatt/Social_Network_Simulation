# Command line arguments
import argparse
import sys
# Interactive menu
import cmd
import readline


class interactive(cmd.Cmd):
    intro = "Type help or ? to list commands.\n"
    prompt = "(social-sim) "

    def do_load(self, arg):
        'Load a social network: load <netfile>'
        print(arg)

    def do_find_user(self, arg):
        'Find a user and display their posts, followers, and following: find_user <name>'
        print(arg)

    def do_add_user(self, arg):
        'Add a user: add_user <name>'
        print(arg)

    def do_remove_user(self, arg):
        'Remove a user: remove_user <name>'
        print(arg)

    def do_like(self, arg):
        'Like a post: like <user>:<post_id>'
        print(arg)

    def do_unlike(self, arg):
        "Unlike a post: unlike <user>:<post_id>"
        print(arg)

    def do_follow(self, arg):
        "Follow a user: follow <follower>:<followed>"
        print(arg)

    def do_unfollow(self, arg):
        "Unfollow a user: unfollow <follower>:<followed>"
        print(arg)

    def do_prob(self, arg):
        'Set the probabilities of the social network: prob <prob_like> <prob_foll>'
        print(arg)

    def do_new_post(self, arg):
        'Create a new post: new_post <name>:<content>'
        print(arg)

    def do_display_network(self, arg):
        'Display the social network: display_network'
        print("display_network")

    def do_display_stats(self, arg):
        'Display social network statistics: display_stats'
        print("display_stats")

    def do_update(self, arg):
        'Run a timestep: update'
        print("update")

    def do_save(self, arg):
        'Save the network: save <filename>'
        print(arg)

    def do_exit(self, arg):
        'Exit the program: exit'
        return True


def simulation(netfile, eventfile, prob_like, prob_foll):
    print("Simulation")


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
            interactive().cmdloop()
        elif args.mode == "-s":
            simulation(args.netfile, args.eventfile, args.prob_like, args.prob_foll)
