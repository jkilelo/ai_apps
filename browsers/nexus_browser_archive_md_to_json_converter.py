"""
NEXUS Task Database Markdown to JSON Converter
Converts the markdown task database to structured JSON format
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib

class TaskDatabaseConverter:
    def __init__(self, md_file_path: str):
        self.md_file_path = Path(md_file_path)
        self.tasks = []
        self.phases = []
        self.metadata = {}
        self.stats = {
            "total_tasks": 0,
            "completed": 0,
            "in_progress": 0,
            "pending": 0,
            "blocked": 0
        }
        
    def parse_markdown(self) -> Dict[str, Any]:
        """Parse markdown file and convert to structured JSON"""
        with open(self.md_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse metadata from header
        self._parse_metadata(lines[:10])
        
        current_phase = None
        current_task_group = None
        current_task = None
        line_num = 0
        
        while line_num < len(lines):
            line = lines[line_num].strip()
            
            # Parse phase (## PHASE_NAME [ID: XXX-000])
            if line.startswith('## ') and '[ID:' in line:
                phase_match = re.match(r'## (.+?) \[ID: ([A-Z]+-\d+)\]', line)
                if phase_match:
                    phase_name = phase_match.group(1)
                    phase_id = phase_match.group(2)
                    
                    # Parse phase metadata
                    phase_data = {
                        "id": phase_id,
                        "name": phase_name,
                        "status": "PENDING",
                        "progress": 0,
                        "priority": "MEDIUM",
                        "time_estimate": "",
                        "risk": "MEDIUM",
                        "tasks": []
                    }
                    
                    # Parse phase metadata lines
                    for i in range(1, 6):
                        if line_num + i < len(lines):
                            meta_line = lines[line_num + i].strip()
                            if meta_line.startswith('Status:'):
                                phase_data["status"] = meta_line.split(':')[1].strip()
                            elif meta_line.startswith('Progress:'):
                                phase_data["progress"] = int(meta_line.split(':')[1].strip().replace('%', ''))
                            elif meta_line.startswith('Priority:'):
                                phase_data["priority"] = meta_line.split(':')[1].strip()
                            elif meta_line.startswith('Time Estimate:'):
                                phase_data["time_estimate"] = meta_line.split(':', 1)[1].strip()
                            elif meta_line.startswith('Risk:'):
                                phase_data["risk"] = meta_line.split(':')[1].strip()
                    
                    current_phase = phase_data
                    self.phases.append(phase_data)
                    line_num += 5
                    
            # Parse individual task (### XXX-NNN: Task Name)
            elif line.startswith('### ') and '-' in line:
                task_match = re.match(r'### ([A-Z]+-\d+): (.+)', line)
                if task_match:
                    task_id = task_match.group(1)
                    task_name = task_match.group(2)
                    
                    task_data = {
                        "id": task_id,
                        "name": task_name,
                        "phase": current_phase["id"] if current_phase else None,
                        "status": "PENDING",
                        "actions": [],
                        "checks": [],
                        "dependencies": [],
                        "time_estimate": "",
                        "verification": "",
                        "automation": False,
                        "line_range": None,
                        "priority": current_phase.get("priority", "MEDIUM") if current_phase else "MEDIUM",
                        "risk": "LOW"
                    }
                    
                    # Parse task details
                    line_num += 1
                    while line_num < len(lines):
                        detail_line = lines[line_num].strip()
                        
                        # Break if we hit another task or phase
                        if detail_line.startswith('###') or detail_line.startswith('##'):
                            line_num -= 1
                            break
                            
                        if detail_line.startswith('Action:'):
                            task_data["actions"].append(detail_line.split(':', 1)[1].strip())
                        elif detail_line.startswith('Check:'):
                            task_data["checks"].append(detail_line.split(':', 1)[1].strip())
                        elif detail_line.startswith('Command:'):
                            task_data["actions"].append(f"Run: {detail_line.split(':', 1)[1].strip()}")
                        elif detail_line.startswith('Dependencies:'):
                            deps = detail_line.split(':', 1)[1].strip()
                            if deps != 'None':
                                task_data["dependencies"] = [d.strip() for d in deps.split(',')]
                        elif detail_line.startswith('Status:'):
                            task_data["status"] = detail_line.split(':')[1].strip()
                        elif detail_line.startswith('Time:'):
                            task_data["time_estimate"] = detail_line.split(':', 1)[1].strip()
                        elif detail_line.startswith('Verification:'):
                            task_data["verification"] = detail_line.split(':', 1)[1].strip()
                        elif detail_line.startswith('Lines:'):
                            task_data["line_range"] = detail_line.split(':', 1)[1].strip()
                        elif '[AUTOMATE]' in detail_line:
                            task_data["automation"] = True
                        elif detail_line.startswith('Priority:'):
                            task_data["priority"] = detail_line.split(':')[1].strip()
                        elif detail_line.startswith('Risk:'):
                            task_data["risk"] = detail_line.split(':')[1].strip()
                            
                        line_num += 1
                    
                    # Update stats
                    self.stats["total_tasks"] += 1
                    status_lower = task_data["status"].lower()
                    if status_lower == "completed":
                        self.stats["completed"] += 1
                    elif status_lower == "in_progress":
                        self.stats["in_progress"] += 1
                    elif status_lower == "blocked":
                        self.stats["blocked"] += 1
                    else:
                        self.stats["pending"] += 1
                    
                    # Add task to current phase and global list
                    if current_phase:
                        current_phase["tasks"].append(task_data)
                    self.tasks.append(task_data)
                    
            line_num += 1
        
        # Calculate overall progress
        if self.stats["total_tasks"] > 0:
            self.metadata["overall_progress"] = round(
                (self.stats["completed"] / self.stats["total_tasks"]) * 100, 2
            )
        
        return self._create_json_structure()
    
    def _parse_metadata(self, header_lines: List[str]):
        """Parse metadata from file header"""
        for line in header_lines:
            line = line.strip()
            if line.startswith('# Total Tasks:'):
                self.metadata["total_tasks"] = int(re.search(r'\d+', line).group())
            elif line.startswith('# Status:'):
                match = re.search(r'(\d+)%', line)
                if match:
                    self.metadata["overall_progress"] = int(match.group(1))
            elif line.startswith('# Last Updated:'):
                self.metadata["last_updated"] = line.split(':', 1)[1].strip()
            elif line.startswith('# Architecture:'):
                self.metadata["architecture"] = line.split(':', 1)[1].strip()
            elif line.startswith('# Recovery Checkpoint:'):
                self.metadata["recovery_checkpoint"] = line.split(':', 1)[1].strip()
    
    def _create_json_structure(self) -> Dict[str, Any]:
        """Create final JSON structure"""
        return {
            "metadata": {
                **self.metadata,
                "generated_at": datetime.now().isoformat(),
                "file_hash": self._calculate_file_hash(),
                "version": "1.0.0"
            },
            "statistics": self.stats,
            "phases": self.phases,
            "tasks": self.tasks,
            "dependencies": self._build_dependency_graph(),
            "checkpoints": self._extract_checkpoints()
        }
    
    def _calculate_file_hash(self) -> str:
        """Calculate MD5 hash of source file for integrity checking"""
        with open(self.md_file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build task dependency graph"""
        graph = {}
        for task in self.tasks:
            if task["dependencies"]:
                graph[task["id"]] = task["dependencies"]
        return graph
    
    def _extract_checkpoints(self) -> List[Dict[str, Any]]:
        """Extract recovery checkpoints from phases"""
        checkpoints = []
        checkpoint_phases = ["ENV-150", "NEX-200", "NEX-500", "NEX-800", "NEX-1000", 
                            "QUA-500", "MCP-400", "INT-300", "VAL-200", "DEP-097"]
        
        for phase_id in checkpoint_phases:
            checkpoint = {
                "id": phase_id,
                "name": f"Checkpoint {phase_id}",
                "description": f"Recovery point after {phase_id}",
                "backup_required": True
            }
            checkpoints.append(checkpoint)
        
        return checkpoints
    
    def save_json(self, output_path: str):
        """Save parsed data as JSON"""
        json_data = self.parse_markdown()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"[SUCCESS] Converted {self.stats['total_tasks']} tasks to JSON")
        print(f"[STATUS] {self.stats['completed']} completed, {self.stats['in_progress']} in progress, {self.stats['pending']} pending")
        print(f"[SAVED] {output_path}")
        
        return json_data


def main():
    # Convert markdown to JSON
    converter = TaskDatabaseConverter(
        r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\nexus_browser\nexus_implementation_tasks.md"
    )
    
    json_output_path = r"C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\nexus_browser\nexus_tasks.json"
    converter.save_json(json_output_path)
    
    print("\n[COMPLETE] Conversion complete! Now open nexus_dashboard.html in your browser.")


if __name__ == "__main__":
    main()