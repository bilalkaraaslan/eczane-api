from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re

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
        
        # HTML temizliği ve Regex (Plan B kodumuz)
        temiz_metin = soup.get_text(separator=" ", strip=True)
        temiz_metin = re.sub(r'\s+', ' ', temiz_metin)

        baslik = "ÇAN NÖBETÇİ ECZANELER"
        baslangic = temiz_metin.find(baslik)

        eczane_adi = "Bulunamadı"
        telefon = "Yok"
        adres = "Adres Bulunamadı"

        if baslangic != -1:
            kesit = temiz_metin[baslangic + len(baslik): baslangic + 600]
            
            isim_match = re.search(r'([A-ZİĞÜŞÖÇ\s]{3,30}ECZANESİ)', kesit)
            if isim_match:
                eczane_adi = isim_match.group(1).strip()
            
            tel_match = re.search(r'(0\s?286\s?\d{3}\s?\d{2}\s?\d{2})', kesit)
            if tel_match:
                telefon = tel_match.group(1).replace(" ", "")

            if isim_match and tel_match:
                adres_ham = kesit[isim_match.end():tel_match.start()].strip()
                adres = adres_ham.replace("Haritada görüntülemek için tıklayınız", "").strip()

        return jsonify({
            "eczane": eczane_adi,
            "tel": telefon,
            "adres": adres
        })

    except Exception as e:
        return jsonify({"hata": str(e)})

# Vercel için gerekli handler
if __name__ == '__main__':
    app.run()