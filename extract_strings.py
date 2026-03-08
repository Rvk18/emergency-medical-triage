import os
import re
import json

app_dir = '/Users/akilanvj/Workspace/Aws_AI_Bharat/emergency-medical-triage/frontend/mobile-android/app/src/main/java/com/medtriage/app/ui'

strings = set()
pattern = re.compile(r'Text\(\s*"([^"]+)"')

for root, _, files in os.walk(app_dir):
    for f in files:
        if f.endswith('.kt'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                matches = pattern.findall(content)
                for m in matches:
                    strings.add(m)

print(f"Found {len(strings)} unique strings.")
with open('/tmp/unique_strings.json', 'w', encoding='utf-8') as outfile:
    json.dump(list(strings), outfile, indent=2)
