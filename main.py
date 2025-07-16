import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, date

st.set_page_config(layout='wide', page_title='Custo Frota x Entrega')
st.markdown(
        """
        <style>
        .main {
            max-width: 80vw;
            margin: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


@st.cache_data
def importar_tabelas():
    return (pd.read_excel('Custo frota CCH.xlsx', sheet_name='Custos'),
            pd.read_excel('Custo frota CCH.xlsx', sheet_name='Carregamento'))


class Dados:

    def tratar_dados(self):
        df_custo, df_entrega = importar_tabelas()

        df_custo.drop(columns=['cd_veiculo', 'nr_frota', 'nr_chassi', 'nr_ano', 'cd_pessoa', 'cd_unidade',
                               'cd_centro_custo', 'cd_historico', 'id_semana', 'cd_pessoa_filial',
                               'qt_produto', 'ds_especificacao', 'vl_unitario', 'vl_participacao',
                               'vl_capacidade_peso', 'vl_rendimento_km', 'vl_rendimento_entrega',
                               'vl_rendimento_peso', 'vl_capacidade_volume', 'cd_pessoa_motorista',
                               'cd_fornecedor', 'cd_carga', 'Mês', 'Ano'], inplace=True)

        df_entrega.drop(columns=['nm_pessoa_trans', 'nm_pessoa_motora', 'Mês', 'Ano'], inplace=True)

        df_custo['dt_documento'] = pd.to_datetime(df_custo['dt_documento'], dayfirst=True, errors='coerce')
        df_entrega['dt_saida'] = pd.to_datetime(df_entrega['dt_saida'], dayfirst=True, errors='coerce')

        df_custo['mes_ano'] = df_custo['dt_documento'].dt.strftime('%m/%Y')
        df_entrega['mes_ano'] = df_entrega['dt_saida'].dt.strftime('%m/%Y')

        return df_custo, df_entrega


class Dashboard:

    def criar_elementos(self):
        st.title('Análise de custo com frota x entregas')
        df_custo, df_entrega = Dados().tratar_dados()

        with st.sidebar.subheader('Filtrar placas'):
            placas = df_entrega['ds_placa'].dropna().unique()
            placas_selecionadas = st.multiselect('Selecione as placas:', options=sorted(placas))

            if placas_selecionadas:
                df_entrega = df_entrega[df_entrega['ds_placa'].isin(placas_selecionadas)]
                df_custo = df_custo[df_custo['ds_placa'].isin(placas_selecionadas)]

        soma_entregas = df_entrega['qt_entregas'].sum()
        df_entregas_por_placa = df_entrega.groupby('ds_placa')['qt_entregas'].sum().reset_index()
        df_tipo_entrega = df_entrega.groupby('Tipo entrega')['qt_entregas'].sum().reset_index()
        soma_custo_total = df_custo['vl_total'].sum()

        soma_custo_total_formatado = (f'R$ {soma_custo_total:,.2f}'.replace(',', 'X')
                                      .replace('.', ',')).replace('X', '.')

        custo_por_frete = soma_custo_total / soma_entregas
        custo_por_frete_formatado = (f'R$ {custo_por_frete:,.2f}'.replace(',', 'X')
                                     .replace('.', ',')).replace('X', '.')

        st.markdown('<div class="center-container">', unsafe_allow_html=True)

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div style="background-color:#e9f7fd; height: 200px; padding:20px; border-radius:10px;
                border: 1.5px solid #94a8b0; box-shadow:0 2px 4px #6a787e;">
                    <h4 style="margin-bottom:5px;">Total de Entregas Realizadas</h4>
                    <p style="font-size:28px; font-weight:bold; color:#e98d2c;">{soma_entregas}</p>
                    <p style="color:#1db954; margin-top:10px;">Atualizado hoje às {datetime.today().time().strftime('%H:%M')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div style="background-color:#e9f7fd; height: 200px; padding:20px; border-radius:10px;
                border: 1.5px solid #94a8b0; box-shadow:0 2px 4px #6a787e;">
                    <h4 style="margin-bottom:5px;">Custo total acumulado</h4>
                    <p style="font-size:28px; font-weight:bold; color:#e98d2c;">{soma_custo_total_formatado}</p>
                    <p style="color:#1db954; margin-top:10px;">Atualizado hoje às {datetime.today().time().strftime('%H:%M')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div style="background-color:#e9f7fd; height: 200px; padding:20px; border-radius:10px;
                border: 1.5px solid #94a8b0; box-shadow:0 2px 4px #6a787e;">
                    <h4 style="margin-bottom:5px;">Custo por entrega</h4>
                    <p style="font-size:28px; font-weight:bold; color:#e98d2c;">{custo_por_frete_formatado}</p>
                    <p style="color:#1db954; margin-top:10px;">Atualizado hoje às {datetime.today().time().strftime('%H:%M')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()
        col3, col4 = st.columns(2)

        with col3:
            st.subheader('Entregas por placa')
            fig = px.bar(df_entregas_por_placa.sort_values(by='qt_entregas', ascending=False), x='ds_placa',
                         y='qt_entregas', text='qt_entregas', title='Entregas por placa',
                         color_discrete_sequence=['#1db954'])
            fig.update_layout(margin=dict(l=40, r=40, t=40, b=40))
            st.plotly_chart(fig, use_container_width=True)
            st.divider()

        with col4:
            st.subheader('Tipos de entrega')
            fig = px.pie(df_tipo_entrega, names='Tipo entrega', values='qt_entregas',
                         color_discrete_sequence=['#1db954', '#e98d2c'])
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
            st.divider()

        st.subheader('Entregas mensal')
        df_entrega_para_grafico = df_entrega.groupby('mes_ano')['qt_entregas'].sum().reset_index()
        fig = px.area(
            df_entrega_para_grafico.sort_values(by='mes_ano'),
            x='mes_ano',
            y='qt_entregas',
            title='Entregas por mês',
            text='qt_entregas',
            color_discrete_sequence=['#1db954'],
            line_shape='spline'
        )
        fig.update_traces(texttemplate='%{text:.2s}', textposition='top center')
        fig.update_layout(margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

        st.subheader('Custo mensal')
        df_custo_para_grafico = df_custo.groupby('mes_ano')['vl_total'].sum().reset_index()
        fig = px.area(
            df_custo_para_grafico.sort_values(by='mes_ano'),
            x='mes_ano',
            y='vl_total',
            title='Custo por mês',
            text='vl_total',
            color_discrete_sequence=['#1db954'],
            line_shape='spline'
        )
        fig.update_traces(texttemplate='%{text:.2s}', textposition='top center')
        fig.update_layout(margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

        st.subheader('Tabela de custos')
        st.dataframe(df_custo, hide_index=True, use_container_width=True)
        st.divider()
        st.subheader('Tabela de entregas')
        st.dataframe(df_entrega, hide_index=True, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)


dashboard = Dashboard()
dashboard.criar_elementos()
