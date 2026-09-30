import os
import subprocess

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HTML_PATH = r"d:\Data Scraping Project POC\OneExtraction\botasaurus\output\presentation\ceo_presentation.html"
ARTIFACT_DIR = r"C:\Users\Lingabarini M\.gemini\antigravity-ide\brain\4c55ae8a-8e37-4ff0-bd4d-5cdc2b86f0c4"

os.makedirs(ARTIFACT_DIR, exist_ok=True)

# 1. Full Dashboard (Tall)
output_full = os.path.join(ARTIFACT_DIR, "ceo_full_platform_dashboard.png")
cmd_full = [
    CHROME,
    "--headless=new",
    "--hide-scrollbars",
    "--window-size=1440,4200",
    f"--screenshot={output_full}",
    HTML_PATH
]
print("Capturing Full Platform Dashboard...")
subprocess.run(cmd_full, check=True)
print(f"Generated: {output_full} (Size: {os.path.getsize(output_full)} bytes)")

# 2. Executive Overview Hero & KPIs
output_hero = os.path.join(ARTIFACT_DIR, "ceo_executive_overview.png")
cmd_hero = [
    CHROME,
    "--headless=new",
    "--hide-scrollbars",
    "--window-size=1440,820",
    f"--screenshot={output_hero}",
    HTML_PATH
]
subprocess.run(cmd_hero, check=True)
print(f"Generated: {output_hero} (Size: {os.path.getsize(output_hero)} bytes)")

print("All screenshots refreshed successfully!")
