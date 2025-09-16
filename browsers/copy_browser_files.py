import os
import shutil
from pathlib import Path

def copy_browser_files():
    output_dir = Path('browsers')
    output_dir.mkdir(exist_ok=True)
    
    file_counter = {}
    total_copied = 0
    
    # Walk through all directories
    for root, dirs, files in os.walk('.'):
        # Skip the browsers directory itself
        if 'browsers' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                full_path = Path(root) / file
                
                try:
                    # Check if file contains 'browser'
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        if 'browser' not in f.read().lower():
                            continue
                    
                    # Create unique filename
                    # Replace path separators with underscores
                    path_prefix = str(full_path.parent).replace('./', '').replace('.\\', '')
                    path_prefix = path_prefix.replace('/', '_').replace('\\', '_')
                    
                    if path_prefix and path_prefix != '.':
                        new_name = f"{path_prefix}_{file}"
                    else:
                        new_name = file
                    
                    # Handle duplicates by adding counter
                    base_new_name = new_name
                    counter = 1
                    while (output_dir / new_name).exists():
                        name_without_ext = base_new_name[:-3]
                        new_name = f"{name_without_ext}_{counter}.py"
                        counter += 1
                    
                    # Copy the file
                    shutil.copy2(full_path, output_dir / new_name)
                    total_copied += 1
                    
                    if total_copied % 50 == 0:
                        print(f"Copied {total_copied} files...")
                        
                except Exception as e:
                    print(f"Error processing {full_path}: {e}")
                    continue
    
    print(f"\nTotal files copied: {total_copied}")
    
    # Show some statistics
    all_files = list(output_dir.glob('*.py'))
    print(f"Files in browsers directory: {len(all_files)}")
    
    # Check for files with same base name
    base_names = {}
    for f in all_files:
        base = f.name.split('_')[-1] if '_' in f.name else f.name
        if base not in base_names:
            base_names[base] = []
        base_names[base].append(f.name)
    
    duplicates = {k: v for k, v in base_names.items() if len(v) > 1}
    if duplicates:
        print(f"\nFiles with same base name but from different directories:")
        for base, files in list(duplicates.items())[:10]:
            print(f"  {base}: {len(files)} copies")
            for f in files[:3]:
                print(f"    - {f}")

if __name__ == "__main__":
    copy_browser_files()