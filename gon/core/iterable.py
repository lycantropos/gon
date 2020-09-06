import sys

if sys.version_info < (3, 6):
    OrderedDict = dict
else:
    from collections import OrderedDict
unique_ever_seen = OrderedDict.fromkeys
del OrderedDict, sys
