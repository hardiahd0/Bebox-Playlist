import requests
import os
import re

# إعدادات ثابتة لتسهيل التعديل مستقبلاً
SOURCES = [
    "https://iptv-org.github.io/iptv/languages/ara.m3u",
    "https://iptv-org.github.io/iptv/languages/kur.m3u",
    "https://iptv-org.github.io/iptv/index.m3u"
]

CATEGORIES_MAP = {
    "KURDISH LOCAL (MANUAL)": r"manual_marker", # وسم خاص للملف اليدوي
    "ARABIC NEWS": r"AL JAZEERA|ARABIYA|HADATH|SKY NEWS|الجزيرة|العربية",
    "KURDISH NEWS (VIP)": r"RUDAW|K24|WAAR|NRT|KURDISTAN|CHANNEL 8",
    "BEIN SPORTS NETWORK": r"BEIN|AFC|XTRA",
    "OSN NETWORK": r"OSN|DISNEY|NICKELODEON",
    "USA CHANNELS": r"USA|\(US\)",
    "FRANCE CHANNELS": r"FRANCE|\(FR\)",
    "TURKEY CHANNELS": r"TURKEY|\(TR\)"
}

def fetch_m3u_content(url):
    """جلب المحتوى مع معالجة الأخطاء والمهلة الزمنية """
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return response.text.splitlines()
    except Exception as e:
        print(f"⚠️ فشل جلب المصدر {url}: {e}")
        return []

def run_bebox_professional_sync():
    categories = {key: [] for key in CATEGORIES_MAP.keys()}
    categories["EUROPE & ASIA"] = [] # فئة احتياطية
    seen_urls = set()

    # 1. معالجة القنوات اليدوية (الأولوية القصوى) [cite: 5, 9]
    if os.path.exists("manual_channels.m3u"):
        print("📂 معالجة القنوات اليدوية...")
        manual_content = fetch_m3u_content("manual_channels.m3u") # أو قراءة الملف محلياً
        # ملاحظة: إذا كان الملف محلياً نستخدم open كما فعلت أنت
        with open("manual_channels.m3u", "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            for i, line in enumerate(lines):
                if line.startswith("#EXTINF") and i+1 < len(lines):
                    url = lines[i+1]
                    if url not in seen_urls:
                        categories["KURDISH LOCAL (MANUAL)"].append(f"{line}\n{url}")
                        seen_urls.add(url)

    # 2. جلب وتصنيف القنوات العالمية [cite: 1, 3]
    for source_url in SOURCES:
        print(f"🌐 جلب القنوات من: {source_url}...")
        content = fetch_m3u_content(source_url)
        
        for i in range(len(content)):
            if content[i].startswith("#EXTINF"):
                info = content[i]
                url = content[i+1] if i+1 < len(content) else ""
                
                # فلاتر الحماية: منع التكرار والتأكد من وجود الرابط [cite: 21]
                if not url or url in seen_urls or not url.startswith("http"):
                    continue
                
                # منطق التصنيف الذكي باستخدام Regex [cite: 7, 20]
                assigned = False
                upper_info = info.upper()
                
                for cat_name, pattern in CATEGORIES_MAP.items():
                    if re.search(pattern, upper_info):
                        # حماية من التداخل (مثال: منع MBC من دخول قائمة USA) 
                        if cat_name == "USA CHANNELS" and "MBC" in upper_info:
                            continue
                            
                        # تنظيف الـ group-title القديم وإضافة الجديد الخاص بتطبيق BeBox [cite: 3]
                        clean_info = re.sub(r'group-title="[^"]*"', '', info)
                        categories[cat_name].append(f'{clean_info} group-title="{cat_name}"\n{url}')
                        assigned = True
                        break
                
                if not assigned:
                    categories["EUROPE & ASIA"].append(f'{info} group-title="OTHERS"\n{url}')
                
                seen_urls.add(url)

    # 3. توليد ملف playlist.m3u النهائي [cite: 1, 14]
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for group_name, channels in categories.items():
            if channels:
                print(f"✅ تم إضافة {len(channels)} قناة إلى {group_name}")
                f.write(f"\n# --- {group_name} ---\n")
                f.write("\n".join(channels) + "\n")

    print("\n✨ تم تحديث القائمة بنجاح! جاهزة للاستخدام في BeBox.")

if __name__ == "__main__":
    run_bebox_professional_sync()
