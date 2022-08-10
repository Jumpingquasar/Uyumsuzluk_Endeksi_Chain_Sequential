from __future__ import print_function
import sys
import pandas as pd
import os
import timeit
import numpy as np
import multiprocessing

# Çalışan veri tablosunu çek
df_orsa = pd.read_excel("Lib/Excel/TezMedikal-oncesi.xlsx")
# İller arası mesafe tablosunu çek
df_distance = pd.read_excel("Lib/Excel/ilmesafe.xlsx")



iller=[]
i=0
while i < len(df_orsa):
    j=0
    while j < len(df_distance):
        x = df_orsa.loc[i]["SGK İL"]
        y = df_distance.loc[j]["İL PLAKA NO"]
        if df_orsa.loc[i]["SGK İL"] == df_distance.loc[j]["İL PLAKA NO"]:
            iller.append(df_distance.loc[j]["İL_ADI"])
            print(df_distance.loc[j]["İL_ADI"])
        j+=1
    i+=1

df = pd.DataFrame(iller)

df.to_csv('iller.csv', encoding='utf-8')