import os
import shutil


def pdfleri_tasi_ve_isimlendir(df_sonuc, pdf_klasoru, ana_klasor):
    """
    - Eşleşen PDF'leri Pdfler/ içinden alır
    - Referans Tarama/HARF/ altına taşır
    - PDF adını referans kodu yapar
    - Aynı isim varsa _1, _2 ekler
    - Orijinal PDF'i siler
    """

    hedef_ana = os.path.join(ana_klasor, "Referans Tarama")
    os.makedirs(hedef_ana, exist_ok=True)

    rapor = []

    for _, row in df_sonuc.iterrows():
        pdf_adi = row.get("dosya")
        referans = row.get("olusan_kod")

        if not pdf_adi or not referans:
            continue

        kaynak_pdf = os.path.join(pdf_klasoru, pdf_adi)
        if not os.path.exists(kaynak_pdf):
            rapor.append((pdf_adi, "PDF bulunamadı"))
            continue

        # 🔹 Referans harfi (F / G / O / E / I / K)
        try:
            harf = referans.split("-")[0]
        except Exception:
            rapor.append((pdf_adi, "Referans format hatası"))
            continue

        hedef_klasor = os.path.join(hedef_ana, harf)
        os.makedirs(hedef_klasor, exist_ok=True)

        # 🔹 Yeni PDF adı
        base_name = referans
        yeni_pdf = f"{base_name}.pdf"
        hedef_pdf = os.path.join(hedef_klasor, yeni_pdf)

        # 🔁 Aynı isim varsa _1, _2 ...
        sayac = 1
        while os.path.exists(hedef_pdf):
            yeni_pdf = f"{base_name}_{sayac}.pdf"
            hedef_pdf = os.path.join(hedef_klasor, yeni_pdf)
            sayac += 1

        # 🔹 Taşı (move = copy + delete)
        shutil.move(kaynak_pdf, hedef_pdf)

        rapor.append((pdf_adi, f"Taşındı → {yeni_pdf}"))

    return rapor
