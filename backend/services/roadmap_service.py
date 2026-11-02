"""
Dynamic Career Roadmap Generator Service
Generates structured multi-phase technical roadmaps for 12+ career tracks,
including daily study plans, weekly targets, monthly milestones, curated free resources,
and task-level completion tracking.
"""
from typing import Dict, Any, List, Optional
from app.services.roadmap_service import RoadmapService

# Canonical singleton instance
roadmap_service = RoadmapService

__all__ = ["RoadmapService", "roadmap_service"]
