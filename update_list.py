import requests
import os
import re

# المصادر العالمية المعتمدة [cite: 1, 29]
SOURCES = [
    "https://iptv-org.github.io/iptv/languages/ara.m3u",
    "https://iptv-org.github.io/iptv/languages/kur.m3u",
    "https://iptv-org.github.io/iptv/index.m3u"
]

# خريطة التصنيف التلقائي [cite: 7, 30, 44]
CATEGORIES_MAP = {
    "ARABIC NEWS": r"AL JAZEERA|ARABIYA|HADATH|SKY NEWS|الجزيرة|العربية",
    "KURDISH NEWS (VIP)": r"RUDAW|K24|WAAR|NRT|KURDISTAN|CHANNEL 8",
    "BEIN SPORTS NETWORK": r"BEIN|AFC|XTRA",
    "OSN NETWORK": r"OSN|DISNEY|NICKELODEON",
    "USA CHANNELS": r"USA|\(US\)",
    "FRANCE CHANNELS": r"FRANCE|\(FR\)",
    "TURKEY CHANNELS": r"TURKEY|\(TR\)"
}

def is_link_working(url):
    """فحص ما إذا كان الرابط يعمل (Status 200) """
    try:
        # نستخدم HEAD بدلاً من GET لتسريع العملية وتقليل استهلاك البيانات
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def run_bebox_validated_sync():
    categories = {key: [] for key in CATEGORIES_MAP.keys()}
    categories["EUROPE & ASIA"] = [] 
    seen_urls = set()

    # 1. معالجة القنوات اليدوية (نفترض دائماً أنها تعمل أو تهم المستخدم) [cite: 9, 31, 57]
    if os.path.exists("manual_channels.m3u"):
        with open("manual_channels.m3u", "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            for i, line in enumerate(lines):
                if line.startswith("#EXTINF") and i+1 < len(lines):
                    url = lines[i+1].strip()
                    if url and url not in seen_urls:
                        group_match = re.search(r'group-title="([^"]*)"', line)
                        group_name = group_match.group(1) if group_match else "MANUAL UPDATES"
                        if group_name not in categories: categories[group_name] = []
                        categories[group_name].append(f"{line}\n{url}")
                        seen_urls.add(url)

    # 2. جلب وتصفية القنوات العالمية مع الفحص [cite: 33, 59, 64]
    for source_url in SOURCES:
        try:
            r = requests.get(source_url, timeout=20) [cite: 19]
            if r.status_code == 200:
                content = r.text.splitlines()
                for i in range(len(content)):
                    if content[i].startswith("#EXTINF"):
                        info, url = content[i], (content[i+1] if i+1 < len(content) else "")
                        
                        # فلاتر الحماية والفحص [cite: 21, 34, 54]
                        if not url or url in seen_urls or not url.startswith("http"): continue
                        
                        # تفعيل فاحص الروابط (اختياري: يمكنك تعطيله لتسريع السكربت)
                        if not is_link_working(url): continue 

                        upper_info = info.upper()
                        assigned = False
                        for cat_name, pattern in CATEGORIES_MAP.items():
                            if re.search(pattern, upper_info): [cite: 20, 43]
                                if cat_name == "USA CHANNELS" and "MBC" in upper_info: continue [cite: 8, 46]
                                clean_info = re.sub(r'group-title="[^"]*"', '', info) [cite: 45]
                                categories[cat_name].append(f'{clean_info} group-title="{cat_name}"\n{url}')
                                assigned = True
                                break
                        
                        if not assigned:
                            categories["EUROPE & ASIA"].append(f'{info} group-title="OTHERS"\n{url}')
                        seen_urls.add(url)
        except: continue

    # 3. بناء الملف النهائي [cite: 39]
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for group in categories:
            if categories[group]:
                f.write(f"\n# --- {group} ---\n" + "\n".join(categories[group]) + "\n")

if __name__ == "__main__":
    run_bebox_validated_sync()
