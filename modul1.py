import pandas as pd

def excelden_faturalari_oku(excel_path):
    # Excel dosyasını oku
    df = pd.read_excel(excel_path)

    # Gerekli sütunları alıyoruz
    # (Not: İleride sütun sırası değişirse burası patlayabilir ama şimdilik o soruna girmiyoruz)
    faturalar_df = pd.DataFrame({
        "excel_ref": df.iloc[:, 0],      # A Sütunu
        "fatura_no": df.iloc[:, 6],      # G Sütunu
        "bakiye_excel": pd.to_numeric(df.iloc[:, 10], errors="coerce") # K Sütunu
    })

    # === DÜZELTME BURADA BAŞLIYOR ===
    
    def fatura_no_temizle(deger):
        """
        Gelen değer 12345.0 şeklindeyse sondaki .0'ı atar.
        Boşsa boş döner.
        """
        if pd.isna(deger):
            return None
        
        # Önce metne çevir: "12345.0"
        metin = str(deger).strip()
        
        # Eğer ".0" ile bitiyorsa o kısmı sil
        if metin.endswith(".0"):
            metin = metin[:-2]
            
        return metin

    # Temizlik fonksiyonunu her satıra uygula
    faturalar_df["fatura_no"] = faturalar_df["fatura_no"].apply(fatura_no_temizle)
    
    # === DÜZELTME BİTTİ ===

    # Boş veya hatalı (nan) satırları tablodan çıkar
    faturalar_df = faturalar_df[
        (faturalar_df["fatura_no"].notna()) & 
        (faturalar_df["fatura_no"] != "") & 
        (faturalar_df["fatura_no"] != "nan")
    ]

    return faturalar_df