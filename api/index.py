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
    
    # RENDER=TRUE GERİ GELDİ! (Cloudflare ekranında o 10 saniyeyi beklemek zorundayız)
    scraper_api_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={hedef_url}&render=true"

    try:
        response = requests.get(scraper_api_url, timeout=45)
        soup = BeautifulSoup(response.content, 'html.parser')
        sayfa_basligi = soup.title.string.strip() if soup.title else "Baslik Yok"

        # Sitedeki tüm metin parçalarını sırayla bir listeye diziyoruz
        metin_parcalari = list(soup.stripped_strings)
        
        eczane_adi = "Bulunamadı"
        telefon = "Yok"
        adres = "Adres Bulunamadı"

        # Listede sırayla gezip "Eczanesi" kelimesini avlıyoruz
        for i, parca in enumerate(metin_parcalari):
            if "Eczanesi" in parca and eczane_adi == "Bulunamadı":
                eczane_adi = parca.upper()
                
                # Eczane ismini bulduğumuz yerden itibaren sonraki 15 kelimeye bakıp Tel ve Adresi çekiyoruz
                for j in range(1, 15):
                    if i + j < len(metin_parcalari):
                        sonraki = metin_parcalari[i+j]
                        
                        # Telefon Numarasını Yakalama (286 veya 5xx ile başlıyorsa)
                        if ("286" in sonraki or "5" in sonraki) and telefon == "Yok":
                            tel_kullanim = re.sub(r'\D', '', sonraki)
                            if len(tel_kullanim) >= 10:
                                telefon = tel_kullanim
                                
                        # Adresi Yakalama (Mah, Cad, Sok vb. kelimeler varsa adrestir)
                        if any(k in sonraki for k in ["Mah", "Cad", "Sok", "No:", "Blv", "Mevki"]) and adres == "Adres Bulunamadı":
                            adres = sonraki

        tr_saati = datetime.now() + timedelta(hours=3)

        return jsonify({
            "eczane": eczane_adi,
            "tel": telefon,
            "adres": adres,
            "son_guncelleme": tr_saati.strftime("%d.%m.%Y %H:%M"),
            "debug_baslik": sayfa_basligi,
            # EĞER YİNE BULAMAZSA BİZE SİTENİN İÇİNDEKİ HAM METNİ GETİRECEK
            "debug_metin": " ".join(metin_parcalari)[:1500] 
        })

    except Exception as e:
        return jsonify({"hata": str(e)})

if __name__ == '__main__':
    app.run()
