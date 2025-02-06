import pandas as pd
import streamlit as st
import logging
import math
from math import cos, sin, atan2, radians, degrees, asin
from numpy import sin, cos, arcsin, radians, sqrt
import numpy as np
import pydeck as pdk
import folium as folim
from streamlit_folium import st_folium
from folium.features import CustomIcon
from pathlib import Path
import pyproj as pyproj
from defect_localisation_sbc.functions import *
from streamlit.components.v1 import html
import uuid
def main():
    # Titre de l'application
    st.title("Traitement Sewerball Camera - Localisation des défauts")

    st.write("""
    ### Prérequis:
    1. **Format CSV Standard** : Les valeurs doivent être séparées par point virgule (`;`).
    2. **En-têtes de Colonnes** : La première ligne doit contenir les noms des colonnes, les colonnes obligatoires:["Regard amont","temps_video","cord1","cord2","Defaut","Gravite"].
    3. **La première ligne** : Assurez-vous que la première ligne contienne l'heure de départ de la sewerball camera.
    4. **Encodage** : Utilisez un encodage UTF-8 pour éviter les problèmes avec des caractères spéciaux.
            """)

    st.markdown(
        """
        <style>
        .big-font {
            font-size: 24px !important;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

    # Affichage du texte agrandi
    st.markdown('<p class="big-font">Choisissez le système de coordonnées d\'entrée</p>', unsafe_allow_html=True)
    systeme = st.selectbox(
            "Système de coordonnées géographiques",
            ("", "WGS84 (Latitude, Longitude)", "Lambert 93 (X, Y)")
            )
    uploaded_file = st.file_uploader("Choisir un fichier CSV", type=["csv"])
    

    if uploaded_file is not None:
        
        try:
            input_file = pd.read_csv(uploaded_file, sep=";", encoding="ISO-8859-1")
            st.success("Fichier chargé avec succès !")

            if systeme == "Lambert 93 (X, Y)":
                input_file["cord2"],input_file["cord1"]=lambert93_to_wgs84(input_file["cord1"],input_file["cord2"])


            copy_input=input_file.copy()
            df1 = copy_input.dropna(subset=['cord1', 'cord2'])
            df1=df1.reset_index(drop=True)
            
            # Séparer les lignes contenant defaut
            df2 = input_file.dropna(subset=['Defaut'])
            df2=df2.reset_index(drop=True)
            df2["temps_video"] = pd.to_timedelta(df2["temps_video"])
            df2 = df2[["temps_video", "Defaut", "Gravite"]]
            st.subheader("Données initiales")
            st.write(df1)
            st.subheader("Données des défauts")
            st.write(df2)

            try:
                df_selection=df1[["temps_video","cord1","cord2"]]
            except Exception as e:
                st.error(f"Les colonnes nécessaires ne sont disponibles ou pas au bon format.")
            
        except Exception as e:
            st.error(f"Erreur inattendue : {e}")

                
        df_selection = df_selection.fillna(0)
        
        distances=[]
        azimuts=[]
        
        for i in range(len(df_selection) - 1):
            lat1, lon1 = df_selection.iloc[i]['cord1'], df_selection.iloc[i]['cord2']
            lat2, lon2 = df_selection.iloc[i + 1]['cord1'], df_selection.iloc[i + 1]['cord2']
            distance=approx_flying_distance_in_m(lat1, lon1, lat2, lon2)
            azimut=calculate_bearing(lat1, lon1, lat2, lon2)
            distances.append(distance)
            azimuts.append(azimut)
            
            df_selection['Appro_dist'] = pd.Series([None] + distances)
            df_selection["bearing"]=pd.Series([None] + azimuts)


        df_selection = df_selection.fillna(0)
        df_selection["Distance"]=df_selection["Appro_dist"].cumsum()
        df_selection["temps_video"] = pd.to_timedelta(df_selection["temps_video"])
        df_selection.set_index("temps_video", inplace=True)
        df_resampled = df_selection.resample("1s").asfreq()
        df_resampled["Distance"] = df_resampled["Distance"].resample("s").interpolate()
        df_resampled["bearing"] = df_resampled["bearing"].fillna(method='bfill')
        df_resampled["cord1_shift"] = df_resampled["cord1"].shift(1)
        df_resampled["cord2_shift"] = df_resampled["cord2"].shift(1)
        
        for i in range(1,len(df_resampled)-1):
            if pd.isna(df_resampled["cord1"][i]):
                df_resampled["cord1_shift"][i+1], df_resampled["cord2_shift"][i+1] = get_destination_lat_long(df_resampled["cord1_shift"][i], df_resampled["cord2_shift"][i],df_resampled["bearing"][i],(df_resampled["Distance"][i+1]-df_resampled["Distance"][i]))
            else:
                continue

        df_resampled["cord1"] = df_resampled["cord1_shift"].shift(-1)
        df_resampled["cord2"] = df_resampled["cord2_shift"].shift(-1)
        df_resampled.drop(columns=['Appro_dist','cord1_shift', 'cord2_shift','bearing'], inplace=True)
        
        st.subheader("Données après resampling et interpolation")
        st.dataframe(df_resampled)

        result_csv = df_resampled.to_csv(index=True,sep=";")
        st.download_button(
            label="Télécharger le fichier résultant",
            data=result_csv,
            file_name="data_manhole_resultant.csv",
            mime="text/csv"
        )


        df_maps = df1[["Regard amont", "cord1", "cord2"]]
        df_maps = df_maps.rename(columns={"cord1": "latitude", "cord2": "longitude"})
        df_defaut_final = pd.merge(df_resampled, df2, on='temps_video', how='left')

        df_defaut_final = df_defaut_final.dropna(subset=['Defaut'])
        df_defaut_final = df_defaut_final.rename(columns={"cord1": "latitude", "cord2": "longitude"})
        df_defaut_final = df_defaut_final[df_defaut_final['Defaut'].notna() & df_defaut_final['Gravite'].notna()]
        st.subheader("Liste des défauts")
        st.dataframe(df_defaut_final)
        result_csv_defaut = df_defaut_final.to_csv(index=True,sep=";")
        st.download_button(
            label="Télécharger la liste des défauts",
            data=result_csv_defaut,
            file_name="df_defaut.csv",
            mime="text/csv"
        )
        m_result = afficher_carte(df_maps,df_defaut_final)
        map_name = f'map_'+str(uuid.uuid4())+'.html'
        html = f"""<iframe src="./{map_name}" width="100%" height="600"></iframe>"""
        path = Path(st.__file__).parent / 'static' / map_name
        
        st.title("Localisation des désordes")
        m_result.save(str(path))



main()
