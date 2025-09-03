#!/usr/bin/env python3
"""
Update nexus_tasks.json and nexus_dashboard.html with current task status
This MUST be run after EVERY task completion per the contract
"""

import json
from datetime import datetime
from pathlib import Path

def update_task_status(task_id, status="COMPLETED"):
    """Update the status of a task in nexus_tasks.json"""
    
    # Load tasks
    tasks_file = Path("nexus_tasks.json")
    with open(tasks_file, 'r') as f:
        tasks_data = json.load(f)
    
    # Find and update the task
    task_found = False
    for phase in tasks_data.get("phases", []):
        for task in phase.get("tasks", []):
            if task["id"] == task_id:
                task["status"] = status
                task_found = True
                break
        if task_found:
            break
    
    # Update statistics
    completed = 0
    in_progress = 0
    pending = 0
    
    for phase in tasks_data.get("phases", []):
        for task in phase.get("tasks", []):
            if task["status"] == "COMPLETED":
                completed += 1
            elif task["status"] == "IN_PROGRESS":
                in_progress += 1
            else:
                pending += 1
    
    tasks_data["statistics"]["completed"] = completed
    tasks_data["statistics"]["in_progress"] = in_progress
    tasks_data["statistics"]["pending"] = pending
    tasks_data["metadata"]["last_updated"] = datetime.now().isoformat()
    
    # Save updated tasks
    with open(tasks_file, 'w') as f:
        json.dump(tasks_data, f, indent=2)
    
    print(f"Updated {task_id} to {status} in nexus_tasks.json")
    return completed, in_progress, pending

def update_dashboard_html(completed, in_progress, pending):
    """Update the dashboard HTML with current statistics"""
    
    dashboard_file = Path("nexus_dashboard.html")
    
    # Read the dashboard
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Calculate totals
    total = completed + in_progress + pending
    progress_percent = (completed / total * 100) if total > 0 else 0
    
    # Update the embedded data
    # Look for the script section and update it
    import re
    
    # Update the data script
    data_pattern = r'const taskData = \{[^}]*\}'
    new_data = f'''const taskData = {{
        total: {total},
        completed: {completed},
        inProgress: {in_progress},
        pending: {pending},
        failed: 0,
        progressPercent: {progress_percent:.1f},
        lastUpdated: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }}'''
    
    if 'const taskData' in html_content:
        html_content = re.sub(data_pattern, new_data, html_content)
    else:
        # Add script section if not exists
        script_section = f'''
    <script>
    {new_data}
    
    // Update display
    document.addEventListener('DOMContentLoaded', function() {{
        document.getElementById('totalTasks').textContent = taskData.total;
        document.getElementById('completedTasks').textContent = taskData.completed;
        document.getElementById('inProgressTasks').textContent = taskData.inProgress;
        document.getElementById('pendingTasks').textContent = taskData.pending;
        document.getElementById('lastUpdated').textContent = taskData.lastUpdated;
        
        // Update progress bar
        const progressBar = document.querySelector('.progress-fill');
        if (progressBar) {{
            progressBar.style.width = taskData.progressPercent + '%';
        }}
    }});
    </script>
</body>'''
        html_content = html_content.replace('</body>', script_section)
    
    # Write updated dashboard
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Updated dashboard: {completed} completed, {in_progress} in progress, {pending} pending")

# Update ENV-001 and ENV-002 as COMPLETED
if __name__ == "__main__":
    # Update ENV-001
    completed, in_progress, pending = update_task_status("ENV-001", "COMPLETED")
    update_dashboard_html(completed, in_progress, pending)
    
    # Update ENV-002  
    completed, in_progress, pending = update_task_status("ENV-002", "COMPLETED")
    update_dashboard_html(completed, in_progress, pending)
    
    print("\nStatus update complete!")
    print(f"Total: {completed + in_progress + pending}")
    print(f"Completed: {completed}")
    print(f"In Progress: {in_progress}")
    print(f"Pending: {pending}")