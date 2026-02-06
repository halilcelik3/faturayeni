import os
import pdfplumber
import pandas as pd
from modul2 import fatura_bilgilerini_al

# OCR Araçlarını Güvenli Bir Şekilde Çağıralım
try:
    import pytesseract
    from pdf2image import convert_from_path
    
    # Yolları ayarla
    user_home = os.path.expanduser("~")
    tesseract_exe = os.path.join(user_home, "AppData", "Local", "Programs", "Tesseract-OCR", "tesseract.exe")
    
    # Tesseract gerçekten orada mı?
    if os.path.exists(tesseract_exe):
        pytesseract.pytesseract.tesseract_cmd = tesseract_exe
        OCR_HAZIR = True
    else:
        OCR_HAZIR = False
except ImportError:
    OCR_HAZIR = False

# Poppler Yolunu Ayarla
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POPPLER_PATH = os.path.join(BASE_DIR, "poppler", "Library", "bin")
POPPLER_VAR_MI = os.path.exists(POPPLER_PATH)


def pdflerden_faturalari_oku(pdf_klasoru):
    sonuclar = []

    for dosya in os.listdir(pdf_klasoru):
        if dosya.lower().endswith(".pdf"):
            pdf_yolu = os.path.join(pdf_klasoru, dosya)
            tam_metin = ""
            yontem = "Normal"

            try:
                # 1. ADIM: Her zaman normal okumayı dene
                with pdfplumber.open(pdf_yolu) as pdf:
                    for sayfa in pdf.pages:
                        sayfa_metin = sayfa.extract_text()
                        if sayfa_metin:
                            tam_metin += sayfa_metin + "\n"

                # 2. ADIM: Metin bulunamadıysa OCR'ı dene (Eğer araçlar varsa)
                if len(tam_metin.strip()) < 10:
                    if OCR_HAZIR and POPPLER_VAR_MI:
                        print(f"🔍 {dosya} için OCR başlatılıyor...")
                        resimler = convert_from_path(pdf_yolu, poppler_path=POPPLER_PATH)
                        for resim in resimler:
                            tam_metin += pytesseract.image_to_string(resim, lang='tur') + "\n"
                        yontem = "OCR"
                    else:
                        print(f"⚠️ {dosya} resim formatında ancak OCR araçları eksik. Atlanıyor.")
                        yontem = "Başarısız (OCR Yok)"

                # Bilgileri ayıkla
                bilgi = fatura_bilgilerini_al(tam_metin)

                sonuclar.append({
                    "dosya": dosya,
                    "fatura_no": bilgi.get("fatura_no"),
                    "toplam_tutar": bilgi.get("toplam_tutar"),
                    "yontem": yontem
                })

            except Exception as e:
                sonuclar.append({"dosya": dosya, "hata": str(e)})

    return pd.DataFrame(sonuclar)