import sys
import re

TARGET = r"c:\Users\faton\MultiDoc-Translator\scripts\python\multidoc_translator.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix Starting tool
text = re.sub(
    r'print\(Fore\.CYAN \+ "\\n\[\+\] Starting Translation Repair Tool\.\.\."\)',
    r'print(Fore.CYAN + f"\\n[+] {t(\'ui.repairStarting\')}")',
    text
)

# Fix Step 1 (YELLOW)
text = re.sub(
    r'print\(Fore\.YELLOW \+ "1\. Cleaning up duplicate switchers and fixing their positions in all READMEs\.\.\."\)',
    r'print(Fore.YELLOW + t(\'ui.repairStep1\'))',
    text
)

# Fix Step 2 (YELLOW)
text = re.sub(
    r'print\(Fore\.YELLOW \+ "\\n2\. Scanning translated documents for failures \(API errors / unchanged English\)\.\.\."\)',
    r'print(Fore.YELLOW + f"\\n{t(\'ui.repairStep2\')}")',
    text
)

# Fix Languages missing translations
text = text.replace(
    'print(f"   Languages: {\', \'.join(ordered_existing)}")',
    'print(f"   {t(\'ui.repairLanguages\', langs=\', \'.join(ordered_existing))}")'
)

# Make sure main README translated name is used, wait, "main README の言語スイッチャーを更新しました" 
# Oh wait! 
# print(t("language_switcher_updated", filename="main README"))
# In jp dictionary, "language_switcher_updated": "{filename} の言語スイッチャーを更新しました",
# So the word "main" was hardcoded. Let's not worry about "main", "main README" is a valid name.

with open(TARGET, 'w', encoding='utf-8') as f:
    f.write(text)

print("Repair tool prints patched!")
