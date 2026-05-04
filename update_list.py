import requests

def fetch_and_filter():
    # المصادر العالمية
    sources = [
        "https://iptv-org.github.io/iptv/languages/ara.m3u", # العربية
        "https://iptv-org.github.io/iptv/countries/iq.m3u",  # العراقية
        "https://iptv-org.github.io/iptv/countries/tr.m3u"   # التركية (اختياري)
    ]
    
    # الكلمات المفتاحية التي تريد الإبقاء عليها فقط
    # يمكنك إضافة أي اسم قناة هنا (بالعربية أو الإنجليزية)
    keywords = [
        "MBC", "BEIN", "OSN", "AD SPORTS", "KIDS", "NEWS", 
        "KURD", "WAR", "RUDAW", "IRAQ", "AL JAZEERA", "ROTANA"
    ]
    
    final_playlist = "#EXTM3U\n"
    urls_found = set()
    count = 0

    for url in sources:
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                lines = r.text.splitlines()
                for i in range(len(lines)):
                    if lines[i].startswith("#EXTINF"):
                        info_line = lines[i]
                        stream_url = lines[i+1] if i + 1 < len(lines) else ""
                        
                        # فحص ما إذا كانت القناة تحتوي على أحد الكلمات المفتاحية
                        if any(key.upper() in info_line.upper() for key in keywords):
                            if stream_url and stream_url not in urls_found:
                                final_playlist += info_line + "\n" + stream_url + "\n"
                                urls_found.add(stream_url)
                                count += 1
        except:
            continue

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(final_playlist)
    
    print(f"تمت الفلترة! حصلنا على {count} قناة مختارة بعناية لتطبيق BEBOX.")

if __name__ == "__main__":
    fetch_and_filter()
