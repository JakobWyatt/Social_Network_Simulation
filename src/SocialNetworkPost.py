from functools import total_ordering

from numpy.random import binomial

from ADT.DSALinkedList import DSALinkedList

@total_ordering
class SocialNetworkPost:
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
        return (f"content: {self.content}\nuser: {self.user().name()}\nliked:\n"
                + '\n'.join([x.name() for x in self.liked()]) + '\n')

    def update(self) -> str:
        # The core of the algorithm. (Finally!)
        newLikes = DSALinkedList()
        for x in self._recentlyLiked:
            for user in x.followers():
                # Does the user like the post?
                if binomial(1, min(1, self._probLike * self.clickbaitFactor)) == 1:
                    if not self._liked.find(user) and not self._recentlyLiked.find(user):
                        newLikes.insertFirst(user)
                    # Does the user follow the original poster?
                    if binomial(1, self._probFollow) == 1:
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
