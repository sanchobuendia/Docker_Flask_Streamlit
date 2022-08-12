from hydralit import HydraHeadApp
import streamlit as st
from utils.functions import plot_bars, process_clients, create_aggrid


def regras_expander():
    """Define an expander box with rule explanations"""
    with st.expander("Explicação das regras"):
        st.write("""
                **Regra 1** : AAGAD (Positivo),  \n
                **Regra 2** : AAINS (Positivo),  \n
                **Regra 3** : AAICA512 (Positivo), \n
                **Regra 4** : AAZNT8 (Positivo), \n
                **Regra 5** : Hemoglobina Glicada (Último exame) >= 6,5 e Eliminar fichas 300, 303, 306, 311 e fichas controle de qualidade, \n
                **Regra 6** : Idade <= 20 e Hemoglobina Glicada Anterior (Somente) <= 5,7 (Sem insulina em medicamentos), \n
                **Regra 7** : Hemoglobina Glicada >= 9,5 e Cetonúria >= 50, \n
                **Regra 8** : Hemoglobina Glicada >= 10 e Hemoglobina Glicada Anterior (Todas Anteriores) < 6,5 e Glicemia (Todas Anteriores) < 126 (Sem insulina em medicamentos), \n
                **Regra 9** : Hemoglobina (Homem) < 12,8 e Hemoglobina (Mulher) < 12, \n
                **Regra 10** : Albuminúria (qualquer uma no último ano) > Valor de Referência, \n
                **Regra 11** : Sem Albuminúria no Último Ano, \n
                **Regra 12** : Creatinina (qualquer uma no último ano) > Valor de Referência, \n
                **Regra 13** : Idade >= 50 (Homem) ou Idade >= 57 (Mulher) e COLNHDL >= 100 """)

class RegrasAppV2(HydraHeadApp):
    
    def __init__(self, db_page, df_clients, title = "Rules"):
        self.db_page = db_page
        self.df_clients = df_clients
        self.title = title

    def run(self):
        df_clients = self.df_clients.copy()

        # Plot bars
        if len(df_clients.CLDI_CD_SEXO) == 0:
            st.error("Please select at least one option for 'Gender'")
            st.stop()

        st.write("Click on the bars to expand patient information.")
        selected_points = plot_bars(df_clients)

        # Rules expander
        regras_expander()

        if len(selected_points) > 0:
            # Show selected bar data
            curve_number_dict = {0: False, 1: True}
            df_show = df_clients[ df_clients[selected_points[0]["x"]] == curve_number_dict[selected_points[0]["curveNumber"]] ]

            # Clean up data
            df_show = process_clients(df_show)

            # Show AgGrid table
            grid_response = create_aggrid(df_show)

            if len(grid_response["selected_rows"]) == 0:
                st.stop()
                
            # Pass patient_id to session_state to be accessed by Patients app
            st.session_state.patient_id = grid_response['selected_rows'][0]["ID"]

            

        


