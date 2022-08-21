#!/usr/bin/env python
# -*- coding: utf-8 -*-

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")


###-----MAPPING DICTS---###
dict_bibs = {'LASH': 'BU Lettres',
             'SJA': 'PBU Saint-Jean d\'Angely',
             'DROIT': 'BU Droit',
             'MEDP': 'BU Médecine Pasteur',
             'SCIEN': 'Bu Sciences',
             'EPU': 'Learning Centre',
             'STAPS': 'BU Staps',
             'ARCHE': 'BU Médecine antenne Archet'
             }

color_discrete_map={0: 'rgb(177, 164, 191)', 1: 'rgb(86, 213, 183)'}

###-----HELPERS FUNCTIONS---###

###-----DATA---###

def load_data():
    df = pd.read_csv("notebooks/data/tous_exemplaires_ready.csv", sep=",", encoding="utf-8")
    # Pour les visus on limite sur les dates de pub sup. à 1900
    df =  df[df.date_pub >= 1900]
    for column_name in ['date_pub', 'statut_ex', 'bib', 'pret', 'acces', 'acq', 'indice']:
        df[column_name] = df[column_name].astype('category')
    return df

data = load_data()

@st.cache(suppress_st_warning=True)
def filtered_data(data,date,bibs):
    df = data[(data.date_pub.astype(int) >= int(date[0])) & (data.date_pub.astype(int) <= int(date[1])) & (data.bib.isin(bibs))]
    return df

###-----LAYOUT---###

# Sidebar
st.sidebar.markdown('''
# Paramètres des graphiques
### Date de publication
''')
date_pub_min = data.date_pub.astype(int).min()
date_pub_max = data.date_pub.astype(int).max()
date_pub_range = range(date_pub_min,date_pub_max)
selected_pub_date = st.sidebar.select_slider(
    'Seélectionner une période',
    options=[i for i in list(map(str,date_pub_range))],
    value=("1950", "2020"))
st.sidebar.write(f"{selected_pub_date[0]} à {selected_pub_date[1]}")

st.sidebar.markdown('''
### Bibliothèque
''')
bib_multiselect = st.sidebar.multiselect(
     'Sélectionner une ou plusieurs bibliothèques',
     dict_bibs.keys(),
     dict_bibs.keys())
#st.sidebar.write([dict_bibs[x] for x in bib_multiselect])

st.sidebar.markdown('''
### Style des graphiques en barre
''')
selected_barchart_type = st.sidebar.radio('Selectionner un type ',["valeurs absolues","pourcentage"])

# Main section
st.title('Analyse & exploration de l\'usage des collections à partir des données d\'exemplaires du SCD UCA')
st.subheader("Les données ne portent que sur les exemplaires créés sur la période 2015-2021")
st.warning('La variable pret est une variable binaire prenant 2 valeurs : 1 pour les documents ayant fait l\'objet d\'au moins un emprunt, 0 pour les documents n\'ayant jamais été empruntés.')

#sub-section 1
with st.container():
    col1,col2 = st.columns((1,2))
    with col1:
        st.markdown("### Proportion de documents empruntés / jamais empruntés")
        fig1_1 = px.pie(filtered_data(data,selected_pub_date,bib_multiselect), names='pret', color='pret', color_discrete_map=color_discrete_map)
        st.plotly_chart(fig1_1,use_container_width=True)
    with col2:
        st.markdown("### Circuit du document")
        fig1_2 = px.parallel_categories(filtered_data(data,selected_pub_date,bib_multiselect), dimensions=['bib', 'acq', 'acces', 'pret'])
        fig1_2.update_layout(autosize=True)
        st.plotly_chart(fig1_2,use_container_width=True)

st.warning('Les variables sont affichées par ordre décroissant de leur capacité prédictive (ie de leur contribution à la variance de la variable cible)')

#sub-section 2
with st.container():
    st.subheader("Date de publication")
    if selected_barchart_type == "pourcentage":
        fig2 = px.histogram(filtered_data(data,selected_pub_date,bib_multiselect), x='date_pub', barnorm='percent', color='pret', color_discrete_map=color_discrete_map)
    else:
        fig2 = px.histogram(filtered_data(data,selected_pub_date,bib_multiselect), x='date_pub', barmode='group', color='pret', color_discrete_map=color_discrete_map)
    fig2.update_xaxes(categoryorder='total descending')
    fig2.update_layout(autosize=True)
    st.plotly_chart(fig2,use_container_width=True)

with st.container():
    st.subheader("Ecart entre date de création des exemplaires et dates de publication")
    selected_outliers = st.radio('Selectionner ',["avec outliers","sans outliers"])
    if selected_outliers == "sans outliers":
        ouliers_data = filtered_data(data,selected_pub_date,bib_multiselect)
        filtered_ouliers_data = ouliers_data[ouliers_data.diff_datecreation_datepub <= 50]
    else:
        filtered_ouliers_data = filtered_data(data,selected_pub_date,bib_multiselect)
    col1,col2 = st.columns((1,1))
    with col1:
        fig3_1 = px.histogram(filtered_ouliers_data, x='diff_datecreation_datepub', color='pret', color_discrete_map=color_discrete_map, title='Histogramme')
        fig3_1.update_xaxes(title_text='écart en nb d\'année')
        fig3_1.update_yaxes(title_text='nombre d\'exemplaires')
        fig3_1.update_layout(autosize=True)
        st.plotly_chart(fig3_1,use_container_width=True)
    with col2:
        fig3_2 = px.box(filtered_ouliers_data, y='diff_datecreation_datepub', facet_col='pret', color='pret', color_discrete_map=color_discrete_map, title='Boxplot')
        fig3_2.update_xaxes(title_text='écart')
        fig3_2.update_yaxes(title_text='nombre d\'exemplaires')
        fig3_2.update_layout(autosize=True)
        st.plotly_chart(fig3_2,use_container_width=True)

#sub-section 3
with st.container():
    st.subheader("Indice de cote")
    col1,col2 = st.columns((1,1))
    with col1:
        fig4_1 = px.treemap(filtered_data(data,selected_pub_date,bib_multiselect), path=['indice'], title='Répartition')
        fig4_1.update_layout(autosize=True)
        st.plotly_chart(fig4_1,use_container_width=True)
    with col2:
        if selected_barchart_type == "pourcentage":
            fig4_2 = px.histogram(filtered_data(data,selected_pub_date,bib_multiselect), x='indice', color='pret', barnorm="percent",color_discrete_map=color_discrete_map, title='Usage par indice de cote')
        else:
            fig4_2 = px.histogram(filtered_data(data,selected_pub_date,bib_multiselect), x='indice', color='pret', color_discrete_map=color_discrete_map, title='Usage par indice de cote')
        fig4_2.update_xaxes(categoryorder='total descending')
        fig4_2.update_xaxes(title_text='indice de cote')
        fig4_2.update_yaxes(title_text='nombre d\'exemplaires')
        fig4_2.update_layout(autosize=True)
        st.plotly_chart(fig4_2,use_container_width=True)

#sub-section 4
with st.container():
    st.subheader("Accès direct/indirect")
    col1,col2 = st.columns((2,1))
    with col1:
        fig5_1 = px.histogram(filtered_data(data,selected_pub_date,bib_multiselect), x='date_pub', color='acces', barnorm='percent', color_discrete_sequence=px.colors.qualitative.Pastel, title='Répartition par date de publication')
        fig5_1.update_xaxes(title_text='date de publication')
        fig5_1.update_yaxes(title_text='nombre d\'exemplaires')
        fig5_1.update_layout(autosize=True)
        st.plotly_chart(fig5_1,use_container_width=True)
    with col2:
        fig5_2 = px.pie(filtered_data(data,selected_pub_date,bib_multiselect), names="acces", color='acces', color_discrete_sequence=px.colors.qualitative.Pastel, title='Répartition globale')
        fig5_2.update_layout(autosize=True)
        st.plotly_chart(fig5_2,use_container_width=True)
