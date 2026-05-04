import requests

def run_bebox_engine():
    # المصادر العالمية والمحلية
    sources = [
        "https://iptv-org.github.io/iptv/languages/ara.m3u", # العربية
        "https://iptv-org.github.io/iptv/languages/kur.m3u", # الكردية
        "https://iptv-org.github.io/iptv/countries/iq.m3u",  # العراق
        "https://iptv-org.github.io/iptv/index.m3u"          # المصدر العالمي للبحث عن الدول
    ]
    
    # تعريف التصنيفات والكلمات المفتاحية لكل تصنيف
    categories = {
        "KURDISH LOCAL": ["KURD", "RUDAW", "WAAR", "KURDISTAN", "ZAGROS", "ARK", "DUHOK"],
        "BEIN SPORTS (HD/4K)": ["BEIN", "AD SPORTS", "SSC", "KASS"],
        "ARABIC NEWS": ["AL JAZEERA", "ARABIYA", "HADATH", "SKY NEWS ARABIA"],
        "MOVIES & SERIES": ["MBC2", "MBC ACTION", "MBC MAX", "OSN", "NETFLIX", "BOX OFFICE"],
        "USA": ["(US)", "USA"],
        "UK": ["(UK)", "UNITED KINGDOM"],
        "FRANCE": ["(FR)", "FRANCE"],
        "TURKEY": ["(TR)", "TURKISH", "TRT"],
        "GERMANY": ["(DE)", "GERMANY"],
        "IRAN": ["(IR)", "IRANIAN", "PERSIAN"],
        "ITALY": ["(IT)", "ITALY"],
        "NORWAY": ["(NO)", "NORWAY"],
        "SPAIN": ["(ES)", "SPAIN"],
        "PORTUGAL": ["(PT)", "PORTUGAL"]
    }

    final_data = "#EXTM3U\n"
    seen_urls = set()
    found_count = 0

    print("جاري تحليل القنوات وترتيب التصنيفات...")

    for url in sources:
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                lines = r.text.splitlines()
                for i in range(len(lines)):
                    if lines[i].startswith("#EXTINF"):
                        info_line = lines[i]
                        stream_url = lines[i+1] if i + 1 < len(lines) else ""
                        
                        if not stream_url or stream_url in seen_urls:
                            continue

                        # فحص التصنيف المناسب للقناة
                        assigned_group = None
                        for group_name, keywords in categories.items():
                            if any(key.upper() in info_line.upper() for key in keywords):
                                assigned_group = group_name
                                break
                        
                        if assigned_group:
                            # تنظيف اسم القناة وإضافة الشعارات وتحديد المجموعة (group-title)
                            clean_name = info_line.split(',')[-1].strip()
                            logo_name = clean_name.lower().replace(" ", "")
                            
                            # بناء السطر الجديد مع التصنيف
                            new_info = f'#EXTINF:-1 tvg-logo="https://raw.githubusercontent.com/iptv-org/database/master/logos/{logo_name}.png" group-title="{assigned_group}",{clean_name}'
                            
                            final_data += new_info + "\n" + stream_url + "\n"
                            seen_urls.add(stream_url)
                            found_count += 1
        except:
            continue

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(final_data)
    
    print(f"تم بنجاح! تم ترتيب {found_count} قناة ضمن تصنيفات BEBOX.")

if __name__ == "__main__":
    run_bebox_engine()
