import gmplot
import pandas as pd
import os

# Create the map plotter:
apikey = '' # (your API key here)
gmap = gmplot.GoogleMapPlotter(38.9637, 35.2433, 6, apikey=apikey)

df_il_konum = pd.read_csv("Lib/Excel/ilkonum.csv")
df_il_konum.set_index("plaka")
df_il_konum.drop('plaka', inplace=True, axis=1)
df_il_konum.drop('northeast_lat', inplace=True, axis=1)
df_il_konum.drop('northeast_lon', inplace=True, axis=1)
df_il_konum.drop('southwest_lat', inplace=True, axis=1)
df_il_konum.drop('southwest_lon', inplace=True, axis=1)

print(df_il_konum)
i = 0
while i < len(df_il_konum):
    gmap.marker(df_il_konum.loc[i]["lat"], df_il_konum.loc[i]["lon"], label= str(i+1), info_window= str(df_il_konum.loc[i]["il_adi"]))
    i+=1

# Draw the map:
gmap.draw('map.html')