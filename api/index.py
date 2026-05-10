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
    hedef_url = "https://www.canakkaleeo.org.tr/nobetci-eczaneler"
    
    # İsteği doğrudan eczaneye değil, engelleri aşan ScraperAPI'ye gönderiyoruz
    scraper_api_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={hedef_url}"

    try:
        response = requests.get(scraper_api_url, timeout=45)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        sayfa_basligi = soup.title.string.strip() if soup.title else "Baslik Yok"
        
        temiz_metin = soup.get_text(separator=" ", strip=True)
        temiz_metin = re.sub(r'\s+', ' ', temiz_metin)

        baslik = "ÇAN NÖBETÇİ ECZANELER"
        baslangic = temiz_metin.find(baslik)

        eczane_adi = "Bulunamadı"
        telefon = "Yok"
        adres = "Adres Bulunamadı"

        if baslangic != -1:
            kalan_metin = temiz_metin[baslangic + len(baslik):]
            bitis = kalan_metin.find("NÖBETÇİ ECZANELER")
            
            if bitis != -1:
                kesit = kalan_metin[:bitis]
            else:
                kesit = kalan_metin[:600]

            # --- VERİ AYIKLAMA ---
            isim_match = re.search(r'([A-ZİĞÜŞÖÇ\.\s]{3,35}ECZANESİ)', kesit)
            tarih_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', kesit)

            if isim_match and tarih_match:
                eczane_adi = isim_match.group(1).strip()
                
                i_son = isim_match.end()
                t_bas = tarih_match.start()
                
                if t_bas > i_son:
                    karisik_veri = kesit[i_son:t_bas].strip()
                    
                    # Telefonu Ayıkla
                    tel_pattern = r'(0?(?:286|5\d{2})\s?\d{3}\s?\d{2}\s?\d{2})'
                    tel_match = re.search(tel_pattern, karisik_veri)
                    
                    if tel_match:
                        ham_tel = tel_match.group(1)
                        if len(ham_tel) == 10:
                            telefon = "0" + ham_tel
                        else:
                            telefon = ham_tel.replace(" ", "")
                        adres_temiz = karisik_veri.replace(ham_tel, "")
                    else:
                        adres_temiz = karisik_veri 
                    
                    adres_temiz = adres_temiz.replace("Haritada görüntülemek için tıklayınız", "")
                    adres = adres_temiz.strip()

        # Sunucu saatine 3 saat ekliyoruz (UTC+3 Türkiye Saati)
        tr_saati = datetime.now() + timedelta(hours=3)

        return jsonify({
            "eczane": eczane_adi,
            "tel": telefon,
            "adres": adres,
            "son_guncelleme": tr_saati.strftime("%d.%m.%Y %H:%M"),
            "debug_baslik": sayfa_basligi,
            "debug_kod": response.status_code
        })

    except Exception as e:
        return jsonify({"hata": str(e)})

if __name__ == '__main__':
    app.run()
