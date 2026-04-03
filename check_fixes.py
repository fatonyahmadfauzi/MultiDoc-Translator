import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/python/multidoc_translator.py', encoding='utf-8') as f:
    content = f.read()

# Check translationCompletedReadmeOnly - should have {count} not {0}
pat = r'"success\.translationCompletedReadmeOnly"\s*:\s*"([^"]+)"'
matches = re.findall(pat, content)
print('translationCompletedReadmeOnly values:')
for m in matches:
    print(' ', repr(m))

# Check progress.barLabel
pat2 = r'"progress\.barLabel"\s*:\s*"([^"]+)"'
bars = re.findall(pat2, content)
print('progress.barLabel values:', bars)

# Check repair_translations function no longer has backslash f-string issue
if "t(\\'ui.repairStarting\\')" in content:
    print("ERROR: backslash f-string still exists for repairStarting")
elif '_msg_repair_starting = t("ui.repairStarting")' in content:
    print("OK: repairStarting fixed")

if "t(\\'ui.repairStep1\\')" in content:
    print("ERROR: backslash f-string still exists for repairStep1")
elif 'print(Fore.YELLOW + t("ui.repairStep1"))' in content:
    print("OK: repairStep1 fixed")

if "t(\\'ui.repairStep2\\')" in content:
    print("ERROR: backslash f-string still exists for repairStep2")
elif '_msg_repair_step2 = t("ui.repairStep2")' in content:
    print("OK: repairStep2 fixed")
