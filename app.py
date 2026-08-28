import streamlit as st
import pandas as pd
import os

# Configurazione pagina Streamlit
st.set_page_config(
    page_title="Enciclopedia Sfida Auto",
    page_icon="🏎️",
    layout="wide"
)

# Titolo ed intestazione
st.title("🏎️ Enciclopedia Sfida Auto")
st.write("Filtra per marca, scegli i due sfidanti e scopri la più veloce!")

# Nome del file CSV nella repository GitHub
CSV_FILE = "database_auto.csv"

@st.cache_data
def load_data():
    if not os.path.exists(CSV_FILE):
        return None
    
    try:
        # skiprows=3 salta le 3 righe di titolo/descrizione presenti nel file Excel
        # sep=None con engine='python' individua automaticamente se il separatore è ';' o tab/virgola
        # decimal=',' converte i numeri decimali italiani (es. 6,7 -> 6.7)
        df = pd.read_csv(
            CSV_FILE, 
            skiprows=3, 
            sep=None, 
            engine='python', 
            decimal=','
        )
        
        # Pulizia nomi colonne da eventuali spazi bianchi extra
        df.columns = df.columns.astype(str).str.strip()
        
        # Conversione colonne numeriche se necessario
        cols_numeriche = ['Potenza (CV)', '0-100 km/h (s)', 'Vel. Max (km/h)', 'Ripresa 80-120 (s)', '1/4 Miglio (s)', 'Nürburgring (s)']
        for col in cols_numeriche:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df
    except Exception as e:
        st.error(f"Errore nella lettura del file CSV: {e}")
        return None

# Caricamento dati
df = load_data()

if df is None or df.empty:
    st.warning("⚠️ Carica il file 'database_auto.csv' nel tuo repository GitHub per accedere alla libreria completa!")
else:
    # --- INTERFACCIA APP STREAMLIT ---
    
    # Barra laterale / Filtri
    st.sidebar.header("🔍 Filtri")
    
    # Selezione Marca
    marche disponibili = ["Tutte"] + sorted(list(df['Marca'].dropna().unique()))
    marca_selezionata = st.sidebar.selectbox("Filtra per Marca:", marche disponibili)
    
    if marca_selezionata != "Tutte":
        df_filtrato = df[df['Marca'] == marca_selezionata]
    else:
        df_filtrato = df

    # Creazione etichetta univoca per le auto (Marca + Modello + Versione)
    df_filtrato['Auto_Label'] = df_filtrato['Marca'] + " " + df_filtrato['Modello'] + " (" + df_filtrato['Versione'].fillna('') + ")"
    auto_list = df_filtrato['Auto_Label'].tolist()
    
    st.subheader("⚔️ Confronto Diretto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Auto 1")
        auto1_label = st.selectbox("Seleziona la prima vettura:", auto_list, key="auto1")
        auto1_data = df_filtrato[df_filtrato['Auto_Label'] == auto1_label].iloc[0]
        
    with col2:
        st.markdown("### Auto 2")
        # Imposta di default la seconda auto se disponibile
        default_index = 1 if len(auto_list) > 1 else 0
        auto2_label = st.selectbox("Seleziona la seconda vettura:", auto_list, index=default_index, key="auto2")
        auto2_data = df_filtrato[df_filtrato['Auto_Label'] == auto2_label].iloc[0]

    st.markdown("---")
    
    # Tabella di confronto prestazioni
    st.subheader("📊 Scheda Tecnica e Prestazioni")
    
    metrics = [
        ('Categoria', 'Categoria', False),
        ('Potenza', 'Potenza (CV)', True),
        ('Accelerazione 0-100 km/h', '0-100 km/h (s)', False), # Minore è meglio
        ('Velocità Massima', 'Vel. Max (km/h)', True),      # Maggiore è meglio
        ('Ripresa 80-120 km/h', 'Ripresa 80-120 (s)', False),  # Minore è meglio
        ('1/4 di Miglio', '1/4 Miglio (s)', False),           # Minore è meglio
        ('Tempo Nürburgring', 'Nürburgring (s)', False)       # Minore è meglio
    ]
    
    comparison_data = []
    
    for label, col_name, higher_is_better in metrics:
        val1 = auto1_data.get(col_name, "-")
        val2 = auto2_data.get(col_name, "-")
        
        comparison_data.append({
            "Parametro": label,
            f"{auto1_data['Marca']} {auto1_data['Modello']}": val1,
            f"{auto2_data['Marca']} {auto2_data['Modello']}": val2
        })
        
    comp_df = pd.DataFrame(comparison_data)
    st.table(comp_df)

    # Visualizzazione dell'intero Database filtrato
    with st.expander("📁 Visualizza intero Database filtrato"):
        st.dataframe(df_filtrato.drop(columns=['Auto_Label'], errors='ignore'))
