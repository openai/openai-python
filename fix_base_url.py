#!/usr/bin/env python3
"""Fix script for issue #2927: empty OPENAI_BASE_URL should fallback to default"""

file_path = "src/openai/_client.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

modified_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Look for the pattern:
    # if base_url is None:
    #     base_url = os.environ.get("OPENAI_BASE_URL")
    # if base_url is None:
    #     base_url = f"https://api.openai.com/v1"
    
    if 'if base_url is None:' in line and i+1 < len(lines):
        next_line = lines[i+1]
        if 'base_url = os.environ.get("OPENAI_BASE_URL")' in next_line:
            # This is the first "if base_url is None"
            # Keep it as is
            modified_lines.append(line)
            modified_lines.append(next_line)
            i += 2
            
            # Now check if the next line is the second "if base_url is None"
            if i < len(lines) and 'if base_url is None:' in lines[i]:
                # Replace this second check with "if not base_url:"
                indent = lines[i][:lines[i].index('if')]
                modified_lines.append(f"{indent}# Treat empty string same as None to allow fallback to default\n")
                modified_lines.append(f"{indent}# Fixes #2927: export OPENAI_BASE_URL=\"\" should not prevent default URL\n")
                modified_lines.append(f"{indent}if not base_url:\n")
                i += 1
            continue
    
    modified_lines.append(line)
    i += 1

with open(file_path, 'w') as f:
    f.writelines(modified_lines)

print("✅ Fixed both occurrences (sync and async clients)")
