from pathlib import Path
import os

# SERVING STATIC FILES
ROOT = Path(
    os.path.abspath(__file__)
).parent.parent  # Root directory of the project
SRC = ROOT / "src"
CLIENT = ROOT / "client" # NOT NEEDED FOR VUE CLI
DIST = CLIENT / "dist" # NOT NEEDED FOR VUE CLI