from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    # Tarayıcı taklidi yap
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0'
    }
    url = "https://www.canakkaleeo.org.tr/nobetci-eczaneler"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # HTML temizliği
        temiz_metin = soup.get_text(separator=" ", strip=True)
        temiz_metin = re.sub(r'\s+', ' ', temiz_metin)

        # --- ÇAN BÖLGESİ İZOLE ---
        baslik = "ÇAN NÖBETÇİ ECZANELER"
        baslangic = temiz_metin.find(baslik)

        eczane_adi = "Bulunamadı"
        telefon = "Yok"
        adres = "Adres Bulunamadı"

        if baslangic != -1:
            kalan_metin = temiz_metin[baslangic + len(baslik):]
            # Bir sonraki ilçeye taşmamak için fren noktası
            bitis = kalan_metin.find("NÖBETÇİ ECZANELER")
            
            if bitis != -1:
                kesit = kalan_metin[:bitis]
            else:
                kesit = kalan_metin[:600]

            # --- VERİ AYIKLAMA ---

            # 1. İSİM BUL
            isim_match = re.search(r'([A-ZİĞÜŞÖÇ\.\s]{3,35}ECZANESİ)', kesit)
            
            # 2. TARİH BUL (Referans Noktası)
            tarih_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', kesit)

            if isim_match and tarih_match:
                eczane_adi = isim_match.group(1).strip()
                
                # İsim ile Tarih arasındaki her şeyi al (Adres + Tel karışık)
                i_son = isim_match.end()
                t_bas = tarih_match.start()
                
                if t_bas > i_son:
                    karisik_veri = kesit[i_son:t_bas].strip()
                    
                    # --- TELEFON AYIKLAMA ---
                    # 286 veya 5xx ile başlayan numaraları bul (Başında 0 opsiyonel)
                    tel_pattern = r'(0?(?:286|5\d{2})\s?\d{3}\s?\d{2}\s?\d{2})'
                    tel_match = re.search(tel_pattern, karisik_veri)
                    
                    if tel_match:
                        ham_tel = tel_match.group(1)
                        # Başına 0 ekleme standardı
                        if len(ham_tel) == 10:
                            telefon = "0" + ham_tel
                        else:
                            telefon = ham_tel.replace(" ", "")
                        
                        # Telefonu adresten SİL
                        adres_temiz = karisik_veri.replace(ham_tel, "")
                    else:
                        adres_temiz = karisik_veri # Tel yoksa olduğu gibi bırak
                    
                    # Son temizlikler
                    adres_temiz = adres_temiz.replace("Haritada görüntülemek için tıklayınız", "")
                    adres = adres_temiz.strip()

        return jsonify({
            "eczane": eczane_adi,
            "tel": telefon,
            "adres": adres,
            "son_guncelleme": datetime.now().strftime("%d.%m.%Y %H:%M")
        })

    except Exception as e:
        return jsonify({"hata": str(e)})

if __name__ == '__main__':
    app.run()
