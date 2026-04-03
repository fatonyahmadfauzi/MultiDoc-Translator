#!/usr/bin/env python3
"""Fix script for multidoc_translator.py"""

with open('scripts/python/multidoc_translator.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixes = 0
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Fix 1: line with t(\'ui.repairStarting\') inside f-string
    if "f\"\\n[+] {t(\\'ui.repairStarting\\')}" in line:
        indent = len(line) - len(line.lstrip())
        spaces = ' ' * indent
        new_lines.append(spaces + '_msg_repair_starting = t("ui.repairStarting")\n')
        new_lines.append(spaces + 'print(Fore.CYAN + f"\\n[+] {_msg_repair_starting}")\n')
        fixes += 1
        i += 1
        continue
    
    # Fix 2: line with t(\'ui.repairStep1\') (not in f-string, just escaped quotes)
    if "t(\\'ui.repairStep1\\')" in line and 'f"' not in line:
        indent = len(line) - len(line.lstrip())
        spaces = ' ' * indent
        new_lines.append(spaces + 'print(Fore.YELLOW + t("ui.repairStep1"))\n')
        fixes += 1
        i += 1
        continue
    
    # Fix 3: line with t(\'ui.repairStep2\') inside f-string
    if "f\"\\n{t(\\'ui.repairStep2\\')}" in line:
        indent = len(line) - len(line.lstrip())
        spaces = ' ' * indent
        new_lines.append(spaces + '_msg_repair_step2 = t("ui.repairStep2")\n')
        new_lines.append(spaces + 'print(Fore.YELLOW + f"\\n{_msg_repair_step2}")\n')
        fixes += 1
        i += 1
        continue
    
    new_lines.append(line)
    i += 1

print(f"Applied {fixes} f-string fixes")

# Now fix {0} positional placeholders in success messages 
# They are called with count= keyword, so {0} never gets replaced
content = ''.join(new_lines)

import re

# Find all occurrences of success.translationCompletedReadmeOnly value with {0}
# and success.translationCompletedWithChangelog value with {0}
# Replace {0} with {count} in those specific string values
def fix_success_placeholder(text):
    # Pattern: "success.translationCompleted...": "... {0} ..."
    # We need to replace {0} with {count} in the VALUE (the string after the colon+quote)
    # Use a careful regex to find these specific keys and fix their {0}
    
    patterns = [
        (r'("success\.translationCompletedReadmeOnly"\s*:\s*"[^"]*)\{0\}([^"]*")',
         r'\1{count}\2'),
        (r'("success\.translationCompletedWithChangelog"\s*:\s*"[^"]*)\{0\}([^"]*")',
         r'\1{count}\2'),
    ]
    
    fix_count = 0
    for pattern, replacement in patterns:
        new_text, n = re.subn(pattern, replacement, text)
        fix_count += n
        text = new_text
    
    print(f"Fixed {fix_count} {{0}} -> {{count}} in success message phrases")
    return text

content = fix_success_placeholder(content)

# Also add progress.barLabel key to all language blocks
# First check if it already exists
if '"progress.barLabel"' in content:
    print("progress.barLabel already exists")
else:
    # Add progress.barLabel to the 'en' block right after progress.completed
    # Find the pattern and insert
    en_insertion_point = '"progress.completed": "✅ Translation process completed",'
    if en_insertion_point in content:
        content = content.replace(
            en_insertion_point,
            en_insertion_point + '\n        "progress.barLabel": "Progress:",'
        )
        print("Added progress.barLabel to en block")
    
    # Add to other language blocks too - just use the same English "Progress:" as fallback
    # The t() function already falls back to English if key not found in current lang
    # So we only NEED to add it to 'en'. Done.

with open('scripts/python/multidoc_translator.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! File saved.")

# Verify syntax
import py_compile
try:
    py_compile.compile('scripts/python/multidoc_translator.py', doraise=True)
    print("✅ Syntax OK - no errors!")
except py_compile.PyCompileError as e:
    print(f"❌ Syntax error: {e}")
