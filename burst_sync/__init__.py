from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

from .asdr import asdr
from .b_stat import b_statistic