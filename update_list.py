import requests

def run_bebox_engine():
    # المصادر الموثوقة لقنوات العراق واللغة العربية
    sources = [
        "https://iptv-org.github.io/iptv/languages/ara.m3u",
        "https://iptv-org.github.io/iptv/countries/iq.m3u"
    ]
    
    # الكلمات المفتاحية التي تهمك في تطبيق BEBOX
    keywords = ["MBC", "BEIN", "OSN", "AD SPORTS", "KIDS", "NEWS", "KURD", "RUDAW", "IRAQ"]
    
    final_data = "#EXTM3U\n"
    seen_urls = set()
    found_count = 0

    print("جاري فحص المصادر...")

    for url in sources:
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                lines = r.text.splitlines()
                for i in range(len(lines)):
                    if lines[i].startswith("#EXTINF"):
                        info_line = lines[i]
                        stream_url = lines[i+1] if i + 1 < len(lines) else ""
                        
                        # تصفية القنوات حسب اهتماماتك
                        if any(key.upper() in info_line.upper() for key in keywords):
                            if stream_url and stream_url not in seen_urls:
                                # إضافة شعار القناة آلياً إذا لم يكن موجوداً
                                if 'tvg-logo=""' in info_line or 'tvg-logo' not in info_line:
                                    clean_name = info_line.split(',')[-1].strip().lower().replace(" ", "")
                                    logo = f' tvg-logo="https://raw.githubusercontent.com/iptv-org/database/master/logos/{clean_name}.png"'
                                    info_line = info_line.replace("#EXTINF:-1", f"#EXTINF:-1{logo}")
                                
                                final_data += info_line + "\n" + stream_url + "\n"
                                seen_urls.add(stream_url)
                                found_count += 1
        except:
            continue

    # حفظ المنتج النهائي لتطبيقك
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(final_data)
    
    print(f"تم التحديث! تم تجهيز {found_count} قناة لتطبيق BEBOX.")

if __name__ == "__main__":
    run_bebox_engine()
