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
    hedef_url = "https://www.eczaneler.gen.tr/nobetci-canakkale-can"
    scraper_api_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={hedef_url}"

    try:
        response = requests.get(scraper_api_url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        sayfa_basligi = soup.title.string.strip() if soup.title else "Baslik Yok"

        # Taktik Değişikliği: HTML etiketleri yan yana yapışmasın diye aralarına " | " koyarak tüm metni alıyoruz
        temiz_metin = soup.get_text(separator=" | ", strip=True)
        
        eczane_adi = "Bulunamadı"
        telefon = "Yok"
        adres = "Adres Bulunamadı"

        # "Eczanesi" kelimesini arıyoruz
        eczane_match = re.search(r'([A-ZİĞÜŞÖÇa-zığüşöç\.\s]{3,35}Eczanesi)', temiz_metin, re.IGNORECASE)
        
        if eczane_match:
            # İsmi temizleyip büyük harfe çeviriyoruz
            eczane_adi = eczane_match.group(1).strip().upper()
            
            # Eczane adından sonraki 500 karakteri alıyoruz (Adres ve Tel kesinlikle bu aralıkta)
            kesit = temiz_metin[eczane_match.end():eczane_match.end() + 500]
            
            # Telefonu Ayıklama (Örn: 0 (286) 416 17 55 veya 02864161755 vb.)
            tel_match = re.search(r'(0\s*\(\s*286\s*\)\s*\d{3}\s*\d{2}\s*\d{2}|0?286\s*\d{3}\s*\d{2}\s*\d{2}|0\s*5\d{2}\s*\d{3}\s*\d{2}\s*\d{2})', kesit)
            if tel_match:
                ham_tel = tel_match.group(1)
                telefon = re.sub(r'\D', '', ham_tel) # Sadece rakamları bırak (ESP32 için en iyisi)
            
            # Adresi Ayıklama (" | " işaretleriyle böldüğümüz parçalardan adres olanı seçiyoruz)
            adres_kesit = kesit.split('|')
            for parca in adres_kesit:
                parca = parca.strip()
                # İçinde Mah, Cad, Sokak vb. geçiyorsa adrestir
                if len(parca) > 15 and any(kelime in parca for kelime in ["Mah", "Cad", "Sok", "Bulvar", "Mevki"]):
                    adres = parca
                    break

        tr_saati = datetime.now() + timedelta(hours=3)

        return jsonify({
            "eczane": eczane_adi,
            "tel": telefon,
            "adres": adres,
            "son_guncelleme": tr_saati.strftime("%d.%m.%Y %H:%M"),
            "debug_baslik": sayfa_basligi,
            "debug_metin": temiz_metin[200:600] # Olası bir aksilikte sitenin bize ne gösterdiğini aynen aktaracak
        })

    except Exception as e:
        return jsonify({"hata": str(e)})

if __name__ == '__main__':
    app.run()
