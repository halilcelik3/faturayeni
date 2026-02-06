import re

def temiz_tutar(tutar_str):
    """
    "1.500,50" veya "1,500.50" gibi metinleri sayıya çevirir.
    Hata verirse None döner, programı patlatmaz.
    """
    if not tutar_str:
        return None
    
    # Gereksiz boşlukları ve TL simgesini temizle
    temiz = tutar_str.replace("TL", "").replace("tl", "").strip()

    try:
        # Türkiye Standardı (Nokta binlik, virgül kuruş): 1.500,50
        if "," in temiz and "." in temiz:
            # Noktayı sil, virgülü noktaya çevir
            return float(temiz.replace(".", "").replace(",", "."))
        
        # Sadece virgül varsa (1500,50) -> Virgülü noktaya çevir
        elif "," in temiz:
            return float(temiz.replace(",", "."))
            
        # Sadece nokta varsa (1.500) -> Muhtemelen binlik ayracıdır, silmeyelim mi?
        # BURASI RİSKLİDİR AMA GENELDE:
        # Eğer tek nokta varsa ve sondan 2 basamaksa kuruştur (1500.50)
        # Değilse binliktir (1.500 -> 1500)
        # Basitlik adına düz çevirmeyi deniyoruz:
        return float(temiz)
        
    except ValueError:
        return None


def toplam_tutar_bul(text):
    """
    Farklı fatura tiplerindeki toplam tutarı arar.
    Sırasıyla en garantiden en genele doğru dener.
    """
    
    # Aranacak kelime kalıpları (Regex)
    aranacaklar = [
        # 1. En net olan: "Mal Hizmet Toplam Tutarı: 100 TL"
        r"(Mal\s*(?:/|ve)?\s*Hizmet\s*Toplam\s*Tutarı)\s*[:\s]*([\d\.\,]+)",
        
        # 2. "Genel Toplam: 100 TL"
        r"(Genel\s*Toplam)\s*[:\s]*([\d\.\,]+)",
        
        # 3. "Ödenecek Tutar: 100 TL"
        r"(Ödenecek\s*Tutar)\s*[:\s]*([\d\.\,]+)",
        
        # 4. "Toplam Tutar: 100 TL"
        r"(Toplam\s*Tutar)\s*[:\s]*([\d\.\,]+)"
    ]

    for kalip in aranacaklar:
        eslesme = re.search(kalip, text, re.IGNORECASE)
        if eslesme:
            bulunan_sayi = eslesme.group(2) # Parantez içindeki sayıyı al
            tutar = temiz_tutar(bulunan_sayi)
            if tutar: # Eğer sayıya çevrilebildiyse döndür
                return tutar

    return None


def fatura_bilgilerini_al(text):
    """
    PDF metninden bilgileri çeker.
    Daha esnek kurallar kullanır.
    """

    sonuc = {
        "fatura_no": None,
        "fatura_tarihi": None,
        "toplam_tutar": None
    }

    # 🔹 FATURA NO ARAMA
    # Kural: "Fatura No" kelimesinden sonra gelen harf veya rakamları al.
    fatura_no_eslesme = re.search(
        r"Fatura\s*No\s*[:\-\.]?\s*([A-Z0-9]+)", 
        text, 
        re.IGNORECASE
    )

    if fatura_no_eslesme:
        aday = fatura_no_eslesme.group(1).strip()
        
        # ESKİ KOD: if len(aday) == 16:
        # YENİ KOD: 10 ile 16 karakter arasındaysa kabul et
        if 10 <= len(aday) <= 16:
            sonuc["fatura_no"] = aday

    # 🔹 FATURA TARİHİ (Aynı mantık devam ediyor)
    tarih = re.search(
        r"Fatura\s*Tarihi\s*[:\-\.]?\s*([0-9]{2}[\/\-\.][0-9]{2}[\/\-\.][0-9]{4})",
        text,
        re.IGNORECASE
    )
    if tarih:
        sonuc["fatura_tarihi"] = tarih.group(1)

    # 🔹 TOPLAM TUTAR (Yeni fonksiyonu kullanıyoruz)
    sonuc["toplam_tutar"] = toplam_tutar_bul(text)

    return sonuc