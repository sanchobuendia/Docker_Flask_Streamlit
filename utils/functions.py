import subprocess
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from streamlit_plotly_events import plotly_events
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from datetime import date

@st.cache(allow_output_mutation=True)

def custom_age_selector():
    """Shows a window in the sidebar for creating custom age groups"""
    # Based on https://discuss.streamlit.io/t/multiselect-only-updating-for-every-second-input/1767
    col1, col2 = st.columns(2)

    with col1:
        range_start = st.number_input("Início", min_value=0, max_value=130, step=1, format="%d")
    with col2:
        range_end = st.number_input("Fim", min_value=0, max_value=130, step=1, format="%d") 
    faixa_str = f"{str(range_start)}-{str(range_end)}"
    
    if st.button("Adicionar"):
        if faixa_str in st.session_state.faixas:
            st.error("Faixa já inserida!")
        elif any([range_start in x for x in st.session_state.faixas_dict.values()]):
            st.error(f"Faixa inserida tem sobreposição com faixas já existentes!")
        elif any([range_end in x for x in st.session_state.faixas_dict.values()]):
            st.error(f"Faixa inserida tem sobreposição com faixas já existentes!")
        else:
            st.session_state.faixas.append(faixa_str)
            st.session_state.faixas_dict[faixa_str] = range(range_start, range_end)
    
    last_faixas = st.session_state.faixas
    st.session_state.faixas = st.multiselect("Faixas etárias", st.session_state.faixas, st.session_state.faixas, key="selected")
    st.session_state.faixas_dict = { key: st.session_state.faixas_dict[key] for key in st.session_state.faixas }
    if last_faixas != st.session_state.faixas or last_faixas != list(st.session_state.faixas_dict.keys()):
        st.experimental_rerun()
        
    return(st.session_state.faixas) 

def read_clients(query_inicial, project_id, credentials):
    """Read patient data and calculate age from date of birth and get ficha number"""
    df_clients = pd.read_gbq(query_inicial, project_id=project_id, dialect='standard', credentials=credentials)
    while any(df_clients.Regra_1.isnull()):
        print("estou no while!")
        subprocess.call("echo 'estou no while!!'", shell=True)
        test = df_clients[df_clients.Regra_1.isnull()]
        print(test[['ID_PEFI_CD_PESSOA_FISICA', 'ID_CLIE_NR_CLIENTE','CLDI_NO_NOME_COMPLETO', 'Regra_1']])       
        df_clients = pd.read_gbq(query_inicial, project_id=project_id, dialect='standard', credentials=credentials)
    df_clients["idade"] = df_clients.CLDI_DT_NASCIMENTO.apply(calculate_age)
    df_clients["Prefixo"] = df_clients["CLDI_NR_ULTIMA_FICHA"].str.slice(0, 3)
    return(df_clients)

def process_clients(df_clients):
    """Cleanup data for displaying in AgGrid component in Regras app"""
    df_clients['sum'] = df_clients[df_clients.columns[pd.Series(df_clients.columns).str.startswith('Regra')]].sum(axis=1)
    cols = [5, 8, 9, 10, 12, 13]
    print(df_clients.columns)
    
    for c in cols:
        df_clients[f"Regra_{c}"] = df_clients[f"Valor_{c}"].apply(lambda x: -1 if np.isnan(x) else x)   
    df_clients = df_clients[['ID_CLIE_NR_CLIENTE', 'CLDI_NO_NOME_COMPLETO', 'CLDI_CD_SEXO', 'idade', 'CLDI_NR_ULTIMA_FICHA', 'DT_ULT_EXAME', 'Regra_1', 'Regra_2', 'Regra_3', 'Regra_4', 'Regra_5', 'Regra_6', 'Regra_7', 'Regra_8', 'Regra_9','Regra_10','Regra_11', 'Regra_12', 'Regra_13', 'sum']]
    df_clients.columns = ['ID', 'Nome', 'Sexo', 'Idade', 'Ficha', 'Data', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9','R10', 'R11', 'R12', 'R13', 'sum']
    df_clients['Data'] = pd.to_datetime(df_clients['Data'], errors='coerce').dt.strftime('%d/%m/%Y')
    df_clients.sort_values(by=['sum'], ascending = False, inplace = True)
    df_clients.drop(columns=['sum'], inplace=True) 
    df_clients.replace({True:'Sim', False: 'Não'}, inplace=True)
    print(df_clients)
    return(df_clients)

def from_to(v, start, end):
    """Helper function for selecting intervals within lists"""
    for i in range(0, len(v)):
        if v[i] == start:
            start_pos = i
        if v[i] == end:
            end_pos = i
    return(v[start_pos:end_pos+1])

def plot_bars(df_sex):
    """Bar chart for showing the number of patients in each Rule in the FILTERED df_clients"""
    df_sex_long = df_sex.loc[:, ~df_sex.columns.str.startswith("Valor")]
    df_sex_long  = df_sex_long.melt(id_vars = from_to(df_sex.columns, 'ID_PEFI_CD_PESSOA_FISICA', 'DT_ULT_EXAME'), 
                          value_vars = df_sex.columns[df_sex.columns.str.startswith("Regra")] )

    fig = px.histogram(df_sex_long, x='variable', y='value', color="value", histfunc="count")
    fig.update_traces(hovertemplate = "<br>".join(["Regra: %{x}","Contagem: %{y}"]))
    fig.update_layout(legend={"title_text": ''}, xaxis={"title":""}, yaxis={"title":"# de Pacientes"})
    selected_points = plotly_events(fig)
    return(selected_points)

def create_aggrid(df_show):
    """Create the AgGrid table to be shown after a rule is selected"""
    gb = GridOptionsBuilder.from_dataframe(df_show)
    gb.configure_selection(selection_mode="single")
    gridOptions = gb.build()
    grid_response = AgGrid(df_show, gridOptions=gridOptions, 
        update_mode=GridUpdateMode.MODEL_CHANGED)
    return(grid_response)

def calculate_age(born):
    """Calculates a person's age given their birth date"""
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def get_color_string(s, color):
    """Helper function to format a string with a given color"""
    color_string = f'<span style="color:{color};font-size:15.0pt"><b>{s}</b></span>'
    return(color_string)

def my_caption(text):
    """Helper function to format text according to st.caption's formatting"""
    st.caption(f'<span style="color:#31333f;">{text}</span>', unsafe_allow_html=True)

def create_checkbox_group(caption, keys, values):
    """Function to create a group of related checkboxes"""
    my_caption(f"{caption}")
    values_list = [st.checkbox(x, value=True) for x in values]
    values_dict = dict(zip(keys, values_list))
    bool_list = [k for k, v in values_dict.items() if v]
    return(bool_list)

def write_plot_title(title):
    """Function for formatting the plot titles in the Analytics app"""
    st.markdown(f"<h5 style='text-align: center; '>{title}</h5>", unsafe_allow_html=True)

def apply_age_filter(df_clients):
    if st.session_state.age_selector_page == "Slider":
        df_clients = df_clients[df_clients.idade.between(st.session_state.age_list[0], st.session_state.age_list[1])]
        df_clients["faixa_etaria"] = pd.cut(df_clients["idade"], bins=[0, 12, 18, 30, 50, 70, 90, np.inf], 
            labels=["0-12", "13-18", "19-30", "31-50", "51-70", "71-90", "91+"], include_lowest=True)
    else:
        bins = make_bins(st.session_state.age_list)
        df_clients["faixa_etaria"] = pd.cut(df_clients["idade"], bins=bins, labels=st.session_state.age_list)
        df_clients = df_clients.dropna(subset=["faixa_etaria"])    
    return(df_clients)

def apply_filters(df):
    """Applies selected filters in sidebar to df_clients and regional_df"""
    # Sex
    df = df[df.CLDI_CD_SEXO.isin(st.session_state.sex_list)]

    # Age
    df = apply_age_filter(df)

    # Regional
    df = df[df.CLDI_SL_REGIONAL.isin(st.session_state.regionais)]

    # Marca
    df = df[df.CLDI_NO_MARCA.isin(st.session_state.marcas)]

    # Unidade
    if len(st.session_state.unidades) > 0:
        df = df[df.Prefixo.isin(st.session_state.unidades)]

    return(df)

def make_bins(age_list):
    """Defines bins from age groups in "x-y" format"""
    bins = []
    bins.append(age_list[0].split("-")[0])
    bins = bins + [x.split("-")[1] for x in age_list]
    bins = [int(x) for x in bins]
    return(bins)
