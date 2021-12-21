class TweepyWrapperError(Exception):
    pass


class TwitterTokenError(TweepyWrapperError):
    pass


class TwitterConnectionError(TweepyWrapperError):
    pass


class TweetNotReachable(TweepyWrapperError):
    pass
