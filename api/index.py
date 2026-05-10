# --- BURAYA KENDİ SCRAPER API ANAHTARINI YAPIŞTIR ---
# API_KEY = "31a50f9deacbd9b3e570e7a30a6639aa"

from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

app = Flask(__name__)

# --- BURAYA KENDİ SCRAPER API ANAHTARINI YAPIŞTIR ---
API_KEY = "31a50f9deacbd9b3e570e7a30a6639aa"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    # HEDEFİ DEĞİŞTİRDİK! Artık doğrudan açık kaynaklı rehbere gidiyoruz.
    hedef_url = "https://www.eczaneler.gen.tr/nobetci-canakkale-can"
    
    # Premium veya render'a gerek yok, bu site çok daha rahat ve hızlı!
    scraper_api_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={hedef_url}"

    try:
        response = requests.get(scraper_api_url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        sayfa_basligi = soup.title.string.strip() if soup.title else "Baslik Yok"

        eczane_adi = "Bulunamadı"
        telefon = "Yok"
        adres = ""

        # Eczaneler sitesinde telefonlar hep aranabilir (tel:) link formatındadır
        tel_links = soup.find_all('a', href=re.compile(r'^tel:'))
        
        if tel_links:
            # İlk sıradaki güncel nöbetçidir
            for tel_link in tel_links:
                tel_text = tel_link.get_text(strip=True)
                
                # Telefon numarasının olduğu tablo satırını veya kutuyu bul
                container = tel_link.find_parent(['tr', 'div', 'li'])
                
                if container:
                    metinler = list(container.stripped_strings)
                    
                    # İçinde "Eczanesi" geçiyorsa doğru bloğu bulduk demektir
                    if any("Eczanesi" in m for m in metinler):
                        # Telefonu sadece rakamlara dönüştür (02864161755 formatı)
                        telefon = re.sub(r'\D', '', tel_text)
                        
                        for m in metinler:
                            if "Eczanesi" in m and eczane_adi == "Bulunamadı":
                                eczane_adi = m
                            elif ("Mah" in m or "Cad" in m or "Sok" in m or "No:" in m) and m not in eczane_adi and m not in tel_text:
                                adres += m + " "
                        
                        adres = adres.replace('»', '').strip()
                        if not adres:
                            adres = "Adres Bulunamadı"
                        
                        # Doğru veriyi bulduğumuz an döngüyü bitir
                        break

        tr_saati = datetime.now() + timedelta(hours=3)

        return jsonify({
            "eczane": eczane_adi,
            "tel": telefon,
            "adres": adres,
            "son_guncelleme": tr_saati.strftime("%d.%m.%Y %H:%M"),
            "debug_baslik": sayfa_basligi
        })

    except Exception as e:
        return jsonify({"hata": str(e)})

if __name__ == '__main__':
    app.run()


