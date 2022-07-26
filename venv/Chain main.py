from __future__ import print_function
import sys
import pandas as pd
import os
import timeit
sum = 0
counter = 0
start = timeit.default_timer()

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

def chain(main_DF):
    chain_points = []
    total_point = 0
    i=0
    chain = [0] * len(main_DF)
    while i < len(main_DF):
        yuzde_farki = 0
        j=0
        used_list = []
        while j <len(main_DF):
            if main_DF[j][i] > yuzde_farki and j not in used_list:
                yuzde_farki = main_DF[j][i]
                chain[i] = j
                used_list.append(j)
                total_point += yuzde_farki

            elif j == len(main_DF)-1:
                if main_DF[j][i] > yuzde_farki:
                    yuzde_farki = main_DF[j][i]
                    chain[i] = j
                    used_list.append(j)
                    total_point += yuzde_farki
                    j+=1
            j+=1
        i+=1
    chain_points.append(chain)
    chain_points.append(total_point)
    return chain_points

def chain_long(main_DF):
    chains_points = []
    all_chains = []
    all_points = []
    temp_chain = [0]*len(main_DF)
    temp_point = 0
    point = 0
    i=0
    while i < len(main_DF):
        j=0
        point = 0
        while j < len(main_DF):
            if point < main_DF[j][i]:
                point = main_DF[j][i]
                temp_chain[i] = j
            j += 1
        temp_point += point
        i+=1
    all_chains.append(temp_chain)
    all_points.append(temp_point)
    chains_points.append(all_chains)
    chains_points.append(all_points)
    i = 0
    max = 0
    max_chain = []
    return_chain_points = []
    while i < len(chains_points[1]):
        max = chains_points[1][i]
        max_chain = chains_points[0][i]
        return_chain_points.append(max_chain)
        return_chain_points.append(max)
        i+=1
    return return_chain_points




df = df_igu
df.reset_index(inplace=True)
main_DF = yuzde_DF(df)
print(main_DF, main_DF.values.sum())
while True:
    points_list = chain_long(main_DF)
    chain_ = points_list[0]
    i=0
    index_location = [0]*2
    while i < len(main_DF):
        index_location[1] = chain_[i]
        gy_cache = df.loc[index_location[1], "GÖREV YERİ"]
        s_cache = df.loc[index_location[1], "İŞYERİ"]
        df.loc[index_location[1], "GÖREV YERİ"] = df.loc[i, "GÖREV YERİ"]
        df.loc[index_location[1], "İŞYERİ"] = df.loc[i, "İŞYERİ"]
        df.loc[i, "GÖREV YERİ"] = gy_cache
        df.loc[i, "İŞYERİ"] = s_cache
        i+=1
    main_DF = yuzde_DF(df)
    print(main_DF, main_DF.values.sum())
    if int(sum) == int(points_list[1]):
        continue
    sum = points_list[1]
stop = timeit.default_timer()
print('Time: ', stop - start)