import requests
import re
import concurrent.futures

# القنوات التي أرسلتها (يمكنك إضافة المزيد هنا)
RAW_DATA = """
#EXTINF:-1 group-title="спорт",Sky Sports Tennis HD 50 UK
http://qkghrsmq.tvclub.xyz/iptv/S8VNGCFUZYYPDT/6546/index.m3u8
#EXTINF:-1 group-title="News",Rudaw
https://svs.itworkscdn.net/rudawlive/rudawlive.smil/playlist.m3u8
#EXTINF:-1 group-title="спорт",Eurosport 1 FHD orig
http://qkghrsmq.tvclub.xyz/iptv/S8VNGCFUZYYPDT/9026/index.m3u8
""" # أضف بقية الروابط هنا داخل العلامات

def check_link(url):
    """تحقق من أن الرابط يعمل ويعيد كود 200"""
    try:
        # استخدام timeout قصير لعدم تعطيل السكربت
        response = requests.head(url, timeout=3, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def clean_name(info):
    """تنظيف اسم القناة"""
    name = info.split(',')[-1]
    name = re.sub(r'HD|SD|FHD|4K|1080p|orig|UK|GR|PT', '', name, flags=re.IGNORECASE)
    return name.strip()

def process_channel(line, url):
    """معالجة القناة الواحدة: فحصها ثم تصنيفها"""
    if check_link(url):
        name = clean_name(line)
        # تصنيف تلقائي بناءً على الكلمات المفتاحية
        if any(word in line.upper() for word in ["RUDAW", "K24", "NRT", "KURD"]):
            return "KURDISH", f'#EXTINF:-1 group-title="KURDISH",{name}\n{url}'
        else:
            return "SPORT Global", f'#EXTINF:-1 group-title="SPORT Global",{name}\n{url}'
    return None, None

def run_bebox_validator():
    print("🔍 جاري فحص الروابط وتنظيف القائمة... يرجى الانتظار")
    lines = RAW_DATA.strip().splitlines()
    channels_to_check = []
    
    # تحضير الروابط للفحص
    for i in range(0, len(lines), 2):
        if lines[i].startswith("#EXTINF"):
            channels_to_check.append((lines[i], lines[i+1]))

    results = {"KURDISH": [], "SPORT Global": []}

    # استخدام ThreadPoolExecutor لتسريع عملية الفحص (فحص روابط متعددة في وقت واحد)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(process_channel, c[0], c[1]): c for c in channels_to_check}
        for future in concurrent.futures.as_completed(future_to_url):
            category, formatted_line = future.result()
            if category:
                results[category].append(formatted_line)

    # حفظ الملف النهائي
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for category, playlist in results.items():
            if playlist:
                f.write(f"\n# --- {category} ---\n")
                f.write("\n".join(playlist) + "\n")

    print(f"✅ تم الانتهاء! تم العثور على {len(results['KURDISH']) + len(results['SPORT Global'])} قناة تعمل.")

if __name__ == "__main__":
    run_bebox_validator()
