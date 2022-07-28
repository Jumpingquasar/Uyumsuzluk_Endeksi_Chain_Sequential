from __future__ import print_function
import sys
import pandas as pd
import os
import timeit

start = timeit.default_timer()

pd.options.mode.chained_assignment = None  # default='warn'
counter = 0

i = 0
# Yasal çalışma saati sınırı
maksimum_saat = 195

used_list = []

ana_kisi = {
    "gorev_yeri": "",
    "ikamet_yeri": "",
    "seviye": "",
    "isyeri_seviye": "",
    "kisi_saat": "",
    "gorevi": ""
}
diger_kisi = {
    "gorev_yeri": "",
    "ikamet_yeri": "",
    "seviye": "",
    "isyeri_seviye": "",
    "kisi_saat": "",
    "gorevi": ""
}

# Çalışan veri tablosunu çek
df_orsa = pd.read_excel("Lib/Excel/orsa.xlsx")
# İller arası mesafe tablosunu çek
df_distance = pd.read_excel("Lib/Excel/ilmesafe.xlsx")

# Çalışan veri tablosundan görevi doktor olanları ayır farklı dataframe'e ata
df_doktorlar = df_orsa[df_orsa["SEVİYE"] == "BOŞ"]
# Çalışan veri tablosundan görevi iş güvenlik uzmanı olanları ayır farklı dataframe'e ata
df_igu = df_orsa[df_orsa["SEVİYE"] != "BOŞ"]

# Kişi index'ine göre saat puanı hesabı
def saat_hesabi(kisi):
    kisi_saat = kisi["kisi_saat"]
    X = 1 - (kisi_saat / maksimum_saat)
    Y = (1 + X) ** 2
    saat_puan = 250 / Y
    return saat_puan

# Kişi index'ine göre mesafe puanı hesabı
def mesafe_hesabi(kisi):
    ikamet_list = df_distance[kisi["ikamet_yeri"]]
    gorev_yeri = kisi["gorev_yeri"]
    il_list = df_distance["İL_ADI"].tolist()
    gorev_index = il_list.index(gorev_yeri)
    mesafe = ikamet_list[gorev_index]
    if 0 < mesafe <= 100:
        return 200
    elif mesafe >= 100:
        return 100
    else:
        return 250

# Kişi index'ine göre uzmanlık puanı hesabı
def uzmanlik_hesabi(kisi):
    seviye = kisi["seviye"]
    isyeri_seviye = kisi["isyeri_seviye"]
    if type(seviye) != int or type(isyeri_seviye) != int:
        return 500
    fark = seviye - isyeri_seviye
    uzmanlik_puan = 500 - 150 * abs(fark)
    return uzmanlik_puan

# Kişi index'ine göre toplam puan hesabı
def puan_hesabi(kisi):
    saat_puan = saat_hesabi(kisi)
    uzmanlik_puan = uzmanlik_hesabi(kisi)
    mesafe_puan = mesafe_hesabi(kisi)
    return saat_puan + uzmanlik_puan + mesafe_puan

# diger_kisi'ye ana_kisi'nin "gorev_yeri" ve "isyeri_seviye"'sini verirsek çıkan yüzdelik puan hesabı
def puan_karsilastirma(ana_kisi, diger_kisi):
    onceki_puan = puan_hesabi(diger_kisi)
    diger_kisi["gorev_yeri"] = ana_kisi["gorev_yeri"]
    diger_kisi["isyeri_seviye"] = ana_kisi["isyeri_seviye"]
    sonraki_puan = puan_hesabi(diger_kisi)
    return (sonraki_puan-onceki_puan)*100/onceki_puan

# Puan karsilaştırmadan gelen yüzdelik verilerin DataFrame'e aktarımı
def yuzde_DF(p_table):
    global counter
    karsilastirma_listoflists = []
    kisi_index = 0
    while kisi_index < len(p_table):
        karsilastirma_list = []
        kisi_index_ = 0
        ana_kisi["ikamet_yeri"] = p_table.iloc[kisi_index]["İKAMETİ"]
        ana_kisi["gorev_yeri"] = p_table.iloc[kisi_index]["GÖREV YERİ"]
        ana_kisi["seviye"] = p_table.iloc[kisi_index]["SEVİYE"]
        ana_kisi["isyeri_seviye"] = p_table.iloc[kisi_index]["İŞYERİ"]
        ana_kisi["kisi_saat"] = p_table.iloc[kisi_index]["ÇALIŞILAN SAAT"]
        ana_kisi["gorevi"] = p_table.iloc[kisi_index]["GÖREVİ"]
        kisi_index += 1
        while kisi_index_ < len(p_table):
            diger_kisi["ikamet_yeri"] = p_table.iloc[kisi_index_]["İKAMETİ"]
            diger_kisi["gorev_yeri"] = p_table.iloc[kisi_index_]["GÖREV YERİ"]
            diger_kisi["seviye"] = p_table.iloc[kisi_index_]["SEVİYE"]
            diger_kisi["isyeri_seviye"] = p_table.iloc[kisi_index_]["İŞYERİ"]
            diger_kisi["kisi_saat"] = p_table.iloc[kisi_index_]["ÇALIŞILAN SAAT"]
            diger_kisi["gorevi"] = p_table.iloc[kisi_index_]["GÖREVİ"]
            kisi_index_ += 1
            karsilastirma_list.append(puan_karsilastirma(ana_kisi, diger_kisi))
            counter += 1
            if counter%1000 == 0:
                print("Total Operations =", counter)
        karsilastirma_listoflists.append(karsilastirma_list)
    return pd.DataFrame(karsilastirma_listoflists)


def yer_bulucu(main_DF, i):
    buyuk_cache = [0, 0, 0]
    j = 0
    while j < len(main_DF.columns):
        if main_DF[j][i] > 0:
            if main_DF[j][i] > buyuk_cache[0]:
                buyuk_cache[0] = main_DF[j][i]
                buyuk_cache[1] = j
                buyuk_cache[2] = i
        j += 1

    return buyuk_cache

df = df_igu
main_DF = yuzde_DF(df)
df.reset_index(inplace=True)
print(main_DF, main_DF.values.sum())
i = 0
while True:
    i = 0
    while i < len(main_DF):
        index_location = yer_bulucu(main_DF, i)
        gy_cache = df.loc[index_location[1], "GÖREV YERİ"]
        s_cache = df.loc[index_location[1], "İŞYERİ"]
        df.loc[index_location[1], "GÖREV YERİ"] = df.loc[index_location[2], "GÖREV YERİ"]
        df.loc[index_location[1], "İŞYERİ"] = df.loc[index_location[2], "İŞYERİ"]
        df.loc[index_location[2], "GÖREV YERİ"] = gy_cache
        df.loc[index_location[2], "İŞYERİ"] = s_cache
        main_DF = yuzde_DF(df)
        i += 1
        print(main_DF, main_DF.values.sum())
    if sum == main_DF.values.sum():
        break
    print(main_DF, main_DF.values.sum())
    sum = main_DF.values.sum()
main_DF = yuzde_DF(df)
print(main_DF, main_DF.values.sum())

writer = pd.ExcelWriter('Degistirilmis.xlsx')
df.to_excel(writer)

# save the excel
writer.save()
print("DataFrame is exported successfully to 'converted-to-excel.xlsx' Excel File.")
stop = timeit.default_timer()

print('Time: ', stop - start)
