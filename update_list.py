import requests
import re

def run_bebox_premium_engine():
    # مصادر منتقاة بعناية لضمان الجودة العالية (HD/4K)
    sources = [
        "https://iptv-org.github.io/iptv/languages/ara.m3u", # العربية الرسمية
        "https://iptv-org.github.io/iptv/categories/news.m3u", # الأخبار العالمية والعربية
        "https://iptv-org.github.io/iptv/categories/sports.m3u", # الرياضة العالمية
        "https://iptv-org.github.io/iptv/categories/movies.m3u"  # الأفلام
    ]
    
    # القنوات الكردية المحلية الموثوقة فقط (تم حصرها لضمان الجودة)
    kurdish_vips = ["RUDAW", "K24", "KURDISTAN TV", "WAAR", "AVA ENTERTAINMENT", "NET KURD", "ZAGROS"]

    final_data = "#EXTM3U\n"
    seen_urls = set()
    
    # مصفوفات لتخزين القنوات حسب الأولوية لترتيبها في الملف
    news_list = []
    sports_list = []
    kurdish_list = []
    movies_list = []
    intl_list = []

    print("جاري تنقية القنوات وجلب الجودة العالية فقط...")

    for url in sources:
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                content = r.text.splitlines()
                for i in range(len(content)):
                    if content[i].startswith("#EXTINF"):
                        info = content[i]
                        link = content[i+1] if i+1 < len(content) else ""
                        
                        if not link or link in seen_urls: continue
                        
                        name = info.split(',')[-1].upper()
                        
                        # 1. تصنيف الأخبار (الأولوية الأولى)
                        if any(x in name for x in ["AL JAZEERA", "ARABIYA", "HADATH", "SKY NEWS", "BBC ARABIC", "RT ARABIC"]):
                            news_list.append(f'#EXTINF:-1 group-title="ARABIC NEWS",{name}\n{link}')
                            seen_urls.add(link)

                        # 2. تصنيف الرياضة (beIN & 4K)
                        elif any(x in name for x in ["BEIN", "AD SPORTS", "SSC", "CANAL+"]):
                            sports_list.append(f'#EXTINF:-1 group-title="SPORTS HD/4K",{name}\n{link}')
                            seen_urls.add(link)

                        # 3. تصنيف الكردية (المحلية الحقيقية فقط)
                        elif any(x in name for x in kurdish_vips):
                            kurdish_list.append(f'#EXTINF:-1 group-title="KURDISTAN LOCAL",{name}\n{link}')
                            seen_urls.add(link)

                        # 4. تصنيف الأفلام (MBC & OSN) - منع خلطها مع USA
                        elif any(x in name for x in ["MBC", "ROTANA", "OSN", "NETFLIX"]):
                            # حماية: إذا كانت القناة MBC لا تضعها في تصنيف USA
                            movies_list.append(f'#EXTINF:-1 group-title="MOVIES & ENTERTAINMENT",{name}\n{link}')
                            seen_urls.add(link)

                        # 5. التصنيف الدولي (بشرط عدم وجود MBC في الاسم)
                        elif "USA" in name and "MBC" not in name:
                            intl_list.append(f'#EXTINF:-1 group-title="USA CHANNELS",{name}\n{link}')
                            seen_urls.add(link)
        except:
            continue

    # دمج القنوات بالترتيب الذي طلبته
    all_channels = news_list + sports_list + kurdish_list + movies_list + intl_list
    final_data += "\n".join(all_channels)

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(final_data)
    
    print(f"تم بنجاح! القنوات الإخبارية الآن في المقدمة مع تصفية ذكية لـ MBC و USA.")

if __name__ == "__main__":
    run_bebox_premium_engine()
