import pandas as pd


def referans_baslangiclarini_oku(excel_path):
    """
    REFERANS_BASLANGIC.xlsx dosyasından
    TDHP → başlangıç sayaçlarını okur

    Çıktı:
    {
        150: 114,
        159: 220,
        780: 5
    }
    """
    df = pd.read_excel(excel_path)

    baslangiclar = {}

    for _, row in df.iterrows():
        try:
            tdhp = int(row.iloc[0])          # A sütunu
            baslangic = int(row.iloc[1])     # B sütunu
            baslangiclar[tdhp] = baslangic
        except Exception:
            continue

    return baslangiclar
