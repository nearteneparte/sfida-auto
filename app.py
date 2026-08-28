import streamlit as st
import pandas as pd
import numpy as np

# Configurazione pagina per iPhone
st.set_page_config(page_title="Sfida Auto 🏎️", page_icon="🏎️", layout="centered")

st.title("🏎️ Sfida Auto: Chi vince?")
st.caption("Seleziona due auto dal listino completo e scopri la più veloce!")

# Caricamento Database Esteso + Auto Manuali Fondamentali
@st.cache_data
def load_data():
    # Base dati manuale (Supercar, SUV top e auto iconiche con dati pista/carwow)
    data_speciali = [
        ["Ferrari", "SF90", "Stradale", "Supercar", 1000, 2.5, 340, np.nan, 9.6, np.nan],
        ["Ferrari", "296", "GTB", "Supercar", 830, 2.9, 330, np.nan, 9.7, np.nan],
        ["Ferrari", "Purosangue", "6.5 V12", "SUV", 725, 3.3, 310, 2.1, 11.1, np.nan],
        ["Porsche", "911", "GT3 RS (992)", "Supercar", 525, 3.2, 296, np.nan, 10.8, 409.32],
        ["Porsche", "911", "Turbo S", "Supercar", 650, 2.7, 330, 1.8, 10.1, 437.30],
        ["Lamborghini", "Revuelto", "6.5 V12 Hybrid", "Supercar", 1015, 2.5, 350, np.nan, 9.5, np.nan],
        ["Lamborghini", "Urus", "Performante", "SUV", 666, 3.3, 306, 2.3, 11.4, 456.30],
        ["Tesla", "Model S", "Plaid", "Berlina Elettrica", 1020, 2.1, 322, 1.2, 9.2, 455.55],
        ["Volkswagen", "Tiguan", "2.0 TDI 150 CV", "SUV", 150, 9.4, 201, 7.1, np.nan, np.nan],
        ["Fiat", "Panda", "1.0 Hybrid", "Citycar", 70, 13.9, 164, 14.5, np.nan, np.nan],
    ]
    cols_spec = ["Marca", "Modello", "Versione", "Categoria", "Potenza_CV", "Zero_100_s", "Vel_Max_kmh", "Ripresa_80_120_s", "Carwow_1_4_miglio_s", "Nurburgring_s"]
    df_spec = pd.DataFrame(data_speciali, columns=cols_spec)

    # Download automatico di un catalogo mondiale con oltre 1.000+ modelli
    url_esteso = "https://raw.githubusercontent.com/fedesoriano/car-features-dataset/main/turkey_car_market.csv"
    try:
        df_ext = pd.read_csv(url_esteso)
        df_ext_clean = pd.DataFrame()
        df_ext_clean["Marca"] = df_ext["Brand"]
        df_ext_clean["Modello"] = df_ext["Model"]
        df_ext_clean["Versione"] = df_ext["Version"].fillna("")
        df_ext_clean["Categoria"] = df_ext["Body_Type"].fillna("Auto")
        df_ext_clean["Potenza_CV"] = pd.to_numeric(df_ext["Hp"], errors='coerce').fillna(100)
        
        # Stima dinamica delle prestazioni (0-100, Vel Max, Ripresa) basata sui CV dove mancano i dati ufficiali
        df_ext_clean["Zero_100_s"] = np.round(np.clip(14.0 - (df_ext_clean["Potenza_CV"] / 35.0), 2.5, 16.0), 1)
        df_ext_clean["Vel_Max_kmh"] = np.round(140 + (df_ext_clean["Potenza_CV"] * 0.22), 0)
        df_ext_clean["Ripresa_80_120_s"] = np.round(df_ext_clean["Zero_100_s"] * 0.8, 1)
        df_ext_clean["Carwow_1_4_miglio_s"] = np.nan
        df_ext_clean["Nurburgring_s"] = np.nan

        df_totale = pd.concat([df_spec, df_ext_clean], ignore_index=True)
    except:
        df_totale = df_spec

    df_totale["Auto_Completa"] = df_totale["Marca"] + " " + df_totale["Modello"] + " " + df_totale["Versione"]
    return df_totale.drop_duplicates(subset=["Auto_Completa"]).reset_index(drop=True)

df = load_data()

# Selezione degli Sfidanti
st.subheader("⚔️ Scegli i due sfidanti")
lista_auto = sorted(df["Auto_Completa"].unique())

col1, col2 = st.columns(2)
with col1:
    auto_1_nome = st.selectbox("🔴 Prima Auto", lista_auto, index=0)
with col2:
    idx_default = 1 if len(lista_auto) > 1 else 0
    auto_2_nome = st.selectbox("🔵 Seconda Auto", lista_auto, index=idx_default)

auto_1 = df[df["Auto_Completa"] == auto_1_nome].iloc[0]
auto_2 = df[df["Auto_Completa"] == auto_2_nome].iloc[0]

# Logica del Punteggio
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
    txt1 = f"{v1:.1f}" if pd.notnull(v1) else "N/D"
    txt2 = f"{v2:.1f}" if pd.notnull(v2) else "N/D"
    vincitore = "Pareggio 🤝"
    
    if pd.notnull(v1) and pd.notnull(v2):
        if (tipo == "max" and v1 > v2) or (tipo == "min" and v1 < v2):
            punti_1 += 1
            vincitore = f"🏆 {auto_1['Marca']}"
        elif (tipo == "max" and v2 > v1) or (tipo == "min" and v2 < v1):
            punti_2 += 1
            vincitore = f"🏆 {auto_2['Marca']}"

    dettagli.append({"Parametro": nome, auto_1_nome: txt1, auto_2_nome: txt2, "Esito": vincitore})

# Risultato Finale
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
