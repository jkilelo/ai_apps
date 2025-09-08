# Ensure project root is on sys.path for test imports when running pytest directly.
import sys
from pathlib import Path

root = Path(__file__).parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
