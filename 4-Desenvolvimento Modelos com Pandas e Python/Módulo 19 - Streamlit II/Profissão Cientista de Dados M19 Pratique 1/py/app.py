import pandas as pd
import timeit
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title="Aula: Análise de Telemarketing",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="..\\img\\telmarketing_icon.png",
)

# Ajuste de tema no seaborn
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

@st.cache_data(show_spinner=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=";")
    except Exception:
        return pd.read_excel(file_data)

@st.cache_data
def multiselect_filter(df, col, selecionados):
    if "all" in selecionados:
        return df
    return df[df[col].isin(selecionados)].reset_index(drop=True)

@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return output.getvalue()

def main():
    st.write("# Análise de Telemarketing")
    st.markdown("---")

    # Sidebar: imagem e upload
    image = Image.open("..\\img\\Bank-Branding.jpg")
    st.sidebar.image(image)
    st.sidebar.write("## Suba o arquivo")
    data_file = st.sidebar.file_uploader("Bank marketing data", type=["csv", "xlsx"])

    if data_file is None:
        st.warning("👋 Para começar, por favor envie um arquivo CSV ou Excel usando a barra lateral.")
        return

    # Carrega dados e cronometra
    start = timeit.default_timer()
    bank_raw = load_data(data_file)
    elapsed = timeit.default_timer() - start
    st.write(f"Tempo de leitura: {elapsed:.2f} segundos")

    bank = bank_raw.copy()
    graph_type = st.radio("Tipo de gráfico:", ("Barras", "Pizza"))

    # Sidebar: filtros
    with st.sidebar.form("filters_form"):
        min_age, max_age = int(bank_raw.age.min()), int(bank_raw.age.max())
        idades = st.slider(
            "Intervalo de idades",
            min_value=min_age,
            max_value=max_age,
            value=(min_age, max_age),
        )
        st.write("Idade mínima:", idades[0])
        st.write("Idade máxima:", idades[1])

        jobs_list = bank.job.unique().tolist() + ["all"]
        jobs_selected = st.multiselect("Profissão", jobs_list, ["all"])

        marital_list = bank.marital.unique().tolist() + ["all"]
        marital_selected = st.multiselect("Estado civil", marital_list, ["all"])

        default_list = bank.default.unique().tolist() + ["all"]
        default_selected = st.multiselect("Default", default_list, ["all"])

        housing_list = bank.housing.unique().tolist() + ["all"]
        housing_selected = st.multiselect("Financiamento", housing_list, ["all"])

        loan_list = bank.loan.unique().tolist() + ["all"]
        loan_selected = st.multiselect("Tem empréstimo?", loan_list, ["all"])

        contact_list = bank.contact.unique().tolist() + ["all"]
        contact_selected = st.multiselect("Contato", contact_list, ["all"])

        month_list = bank.month.unique().tolist() + ["all"]
        month_selected = st.multiselect("Mês do contato", month_list, ["all"])

        dow_list = bank.day_of_week.unique().tolist() + ["all"]
        dow_selected = st.multiselect("Dia da semana", dow_list, ["all"])

        submit_button = st.form_submit_button("Aplicar")

    # Aplica filtros
    if submit_button:
        bank = (
            bank
            .query("age >= @idades[0] and age <= @idades[1]")
            .pipe(multiselect_filter, "job", jobs_selected)
            .pipe(multiselect_filter, "marital", marital_selected)
            .pipe(multiselect_filter, "default", default_selected)
            .pipe(multiselect_filter, "housing", housing_selected)
            .pipe(multiselect_filter, "loan", loan_selected)
            .pipe(multiselect_filter, "contact", contact_selected)
            .pipe(multiselect_filter, "month", month_selected)
            .pipe(multiselect_filter, "day_of_week", dow_selected)
        )

    # Calcula proporções
    bank_raw_target_perc = (
        bank_raw.y
        .value_counts(normalize=True)
        .to_frame(name="proportion")
        .sort_index() * 100
    )
    try:
        bank_filtered_target_perc = (
            bank.y
            .value_counts(normalize=True)
            .to_frame(name="proportion")
            .sort_index() * 100
        )
    except Exception as e:
        st.error(f"Erro ao calcular proporção filtrada: {e}")
        bank_filtered_target_perc = pd.DataFrame(columns=["proportion"])

    # Download: tabela filtrada
    xlsx_full = to_excel(bank)
    st.download_button(
        "📥 Download tabela filtrada em EXCEL",
        data=xlsx_full,
        file_name="bank_filtered.xlsx"
    )
    st.markdown("---")

    # Download: proporções
    col1, col2 = st.columns(2)
    xlsx_raw_perc = to_excel(bank_raw_target_perc)
    col1.write("### Proporção original")
    col1.dataframe(bank_raw_target_perc)
    col1.download_button(
        "📥 Download proporção original",
        data=xlsx_raw_perc,
        file_name="bank_raw_y.xlsx"
    )

    xlsx_filt_perc = to_excel(bank_filtered_target_perc)
    col2.write("### Proporção filtrada")
    col2.dataframe(bank_filtered_target_perc)
    col2.download_button(
        "📥 Download proporção filtrada",
        data=xlsx_filt_perc,
        file_name="bank_y.xlsx"
    )
    st.markdown("---")

    # Exibição de tabelas
    st.write("# Antes dos filtros")
    st.dataframe(bank_raw.head())
    st.write("# Depois dos filtros")
    st.dataframe(bank.head())
    st.markdown("---")

    # Gráficos de proporção
    st.write("## Proporção de aceite")
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    if graph_type == "Barras":
        # Gráfico de barras
        sns.barplot(
            x=bank_raw_target_perc.index,
            y="proportion",
            data=bank_raw_target_perc,
            ax=ax[0],
            palette="muted"
        )
        ax[0].bar_label(ax[0].containers[0])
        ax[0].set_ylabel("Porcentagem de Aceites (%)")
        ax[0].set_title("Referência (dados brutos)", fontweight="bold")

        sns.barplot(
            x=bank_filtered_target_perc.index,
            y="proportion",
            data=bank_filtered_target_perc,
            ax=ax[1],
            palette="muted"
        )
        ax[1].bar_label(ax[1].containers[0])
        ax[1].set_ylabel("Porcentagem de Aceites (%)")
        ax[1].set_title("Dados filtrados", fontweight="bold")

    else:
        # Gráfico de pizza
        bank_raw_target_perc.plot(
            kind="pie",
            y="proportion",
            autopct="%.2f%%",
            ax=ax[0],
            legend=False
        )
        ax[0].set_ylabel("")
        ax[0].set_title("Referência (dados brutos)", fontweight="bold")

        bank_filtered_target_perc.plot(
            kind="pie",
            y="proportion",
            autopct="%.2f%%",
            ax=ax[1],
            legend=False
        )
        ax[1].set_ylabel("")
        ax[1].set_title("Dados filtrados", fontweight="bold")

    st.pyplot(fig)


if __name__ == "__main__":
    main()