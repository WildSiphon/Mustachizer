class TweepyWrapperError(Exception):
    pass


class TwitterTokenError(TweepyWrapperError):
    pass


class TwitterConnectionError(TweepyWrapperError):
    pass


class TweetNotReachable(TweepyWrapperError):
    pass


class MediaUploadError(TweepyWrapperError):
    pass


class MediaTypeError(TweepyWrapperError):
    pass


class MultipleUploadError(MediaUploadError):
    pass


class MixedMediasError(MediaUploadError):
    pass
