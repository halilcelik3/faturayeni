import fitz  # PyMuPDF
import os


def pdfde_referans_var_mi(pdf_yolu, referans_kodu):
    """
    PDF'in ilk sayfasında referans kodu var mı kontrol eder
    """
    doc = fitz.open(pdf_yolu)
    sayfa = doc[0]
    metin = sayfa.get_text()
    doc.close()

    return referans_kodu in metin


def pdfye_referans_yaz(pdf_yolu, referans_kodu):
    """
    Referans Tarama klasörü altındaki PDF'e
    sağ üst köşeye kırmızı, bold görünümlü referans yazar.

    PDF zaten işaretliyse atlar.
    """

    if not os.path.exists(pdf_yolu):
        return {
            "pdf": pdf_yolu,
            "durum": "PDF bulunamadı"
        }

    # 🔴 ZATEN VAR MI?
    if pdfde_referans_var_mi(pdf_yolu, referans_kodu):
        return {
            "pdf": os.path.basename(pdf_yolu),
            "durum": "Zaten işaretli"
        }

    doc = fitz.open(pdf_yolu)
    sayfa = doc[0]

    rect = sayfa.rect
    sayfa_genislik = rect.width

    # Sağ üst konum (standart)
    x = sayfa_genislik - 180
    y = 40

    # 🔴 FAKE-BOLD (gözle net görünsün diye)
    for dx in (0, 0.8):
        sayfa.insert_text(
            (x + dx, y),
            referans_kodu,
            fontsize=18,
            fontname="helv",
            fill=(1, 0, 0),
            overlay=True
        )

    doc.save(pdf_yolu)
    doc.close()

    return {
        "pdf": os.path.basename(pdf_yolu),
        "durum": "Referans yazıldı"
    }


