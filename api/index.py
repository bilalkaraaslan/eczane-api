# --- BURAYA KENDİ SCRAPER API ANAHTARINI YAPIŞTIR ---
# API_KEY = "31a50f9deacbd9b3e570e7a30a6639aa"

from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

app = Flask(__name__)

# --- KENDİ SCRAPER API ANAHTARINI BURAYA YAZ ---
API_KEY = "31a50f9deacbd9b3e570e7a30a6639aa"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    # HEDEFİ YİNE DEĞİŞTİRDİK: Ağır koruması olmayan haber sitesine gidiyoruz!
    hedef_url = "https://www.cnnturk.com/nobetci-eczaneler/canakkale/can/"
    
    # DİKKAT: render=true KULLANMIYORUZ! (Sistem artık çok daha hızlı olacak)
    scraper_api_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={hedef_url}"

    try:
        response = requests.get(scraper_api_url, timeout=20)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        metin_parcalari = list(soup.stripped_strings)
        sayfa_basligi = soup.title.string.strip() if soup.title else "Baslik Yok"
        
        eczane_adi = "Bulunamadı"
        telefon = "Yok"
        adres = "Adres Bulunamadı"

        for i, parca in enumerate(metin_parcalari):
            # Haber sitesindeki eczane ismini buluyoruz
            if "Eczanesi" in parca and eczane_adi == "Bulunamadı":
                eczane_adi = parca.strip().upper()
                
                # Eczane adını bulduktan sonraki 15 kelimeye bakıp Adres ve Telefonu seçiyoruz
                for j in range(1, 15):
                    if i + j < len(metin_parcalari):
                        son_parca = metin_parcalari[i+j]
                        
                        # --- ADRES YAKALAMA ---
                        if ("Adres" in son_parca or "Mah" in son_parca or "Cad" in son_parca) and adres == "Adres Bulunamadı":
                            # Eğer başında "Adres:" yazıyorsa onu temizleyelim
                            adres = son_parca.replace("Adres:", "").replace("Adres", "").strip()
                            
                        # --- TELEFON YAKALAMA ---
                        if ("Telefon" in son_parca or "286" in son_parca) and telefon == "Yok":
                            # Tüm harf ve boşlukları sil, sadece rakamı al
                            tel_rakam = re.sub(r'\D', '', son_parca)
                            if len(tel_rakam) >= 10:
                                if len(tel_rakam) == 10:
                                    telefon = "0" + tel_rakam
                                else:
                                    telefon = tel_rakam

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
