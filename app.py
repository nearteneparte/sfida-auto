import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Enciclopedia Sfida Auto 🏎️", page_icon="🏎️", layout="centered")

st.title("🏎️ Enciclopedia Sfida Auto")
st.caption("Filtra per marca, scegli i due sfidanti e scopri la più veloce!")

# Caricamento del Database dal file CSV
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("database_auto.csv")
    except:
        st.error("⚠️ Carica il file 'database_auto.csv' nel tuo repository GitHub per accedere alla libreria completa!")
        return pd.DataFrame()

    # Stima automatica 1/4 miglio per auto senza dato Carwow da pista
    mask_carwow = df['Carwow_1_4_miglio_s'].isna()
    df.loc[mask_carwow, 'Carwow_1_4_miglio_s'] = np.round(df.loc[mask_carwow, 'Zero_100_s'] + 5.4, 2)

    df["Auto_Completa"] = df["Marca"].astype(str) + " " + df["Modello"].astype(str) + " (" + df["Versione"].astype(str) + ")"
    return df.sort_values(by=["Marca", "Modello"]).reset_index(drop=True)

df = load_data()

if not df.empty:
    st.subheader("🔍 Selezione Sfidanti")
    
    marchi = ["Tutti i Marchi"] + sorted(df["Marca"].astype(str).unique().tolist())
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_m1 = st.selectbox("Marca 🔴 Prima Auto", marchi, index=0)
    with col_f2:
        filtro_m2 = st.selectbox("Marca 🔵 Seconda Auto", marchi, index=0)

    lista_1 = df["Auto_Completa"] if filtro_m1 == "Tutti i Marchi" else df[df["Marca"] == filtro_m1]["Auto_Completa"]
    lista_2 = df["Auto_Completa"] if filtro_m2 == "Tutti i Marchi" else df[df["Marca"] == filtro_m2]["Auto_Completa"]

    col1, col2 = st.columns(2)
    with col1:
        auto_1_nome = st.selectbox("🔴 Seleziona Auto 1", lista_1, index=0)
    with col2:
        idx_def = 1 if len(lista_2) > 1 else 0
        auto_2_nome = st.selectbox("🔵 Seleziona Auto 2", lista_2, index=idx_def)

    auto_1 = df[df["Auto_Completa"] == auto_1_nome].iloc[0]
    auto_2 = df[df["Auto_Completa"] == auto_2_nome].iloc[0]

    # Logica Sfida e Punteggi
    metriche = [
        ("Potenza (CV)", "Potenza_CV", "max"),
        ("Accelerazione 0-100 km/h (s)", "Zero_100_s", "min"),
        ("Velocità Max (km/h)", "Vel_Max_kmh", "max"),
        ("Ripresa 80-120 km/h (s)", "Ripresa_80_120_s", "min"),
        ("1/4 Miglio Carwow (s)", "Carwow_1_4_miglio_s", "min"),
        ("Giro Nürburgring (s)", "Nurburgring_s", "min")
    ]

    punti_1, punti_2 = 0, 0
    dettagli = []

    for nome, col, tipo in metriche:
        v1, v2 = auto_1[col], auto_2[col]
        txt1 = f"{v1:.2f}".rstrip('0').rstrip('.') if pd.notnull(v1) else "N/D"
        txt2 = f"{v2:.2f}".rstrip('0').rstrip('.') if pd.notnull(v2) else "N/D"
        vincitore = "Pareggio 🤝"
        
        if pd.notnull(v1) and pd.notnull(v2):
            if (tipo == "max" and v1 > v2) or (tipo == "min" and v1 < v2):
                punti_1 += 1
                vincitore = f"🏆 {auto_1['Marca']}"
            elif (tipo == "max" and v2 > v1) or (tipo == "min" and v2 < v1):
                punti_2 += 1
                vincitore = f"🏆 {auto_2['Marca']}"

        dettagli.append({"Parametro": nome, auto_1_nome: txt1, auto_2_nome: txt2, "Esito": vincitore})

    # Risultati
    st.markdown("---")
    res_a, res_b = st.columns(2)
    res_a.metric(f"🔴 {auto_1['Marca']} {auto_1['Modello']}", f"{punti_1} Punti")
    res_b.metric(f"🔵 {auto_2['Marca']} {auto_2['Modello']}", f"{punti_2} Punti")

    if punti_1 > punti_2:
        st.balloons()
        st.success(f"🎉 **Vince la {auto_1_nome}!**")
    elif punti_2 > punti_1:
        st.balloons()
        st.success(f"🎉 **Vince la {auto_2_nome}!**")
    else:
        st.info("🤝 **Incredibile pareggio!**")

    st.subheader("🔍 Dettaglio Sfida")
    st.dataframe(pd.DataFrame(dettagli), use_container_width=True)

    st.markdown("---")
    if st.button("🔄 Aggiorna dati se aggiungi nuove auto"):
        st.cache_data.clear()
        st.rerun()
