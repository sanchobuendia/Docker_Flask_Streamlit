from hydralit import HydraApp

#### Streamlit packages
import streamlit as st
from streamlit_tags import st_tags_sidebar

# google cloud packages
from google.oauth2 import service_account  

# utils is a folder with .py files where you can find functions used in the process
from utils.functions import read_clients, create_checkbox_group, apply_filters, my_caption, custom_age_selector
from patients.pacientes_v2 import PacientesAppV2

# rules is a folder with .py files where you can find the all rules used in the process
from rules.regras_v2 import RegrasAppV2

# analytics is a folder with .py files where you can find the analytics process
from analytics.analytics_v2 import AnalyticsAppV2   

########################################################################################
# The first step to create a dashboard using streamlit is to choose the kind and position of bottons/sidebar/ etc.
# The app.py is where we difine the first interface.
# Here the user will choose the parameters and the streamlit will send the chosen parameters to the analisys in background.
# It is necessary to define which parameters the user can choose and this is done here in app.py



if __name__ == '__main__':
    
    # Initialize session_state variables
    
    # If the "patient_id" is not defined the streamlit will indentify it as None
    if "patient_id" not in st.session_state:
        st.session_state.patient_id = None
        
    # The dataset used in this project is stored in the google cloud.
    # The Google Cloud has a structure divided in projects and it is necessary to specify the project name.
    # Here the our project name is "ped-prd".
    if "project_id" not in st.session_state:
        st.session_state.project_id = "ped-prd"
        
    # The access to Google Cloud is restrict and it is necessary permissions to access the project.
    # The credentials are in a json file.
    if "credentials" not in st.session_state:
        st.session_state.credentials = service_account.Credentials.from_service_account_file(r'ped-prd-5b950150a8e0.json')
        
        
    # Initialize bottons parameters 
    
    if "sex_list" not in st.session_state:
        st.session_state.sex_list = ["M", "F"]
        
    if "age_selector_page" not in st.session_state:
        st.session_state.age_selector_page = "Slider"
        
    if "age_list" not in st.session_state:
        st.session_state.age_list = [0, 130]
        
    if "faixas" not in st.session_state or st.session_state.age_selector_page == "Slider":
        st.session_state.faixas = ["0-12", "13-18", "19-30", "31-50", "51-70", "71-90"]
        
    if "faixas_dict" not in st.session_state or st.session_state.age_selector_page == "Slider":
        st.session_state.faixas_dict = { "0-12":range(0, 13), "13-18":range(13, 19), 
            "19-30": range(19, 31), "31-50": range(31, 51), "51-70":range(31, 71), "71-90": range(71, 91) }
    
    if "regionais" not in st.session_state:
        st.session_state.regionais = ['SP', 'RJ', 'RS', 'PE', 'PR', 'MA', 'BA', 'RN', 'DF', None]
        
    if "marcas" not in st.session_state:
        st.session_state.marcas = ['AM', 'FL', 'WE', 'CA', 'SC', 'NO', 'DM', 'LA', 'LC', 'IL', 'CC', 'FM', None]
        
    if "unidades" not in st.session_state:
        st.session_state.unidades = []
        

    # Fix streamlit to 'wide' mode
    st.set_page_config(page_title='Template', layout="wide", page_icon="⚕️")

    # Remove padding at top of app
    hide_streamlit_style = "<style>#root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 1rem;}</style>"
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    #this is the host application, we add children to it and that's it!
    app = HydraApp(title='Template', navbar_animation=False, hide_streamlit_markers=False)
    
    ##############################################################################################################################

    st.title('Template')

    date_changed = False

    with st.sidebar:
        
        db_page = st.radio("Status", ["Diabéticos", "Pré-Diabéticos"])
        # Gender selector
        st.session_state.sex_list = create_checkbox_group("Gender", ["M", "F"], ["Men", "Women"])
        
        if len(st.session_state.sex_list) == 0:
            st.error("Please select at least one gender!")
            st.stop()

        # Age type selector 
        st.session_state.age_selector_page = st.radio("Age selector", ["Slider", "Customizado"])
        if st.session_state.age_selector_page == "Slider":
            st.session_state.age_list = st.slider("Age", value=[0, 130])
            st.session_state.faixas = ["0-12", "13-18", "19-30", "31-50", "51-70", "71-90"]
        else:
            st.session_state.age_list = custom_age_selector()
            if len(st.session_state.age_list) == 0:
                st.error("Please create at least one age group!")
                st.stop()

        # State selector
        last_regionais = st.session_state.regionais
        regionais = ['SP', 'RJ', 'RS', 'PE', 'PR', 'MA', 'BA', 'RN', 'DF', None]
        st.session_state.regionais  = st.multiselect("State", regionais, regionais)
        if len(st.session_state.regionais) == 0:
                st.error("Please select at least one state!")
                st.stop()

        # Brand selector
        marcas = ['AM', 'FL', 'WE', 'CA', 'SC', 'NO', 'DM', 'LA', 'LC', 'IL', 'CC', 'FM', None]
        last_marcas = st.session_state.marcas
        st.session_state.marcas  = st.multiselect("Brand", marcas, marcas)
        if len(st.session_state.marcas) == 0:
            st.error("Please select at least one brand!")
            st.stop()

        # Unit selector
        my_caption("Unit")
        st.session_state.unidades = st_tags_sidebar(
            label= "",
            text='Enter units or nothing to use all!',
            value=[],
            #suggestions=st.session_state.suggestions,
            maxtags = -1)

        # Date ranges selector
        dates_range = st.date_input('Initial date  - Final date ', [])
        
        # If no date has been set yet.
        # The Streamlit defines it.
    
        if len(dates_range) > 0:
            date_changed = True
            start_date = dates_range[0]
            end_date = dates_range[1]

            if start_date is None or end_date is None:
                pass
            # If the dates are updated.
            # We build a new dataset based on the chosen dates.
            # 
            else:
                if start_date <= end_date:
                    query_clients = f"""
                        call `ped-prd.bdiabetes.pd__ajusta_dtResultado`(DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY), current_date());
                        call `ped-prd.bdiabetes.pd_cria_cliente_dl`('{start_date}', '{end_date}');
                        call `ped-prd.bdiabetes.pd_gera_regra_1_13_vs2`('{start_date}', '{end_date}');
                        call `ped-prd.bdiabetes.pd_exibe_regra_1_13_vs2`(null);"""
                    df_clients = read_clients(query_clients, st.session_state.project_id, st.session_state.credentials)
                else:
                    st.error('Error: End date must be equal to or later than start date.')
    
    ####################### Pages #####################################
    # As can see on page we can choose between two options: Rules and Analytics
    # By default the page that is showed is the Rules page, because it is the first to be declared here in the script.
    
    
    # Initially for the default configuration, streamlit shows the results of a prepared dataset that is saved in BigQuery.
    # Thi query get the dataset
    query_inicial = f"call `ped-prd.bdiabetes.pd_exibe_regra_1_13_vs2`(null);"
    
    # Read clients data and apply filters
    if not date_changed: # If no date range was selected in sidebar
        df_clients = read_clients(query_inicial, st.session_state.project_id, st.session_state.credentials)

    # Apply filters selected in sidebar to df_clients
    #st.session_state
    
    
    # In the end we need to pass to the streamlit a data set with the user's choices.
    # At the first moment before the user makes any choice.
    # The Streamlit shows the default to each botton in the left tree.
    # The apply_filters is the function that applies all user's choices.
    
    df_clients = apply_filters(df_clients)

    # Add apps. The apps appear as three options. Each option represents a different page 
    app.add_app("Analytics", icon="📈", app=AnalyticsAppV2(db_page, df_clients))
    app.add_app("Rules", icon="✍", app=RegrasAppV2(db_page, df_clients))
    app.add_app("Patients", icon="😷", app=PacientesAppV2())
        
    # run the streamlit interface
    app.run()