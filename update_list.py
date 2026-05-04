import requests

def fetch_and_clean():
    # روابط المصادر العالمية الموثوقة
    sources = [
        "https://iptv-org.github.io/iptv/countries/iq.m3u", # العراق
        "https://iptv-org.github.io/iptv/languages/ara.m3u"  # القنوات العربية
    ]
    
    combined_content = "#EXTM3U\n"
    urls_found = set()

    for url in sources:
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                lines = r.text.splitlines()
                for i in range(len(lines)):
                    if lines[i].startswith("#EXTINF"):
                        # جلب رابط القناة الذي يليه مباشرة
                        if i + 1 < len(lines):
                            stream_url = lines[i+1]
                            if stream_url not in urls_found:
                                combined_content += lines[i] + "\n" + stream_url + "\n"
                                urls_found.add(stream_url)
        except:
            continue

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(combined_content)
    print(f"تم تحديث القائمة بنجاح! إجمالي القنوات: {len(urls_found)}")

if __name__ == "__main__":
    fetch_and_clean()
