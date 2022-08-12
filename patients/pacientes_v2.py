from hydralit import HydraHeadApp
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.functions import create_aggrid, calculate_age
import plotly.express as px

@st.cache
def get_patient_info(patient_id, project_id, credentials):
    """Retrieves patient information from BigQuery"""
    if patient_id is None:
        st.stop()

    # pay attention that the query takes the columns of an array
    df_sql = f"""
        SELECT 
            CLDI.CLDI_NO_NOME_COMPLETO as Nome,  
            CLDI.CLDI_CD_SEXO          as Sexo, 
            CLDI.CLDI_DT_NASCIMENTO    as Data_Nascimento,
            CLDI.CLDI_NO_MARCA         as Marca,
            CLDI.CLDI_DH_ULTIMA_FICHA  as Data_Abertura_Ficha,
            CLDI.CLDI_NO_MEDICO        as Medico,  
            CLDI.CLDI_SL_REGIONAL      as Regional,
            CLDI.CLDI_NR_CONTATO       as Contato,
            CLDI.CLDI_NR_ULTIMA_FICHA  as Ficha
        FROM ped-prd.bdiabetes.PD_CZTB_CLIENTE_DIABETE_CLDI CLDI
        WHERE CLDI.ID_CLIE_NR_CLIENTE = {patient_id}
        ORDER BY Data_Abertura_Ficha DESC
        """

    patient_df = pd.read_gbq(df_sql, project_id=project_id, dialect='standard', credentials=credentials)
    return(patient_df)

def show_patient_info(patient_df):
    """Formats patient information into columns"""
    
    st.markdown("# Patient:")
    st.markdown(f"## {patient_df.Nome[0]}")

    col1, col2 = st.columns(2)
    
    with col1: 
        st.markdown(f"### Gender: {patient_df.Sexo[0]}")
        idade = calculate_age(patient_df.Data_Nascimento[0])
        st.markdown(f"### Age: {idade}")
        st.markdown(f"### Unit: {patient_df.Regional[0]}")
        st.markdown(f"### Brand: {patient_df.Marca[0]}")

    with col2: 
        st.markdown(f"### Requester: {patient_df.Medico[0]}")
        st.markdown(f"### Contact: {patient_df.Contato[0]}")
        ult_data_str = patient_df['Data_Abertura_Ficha'].astype(str).iloc[0]
        ult_data = ult_data_str.split(" ")[0]#.replace("-", "/")
        ult_data = datetime.strftime(datetime.strptime(ult_data, "%Y-%m-%d"), "%d/%m/%Y")
        st.markdown(f"### Last exam (HGBGLIC): {ult_data}")
        st.markdown(f"### Last medical record: {patient_df.Ficha[0]}")    

@st.cache(allow_output_mutation=True)
def graph_evol(analitos_dict, graph_option, patient_id, project_id, credentials):
    """Creates graphs pertaining to patient analyte information"""

    analitos = ', '.join(f"'{x}'" for x in analitos_dict[graph_option])
    query_analito = f"""
        SELECT * FROM ped-prd.bdiabetes.PD_CZTB_ANALITO_CLIENTE 
        WHERE ID_CLIE_NR_CLIENTE = {patient_id} AND Exame IN ({analitos})
        ORDER BY horario"""

    analitos_df = pd.read_gbq(query_analito, project_id=project_id, dialect='standard', credentials=credentials)

    fig_analito = px.line(analitos_df, x='Data', 
                    y='Resultado', 
                    hover_data=["Ficha", 'Exame'])
    fig_analito.update_layout(
        xaxis_title="<b>Date", 
        yaxis_title="<b>Result",
        title=f'<b>{graph_option}',
        title_x=0.5,
        font_color='black',
        plot_bgcolor='rgba(0,0,0,0)')
    fig_analito.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#F8F8F8', tickfont=dict(color='black', size=12))
    fig_analito.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#F8F8F8', tickfont=dict(color='black', size=12))
    fig_analito.update_traces(mode='lines+markers', 
                            line=dict(color='#363841', width=7), 
                            marker=dict(color='#FFFFFF', 
                                        size=13,
                                        line = dict(color='#363841', width=6)), 
                            connectgaps=True)
    return(fig_analito)

@st.cache(suppress_st_warning=True)
def ficha_patient(patient_id, project_id, credentials):
    """Get past patient records"""

    df_sql = f"""
        SELECT concat(right(concat('0000000',FICH.ID_UNID_CD_UNIDADE_FICHA),3),right(concat('0000000',FICH.ID_FICH_NR_FICHA),7)) as Ficha,
            cast(FICH.FICH_DH_ABERTURA as date) as Data
        FROM ped-prd.bdiabetes.FI_SZTB_FICHA_FICH FICH
        WHERE ID_CLIE_NR_CLIENTE = {patient_id}  
        ORDER by FICH.FICH_DH_ABERTURA DESC
    """ 
    df = pd.read_gbq(df_sql, project_id=project_id, dialect='standard', credentials=credentials)
    df['Data'] = pd.to_datetime(df['Data']).dt.strftime('%d/%m/%Y')
    df.columns = ['Ficha', 'Data de Abertura']
    #_ = create_aggrid(df)
    grid_response = create_aggrid(df)

class PacientesAppV2(HydraHeadApp):
    analitos_dict = {
        "Hemoglobina Glicada" : ['HGBGLIC', 'HGBGLICTE'],
        "Glicose" : ['GLIC','GLICPL','GLICURG','GTT2'],
        "Frutosamina" : ['FRUT'],
        "Anidroglucitol": ['ANIDROGLUT'],
        "Glicosúria": ['GLICUR','GLIURURG','URIN','URIN1J','URIN2J','URIN3J',
            'URINFITA','URINMP','URINSV','URINUNI','URIN1JUNI','URIN2JUNI',
            'URIN3JUNI','URINURG','URIN1JURG','URIN2JURG','URIN3JURG'],
        "Cetonúria": ['CETON','URIN','URIN1J','URIN2J','URIN3J','URINFITA','URINMP',
            'URINSV','URINUNI','URIN1JUNI','URIN2JUNI','URINURG','URIN1JURG',
            'URIN2JURG','URIN3JURG','URIN3JUNI'],
        "Albuminúria": ['CETON','URIN','URIN1J','URIN2J','URIN3J','URINFITA','URINMP',
            'URINSV','URINUNI','URIN1JUNI','URIN2JUNI','URINURG','URIN1JURG',
            'URIN2JURG','URIN3JURG','URIN3JUNI'],
        "Creatinina": ['CREAT','CREATISO','CREATURG','CALCDEPCRE','DEPCREAT'],
        "AAGAD": ["AAGAD"],
        "AAINS": ['AAINS', 'AAINSTE'],
        "AAICA512": ['AAICA512','AAICA512TE'],
        "AAZNT8": ["AAZNT8"],
        "COLNHDL": ["COLNHDL"]
    }

    def __init__(self, title = "Patients"):
        self.title = title
    
    def run(self):
        # Error message if no patient is selected in 'Regras'
        if st.session_state.patient_id is None:
            st.error("Please select a patient in the 'Rules' tab")
        # Get patient information
        patient_df = get_patient_info(st.session_state.patient_id, st.session_state.project_id, st.session_state.credentials)
        # Display patient information
        show_patient_info(patient_df)
        # Show options for patient info visualization - Laudo evolutivo / Fichas
        info_page = st.radio("", options=["Evolutionary report", "Medical records"])
        if info_page == "Evolutionary report":
            # Graph selection
            graph_option = st.selectbox('Select the desired graphic', self.analitos_dict.keys())
            st.write(f'Has been selected: {graph_option}')
            # Show graph
            st.plotly_chart(graph_evol(self.analitos_dict, graph_option, st.session_state.patient_id, st.session_state.project_id, st.session_state.credentials), use_container_width=True)
        elif info_page == "Medical records":
            # Show patient records (fichas)
            ficha_patient(st.session_state.patient_id, st.session_state.project_id, st.session_state.credentials)


