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
    scraper_api_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={hedef_url}&render=true"

    try:
        response = requests.get(scraper_api_url, timeout=45)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Sitedeki tüm anlamlı metinleri listeye döküyoruz
        metin_parcalari = list(soup.stripped_strings)
        
        eczane_adi = "Bulunamadı"
        telefon = "Yok"
        adres = "Adres Bulunamadı"

        for i, parca in enumerate(metin_parcalari):
            # "Eczanesi" veya "Eczanesi" (büyük/küçük duyarsız) arıyoruz
            if "ECZANESİ" in parca.upper() and eczane_adi == "Bulunamadı":
                eczane_adi = parca.upper()
                
                # Eczane isminden sonraki parçaları tarayarak adres ve telefonu buluyoruz
                for j in range(1, 25): # Arama menzilini 25 parçaya çıkardık
                    if i + j < len(metin_parcalari):
                        sonraki = metin_parcalari[i+j]
                        
                        # --- TELEFON YAKALAMA (Daha Esnek Mantık) ---
                        # Parçadaki tüm rakamları ayıklıyoruz
                        sadece_rakam = re.sub(r'\D', '', sonraki)
                        if telefon == "Yok":
                            # 10 haneli (286...) veya 11 haneli (0286...) kontrolü
                            if (len(sadece_rakam) == 10 or len(sadece_rakam) == 11) and (sadece_rakam.startswith('286') or sadece_rakam.startswith('0286') or sadece_rakam.startswith('05') or sadece_rakam.startswith('5')):
                                if len(sadece_rakam) == 10:
                                    telefon = "0" + sadece_rakam
                                else:
                                    telefon = sadece_rakam
                        
                        # --- ADRES YAKALAMA ---
                        if adres == "Adres Bulunamadı":
                            if any(kelime in sonraki for kelime in ["Mah", "Cad", "Sok", "No:", "Blv", "Mevki", "Yolu"]):
                                # Adres, telefon numarasıyla aynı parça içinde değilse kaydet
                                if not re.sub(r'\D', '', sonraki).startswith(('0286', '286')):
                                    adres = sonraki

        # Zaman Ayarı (UTC+3)
        tr_saati = datetime.now() + timedelta(hours=3)

        return jsonify({
            "eczane": eczane_adi,
            "tel": telefon,
            "adres": adres,
            "son_guncelleme": tr_saati.strftime("%d.%m.%Y %H:%M")
        })

    except Exception as e:
        return jsonify({"hata": str(e)})

if __name__ == '__main__':
    app.run()
