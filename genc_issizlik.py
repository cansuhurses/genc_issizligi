# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 20:51:35 2021

@author: cansu
"""

from matplotlib.backends.backend_agg import RendererAgg
import matplotlib
import streamlit as st
import pandas as pd
from itertools import chain
import plotly.graph_objects as go
import plotly.express as px
import geopandas as gpd
import folium
from streamlit_folium import folium_static

st.set_option('deprecation.showPyplotGlobalUse', False)

## Yanyana objeler koymak için
matplotlib.use("agg")

_lock = RendererAgg.lock

## Sayfayı genişletme
def _max_width_():
    max_width_str = f"max-width: 3000px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )
    
_max_width_()

##Veriyi yükleme
data = pd.read_csv('linkedin_son.csv', index_col = 0)
uni_sıra = pd.read_csv('uni_data.csv', index_col = 0)

##Sidebar'a başlık ve farklı sayfalar oluşturmak için filtre ekleme
st.sidebar.title("Genç İşsizliği")

sidebar_select = st.sidebar.radio(" ", ('Öğrenci Kariyer Planı', 'Kariyer Merkezi', 'Trend'))

if sidebar_select == 'Öğrenci Kariyer Planı':

    row0_1, row0_2 = st.beta_columns((.85, .15))

    with row0_1:
        st.title('Kariyer Planı')
        st.markdown(' ')
        st.markdown("Bu uygulamada kullanılan veri seti, LinkedIn sitesiden 'yazılım' ve 'veri' anahtar kelimeleri geçen iş ilanları çekilerek oluşturulmuştur. Yazılım ve veri alanında çalışmak istediğiniz pozisyonu/pozisyonları ve okuduğunuz/mezun olduğunuz bölümü ve üniversiteyi seçerek size uygun iş ilanlarını görüntüleyebilirsiniz.")
            
    with row0_2:
        st.image('https://www.pngkit.com/png/full/126-1268278_faqs-for-students-college-student-students-icon.png')
    
    pozisyon_liste = list(data.Pozisyon.unique())
    
    bolum_liste = []

    for i in data.index:
        filt = eval(data['istenen_bölümler'][i])
        bolum_liste.append(filt)
    
    bolum_liste = list(pd.unique(list(chain.from_iterable(bolum_liste))))
    
    uni_liste = list(uni_sıra.Üniversite.unique())
    
    st.header('Sizinle aynı bölümden mezun kişilerin aradığı ve başvurduğu pozisyonlar hangileri?')
    
    row1_1, row1_2 = st.beta_columns((1, 1))
    
    with row1_1:
        select = st.multiselect('Hangi bölümde okuyorsunuz?/Hangi bölümden mezunsunuz?', bolum_liste, default = ['Bilgisayar Mühendisliği'])
        
        if select == []:
            filtered = data
        else:
            index = []
            for i in data.index:
                for j in select:
                    if j in data['istenen_bölümler'][i]:
                        index.append(i)
            index = list(set(index))
            filtered = data.iloc[index, :].reset_index(drop = True)
    
    st.markdown(' ')
    
    row2_1, row2_2 = st.beta_columns((1, 1))
    
    with row2_1:
        st.subheader('Bu bölümden mezun kişiler hangi pozisyonlar için aranıyor?')
        grafik = filtered['Pozisyon'].value_counts().to_frame().reset_index().rename(columns={'index': 'Pozisyon', 'Pozisyon':'İlan Sayısı'}).sort_values(by='İlan Sayısı', ascending=False)
        fig = px.bar(grafik[0:10], x = 'İlan Sayısı', y = 'Pozisyon')
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig)
        need_help = st.beta_expander('Bu alandaki pozisyonlar konusunda yardıma mı ihtiyacınız var? 👉')
        with need_help:
            st.markdown("[Bu](https://www.kariyer.net/pozisyonlar) siteden bilgi alabilirsiniz.")

    with row2_2:
        st.subheader('Bu bölümden mezun kişiler hangi pozisyonlara başvuruyor?')
        grafik = filtered.groupby(by=['Pozisyon'])[['Pozisyon','Başvuru Sayısı']].sum().reset_index().sort_values(by='Başvuru Sayısı', ascending =False)
        fig = px.bar(grafik[0:10], y = 'Pozisyon', x = 'Başvuru Sayısı')
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig)
        
    st.markdown(' ')
        
    row3_1, row3_2 = st.beta_columns((.8, 1.2))
    
    with row3_1:
        st.header('Bu ve benzeri iş ilanlarına kaç kişi başvurmuş?')
        st.markdown(' ')
        
        select2 = st.multiselect('Hangi bölümde okuyorsunuz?/Hangi bölümden mezunsunuz?', bolum_liste, default = ['Bilgisayar Mühendisliği'], key="iki")
        
        hepsi2 = st.checkbox("Hepsini seç.", key="dört")
        
        if hepsi2:
            select2 = bolum_liste
        
        if select2 == []:
            filtered = data
        else:
            index = []
            for i in data.index:
                for j in select2:
                    if j in data['istenen_bölümler'][i]:
                        index.append(i)
            index = list(set(index))
            filtered = data.iloc[index, :].reset_index(drop = True)
        
        select3 = st.selectbox('Hangi üniversitede okuyorsunuz?/Hangi üniversiteden mezunsunuz?', uni_liste)
            
        index = uni_sıra[uni_sıra.Üniversite == select3].index[0]
        toplam_bas = uni_sıra.iloc[0:index, :].Toplam.sum()
        
        st.markdown(' ')
        st.markdown('**URAP üniversite sıralamasına göre, sizin üniversitenizden daha üst sıralamadaki bir üniversiteden mezun olan kişilerden, 2019 ve 2020 senelerinde Kariyer.net sitesinde yayınlanan yazılım ve veri ile alakalı iş ilanlarına {} kişi başvurmuş.**'.format(toplam_bas))
    
    with row3_2:
        st.markdown(' ')
        st.markdown(' ')
        st.markdown(' ')
        st.markdown('**Bu bölüm mezunlarını arayan Linkedinde bulunan {} ilana toplamda {} başvuru yapılmış.**'.format(len(filtered), int(filtered['Başvuru Sayısı'].sum())))
        
        basvuru = filtered.groupby('Pozisyon')['Başvuru Sayısı'].sum().round().to_frame().reset_index().sort_values('Başvuru Sayısı', ascending = False)
        fig = go.Figure(data=[go.Table(
        header=dict(values=list(['Pozisyon', 'Başvuru Sayısı']),
                    fill_color= '#f63366',
                    font=dict(color='white'),
                    align='center', ),
        cells=dict(values=[basvuru['Pozisyon'], basvuru['Başvuru Sayısı']],
                   fill_color='#f0f2f6',
                   align='center'))
        ])
        
        fig.update_layout(
            margin=dict(l=50, r=0, b=0, t=0)
        )
    
        fig.update_layout(width=600)
        st.plotly_chart(fig)
        
    st.markdown('__________________________________________________________________________________________')
    
    st.header('Bu alanda hangi iş ilanları var?')
    
    row4_1, row4_2 = st.beta_columns((1, 1))
    
    with row4_1:
        select1 = st.multiselect('Hangi pozisyonda çalışmak istiyorsunuz?', pozisyon_liste, default = ['Yazılım Mühendisi'], key="bir")
            
        hepsi1 = st.checkbox("Hepsini seç.", key="bir")
        
        if hepsi1:
            select1 = pozisyon_liste
        
        if select1 == []:
            pozisyon = data
        else:
             pozisyon = data[data.Pozisyon.isin(select1)]
             pozisyon.reset_index(drop = True, inplace = True)
        
    with row4_2:
        select2 = st.multiselect('Hangi bölümde okuyorsunuz?/Hangi bölümden mezunsunuz?', bolum_liste, default = ['Bilgisayar Mühendisliği'], key="bir")
        
        hepsi2 = st.checkbox("Hepsini seç.", key="iki")
        
        if hepsi2:
            select2 = bolum_liste
        
        if select2 == []:
            filtered = pozisyon
        else:
            index = []
            for i in pozisyon.index:
                for j in select2:
                    if j in pozisyon['istenen_bölümler'][i]:
                        index.append(i)
            index = list(set(index))
            filtered = pozisyon.iloc[index, :].reset_index(drop = True)
    
    st.markdown(' ')
    
    row5_1, row5_2 = st.beta_columns((.2, .8))

    with row5_2:
        fig = go.Figure(data=[go.Table(
        header=dict(values=list(['Şirket', 'Pozisyon', 'Şehir', 'İş Birimi', 'Sektör']),
                    fill_color= '#f63366',
                    font=dict(color='white'),
                    align='center', ),
        cells=dict(values=[filtered['Şirket'], filtered['Pozisyon'], filtered['Şehir'], filtered['İş Birimi'], filtered['Sektör']],
                   fill_color='#f0f2f6',
                   align='center'))
        ])
        
        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0)
        )
    
        fig.update_layout(width=800)
        st.plotly_chart(fig)
        
    st.markdown('__________________________________________________________________________________________')
    
    row6_1, row6_2 = st.beta_columns((.8, 1.2))
    
    with row6_1:
        st.header('İş ilanlarında hangi tecrübe seviyeleri isteniyor?')
        st.markdown(' ')
        select1 = st.multiselect('Hangi pozisyonda çalışmak istiyorsunuz?', pozisyon_liste, default = ['Yazılım Mühendisi'], key="üç")
            
        hepsi1 = st.checkbox("Hepsini seç.", key="beş")
        
        if hepsi1:
            select1 = pozisyon_liste
        
        if select1 == []:
            pozisyon = data
        else:
             pozisyon = data[data.Pozisyon.isin(select1)]
             pozisyon.reset_index(drop = True, inplace = True)
        
        select2 = st.multiselect('Hangi bölümde okuyorsunuz?/Hangi bölümden mezunsunuz?', bolum_liste, default = ['Bilgisayar Mühendisliği'], key="üç")
        
        hepsi2 = st.checkbox("Hepsini seç.", key="altı")
        
        if hepsi2:
            select2 = bolum_liste
        
        if select2 == []:
            filtered = pozisyon
        else:
            index = []
            for i in pozisyon.index:
                for j in select2:
                    if j in pozisyon['istenen_bölümler'][i]:
                        index.append(i)
            index = list(set(index))
            filtered = pozisyon.iloc[index, :].reset_index(drop = True)
    
    with row6_2:
        grafik = filtered['Kıdem Düzeyi'].value_counts().to_frame().reset_index().rename(columns={'index': 'Kıdem Düzeyi', 'Kıdem Düzeyi':'İlan Sayısı'})
        fig = go.Figure(data=[go.Pie(labels=grafik['Kıdem Düzeyi'], values=grafik['İlan Sayısı'], hole=.3)])
        
        st.plotly_chart(fig)
        
    st.markdown('__________________________________________________________________________________________')
    
    st.header('Bilinmesi İstenen Analitik Araçlar ve Aranan Bölümler')
    st.markdown(' ')
    
    row7_1, row7_2 = st.beta_columns((.8, 1.2))
    
    with row7_1:
        select1 = st.multiselect('Hangi pozisyonda çalışmak istiyorsunuz?', pozisyon_liste, default = ['Yazılım Mühendisi'], key="dört")
            
        hepsi1 = st.checkbox("Hepsini seç.", key="yedi")
        
        if hepsi1:
            select1 = pozisyon_liste
        
        if select1 == []:
            pozisyon = data
        else:
             pozisyon = data[data.Pozisyon.isin(select1)]
             pozisyon.reset_index(drop = True, inplace = True)
             
    with row7_2:
        select2 = st.multiselect('Hangi bölümde okuyorsunuz?/Hangi bölümden mezunsunuz?', bolum_liste, default = ['Bilgisayar Mühendisliği'], key="dört")
        
        hepsi2 = st.checkbox("Hepsini seç.", key="sekiz")
        
        if hepsi2:
            select2 = bolum_liste
        
        if select2 == []:
            filtered = pozisyon
        else:
            index = []
            for i in pozisyon.index:
                for j in select2:
                    if j in pozisyon['istenen_bölümler'][i]:
                        index.append(i)
            index = list(set(index))
            filtered = pozisyon.iloc[index, :].reset_index(drop = True)
    
    row8_1, row8_2 = st.beta_columns((.9, 1.1))
    
    with row8_1:
        araclar = []

        for i in filtered.index:
            filt = eval(filtered.analitik_araclar[i])
            araclar.append(filt)
    
        araclar = list(chain.from_iterable(araclar))

        araclar = pd.Series(araclar).value_counts().to_frame(name = 'İlan Sayısı').reset_index().rename(columns={'index': 'Analitik Araçlar'})

        st.subheader('İş ilanlarında hangi analitik araçları bilmeniz isteniyor?')
        fig = px.funnel(araclar.iloc[0:10, :], x = 'İlan Sayısı', y = 'Analitik Araçlar')
        fig.update_layout(width=600,
            margin=dict(t=5)
        )
        st.plotly_chart(fig)
        
    with row8_2:
        bolumler = []

        for i in filtered.index:
            bolum = eval(filtered.istenen_bölümler[i])
            bolumler.append(bolum)
    
        bolumler = list(chain.from_iterable(bolumler))
    
        bolumler = pd.Series(bolumler).value_counts().to_frame(name = 'İlan Sayısı').reset_index().rename(columns={'index': 'Aranan Bölümler'})
    
        st.subheader('İş ilanlarında hangi bölümlerden mezun kişiler aranıyor?')
        fig = px.funnel(bolumler, x = 'İlan Sayısı', y = 'Aranan Bölümler')
        fig.update_layout(width=700,
            margin=dict(t=5)
        )
        st.plotly_chart(fig)

if sidebar_select == 'Kariyer Merkezi':
    
    sektor_liste = list(data.Sektör.unique())
    sektor_liste.remove('-')
    
    bolum_liste = []

    for i in data.index:
        filt = eval(data['istenen_bölümler'][i])
        bolum_liste.append(filt)
    
    bolum_liste = list(pd.unique(list(chain.from_iterable(bolum_liste))))
    
    row0_1, row0_2 = st.beta_columns((.85, .15))

    with row0_1:
        st.title('Kariyer Merkezi')
        st.markdown(' ')
        st.markdown("Bu uygulamada kullanılan veri seti, LinkedIn sitesiden 'yazılım' ve 'veri' anahtar kelimeleri geçen iş ilanları çekilerek oluşturulmuştur. Yazılım ve veri alanında iş ilanlarının olduğu şehirleri, sektörleri, aranan pozisyonları, bilinmesi istenen analitik araçları filtreleri kullanarak görüntüleyebilirsiniz.")

    with row0_2:
        st.write('')
        st.image('data:image/png;base64,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')
    
    row1_1, row1_2 = st.beta_columns((.8, 1.2))
    
    with row1_1:
        st.header('İş İlanlarının Şehirlere Göre Dağılımı')
        st.markdown(' ')
        select1 = st.multiselect('Sektör seçiniz.', sektor_liste, default = ['Bilgi Teknolojisi ve Hizmetleri'], key="bir")
        
        hepsi1 = st.checkbox("Hepsini seç.", key="bir")
        
        if hepsi1:
            select1 = sektor_liste
        
        if select1 == []:
            sektor = data
        else:
            sektor = data[data.Sektör.isin(select1)]
            sektor.reset_index(drop = True, inplace = True)
        
        select2 = st.multiselect('Bölüm seçiniz.', bolum_liste, default = ['Bilgisayar Mühendisliği'], key="bir")
        
        hepsi2 = st.checkbox("Hepsini seç.", key="iki")
        
        if hepsi2:
            select2 = bolum_liste
        
        if select2 == []:
            filtered = sektor      
        else:
            index = []
            for i in sektor.index:
                for j in select2:
                    if j in sektor['istenen_bölümler'][i]:
                        index.append(i)

            index = list(set(index))
    
            filtered = sektor.iloc[index, :].reset_index(drop = True)
            
        sehir = filtered['Şehir'].value_counts().to_frame().reset_index().rename(columns={'index': 'Şehir', 'Şehir':'İlan Sayısı'})
        
    with row1_2:
        turkiye_sehir = gpd.read_file('https://raw.githubusercontent.com/cads-tedu/DSPG/master/Veri%20Setleri/tr-cities-utf8.json')
    
        sehir_ilan = sehir.merge(turkiye_sehir, how = 'left', left_on = 'Şehir', right_on = 'name')
        sehir_ilan.dropna(inplace = True)
        sehir_ilan = gpd.GeoDataFrame(sehir_ilan)
    
        #bins = [0, 150, 250, 500, 615, 1400, 1900, 2500, 5000, 23900]

        m = folium.Map(location=[39.1667, 35.6667], zoom_start=5)

        choropleth = folium.Choropleth(geo_data = sehir_ilan,
                              data = sehir,
                              columns = ['Şehir', 'İlan Sayısı'],
                              key_on = 'properties.name',
                              fill_color = 'OrRd',
                              fill_opacity = 0.8,
                              line_opacity = 0.5,
                              bins = 9,
                              legend_name = 'İlan Sayısı',
                              highlight = True)
        
        for key in choropleth._children:
            if key.startswith('color_map'):
                del(choropleth._children[key])
        
        choropleth.add_to(m)

        choropleth.geojson.add_child(folium.features.GeoJsonPopup(fields = ['Şehir', 'İlan Sayısı'], labels = False))

        folium_static(m)
    
    st.markdown('__________________________________________________________________________________________')
    
    st.header('İş İlanlarında En Çok Aranan ve Başvurulan Pozisyonlar')
    st.markdown(' ')
    
    row2_1, row2_2 = st.beta_columns((1, 1))
    
    with row2_1:    
        select1 = st.multiselect('Sektör seçiniz.', sektor_liste, default = ['Bilgi Teknolojisi ve Hizmetleri'], key='iki')
        
        hepsi1 = st.checkbox("Hepsini seç.", key="üç")
        
        if hepsi1:
            select1 = sektor_liste
        
        if select1 == []:
            sektor = data
        else:
            sektor = data[data.Sektör.isin(select1)]
            sektor.reset_index(drop = True, inplace = True)
        
    with row2_2:        
        select2 = st.multiselect('Bölüm seçiniz.', bolum_liste, default = ['Bilgisayar Mühendisliği'], key='iki')
        
        hepsi2 = st.checkbox("Hepsini seç.", key="dört")
        
        if hepsi2:
            select2 = bolum_liste
        
        if select2 == []:
            filtered = sektor      
        else:
            index = []
            for i in sektor.index:
                for j in select2:
                    if j in sektor['istenen_bölümler'][i]:
                        index.append(i)

            index = list(set(index))
    
            filtered = sektor.iloc[index, :].reset_index(drop = True)
    
    row3_1, row3_2 = st.beta_columns((1, 1))
    
    with row3_1:
        st.subheader('En Çok Aranan Pozisyonlar')
        grafik = filtered['Pozisyon'].value_counts().to_frame().reset_index().rename(columns={'index': 'Pozisyon', 'Pozisyon':'İlan Sayısı'})
        fig = px.bar(grafik.sort_values('İlan Sayısı', ascending = False)[0:10], x = 'İlan Sayısı', y = 'Pozisyon', orientation='h')
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig)
        
    with row3_2:
        st.subheader('En Çok Başvurulan Pozisyonlar')
        grafik= filtered.groupby(by=['Pozisyon'])[['Pozisyon','Başvuru Sayısı']].sum().reset_index().sort_values(by='Başvuru Sayısı', ascending =False)
        fig = px.bar(grafik[0:10], x = 'Başvuru Sayısı', y = 'Pozisyon', orientation='h')
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig)
    
    st.markdown('__________________________________________________________________________________________')
    
    row4_1, row4_2 = st.beta_columns((.8, 1.2))
    
    with row4_1:
        st.header('İş İlanlarında Aranan Bölümler')
        st.markdown(' ')
        select1 = st.multiselect('Sektör seçiniz.', sektor_liste, default = ['Bilgi Teknolojisi ve Hizmetleri'], key="üç")
        
        hepsi1 = st.checkbox("Hepsini seç.", key="beş")
        
        if hepsi1:
            select1 = sektor_liste
        
        if select1 == []:
            sektor = data
        else:
            sektor = data[data.Sektör.isin(select1)]
            sektor.reset_index(drop = True, inplace = True)
        
        select2 = st.multiselect('Bölüm seçiniz.', bolum_liste, default = ['Bilgisayar Mühendisliği'], key="üç")
        
        hepsi2 = st.checkbox("Hepsini seç.", key="altı")
        
        if hepsi2:
            select2 = bolum_liste
        
        if select2 == []:
            filtered = sektor      
        else:
            index = []
            for i in sektor.index:
                for j in select2:
                    if j in sektor['istenen_bölümler'][i]:
                        index.append(i)

            index = list(set(index))
    
            filtered = sektor.iloc[index, :].reset_index(drop = True)
        
    with row4_2:
        bolumler = []

        for i in filtered.index:
            filt = eval(filtered['istenen_bölümler'][i])
            bolumler.append(filt)
    
        bolumler = list(chain.from_iterable(bolumler))

        grafik = pd.Series(bolumler).value_counts().to_frame(name = 'İlan Sayısı').reset_index().rename(columns={'index': 'Bölüm'})

        fig = px.funnel(grafik.iloc[0:10,:], x = 'İlan Sayısı',  y = 'Bölüm')
        st.plotly_chart(fig)
    
    st.markdown('__________________________________________________________________________________________')
    
    row5_1, row5_2 = st.beta_columns((.8, 1.2))
    
    with row5_1:
        st.header('İş İlanlarında Bilinmesi İstenen Analitik Araçlar')
        st.markdown(' ')
        select1 = st.multiselect('Sektör seçiniz.', sektor_liste, default = ['Bilgi Teknolojisi ve Hizmetleri'], key="dört")
        
        hepsi1 = st.checkbox("Hepsini seç.", key="yedi")
        
        if hepsi1:
            select1 = sektor_liste
        
        if select1 == []:
            sektor = data
        else:
            sektor = data[data.Sektör.isin(select1)]
            sektor.reset_index(drop = True, inplace = True)
        
        select2 = st.multiselect('Bölüm seçiniz.', bolum_liste, default = ['Bilgisayar Mühendisliği'], key="dört")
        
        hepsi2 = st.checkbox("Hepsini seç.", key="sekiz")
        
        if hepsi2:
            select2 = bolum_liste
        
        if select2 == []:
            filtered = sektor      
        else:
            index = []
            for i in sektor.index:
                for j in select2:
                    if j in sektor['istenen_bölümler'][i]:
                        index.append(i)

            index = list(set(index))
    
            filtered = sektor.iloc[index, :].reset_index(drop = True)
        
    with row5_2:
        araclar = []

        for i in filtered.index:
            filt = eval(filtered['analitik_araclar'][i])
            araclar.append(filt)
    
        araclar = list(chain.from_iterable(araclar))

        grafik = pd.Series(araclar).value_counts().to_frame(name = 'İlan Sayısı').reset_index().rename(columns={'index': 'Analitik Araç'})

        fig = px.funnel(grafik.iloc[0:10,:], x = 'İlan Sayısı',  y = 'Analitik Araç')
        st.plotly_chart(fig)
        
    st.markdown('__________________________________________________________________________________________')
    
    row6_1, row6_2 = st.beta_columns((.8, 1.2))
    
    with row6_1:
        st.header('İş İlanlarındaki Şirketlerin Çalışan Sayıları')
        st.markdown(' ')
        select1 = st.multiselect('Sektör seçiniz.', sektor_liste, default = ['Bilgi Teknolojisi ve Hizmetleri'], key="beş")
        
        hepsi1 = st.checkbox("Hepsini seç.", key="dokuz")
        
        if hepsi1:
            select1 = sektor_liste
        
        if select1 == []:
            sektor = data
        else:
            sektor = data[data.Sektör.isin(select1)]
            sektor.reset_index(drop = True, inplace = True)
        
        select2 = st.multiselect('Bölüm seçiniz.', bolum_liste, default = ['Bilgisayar Mühendisliği'], key="beş")
        
        hepsi2 = st.checkbox("Hepsini seç.", key="on")
        
        if hepsi2:
            select2 = bolum_liste
        
        if select2 == []:
            filtered = sektor      
        else:
            index = []
            for i in sektor.index:
                for j in select2:
                    if j in sektor['istenen_bölümler'][i]:
                        index.append(i)

            index = list(set(index))
    
            filtered = sektor.iloc[index, :].reset_index(drop = True)
        
    with row6_2:
        grafik = filtered['Çalışan Sayısı'].value_counts().to_frame().reset_index().rename(columns={'index': 'Çalışan Sayısı', 'Çalışan Sayısı':'İlan Sayısı'})
        grafik = grafik[grafik['Çalışan Sayısı'] != 'Bilgi Teknolojisi ve Hizmetleri']
        fig = go.Figure(data=[go.Pie(labels=grafik['Çalışan Sayısı'], values=grafik['İlan Sayısı'], hole=.3)])
        
        st.plotly_chart(fig)
    
if sidebar_select == 'Trend':
    
    #Başlık
    row0_0, row0_1 = st.beta_columns([0.85, 0.15])
    with row0_0:
        st.markdown('# Yazılım ve Veri Konularında Kariyer.net İlanlarındaki Trend')
        st.markdown('Kariyer.net verisi, **"yazılım"** ve **"veri"** anahtar kelimelerine sahip, 2019 ve 2020 yıllarında aylık bazda yayınlanan iş ilanlarını ve bu ilanlara başvuran adayların bilgilerini içermektedir.')
        st.markdown('Her grafiğin yanındaki filtreleri kullanarak şehir, sektör, üniversite, bölüm, tecrübe ve cinsiyet konularında karşılaştırmalı grafikler oluşturabilirsiniz.')
    with row0_1:
        st.image("https://icon-library.com/images/graph-icon-png/graph-icon-png-7.jpg")
        
    st.markdown(' ')
    st.header('**İş İlanları**')
    st.markdown(' ')
    
    #Şehirlere göre ilan haritası
    row1_0, row1_1= st.beta_columns([.8,1.2])
    
    with row1_0:
        st.header('Yıla ve Şehirlere Göre İş İlanları')
        st.markdown('')
        st.markdown('Yılı seçtikten sonra interaktif harita üzerinde şehirlerin üzerine tıklayarak ilan sayısını görebilirsiniz. Daha koyu renk o şehire ait daha çok ilan olduğu anlamına gelmektedir.')
        st.markdown('')
        yıl = st.radio('Yıl seçiniz:', ['2019', '2020'])
        
        
    with row1_1:
        ilan_sehir = pd.read_csv('ilan_sehir.csv', index_col = 0)
        ilan_sehir = ilan_sehir[ilan_sehir['Tarih'] == int(yıl)].reset_index(drop = True)
        turkiye_sehir = gpd.read_file('https://raw.githubusercontent.com/cads-tedu/DSPG/master/Veri%20Setleri/tr-cities-utf8.json')
    
        sehir = ilan_sehir.merge(turkiye_sehir, how = 'left', left_on = 'Şehir', right_on = 'name')
        sehir = gpd.GeoDataFrame(sehir)
    
        bins = [0, 150, 250, 500, 615, 1400, 1900, 2500, 5000, 23900]

        m = folium.Map(location=[39.1667, 35.6667], zoom_start=5)

        choropleth = folium.Choropleth(geo_data = sehir,
                              data = ilan_sehir,
                              columns = ['Şehir', 'İlan Sayısı'],
                              key_on = 'properties.name',
                              fill_color = 'OrRd',
                              fill_opacity = 0.8,
                              line_opacity = 0.5,
                              bins = bins,
                              legend_name = 'İlan Sayısı',
                              highlight = True)
        
        for key in choropleth._children:
            if key.startswith('color_map'):
                del(choropleth._children[key])
        
        choropleth.add_to(m)

        choropleth.geojson.add_child(folium.features.GeoJsonPopup(fields = ['Şehir', 'İlan Sayısı'], labels = False))

        folium_static(m)

    st.markdown('__________________________________________________________________________________________')
    
    #Sektörlere göre ilan haritası
    row2_0, row2_1= st.beta_columns([.8,1.2])
    
    ilan_sektor = pd.read_csv('ilan_sektor.csv')
    
    with row2_0:
        st.header('Sektörlere Göre İş İlanları')
        st.markdown('')
        st.markdown('Ay bazında tarih ve sektör seçerek interaktif grafik oluşturabilirsiniz. Grafiğin üstüne geldiğinizde o tarihe ve sektöre ait ilan sayısını görüntüleyebilirsiniz.')
        st.markdown('')
        tarih = st.multiselect('Karşılaştırmak istediğiniz tarihleri seçiniz:', list(ilan_sektor.Tarih.unique()), default = ['2019-1', '2020-1'])
        sektor = st.multiselect('Karşılaştırmak istediğiniz sektörleri seçiniz:', list(ilan_sektor['Firma Sektörü'].unique()), default = ['Üretim / Endüstriyel Ürünler', 'Elektrik & Elektronik', 'Otomotiv'])
        
    ilan_sektor = ilan_sektor[ilan_sektor['Tarih'].isin(tarih)].reset_index(drop=True)
    ilan_sektor = ilan_sektor[ilan_sektor['Firma Sektörü'].isin(sektor)].reset_index(drop=True)
    
    with row2_1:
        fig = px.bar(ilan_sektor, x="Tarih", y="İlan Sayısı",
             color='Firma Sektörü', barmode='group',
             height=500)
        
        st.plotly_chart(fig)
        
    st.markdown('__________________________________________________________________________________________')
        
    #Bölümlere göre ilan grafiği
    st.header('Aranan Bölümlere Göre İş İlanları')
    st.markdown('')
    
    row3_0, row3_1= st.beta_columns([.7,1.3])
    
    ilan_bolum = pd.read_csv('ilan_bolum.csv', index_col = 0)
    
    with row3_0:
        st.markdown('Ay bazında tarih ve bölüm seçerek interaktif grafik oluşturabilirsiniz. Grafiğin üstüne geldiğinizde o tarihe ve aranan bölümlere ait ilan sayısını görüntüleyebilirsiniz.')

    with row3_1:
        tarih = st.multiselect('Karşılaştırmak istediğiniz tarihleri seçiniz:', list(ilan_bolum.columns)[0:25], default = ['2020-3','2020-4', '2020-5', '2020-6', '2020-7', '2020-8'])
        bolum = st.multiselect('Karşılaştırmak istediğiniz bölümleri seçiniz:', list(ilan_bolum.index), default = ['Yazılım Mühendisliği', 'Elektrik/Elektronik Mühendisliği', 'Matematik Mühendisliği', 'Makine Mühendisliği'])
    
    ilan_bolum = ilan_bolum.loc[:, tarih]
    ilan_bolum = ilan_bolum.loc[bolum]
    
    row4_0, row4_1= st.beta_columns([.1,.9])
    
    with row4_1:
        fig = px.imshow(ilan_bolum, 
                color_continuous_scale = px.colors.sequential.OrRd,
               labels=dict(x='Tarih', y='İlanda İstenilen Bölüm Bilgisi', color='İlan Sayısı'),
               width = 1000)
        fig.update_layout(
            title={
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'})

        st.plotly_chart(fig)   
        
    st.markdown('__________________________________________________________________________________________')   
        
    #Tecrübeye göre ilan grafiği    
    row5_0, row5_1= st.beta_columns([.6,1.4])
    
    ilan_tecrube = pd.read_csv('trend_tecrübe.csv', index_col = 0)
    
    with row5_0:
        st.header('İş İlanlarında İstenen Tecrübe Seviyesinin Değişimi')
        st.markdown('')
        st.markdown('Grafik lejantı üzerinden görmek istemediğiniz tecrübe seviyelerini kapatarak filtreleme yapabilirsiniz.')

        
    with row5_1:
        fig = px.line(ilan_tecrube, x="Tarih", y=['1 Yıl', '2 Yıl', '3 Yıl', '4 Yıl', '5 Yıl', '6-7 Yıl', '8-10 Yıl',  '10+ Yıl', 'Tecrübesiz adaylar'],
              labels = {'value':'İlan Sayısı', 'variable':'Tecrübe'})
        fig.update_xaxes(
            dtick="M1",
            tickformat="%b\n%Y",
            ticklabelmode="period",
            tickangle=0)
        
        fig.update_layout(width=850)
        st.plotly_chart(fig)
        
    st.header('**İş İlanlarına Başvuranlar**')
    st.markdown(' ')    

    #Başvuranların üniversite bilgisi   
    row6_0, row6_1= st.beta_columns([.75,1.25])
    
    basvuru_uni = pd.read_csv('basvuru_uni.csv', index_col = 0)
    
    with row6_0:
        st.header('İş İlanlarına Başvuranların Üniversite Bilgisi')
        st.markdown('')
        st.markdown('Ay bazında tarih ve üniversite seçerek interaktif grafik oluşturabilirsiniz. Grafiğin üstüne geldiğinizde belirli bir üniversitenin öğrencilerinin/mezunlarının o tarihte başvurdukları ilan sayısını görüntüleyebilirsiniz.')
        tarih = st.multiselect('Karşılaştırmak istediğiniz tarihleri seçiniz:', list(basvuru_uni.Tarih.unique()), default = ['2020-3','2020-4', '2020-5', '2020-6', '2020-7', '2020-8'])
        uni = st.multiselect('Karşılaştırmak istediğiniz üniversiteleri seçiniz:', list(basvuru_uni.Üniversite.unique()), default = ['Anadolu Üniversitesi', 'Kocaeli Üniversitesi', 'İstanbul Üniversitesi (İÜ)', 'Sakarya Üniversitesi', 'Yıldız Teknik Üniversitesi (YTÜ)'])
    
    basvuru_uni = basvuru_uni[basvuru_uni['Tarih'].isin(tarih)].reset_index(drop=True)
    basvuru_uni = basvuru_uni[basvuru_uni['Üniversite'].isin(uni)].reset_index(drop=True)
    
    with row6_1:
        fig = px.bar(basvuru_uni, x="Tarih", y="İlan Sayısı",
             color='Üniversite', barmode='group',
             height=500, width=800)
        
        st.plotly_chart(fig)
    
    st.markdown('__________________________________________________________________________________________')
        
    #Başvuranların bölüm bilgisi   
    st.header('İş İlanlarına Başvuranların Bölüm Bilgisi')
    
    row7_0, row7_1= st.beta_columns([.7,1.3])
    
    basvuru_bolum = pd.read_csv('basvuru_bolum.csv', index_col = 0)
    
    with row7_0:
        st.markdown(' ')
        st.markdown('Ay bazında tarih ve bölüm seçerek interaktif grafik oluşturabilirsiniz. Grafiğin üstüne geldiğinizde belirli bir bölümün öğrencilerinin/mezunlarının o tarihte başvurdukları ilan sayısını görüntüleyebilirsiniz.')

    with row7_1:
        tarih = st.multiselect('Karşılaştırmak istediğiniz tarihleri seçiniz:', list(basvuru_bolum.columns), default = ['2020-2', '2020-3', '2020-4', '2020-5', '2020-6', '2020-7', '2020-8', '2020-9'])
        bolum = st.multiselect('Karşılaştırmak istediğiniz bölümleri seçiniz:', list(basvuru_bolum.index), default = ['Makine Mühendisliği', 'Bilgisayar Mühendisliği', 'Elektrik/Elektronik Mühendisliği', 'Endüstri Mühendisliği', 'İşletme', 'İnşaat Mühendisliği', 'Bilgisayar Programcılığı'])
    
    basvuru_bolum = basvuru_bolum.loc[:, tarih]
    basvuru_bolum = basvuru_bolum.loc[bolum]
    
    row8_0, row8_1= st.beta_columns([.1,.9])
    
    with row8_1:
        fig = px.imshow(basvuru_bolum, color_continuous_scale = px.colors.sequential.OrRd,
               labels=dict(x='Tarih', y='Üniversite Bölümü', color='İlan Sayısı'),
               width = 1000)
        fig.update_layout(
            title={
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
        
        st.plotly_chart(fig)
        
    st.markdown('__________________________________________________________________________________________')
        
    #Başvuranların cinsiyet bilgisi   
    row6_0, row6_1= st.beta_columns([1,1])
    
    basvuru_sex = pd.read_csv('trend_cinsiyet.csv', index_col = 0)
    
    with row6_0:
        st.header('İş İlanlarına Başvuranların Cinsiyet Bilgisi')
        st.markdown('')
        st.markdown('Ay bazında tarih seçerek interaktif grafik oluşturabilirsiniz. Grafiğin üstüne geldiğinizde belirli bir ay boyunca iş ilanlarına başvuranların cinsiyet dağılımını görüntüleyebilirsiniz.')
        tarih = st.multiselect('Karşılaştırmak istediğiniz tarihleri seçiniz:', list(basvuru_sex.Tarih.unique()), default = ['2019-1','2020-12'])

    basvuru_sex = basvuru_sex[basvuru_sex['Tarih'].isin(tarih)].reset_index(drop=True)
    
    
    with row6_1:
        fig =px.sunburst(basvuru_sex,
                  path=["Tarih", "Cinsiyet"],
                  values='İlan Sayısı',
                  width=500, height=500)
        
        st.plotly_chart(fig)
     
    st.markdown('__________________________________________________________________________________________')
    
    #Pozisyon sınıfları talep-başvuru karşılaştırması    
    st.subheader('**En çok aranan pozisyon sınıflarıyla, bu alanda çalışmak isteyen kişilerin başvurduğu pozisyon sınıfları örtüşüyor mu?**')
    st.markdown(' ') 
    st.header('Aranan Pozisyon Sınıfları / Başvurulan Pozisyon Sınıfları')
    st.markdown('')
    st.markdown('Seçilen yıla göre en çok ilanın yayınlandığı pozisyon sınıflarını ve en çok başvurunun yapıldığı pozisyon sınıflarını görüntüleyebilirsiniz. "En Çok Başvuru Yapılan Pozisyon Sınıfları" grafiğindeki rakamlar bir ilana başvuran kişi sayısını göstermektedir.')
    
    pozisyon_sınıf = pd.read_csv('pozisyon_sınıf.csv', index_col = 0)
    
    row7_0, row7_1= st.beta_columns([.5,1.5])
    
    with row7_0:
        tarih = st.multiselect('Yıl seçiniz:', ['2019', '2020'], default = ['2019','2020'])
    
    row8_0, row8_1= st.beta_columns([1,1])
    
    with row8_0:
        st.subheader('En Çok İş İlanı Yayınlanan Pozisyon Sınıfları')
        if tarih == ['2019']:
            fig = px.funnel(pozisyon_sınıf.sort_values('İlan_Sayısı_2019', ascending = False)[0:15], 
                            x = 'İlan_Sayısı_2019', y = 'Pozisyon_Sınıfı', labels = {'Pozisyon_Sınıfı':'Pozisyon Sınıfı'})
        elif tarih == ['2020']:
            fig = px.funnel(pozisyon_sınıf.sort_values('İlan_Sayısı_2020', ascending = False)[0:15], 
                            x = 'İlan_Sayısı_2020', y = 'Pozisyon_Sınıfı', labels = {'Pozisyon_Sınıfı':'Pozisyon Sınıfı'})
        else:
            fig = px.funnel(pozisyon_sınıf.sort_values('Toplam_İlan_Sayısı', ascending = False)[0:15], 
                            x = 'Toplam_İlan_Sayısı', y = 'Pozisyon_Sınıfı', labels = {'Pozisyon_Sınıfı':'Pozisyon Sınıfı'})
            
        st.plotly_chart(fig)
        
    with row8_1:
        st.subheader('En Çok Başvuru Yapılan Pozisyon Sınıfları')
        if tarih == ['2019']:
            fig = px.funnel(pozisyon_sınıf.sort_values('Başvuru/İlan_Oran_2019', ascending = False)[0:15], 
                            x = 'Başvuru/İlan_Oran_2019', y = 'Pozisyon_Sınıfı', labels = {'Pozisyon_Sınıfı':'Pozisyon Sınıfı'})
        elif tarih == ['2020']:
            fig = px.funnel(pozisyon_sınıf.sort_values('Başvuru/İlan_Oran_2020', ascending = False)[0:15], 
                            x = 'Başvuru/İlan_Oran_2020', y = 'Pozisyon_Sınıfı', labels = {'Pozisyon_Sınıfı':'Pozisyon Sınıfı'})
        else:
            fig = px.funnel(pozisyon_sınıf.sort_values('Başvuru/İlan_Oran', ascending = False)[0:15], 
                            x = 'Başvuru/İlan_Oran', y = 'Pozisyon_Sınıfı', labels = {'Pozisyon_Sınıfı':'Pozisyon Sınıfı'})
        
        st.plotly_chart(fig)
        
    st.markdown('__________________________________________________________________________________________')
        
    st.header('İş İlanlarına Yapılan Alakalı / Alakasız Başvurular')
    st.markdown('')
    st.markdown('Seçilen yıla ve pozisyon sınıflarına göre iş ilanlarına yapılan başvuruların yüzdesel olarak ne kadarının görüntülenip ne kadarının görüntülenmediğini görebilirsiniz.')
    
    basvuru_alaka = pd.read_csv('basvuru_alaka.csv', index_col = 0)
    basvuru_alaka.columns = ['Pozisyon_Sınıfı', 'Görüntülenen Başvuru/Toplam Başvuru(%)', 
                             'Görüntülenmeyen Başvuru/Toplam Başvuru(%)', 'Görüntülenen Başvuru/Toplam Başvuru(%) - 2019',
                             'Görüntülenmeyen Başvuru/Toplam Başvuru(%) - 2019','Görüntülenen Başvuru/Toplam Başvuru(%) - 2020',
                             'Görüntülenmeyen Başvuru/Toplam Başvuru(%) - 2020']
    
    row9_0, row9_1= st.beta_columns([.6,1.4])
    
    with row9_0:
        tarih1 = st.multiselect('Yıl seçiniz:', ['2019', '2020'], default = ['2019','2020'], key = 'ikinci')
        pozisyon = st.multiselect('Karşılaştırmak istediğiniz pozisyon sınıflarını seçiniz:', list(basvuru_alaka.Pozisyon_Sınıfı), default = ['Yazılım', 'Proje Yönetimi', '3D / Grafik Tasarım', 'Arge', 'Sistem', 'Bilgi İşlem', 'Bilgi Teknolojileri', 'İş Analizi', 'Web'])
    
    basvuru_alaka = basvuru_alaka[basvuru_alaka['Pozisyon_Sınıfı'].isin(pozisyon)].reset_index(drop=True)
    
    with row9_1:
        #st.subheader('En Çok İş İlanı Yayınlanan Pozisyon Sınıfları')
        if tarih1 == ['2019']:
            fig = px.funnel(basvuru_alaka, x = ['Görüntülenen Başvuru/Toplam Başvuru(%) - 2019', 'Görüntülenmeyen Başvuru/Toplam Başvuru(%) - 2019'], y = 'Pozisyon_Sınıfı', 
                            width = 900, labels = {'Pozisyon_Sınıfı':'Pozisyon Sınıfı', 'variable':'Başvuru'})
        elif tarih1 == ['2020']:
            fig = px.funnel(basvuru_alaka, x = ['Görüntülenen Başvuru/Toplam Başvuru(%) - 2020', 'Görüntülenmeyen Başvuru/Toplam Başvuru(%) - 2020'], y = 'Pozisyon_Sınıfı',
                            width = 900, labels = {'Pozisyon_Sınıfı':'Pozisyon Sınıfı', 'variable':'Başvuru'})
        else:
            fig = px.funnel(basvuru_alaka, x = ['Görüntülenen Başvuru/Toplam Başvuru(%)', 'Görüntülenmeyen Başvuru/Toplam Başvuru(%)'], y = 'Pozisyon_Sınıfı', 
                            width = 900, labels = {'Pozisyon_Sınıfı':'Pozisyon Sınıfı', 'variable':'Başvuru'})
            
        st.plotly_chart(fig)

