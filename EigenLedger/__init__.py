# Only import main module if explicitly requested
# This prevents import errors when accessing submodules like google_auth
try:
    from .main import *
except ImportError:
    # If main.py dependencies aren't installed, skip
    pass
from .modules.empyrical import *