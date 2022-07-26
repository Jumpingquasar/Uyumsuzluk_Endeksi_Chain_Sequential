from __future__ import print_function
import sys
import pandas as pd
import os
import timeit
import numpy as np
import multiprocessing

sys.setrecursionlimit(15000)
print("Number of cores:", multiprocessing.cpu_count())
counter = 0
start = timeit.default_timer()
chains = []
total = 0
all_chains = []

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
df_orsa = pd.read_excel("Lib/Excel/TezMedikal-oncesi.xlsx")
# İller arası mesafe tablosunu çek
df_distance = pd.read_excel("Lib/Excel/ilmesafe.xlsx")

# Çalışan veri tablosundan görevi doktor olanları ayır farklı dataframe'e ata
df_doktorlar1 = df_orsa[df_orsa["Sertifika"] == "İşyeri Hekimi"]
df_doktorlar2 = df_orsa[df_orsa["Sertifika"] == "Diğer Sağlık Personeli"]
frames = [df_doktorlar1, df_doktorlar2]
df_doktorlar = pd.concat(frames)
# Çalışan veri tablosundan görevi iş güvenlik uzmanı olanları ayır farklı dataframe'e ata
df_igu = df_orsa[df_orsa["Sertifika"] != "İşyeri Hekimi"]

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
    if seviye == "İş Güvenliği Uzmanı (Tehlikeli Sınıf-A)":
        seviye = 1
    elif seviye == "İş Güvenliği Uzmanı (Tehlikeli Sınıf-B)":
        seviye = 2
    elif seviye == "İş Güvenliği Uzmanı (Tehlikeli Sınıf-C)":
        seviye = 3
    isyeri_seviye = kisi["isyeri_seviye"]
    if isyeri_seviye == "A SINIFI UZMAN":
        isyeri_seviye = 1
    elif isyeri_seviye == "B SINIFI UZMAN":
        isyeri_seviye = 2
    elif isyeri_seviye == "C SINIFI UZMAN":
        isyeri_seviye = 3
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
def puan_karsilastirma(ana_kisi_f, diger_kisi_f, Doktor):
    onceki_puan = puan_hesabi(diger_kisi_f)
    diger_kisi_f["gorev_yeri"] = ana_kisi_f["gorev_yeri"]
    if Doktor is not True:
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
        ana_kisi["ikamet_yeri"] = p_table.iloc[kisi_index]["İL"]
        ana_kisi["gorev_yeri"] = p_table.iloc[kisi_index]["SGK İL İSİM"]
        ana_kisi["seviye"] = p_table.iloc[kisi_index]["Sertifika"]
        ana_kisi["isyeri_seviye"] = p_table.iloc[kisi_index]["TEHLİKE SINIFI"]
        ana_kisi["kisi_saat"] = p_table.iloc[kisi_index]["TOPLAM ATAMA SÜRESİ (sa)"]
        ana_kisi["gorevi"] = p_table.iloc[kisi_index]["HİZMET TİPİ"]
        kisi_index += 1
        while kisi_index_ < len(p_table):
            Doktor = False
            diger_kisi["ikamet_yeri"] = p_table.iloc[kisi_index_]["İL"]
            diger_kisi["gorev_yeri"] = p_table.iloc[kisi_index_]["SGK İL İSİM"]
            diger_kisi["seviye"] = p_table.iloc[kisi_index_]["Sertifika"]
            diger_kisi["isyeri_seviye"] = p_table.iloc[kisi_index_]["TEHLİKE SINIFI"]
            diger_kisi["kisi_saat"] = p_table.iloc[kisi_index_]["TOPLAM ATAMA SÜRESİ (sa)"]
            diger_kisi["gorevi"] = p_table.iloc[kisi_index_]["HİZMET TİPİ"]
            kisi_index_ += 1
            if diger_kisi["seviye"] == "İşyeri Hekimi" or diger_kisi["seviye"] == "Diğer Sağlık Personeli":
                Doktor = True
            karsilastirma_list.append(puan_karsilastirma(ana_kisi, diger_kisi, Doktor))
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
def chain(dataframe, total_point, col, current_chain, used_list):
    if len(used_list) == len(dataframe):
        return
    current_chain.append(col)
    used_list.append(col)
    arr = positive_finder(dataframe, col)
    temp = 0
    i = 0
    temp_index = None
    if arr is not None:
        while i < len(arr[1]):
            if arr[1][i] > temp and arr[0][i] not in used_list:
                temp = arr[1][i]
                temp_index = arr[0][i]
            i+=1
    if temp_index is None:
        for val in dataframe:
            if val not in used_list:
                chain(dataframe, total_point, val, current_chain, used_list)
    total_point += temp
    chain(dataframe, total_point, temp_index, current_chain, used_list)
    return current_chain, total_point

# Başlangıç
for df in [df_igu, df_doktorlar]:
    print(df)
    percentage_dataframe = yuzde_df(df)
    print(percentage_dataframe)
    percentage_dataframe.to_csv()
#
# # Zincirlerin başlangıç noktası
# j=0
# max_change = 0
# while j < len(percentage_dataframe):
#     arr = positive_finder(percentage_dataframe, j)
#     if arr is None:
#         j+=1
#         continue
#     used_list = []
#     current_chain = []
#     total_point = np.max(arr[1])
#     chainsandvalues = [chain(percentage_dataframe, total_point, j, current_chain, used_list)]
#     j+=1
#     print("chain count:", j)
#     all_chains.append(chainsandvalues)
#
#
#
# all_values = []
# i = 0
# while i < len(all_chains):
#     temp = all_chains[i]
#     temp = temp[0]
#     all_values.append(temp[1])
#     i+=1
#
# print(np.max(all_values))
# print(np.argmax(all_values))
# stop = timeit.default_timer()
# print('Time: ', stop - start)