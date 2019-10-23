# Interactive menu
import cmd
import readline
# File interaction
import os
import errno

# Simulation
from SocialNetworkCore import SocialNetwork

# Ben said ok
class interactive(cmd.Cmd):
    intro = "Type help or ? to list commands.\n"
    prompt = "(social-sim) "

    def __init__(self):
        super(interactive, self).__init__()
        self._network = SocialNetwork()

    def do_load(self, arg):
        'Load a social network: load <netfile>'
        try:
            with open(arg, "r") as f:
                self._network.loadNetwork(f)
        except IOError as ioex:
            print(f"File could not be read: {os.strerror(ioex.errno)}")
        except ValueError as vEx:
            print(str(vEx))

    def do_find_user(self, arg):
        'Find a user and display their posts, followers, and following: find_user <name>'
        try:
            user = self._network.findUser(arg)
            print("#posts")
            for x in user.posts:
                print(f"content: {x.content}")
                print("liked:")
                [print(y.name()) for y in x.liked()]
            print("#followers")
            [print(x.name()) for x in user.followers()]
            print("#following")
            [print(x.name()) for x in user.following()]
        except ValueError as ex:
            print(str(ex))
        
    def do_add_user(self, arg):
        'Add a user: add_user <name>'
        try:
            self._network.addUser(arg)
        except ValueError as ex:
            print(str(ex))

    def do_remove_user(self, arg):
        'Remove a user: remove_user <name>'
        try:
            self._network.removeUser(arg)
        except ValueError as ex:
            print(str(ex))

    def do_like(self, arg):
        'Like a post: like <user>'
        try:
            self._network.like(arg)
        except ValueError as ex:
            print(str(ex))

    def do_unlike(self, arg):
        "Unlike a post: unlike <user>"
        try:
            self._network.unlike(arg)
        except ValueError as ex:
            print(str(ex))

    def do_follow(self, arg):
        "Follow a user: follow <followed>:<follower>"
        args = arg.split(':')
        if len(args) == 2:
            try:
                if not self._network.follow(args[1], args[0]):
                    print(f"{args[1]} is already following {args[0]}.")
            except ValueError as ex:
                print(str(ex))
        else:
            print("Invalid usage.")

    def do_unfollow(self, arg):
        "Unfollow a user: unfollow <followed>:<follower>"
        args = arg.split(':')
        if len(args) == 2:
            try:
                self._network.unfollow(args[1], args[0])
            except ValueError as ex:
                print(str(ex))
        else:
            print("Invalid usage.")

    def do_prob(self, arg):
        'Set the probabilities of the social network: prob <prob_like> <prob_foll>'
        args = arg.split()
        if len(args) == 2:
            try:
                self._network.probLike = float(args[0])
                self._network.probFollow = float(args[1])
            except ValueError as ex:
                print(str(ex))
        else:
            print("Invalid usage.")

    def do_post(self, arg):
        'Create a new post: post <name>:<content>:<(optional) clickbaitFactor>'
        args = arg.split(':')
        try:
            if len(args) == 2:
                self._network.addPost(args[0], args[1])
            elif len(args) == 3:
                self._network.addPost(args[0], args[1], float(args[2]))
            else:
                print("Invalid usage.")
        except ValueError as ex:
            print(str(ex))

    def do_display(self, arg):
        'Display the social network: display'
        self._network.display()

    def do_stats(self, arg):
        'Display social network statistics: stats'
        print(self._network.optionalStats())

    def do_posts(self, arg):
        'Display posts in order of popularity: posts'
        [print(f"user: {x.user().name()}\ncontent: {x.content}\nlikes: {sum(1 for _ in x.liked())}\n") for x in self._network.popularPosts()]

    def do_users(self, arg):
        'Display users in order of popularity: users'
        [print(f"user: {x.name()}\nfollowers: {len(x.followers())}\n") for x in self._network.popularUsers()]

    def do_update(self, arg):
        'Run a timestep: update'
        try:
            self._network.update()
        except ValueError as vEx:
            print(str(vEx))

    def do_save(self, arg):
        'Save the network: save <filename>'
        try:
            with open(arg, "f") as f:
                f.write(self._network.save())
        except IOError as ioex:
            print(f"File could not be read: {os.strerror(ioex.errno)}")

    def do_exit(self, arg):
        'Exit the program: exit'
        return True
