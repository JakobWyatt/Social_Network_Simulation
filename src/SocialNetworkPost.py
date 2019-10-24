from functools import total_ordering

import numpy.random

from ADT.DSALinkedList import DSALinkedList


@total_ordering
class SocialNetworkPost:
    """
    This class represents a post on the social network, and can be queried
    to obtain the users that have liked the post, the original poster,
    and the post content.
    It also contains a method func:`update`, which propogates the
    post through the network by one timestep. The core of the propogation
    algorithm is implemented in this method.
    """

    def __init__(self, user: 'SocialNetworkUser', content: str,
                 clickbaitFactor: float, probLike: float, probFollow: float):
        self._recentlyLiked = DSALinkedList()
        self._liked = DSALinkedList()
        self._recentlyLiked.insertFirst(user)
        self._content = content
        self._probLike = probLike
        self._probFollow = probFollow
        self.clickbaitFactor = clickbaitFactor

    @property
    def clickbaitFactor(self):
        return self._clickbaitFactor

    @clickbaitFactor.setter
    def clickbaitFactor(self, clickbaitFactor: float):
        if clickbaitFactor < 0:
            raise ValueError("clickbaitFactor must be positive.")
        self._clickbaitFactor = clickbaitFactor

    def user(self) -> 'SocialNetworkUser':
        if len(self._liked) == 0:
            user = self._recentlyLiked.peekLast()
        else:
            user = self._liked.peekLast()
        return user

    def like(self, user: 'SocialNetworkUser'):
        if self._recentlyLiked.find(user) or self._liked.find(user):
            raise ValueError("User has already liked post.")
        self._recentlyLiked.insertFirst(user)

    def unlike(self, user: 'SocialNetworkUser'):
        ret = self._liked.remove(user)
        if ret is None:
            ret = self._recentlyLiked.remove(user)
        return ret

    @property
    def content(self) -> str:
        return self._content

    def done(self) -> bool:
        return len(self._recentlyLiked) == 0

    def save(self) -> str:
        return (f"content: {self.content}\n"
                f"user: {self.user().name()}\n"
                f"liked:\n"
                + '\n'.join([x.name() for x in self.liked()])
                + '\n')

    def update(self) -> str:
        """
        The update algorithm works as follows:
        Check that there exists some users that have liked the post in the
        previous timestep. If there are none, the update ends and the next
        post is loaded. Iterate through all users who liked the post in the
        previous timestep. Each of their followers is 'exposed' to the post,
        and have a chance of liking the post.
        This chance is sampled from a Bernoulli distribution with probability
        clamp(prob_like * clickbait_factor, 0, 1).
        If a user likes a post in the current timestep, they have a chance of
        following the original poster.
        This is sampled using the same technique as above,
        with global probability prob_foll.

        Note that in the above algorithm, if a user does not like a post,
        they may potentially be exposed to it later via a different friend.
        This behaviour is intentional, as it incentivises
        a highly connected network.
        """
        newLikes = DSALinkedList()
        for x in self._recentlyLiked:
            for user in x.followers():
                # Does the user like the post?
                if numpy.random.binomial(1, min(1, self._probLike *
                                                self.clickbaitFactor)) == 1:
                    if (not self._liked.find(user)
                       and not self._recentlyLiked.find(user)
                       and not newLikes.find(user)):
                        newLikes.insertFirst(user)
                    # Does the user follow the original poster?
                    if numpy.random.binomial(1, self._probFollow) == 1:
                        try:
                            user.follow(self.user())
                        except ValueError:
                            pass
        self._liked = self._recentlyLiked.concat(self._liked)
        self._recentlyLiked = newLikes

    def liked(self):
        def generateLiked(l1, l2):
            for x in l1:
                yield x
            for x in l2:
                yield x
        return generateLiked(self._recentlyLiked, self._liked)

    def __eq__(self, other):
        return self is other

    def __lt__(self, other):
        return (len(self._liked) + len(self._recentlyLiked)
                < len(other._recentlyLiked) + len(other._liked))
