"""
Base classes for interfacing with APIs and other services
"""

import sys
from abc import ABC, abstractmethod
import typing
from typing import Optional, Union, Tuple, List, Dict
if sys.version_info.minor >= 8:
    from typing import Literal
else:
    from typing_extensions import Literal


class Interface(ABC):
    """
    Root class for declaring an interface, just a stub for now!
    """