#!/usr/bin/env python3
"""Update progress for a completed task."""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def update_task_progress(task_id: str, quality_results: Dict[str, Any]) -> None:
    """Update progress for a completed task."""
    progress_file = Path("nexus_progress.json")
    
    # Load current progress
    with open(progress_file, 'r') as f:
        progress = json.load(f)
    
    # Update metadata
    progress["metadata"]["last_updated"] = datetime.now().isoformat()
    progress["metadata"]["current_task"] = f"ENV-{int(task_id.split('-')[1]) + 1:03d}"
    progress["metadata"]["total_completed"] = len(progress["task_progress"]) + 1
    
    # Add task progress
    progress["task_progress"][task_id] = {
        "status": "completed",
        "completed_at": datetime.now().isoformat(),
        "quality_checks": quality_results
    }
    
    # Update phase progress
    if task_id.startswith("ENV-"):
        phase_key = "ENV-000"
        if phase_key not in progress["phase_progress"]:
            progress["phase_progress"][phase_key] = {
                "status": "in_progress",
                "completed_tasks": 0,
                "total_tasks": 100,
                "percentage": 0.0
            }
        
        progress["phase_progress"][phase_key]["completed_tasks"] += 1
        progress["phase_progress"][phase_key]["percentage"] = (
            progress["phase_progress"][phase_key]["completed_tasks"] / 
            progress["phase_progress"][phase_key]["total_tasks"] * 100
        )
    
    # Save updated progress
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2)
    
    print(f"[PROGRESS] Task {task_id} marked as completed")
    print(f"[PROGRESS] Total completed: {progress['metadata']['total_completed']}/5700")
    print(f"[PROGRESS] Next task: {progress['metadata']['current_task']}")


if __name__ == "__main__":
    # Update ENV-002 as completed
    quality_results = {
        "mypy_strict": "PASS",
        "flake8": "PASS",
        "type_coverage": 100.0,
        "pydantic": "USED"
    }
    
    update_task_progress("ENV-002", quality_results)