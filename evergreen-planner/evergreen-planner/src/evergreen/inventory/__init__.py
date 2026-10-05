"""Inventory system. Independent from the mapping package."""
from .loader import load_inventory, load_building_counts
from .grouping import (summarize_by_building, group_by_model, group_by_category,
                       counts_by_building)

__all__ = ["load_inventory", "load_building_counts", "summarize_by_building",
           "group_by_model", "group_by_category", "counts_by_building"]
