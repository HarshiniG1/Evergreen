"""Central settings. Change values here, not inside the logic."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DATA_DIR = PROJECT_ROOT / "data" / "sample"
REAL_DATA_DIR = PROJECT_ROOT / "data" / "real"  # git-ignored

# Extra "walking cost" (metres-equivalent) for each floor changed (stairs/elevator).
# ASSUMPTION: placeholder value, tune later.
FLOOR_CHANGE_COST_M = 15.0
