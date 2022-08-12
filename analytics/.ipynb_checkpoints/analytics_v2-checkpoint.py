from hydralit import HydraHeadApp
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import streamlit as st

from utils.functions import get_color_string, write_plot_title, calculate_age, apply_filters


class AnalyticsAppV2(HydraHeadApp):
    def __init__(self, db_page, df_clients, title = "Analytics"):
        self.db_page = db_page
        self.df_clients = df_clients
        self.title = title

    def write_period(self):
        """Create and format a string with selected start and end dates"""
        min_date = str(self.df_clients.DT_ULT_EXAME.min()).split(" ")[0]
        max_date = str(self.df_clients.DT_ULT_EXAME.max()).split(" ")[0]
        st.markdown(f"Selected period: from {get_color_string(min_date, '#0068c9')} a {get_color_string(max_date, '#0068c9')}", unsafe_allow_html=True)
        
    ################### Analysis page charts    ###########################################################
        
    def plot_sex_pie(self):
        """Display a pie chart showing male and female % in the FILTERED df_clients"""
        df_pie = pd.DataFrame(self.df_clients.CLDI_CD_SEXO.value_counts())
        fig = px.pie(df_pie, values='CLDI_CD_SEXO', hole=0.7, names=df_pie.index, color=df_pie.index.to_list(),
            color_discrete_map={"F": "#EF553B","M": "#636EFA"})
        fig.update_layout(yaxis={"title":"# of patients"})
        st.plotly_chart(fig, use_container_width=True)

    def plot_single_age_bar(self):
        """Show a barplot containing the % of each age group in the FILTERED df_clients"""
        # bar
        age_values = self.df_clients.value_counts("faixa_etaria", normalize=True).to_frame()
        age_values = age_values.reset_index()
        age_values["order"] = age_values["faixa_etaria"].str.slice(0, 1)
        age_values = age_values.sort_values("order")
        age_values.columns = ["faixa_etaria", "prop", "order"]
        age_values["x"] = 0
        age_values["values"] = round(100*age_values["prop"], 2)
        age_values["values"] = age_values["values"].astype(str) + "%"
        bar = px.bar(age_values, y="x", x="prop", color="faixa_etaria", height=200, 
            text="values", orientation="h")
        bar.update_layout(legend={"orientation": "h", "title_text": 'Age group:'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis={'visible': False, 'showticklabels': False}, yaxis={'visible': False, 'showticklabels': False})
        st.plotly_chart(bar, use_container_width=True)

    def plot_age_bars(self):
        """Show a barplot containing the % of each age group/sex in the FILTERED df_clients"""
        age_df = self.df_clients.copy()
        age_df["order"] = age_df["faixa_etaria"].str.slice(0, 1)
        age_df = age_df.sort_values("order")

        age_bars = px.histogram(age_df.sort_values("idade"), x="faixa_etaria", color="CLDI_CD_SEXO",
            labels={"faixa_etaria":"Faixa Etária", "CLDI_CD_SEXO":""}, 
            color_discrete_map={"M": "#636EFA", "F": "#EF553B"}, category_orders={"CLDI_CD_SEXO": ["F", "M"]}) 
        age_bars.update_layout(yaxis={"title":"# de Pacientes"})
        st.plotly_chart(age_bars, use_container_width=True)

    def analito_hist(self, analito_option):
        """Show a histogram + density curve + rug plot for selected analytes"""
        analito_dict = {
            "Hemoglobina Glicada" : "Valor_5",
            #"Glicose" : , 
            "Colesterol não-HDL" : "Valor_13", 
            "Albuminúria" : "Valor_10"}

        hist_data = [self.df_clients[analito_dict[analito_option]].dropna()]
        group_labels = [analito_option] 

        fig = ff.create_distplot(hist_data, group_labels)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    def regional_sunburst(self):
        """Plot a sunburst chart for viewing regional info"""

        df = self.df_clients[["CLDI_SL_REGIONAL", "CLDI_NO_MARCA", "Prefixo"]]
        regional_counts = df.value_counts().reset_index()
        regional_counts.columns = ["Regional", "Marca", "Prefixo", "Counts"]

        fig = px.sunburst(regional_counts, path=["Regional", "Marca", "Prefixo"], values="Counts")
        return(fig)
    
    ###################################################################################################


    # Organization of plots on the page
    # Page layout setup
    
    def run(self): 
        # Show selected period
        self.write_period()

        col1, col2, col3 = st.columns(3)
        with col1:
            # Pie chart
            write_plot_title('Gender Proportion of Patients')
            self.plot_sex_pie()
        
        with col2: 
            # Age/Sex bar chart
            write_plot_title('Gender Count by Age Group of Patients')
            self.plot_age_bars()

        with col3: 
            # Analyte density
            if "analito_option" not in st.session_state:
                st.session_state["analito_option"] = "Hemoglobina Glicada"
            write_plot_title(f'Densidade de {st.session_state.analito_option}')
            st.selectbox('Select the desired analyte', ["Hemoglobina Glicada", "Colesterol não-HDL", "Albuminúria"], 
                key='analito_option')
            self.analito_hist(st.session_state.analito_option)
        
        # Age groups bar
        write_plot_title('Proportion of Age Group of Patients')
        self.plot_single_age_bar()

        col4, col5 = st.columns(2)
        with col4:
            
            write_plot_title('Medical Records Regional')
            sun = self.regional_sunburst()
            st.plotly_chart(sun)
        with col5:
            pass
            
        
