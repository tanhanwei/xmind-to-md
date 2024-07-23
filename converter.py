import zipfile
import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path
import os

def xmind_to_markdown(xmind_file, output_file):
    # Extract content from XMind file
    with zipfile.ZipFile(xmind_file, 'r') as zf:
        content_json = zf.read('content.json')
    
    # Parse JSON content
    content = json.loads(content_json)
    
    # Convert to markdown
    markdown_content = convert_sheet_to_markdown(content[0])  # Assume first sheet
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

def convert_sheet_to_markdown(sheet, level=1):
    content = ""
    root_topic = sheet['rootTopic']
    content += convert_topic_to_markdown(root_topic, level)
    return content

def convert_topic_to_markdown(topic, level):
    content = f"{'#' * level} {topic['title']}\n\n"
    
    # Add notes if any
    if 'notes' in topic:
        content += f"{topic['notes']['plain']['content']}\n\n"
    
    # Process subtopics
    if 'children' in topic:
        for subtopic in topic['children']['attached']:
            content += convert_topic_to_markdown(subtopic, level + 1)
    
    return content

def markdown_to_xmind(markdown_file, output_file):
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    lines = markdown_content.split('\n')
    root_topic = {"title": "Root", "children": {"attached": []}}
    topic_stack = [root_topic]
    current_level = 0
    current_content = ""

    for line in lines:
        header_match = re.match(r'^(#+)\s+(.+)$', line)
        if header_match:
            # If there's accumulated content, add it to the current topic
            if current_content.strip():
                topic_stack[-1]["title"] += "\n" + current_content.strip()
                current_content = ""

            level = len(header_match.group(1))
            title = header_match.group(2)

            while level <= current_level and len(topic_stack) > 1:
                topic_stack.pop()
                current_level -= 1

            new_topic = {"title": title, "children": {"attached": []}}
            topic_stack[-1]["children"]["attached"].append(new_topic)
            topic_stack.append(new_topic)
            current_level = level
        else:
            # Accumulate content instead of treating it as notes
            current_content += line + "\n"

    # Add any remaining content to the last topic
    if current_content.strip():
        topic_stack[-1]["title"] += "\n" + current_content.strip()

    xmind_content = [{
        "id": "root",
        "class": "sheet",
        "title": "Sheet 1",
        "rootTopic": root_topic["children"]["attached"][0]
    }]

    with zipfile.ZipFile(output_file, 'w') as zf:
        zf.writestr('content.json', json.dumps(xmind_content))
        zf.writestr('metadata.json', json.dumps({"creator":{"name":"Python Script","version":"1.0"}}))

def batch_convert_xmind_to_markdown(input_folder, output_folder):
    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # Get all XMind files in the input folder
    xmind_files = list(Path(input_folder).glob('*.xmind'))

    for xmind_file in xmind_files:
        # Create output Markdown filename
        markdown_file = Path(output_folder) / f"{xmind_file.stem}.md"

        # Convert XMind to Markdown
        xmind_to_markdown(str(xmind_file), str(markdown_file))
        print(f"Converted {xmind_file} to {markdown_file}")

# Example usage
if __name__ == "__main__":
    # Single file conversion
    xmind_file = "赛道智能体Race Track Agent.xmind"
    markdown_file = "md_test.md"
    new_xmind_file = "new_output_2_new.xmind"

    # Convert XMind to Markdown
    # xmind_to_markdown(xmind_file, markdown_file)
    # print(f"Converted {xmind_file} to {markdown_file}")

    # Convert Markdown back to XMind
    # markdown_to_xmind(markdown_file, new_xmind_file)
    # print(f"Converted {markdown_file} to {new_xmind_file}")

    # Batch conversion
    input_folder = "xmind"
    output_folder = "output_md"
    batch_convert_xmind_to_markdown(input_folder, output_folder)
    print(f"Batch conversion completed. Check the '{output_folder}' folder for results.")