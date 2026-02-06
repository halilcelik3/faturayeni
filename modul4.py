import pandas as pd

# === MODÜL 4: EXCEL ↔ PDF FATURA EŞLEŞTİRME + KOD ÜRETME ===

# Excel A sütunundaki değerlere göre kod haritası
KOD_HARITASI = {
    150: ("F", 150), 151: ("F", 151), 152: ("F", 152), 153: ("F", 153),
    154: ("F", 154), 155: ("F", 155), 156: ("F", 156), 157: ("F", 157),
    158: ("F", 158), 159: ("F", 159),

    250: ("O", 250), 251: ("O", 251), 252: ("O", 252), 253: ("O", 253),
    254: ("O", 254), 255: ("O", 255), 256: ("O", 256), 257: ("O", 257),
    258: ("O", 258), 259: ("O", 259), 260: ("O", 260), 261: ("O", 261),
    262: ("O", 262), 263: ("O", 263), 264: ("O", 264), 265: ("O", 265),
    266: ("O", 266), 267: ("O", 267), 268: ("O", 268), 269: ("O", 269),

    600: ("E", 600), 601: ("E", 601), 602: ("E", 602), 603: ("E", 603),
    604: ("E", 604), 605: ("E", 605), 606: ("E", 606), 607: ("E", 607),
    608: ("E", 608), 609: ("E", 609), 610: ("E", 610), 611: ("E", 611),
    612: ("E", 612), 613: ("E", 613), 614: ("E", 614), 615: ("E", 615),
    616: ("E", 616), 617: ("E", 617), 618: ("E", 618), 619: ("E", 619),

    730: ("G", 621),
    740: ("G", 622),
    750: ("I", 630),
    760: ("I", 631),
    770: ("I", 632),
    780: ("K", 660),
}


def excel_pdf_eslestir(df_excel, df_pdf, baslangic_sayaclari):
    """
    Excel ve PDF verilerini fatura_no üzerinden eşleştirir
    + eşleşenlere otomatik kod üretir
    Başlangıç sayaçları MODÜL-5'ten gelir
    """

    # === AYNI FATURA NO VARSA EXCEL BAKİYELERİNİ TOPLA ===
    df_excel_toplam = (
        df_excel
        .groupby(["fatura_no", "excel_ref"], as_index=False)
        .agg({
            "bakiye_excel": "sum"
        })
    )

    # === EXCEL ↔ PDF BİRLEŞTİR ===
    eslesme = df_excel_toplam.merge(
        df_pdf,
        on="fatura_no",
        how="left"
    )

    # === FARK HESABI ===
    eslesme["fark"] = eslesme["bakiye_excel"] - eslesme["toplam_tutar"]

    # === DURUM ETİKETİ ===
    def durum_belirle(row):
        if pd.isna(row["toplam_tutar"]):
            return "PDF yok"
        if pd.isna(row["bakiye_excel"]):
            return "Excel bakiyesi yok"
        if abs(row["fark"]) < 0.01:
            return "Eşleşiyor"
        return "Fark var"

    eslesme["durum"] = eslesme.apply(durum_belirle, axis=1)

    # === KOD ÜRETME ===
    eslesme["olusan_kod"] = ""
    sayaclar = {}

    for idx, row in eslesme.iterrows():
        if pd.isna(row["toplam_tutar"]) or pd.isna(row["excel_ref"]):
            continue

        try:
            ana_kod = int(row["excel_ref"])
        except Exception:
            continue

        if ana_kod not in KOD_HARITASI:
            continue

        prefix, orta_kod = KOD_HARITASI[ana_kod]

        # 🔹 BAŞLANGIÇ SAYACI MANTIĞI
        if ana_kod not in sayaclar:
            sayaclar[ana_kod] = baslangic_sayaclari.get(ana_kod, 100)
        else:
            sayaclar[ana_kod] += 1

        eslesme.at[idx, "olusan_kod"] = f"{prefix}-{orta_kod}.{sayaclar[ana_kod]}"

    return eslesme
