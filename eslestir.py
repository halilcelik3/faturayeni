import os
import sys
import logging
from datetime import datetime

# Mevcut modüller
from modul1 import excelden_faturalari_oku
from modul3 import pdflerden_faturalari_oku
from modul4 import excel_pdf_eslestir
from modul5 import referans_baslangiclarini_oku

# YENİ EKLENEN MODÜLLER
from modul6 import pdfleri_tasi_ve_isimlendir
from modul7 import pdfye_referans_yaz


# ===============================
# PATH TESPİTİ (EXE + PY UYUMLU)
# ===============================
if getattr(sys, 'frozen', False):
    ana_klasor = os.path.dirname(sys.executable)
else:
    ana_klasor = os.path.dirname(os.path.abspath(__file__))

excel_yolu = os.path.join(ana_klasor, "Fatura Örneklem.xlsx")
pdf_klasoru = os.path.join(ana_klasor, "Pdfler")
referans_excel = os.path.join(ana_klasor, "REFERANS_BASLANGIC.xlsx")


# ===============================
# 🔹 SONUC KLASÖRÜ
# ===============================
sonuc_klasoru = os.path.join(ana_klasor, "sonuc")
os.makedirs(sonuc_klasoru, exist_ok=True)


# ===============================
# LOG AYARLARI
# ===============================
log_dosyasi = os.path.join(
    sonuc_klasoru,
    f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
)

logging.basicConfig(
    filename=log_dosyasi,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def main():
    print("=== FATURA EŞLEŞTİRME OTOMASYONU BAŞLADI ===")
    logging.info("Otomasyon başlatıldı")

    try:
        # === MODÜL 1: EXCEL OKU ===
        logging.info("Excel okunuyor...")
        print(">> Excel okunuyor...")
        df_excel = excelden_faturalari_oku(excel_yolu)
        logging.info(f"Excel kayıt sayısı: {len(df_excel)}")

        # === MODÜL 3: PDF OKU ===
        logging.info("PDF'ler okunuyor...")
        print(">> PDF'ler taranıyor...")
        df_pdf = pdflerden_faturalari_oku(pdf_klasoru)
        logging.info(f"PDF kayıt sayısı: {len(df_pdf)}")

        # === MODÜL 5: SAYAÇLARI AL ===
        logging.info("Referans başlangıç sayaçları okunuyor...")
        baslangic_sayaclari = referans_baslangiclarini_oku(referans_excel)

        # === MODÜL 4: EŞLEŞTİR VE KOD ÜRET ===
        logging.info("Eşleştirme yapılıyor...")
        print(">> Eşleştirme ve kod üretimi yapılıyor...")
        df_sonuc = excel_pdf_eslestir(
            df_excel,
            df_pdf,
            baslangic_sayaclari
        )

        # ===============================
        # 🔹 RAPOR ÇIKTISI (EXCEL)
        # ===============================
        cikti_yolu = os.path.join(
            sonuc_klasoru,
            f"eslestirme_sonucu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        df_sonuc.to_excel(cikti_yolu, index=False)
        print(f"✔ Rapor oluşturuldu: {cikti_yolu}")
        logging.info(f"Excel raporu kaydedildi: {cikti_yolu}")

        # ===============================
        # 🔹 MODÜL 6: DOSYA TAŞIMA VE İSİMLENDİRME
        # ===============================
        print(">> Dosyalar taşınıyor ve isimlendiriliyor (Modül 6)...")
        logging.info("Dosya taşıma işlemi başladı.")
        
        tasima_sonuclari = pdfleri_tasi_ve_isimlendir(df_sonuc, pdf_klasoru, ana_klasor)

        # Taşıma işleminin loglanması
        for dosya, mesaj in tasima_sonuclari:
            logging.info(f"TAŞIMA: {dosya} -> {mesaj}")

        # ===============================
        # 🔹 MODÜL 7: PDF ÜZERİNE REFERANS YAZMA (DAMGALAMA)
        # ===============================
        print(">> PDF üzerine referanslar yazılıyor (Modül 7)...")
        logging.info("Referans damgalama işlemi başladı.")

        # Modül 6, dosyaları "Referans Tarama/HARF/" altına taşıdı.
        # Şimdi o yolları bulup Modül 7'yi çalıştıracağız.
        
        referans_ana_path = os.path.join(ana_klasor, "Referans Tarama")

        for dosya_eski_adi, mesaj in tasima_sonuclari:
            # Sadece başarıyla taşınanlara işlem yap
            if "Taşındı" in mesaj:
                try:
                    # Mesaj şuna benziyor: "Taşındı → F-150.114.pdf"
                    yeni_dosya_adi = mesaj.split("→")[1].strip()
                    
                    # Dosya isminin başındaki harfi al (Örn: F, G, E...)
                    harf_klasoru = yeni_dosya_adi.split("-")[0]
                    
                    # Tam dosya yolunu oluştur
                    yeni_tam_yol = os.path.join(referans_ana_path, harf_klasoru, yeni_dosya_adi)
                    
                    # Üzerine yazılacak kod (dosya adının uzantısız hali)
                    basilacak_kod = os.path.splitext(yeni_dosya_adi)[0]

                    # Modül 7'yi çağır
                    sonuc_damga = pdfye_referans_yaz(yeni_tam_yol, basilacak_kod)
                    
                    logging.info(f"DAMGALAMA: {sonuc_damga['durum']} ({yeni_dosya_adi})")
                
                except Exception as hata:
                    logging.error(f"Damgalama hatası ({dosya_eski_adi}): {hata}")

    except Exception as e:
        print("\n❌ KRİTİK HATA OLUŞTU!")
        print(f"Hata detayı: {e}")
        logging.exception("Ana döngüde kritik hata")
        sys.exit(1)

    print("\n=== OTOMASYON BAŞARIYLA TAMAMLANDI ===")
    print(f"Log dosyası: {log_dosyasi}")
    logging.info("Otomasyon başarıyla sonlandı.")


if __name__ == "__main__":
    main()
