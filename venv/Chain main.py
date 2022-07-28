from __future__ import print_function
import sys
import pandas as pd
import os
import timeit
sys.setrecursionlimit(20000)
counter = 0
start = timeit.default_timer()
chains = []
total = 0

pd.options.mode.chained_assignment = None  # default='warn'

# Yasal çalışma saati sınırı
maksimum_saat = 195

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
def puan_karsilastirma(ana_kisi_f, diger_kisi_f):
    onceki_puan = puan_hesabi(diger_kisi_f)
    diger_kisi_f["gorev_yeri"] = ana_kisi_f["gorev_yeri"]
    diger_kisi_f["isyeri_seviye"] = ana_kisi_f["isyeri_seviye"]
    sonraki_puan = puan_hesabi(diger_kisi_f)
    return (sonraki_puan - onceki_puan) * 100 / onceki_puan


# Puan karsilaştırmadan gelen yüzdelik verilerin DataFrame'e aktarımı
def yuzde_df(p_table):
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
            if counter % 1000 == 0:
                print("Total Operations =", counter)
        karsilastirma_listoflists.append(karsilastirma_list)
    return pd.DataFrame(karsilastirma_listoflists)

# Verilen column içinde pozitif verileri ve puanlarını ver
def positive_finder(dataframe, col):
    chain_vals = []
    positive_chain = []
    vals = []
    i = 0
    while i < len(dataframe[col]):
        if dataframe[col][i] > 0:
            vals.append(dataframe[col][i])
            positive_chain.append(i)
        i += 1
    chain_vals.append(positive_chain)
    chain_vals.append(vals)
    if not positive_chain:
        return None
    return chain_vals

# Chain self-feeding fonksiyonu. Dalları çıkaran ana fonksiyon
def chain(dataframe, col, current_chain, used_list, total):
    used_list.append(col)
    arr = positive_finder(dataframe, col)
    if arr is not None:
        for i in arr[0]:
            if i not in used_list:
                current_chain.append(i)
                index_ = arr[0].index(i)
                total += arr[1][index_]
                print(current_chain)
                chain(dataframe, i, current_chain, used_list, total)
                chains.append(current_chain)
                chains.append(total)
                current_chain.pop(-1)
                used_list.pop(-1)
    else:
        current_chain.append(None)
        for j in range(len(dataframe)):
            if j not in used_list:
                current_chain.append(j)
                chains.append(current_chain)
                chains.append(total)
                print(current_chain)
                chain(dataframe, j, current_chain, used_list, total)



a = 0

# Zincirlerin başlangıç noktası
def main(dataframe, a):
    i = 0
    arr = positive_finder(dataframe, a)
    total = 0
    if arr is None:
        a+=1
        main(dataframe, a)
    else:
        for col in arr[0]:
            current_chain = [a, col]
            used_list = [a]
            index_ = arr[0].index(col)
            total += arr[1][index_]
            print(current_chain)
            chain(dataframe, col, current_chain, used_list, total)


# Başlangıç
df = df_igu
print(df)
percentage_dataframe = yuzde_df(df)

main(percentage_dataframe, a)

stop = timeit.default_timer()
print('Time: ', stop - start)