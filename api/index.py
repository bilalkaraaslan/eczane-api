# --- BURAYA KENDİ SCRAPER API ANAHTARINI YAPIŞTIR ---
# API_KEY = "31a50f9deacbd9b3e570e7a30a6639aa"


from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    hedef_url = "https://www.cnnturk.com/nobetci-eczaneler/canakkale/can/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(hedef_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        metin_parcalari = list(soup.stripped_strings)
        
        eczane_adi = "Bulunamadı"
        telefon = "Yok"
        adres = "Adres Bulunamadı"

        for i, parca in enumerate(metin_parcalari):
            if "Eczanesi" in parca and eczane_adi == "Bulunamadı":
                eczane_adi = parca.strip().upper()
                
                for j in range(1, 15):
                    if i + j < len(metin_parcalari):
                        son_parca = metin_parcalari[i+j].strip()
                        
                        # --- ADRES YAKALAMA ---
                        if "Adres" in son_parca and adres == "Adres Bulunamadı":
                            adres_adayi = son_parca.replace("Adres:", "").replace("Adres", "").strip()
                            
                            if len(adres_adayi) > 3:
                                adres = adres_adayi
                            else:
                                if i + j + 1 < len(metin_parcalari):
                                    adres = metin_parcalari[i+j+1].strip()
                                    
                        # --- TELEFON YAKALAMA ---
                        if ("Telefon" in son_parca or "286" in son_parca) and telefon == "Yok":
                            tel_rakam = re.sub(r'\D', '', son_parca)
                            if len(tel_rakam) >= 10:
                                if len(tel_rakam) == 10:
                                    telefon = "0" + tel_rakam
                                else:
                                    telefon = tel_rakam

        tr_saati = datetime.now() + timedelta(hours=3)

        # ESP32 için sadece en hayati 4 veri gönderiliyor
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
