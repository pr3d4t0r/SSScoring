# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


import json


# +++ classes +++

class SSScoringError(Exception):
    """
    Abstract class that defines all exceptions and errors and has a dictionary
    representation of itself, for cleaner structured logging.

    Arguments
    ---------
        message : str
    A meaningful error message, human-readable
        errno : int
    An optional integer value, similar to ERRNO in C/UNIX
    """
    def __init__(self, message: str, errno: int = -1):
        self._info = message
        self._errno = errno


    def __str__(self):
        e = {  'SSScoringError': self._info, 'errno': self._errno, }

        return json.dumps(e)

