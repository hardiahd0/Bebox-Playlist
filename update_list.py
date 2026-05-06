import requests
import os
import re

# Expanded sources for maximum Kurdish & Global coverage
SOURCES = [
    "https://iptv-org.github.io/iptv/languages/kur.m3u", # Primary Kurdish
    "https://iptv-org.github.io/iptv/countries/iq.m3u",    # Iraq (Contains many Kurdish)
    "https://iptv-org.github.io/iptv/countries/tr.m3u",    # Turkey (Contains Kurdish channels)
    "https://iptv-org.github.io/iptv/languages/ara.m3u", # Arabic News
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/kur.m3u" # Deep crawl
]

def is_link_working(url):
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def run_bebox_kurdish_max():
    print("Starting Deep Sync for Kurdish Channels...")
    seen_urls = set()
    # Organized groups for BeBox app
    kurdish_channels = []
    other_channels = []
    
    # 1. Load manual channels (Top Priority)
    if os.path.exists("manual_channels.m3u"):
        with open("manual_channels.m3u", "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            for i, line in enumerate(lines):
                if line.startswith("#EXTINF") and i+1 < len(lines):
                    url = lines[i+1].strip()
                    if url:
                        kurdish_channels.append(f"{line}\n{url}")
                        seen_urls.add(url)

    # 2. Advanced filtering for Kurdish content
    kurdish_keywords = r"RUDAW|K24|KURDISTAN|NRT|WAAR|ZAGROS|SPREDA|ARK|PELISTANK|RONAHI|ARYEN|STRK|KNN|CHANNEL8|KURD"

    for source_url in SOURCES:
        try:
            r = requests.get(source_url, timeout=20)
            if r.status_code == 200:
                content = r.text.splitlines()
                for i in range(len(content)):
                    if content[i].startswith("#EXTINF"):
                        info = content[i]
                        url = content[i+1].strip() if i+1 < len(content) else ""
                        
                        if not url or url in seen_urls: continue
                        
                        # Check if channel is Kurdish using Regex
                        if re.search(kurdish_keywords, info.upper()):
                            # Clean and assign to Kurdish Group
                            clean_info = re.sub(r'group-title="[^"]*"', '', info)
                            kurdish_channels.append(f'{clean_info} group-title="KURDISH MAX"\n{url}')
                            seen_urls.add(url)
                        elif "AL JAZEERA" in info.upper() or "ARABIYA" in info.upper():
                            other_channels.append(f'{info} group-title="NEWS"\n{url}')
                            seen_urls.add(url)
        except: continue

    # 3. Final M3U Generation
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        if kurdish_channels:
            f.write("\n# --- KURDISH MAX (APPROX 100 CHANNELS) ---\n")
            f.write("\n".join(kurdish_channels) + "\n")
        if other_channels:
            f.write("\n# --- GLOBAL NEWS ---\n")
            f.write("\n".join(other_channels) + "\n")
            
    print(f"Sync Finished. Found {len(kurdish_channels)} Kurdish channels.")

if __name__ == "__main__":
    run_bebox_kurdish_max()
