import requests
import re
import concurrent.futures
import os

# وظيفة لقراءة ملف القنوات اليدوية
def get_manual_channels():
    file_path = 'manual_channels.m3u'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def check_link(url):
    try:
        # تقليل الـ timeout لتجنب فشل الـ Action بسبب الوقت
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

# ... (بقية دوال التنظيف والتصنيف كما هي) ...

def run_bebox_sync():
    print("📖 قراءة القنوات اليدوية من الملف...")
    raw_manual = get_manual_channels()
    
    final_collections = {"KURDISH": [], "SPORT Global": [], "GENERAL": []}
    seen_urls = set()

    # معالجة البيانات
    lines = raw_manual.strip().splitlines()
    tasks = []
    for i in range(0, len(lines)):
        if lines[i].startswith("#EXTINF") and i + 1 < len(lines):
            tasks.append((lines[i], lines[i+1]))

    print(f"🔍 فحص {len(tasks)} قناة...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_channel, t[0], t[1]) for t in tasks]
        for future in concurrent.futures.as_completed(futures):
            cat, entry = future.result()
            if cat and entry:
                url = entry.splitlines()[-1]
                if url not in seen_urls:
                    final_collections[cat].append(entry)
                    seen_urls.add(url)

    # حفظ النتيجة في playlist.m3u
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for group in ["KURDISH", "SPORT Global", "GENERAL"]:
            if final_collections[group]:
                f.write(f"\n# --- {group} ---\n")
                f.write("\n".join(final_collections[group]) + "\n")
    print("✅ تم تحديث playlist.m3u بنجاح!")

if __name__ == "__main__":
    run_bebox_sync()
