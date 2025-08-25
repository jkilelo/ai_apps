import os

def create_html_from_directory(directory_path, output_html_file):
    """
    Creates a single HTML document from all text files in a directory and its subdirectories.

    Args:
        directory_path (str): The path to the directory to process.
        output_html_file (str): The path to the output HTML file.
    """
    html_content = "<html>\n<head>\n<title>Directory Contents</title>\n</head>\n<body>\n"

    for root, _, files in os.walk(directory_path):
        for file in files:
            # Construct the full path to the file
            file_path = os.path.join(root, file)

            try:
                # Read the content of the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()

                # Add a heading with the full path and the file content to the HTML string
                html_content += f"<h2>{file_path}</h2>\n"
                html_content += f"<pre>{file_content}</pre>\n"

            except Exception as e:
                # Handle potential errors (e.g., binary files)
                print(f"Could not read file {file_path}: {e}")

    html_content += "</body>\n</html>"

    # Write the complete HTML content to the output file
    with open(output_html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

# Example usage:
create_html_from_directory(r'C:\Users\kleiy\OneDrive\Desktop\python-ai-apps\ai_apps\simple_apps_v2\shared_modules\ui_web_auto_testing_v2', 'output.html')