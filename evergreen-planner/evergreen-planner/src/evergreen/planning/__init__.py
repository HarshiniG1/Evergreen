"""Planning: uses inventory + (optionally) the map. Optimisation comes later."""
from .planner import suggest_targets, plan_consolidation

__all__ = ["suggest_targets", "plan_consolidation"]
