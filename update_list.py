import requests
import re
import os
import concurrent.futures

# ملفات المشروع
MANUAL_FILE = 'manual_channels.m3u'
OUTPUT_FILE = 'playlist.m3u'

def check_link(url):
    try:
        # استخدام GET مع استجابة جزئية لتوفير الوقت
        r = requests.get(url, timeout=5, stream=True)
        return r.status_code == 200
    except:
        return False

def clean_name(info):
    name = info.split(',')[-1]
    name = re.sub(r'\(.*?\)|\[.*?\]|HD|SD|FHD|4K|1080p|orig|UK|GR|PT', '', name, flags=re.IGNORECASE)
    return name.strip()

def process_channel(line, url):
    if check_link(url):
        name = clean_name(line)
        info_upper = line.upper()
        # تصنيف ذكي
        if any(w in info_upper for w in ["KURD", "RUDAW", "K24", "NRT", "AVA", "GK", "ZAROK"]):
            cat = "KURDISH"
        elif any(w in info_upper for w in ["SPORT", "SKY", "BEIN", "ARENA", "DAZN", "ELEVEN"]):
            cat = "SPORT Global"
        else:
            cat = "GENERAL"
        
        # الحفاظ على اللوجو إن وجد
        logo = ""
        logo_match = re.search(r'tvg-logo="([^"]+)"', line)
        if logo_match:
            logo = f' tvg-logo="{logo_match.group(1)}"'
            
        return cat, f'#EXTINF:-1{logo} group-title="{cat}",{name}\n{url}'
    return None, None

def run_sync():
    if not os.path.exists(MANUAL_FILE):
        print(f"❌ Error: {MANUAL_FILE} not found!")
        return

    with open(MANUAL_FILE, 'r', encoding='utf-8') as f:
        content = f.read().splitlines()

    tasks = []
    for i in range(len(content)):
        if content[i].startswith("#EXTINF") and i+1 < len(content):
            tasks.append((content[i], content[i+1].strip()))

    final_list = {"KURDISH": [], "SPORT Global": [], "GENERAL": []}
    
    print(f"🔍 Checking {len(tasks)} links...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_channel, t[0], t[1]) for t in tasks]
        for future in concurrent.futures.as_completed(futures):
            cat, result = future.result()
            if cat:
                final_list[cat].append(result)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for group in ["KURDISH", "SPORT Global", "GENERAL"]:
            if final_list[group]:
                f.write(f"\n# --- {group} ---\n")
                f.write("\n".join(final_list[group]) + "\n")
    print("✅ Done!")

if __name__ == "__main__":
    run_sync()
