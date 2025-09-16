"""
Open NEXUS Dashboard in Browser
Quick launcher for the task tracking dashboard
"""

import webbrowser
import os
from pathlib import Path

def open_dashboard():
    """Open the NEXUS dashboard HTML file in the default browser"""
    
    # Get the path to the dashboard HTML file
    dashboard_path = Path(__file__).parent / "nexus_dashboard.html"
    
    if not dashboard_path.exists():
        print("[ERROR] Dashboard file not found!")
        print(f"[ERROR] Expected at: {dashboard_path}")
        return False
    
    # Check if JSON data file exists
    json_path = Path(__file__).parent / "nexus_tasks.json"
    if not json_path.exists():
        print("[WARNING] JSON data file not found!")
        print("[INFO] Run md_to_json_converter.py first to generate the data file")
        return False
    
    # Convert to file URL
    file_url = f"file:///{dashboard_path.absolute()}".replace("\\", "/")
    
    print("[INFO] Opening NEXUS Dashboard...")
    print(f"[INFO] URL: {file_url}")
    
    # Open in default browser
    webbrowser.open(file_url)
    
    print("[SUCCESS] Dashboard opened in browser!")
    print("\n[TIPS]:")
    print("- Use the search box to find specific tasks")
    print("- Click on phase cards to filter by phase")
    print("- Switch between Table, Cards, and Kanban views")
    print("- Click on any task to see full details")
    print("- Drag tasks in Kanban view to change status")
    print("- Data auto-refreshes every 30 seconds")
    
    return True

if __name__ == "__main__":
    open_dashboard()