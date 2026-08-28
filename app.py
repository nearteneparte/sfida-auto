import streamlit as st
import pandas as pd
import os

# Configurazione pagina Streamlit
st.set_page_config(
    page_title="Enciclopedia Sfida Auto",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ Enciclopedia Sfida Auto")
st.write("Filtra per marca, scegli i due sfidanti e scopri la più veloce!")

CSV_FILE = "database_auto.csv"

# @st.cache_data
def load_data():
    if not os.path.exists(CSV_FILE):
        return None
    
    try:
        # skiprows=3 salta le prime 3 righe di intestazione del file Excel
        df = pd.read_csv(
            CSV_FILE, 
            skiprows=3, 
            sep=None, 
            engine='python', 
            decimal=','
        )
        
        # Pulizia nomi colonne
        df.columns = df.columns.astype(str).str.strip()
        
        # Pulizia dati e conversione numerica
        for col in df.columns:
            # Sostituisce trattini o caratteri non validi con NaN
            df[col] = df[col].replace(['-', ' - ', 'N/A', 'nan'], None)
            
        return df
    except Exception as e:
        st.error(f"Errore nella lettura del file CSV: {e}")
        return None

df = load_data()

if df is None or df.empty:
    st.warning("⚠️ Carica il file 'database_auto.csv' nel tuo repository GitHub per accedere alla libreria completa!")
else:
    # --- FILTRI LATERALE ---
    st.sidebar.header("🔍 Filtri")
    marche_disponibili = ["Tutte"] + sorted(list(df['Marca'].dropna().astype(str).unique()))
    marca_selezionata = st.sidebar.selectbox("Filtra per Marca:", marche_disponibili)
    
    if marca_selezionata != "Tutte":
        df_filtrato = df[df['Marca'] == marca_selezionata].copy()
    else:
        df_filtrato = df.copy()

    # Etichetta unificata per la selezione
    df_filtrato['Versione'] = df_filtrato['Versione'].fillna('')
    df_filtrato['Auto_Label'] = df_filtrato['Marca'].astype(str) + " " + df_filtrato['Modello'].astype(str) + " " + df_filtrato['Versione'].astype(str)
    auto_list = df_filtrato['Auto_Label'].tolist()
    
    st.subheader("⚔️ SFIDA DIRETTA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔴 Sfidante 1")
        auto1_label = st.selectbox("Seleziona la prima vettura:", auto_list, key="auto1")
        auto1_data = df_filtrato[df_filtrato['Auto_Label'] == auto1_label].iloc[0]
        
    with col2:
        st.markdown("### 🔵 Sfidante 2")
        default_index = 1 if len(auto_list) > 1 else 0
        auto2_label = st.selectbox("Seleziona la seconda vettura:", auto_list, index=default_index, key="auto2")
        auto2_data = df_filtrato[df_filtrato['Auto_Label'] == auto2_label].iloc[0]

    st.markdown("---")
    
    # --- LOGICA DI CONFRONTO E ATTRIBUZIONE PUNTI ---
    
    # Definizione delle metriche e se "più alto è meglio" (True) o "più basso è meglio" (False)
    # Cerchiamo le colonne corrispondenti nel DataFrame
    metrics_config = [
        ('Potenza', 'Potenza', True, 'CV'),
        ('0-100 km/h', '0-100', False, 's'),
        ('Velocità Massima', 'Vel. Max', True, 'km/h'),
        ('Ripresa 80-120 km/h', 'Ripresa', False, 's'),
        ('1/4 di Miglio', '1/4 Miglio', False, 's'),
        ('Tempo Nürburgring', 'Nürburgring', False, 's')
    ]

    punti_auto1 = 0
    punti_auto2 = 0
    
    table_rows = []

    # Aggiungi informazioni generali non valutate
    for info_col in ['Categoria']:
        for col_name in df.columns:
            if info_col.lower() in col_name.lower():
                val1 = auto1_data.get(col_name, '-')
                val2 = auto2_data.get(col_name, '-')
                table_rows.append({
                    "Parametro": info_col,
                    f"🔴 {auto1_label}": str(val1) if pd.notna(val1) else "-",
                    f"🔵 {auto2_label}": str(val2) if pd.notna(val2) else "-",
                    "Esito": "-"
                })

    # Ciclo di confronto metriche prestazionali
    for label, search_kw, higher_is_better, unit in metrics_config:
        # Individua la colonna esatta
        matched_col = None
        for c in df.columns:
            if search_kw.lower() in c.lower():
                matched_col = c
                break
        
        val1_raw = auto1_data.get(matched_col, None) if matched_col else None
        val2_raw = auto2_data.get(matched_col, None) if matched_col else None
        
        # Conversione a float per il confronto
        try:
            val1 = float(str(val1_raw).replace(',', '.')) if pd.notna(val1_raw) else None
        except:
            val1 = None
            
        try:
            val2 = float(str(val2_raw).replace(',', '.')) if pd.notna(val2_raw) else None
        except:
            val2 = None

        esito = "-"
        
        if val1 is not None and val2 is not None:
            if val1 == val2:
                esito = "Pareggio"
            elif (higher_is_better and val1 > val2) or (not higher_is_better and val1 < val2):
                punti_auto1 += 1
                esito = f"🏆 {auto1_data['Marca']}"
            else:
                punti_auto2 += 1
                esito = f"🏆 {auto2_data['Marca']}"
        elif val1 is not None and val2 is None:
            punti_auto1 += 1
            esito = f"🏆 {auto1_data['Marca']} (Dato unico)"
        elif val2 is not None and val1 is None:
            punti_auto2 += 1
            esito = f"🏆 {auto2_data['Marca']} (Dato unico)"

        str_val1 = f"{val1} {unit}" if val1 is not None else "-"
        str_val2 = f"{val2} {unit}" if val2 is not None else "-"

        table_rows.append({
            "Parametro": label,
            f"🔴 {auto1_label}": str_val1,
            f"🔵 {auto2_label}": str_val2,
            "Esito": esito
        })

    # --- TABELLA E PUNTEGGI ---
    st.subheader("📊 Confronto Prestazioni e Punteggio")
    
    comp_df = pd.DataFrame(table_rows)
    st.table(comp_df)

    # Box Risultato Finale
    st.markdown("### 🏁 Risultato Finale")
    
    score_col1, score_col2 = st.columns(2)
    with score_col1:
        st.metric(label=f"Punti 🔴 {auto1_label}", value=f"{punti_auto1} Punti")
    with score_col2:
        st.metric(label=f"Punti 🔵 {auto2_label}", value=f"{punti_auto2} Punti")

    if punti_auto1 > punti_auto2:
        st.success(f"🎉 **VINCITRICE: {auto1_label}** con {punti_auto1} punti contro {punti_auto2}!")
    elif punti_auto2 > punti_auto1:
        st.success(f"🎉 **VINCITRICE: {auto2_label}** con {punti_auto2} punti contro {punti_auto1}!")
    else:
        st.info("⚖️ **PAREGGIO PERFETTO!** Le due vetture hanno ottenuto lo stesso punteggio.")

    # Visualizzazione dell'intero Database filtrato
    with st.expander("📁 Visualizza intero Database filtrato"):
        st.dataframe(df_filtrato.drop(columns=['Auto_Label'], errors='ignore'))   
