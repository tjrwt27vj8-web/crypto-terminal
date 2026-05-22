import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# 1. INITIALISATION DE LA PAGE
st.set_page_config(page_title="Terminal Crypto Global Pro", layout="wide")
st.title("🛡️ Terminal Crypto Professionnel - Vision Globale & Confluence")

# --- REPERTOIRE FONDAMENTAL AVEC ANCRES D'ACTUALITÉS INVIOLABLES ---
repo_fondamental = {
    "Bitcoin (BTC)": {
        "tokenomics": "**Offre bloquée à 21M**. Actif déflationniste par nature. Plus de 94% des jetons sont déjà en circulation.",
        "roadmap": "Halving prévu en 2028 (réduction de l'émission à 1.56 BTC/bloc). Développement des protocoles de scalabilité (Lightning Network).",
        "sensibilite": "Or numérique. Très sensible aux politiques de taux d'intérêt de la Fed et à la liquidité mondiale.",
        "ticker_news": "BTC",
        "lien_x": "https://x.com/Bitcoin",
        "fallback_news": [
            {
                "title": "Flux Institutionnels : Suivi des flux nets sur les ETF Bitcoin Spot", 
                "body": "Consultez les volumes d'achat quotidiens, les entrées/sorties de capitaux des fonds de gestion et les positions des institutionnels.",
                "url": "https://coinmarketcap.com/currencies/bitcoin/#News"
            },
            {
                "title": "Analyse de Cycle : Métriques de marché et actualités du BTC", 
                "body": "Accédez au flux d'actualités continues compilé par CoinDesk pour analyser les mouvements des portefeuilles à long terme.",
                "url": "https://www.coindesk.com/price/bitcoin/"
            }
        ]
    },
    "Ethereum (ETH)": {
        "tokenomics": "Offre dynamique avec mécanisme de destruction ('burn') partiel des frais de réseau en fonction de l'activité.",
        "roadmap": "Phase 'The Surge' en cours (optimisation des Layer 2 pour atteindre plus de 100 000 transactions par seconde).",
        "sensibilite": "Actif de croissance technologique. Fortement lié à l'écosystème de la DeFi et des Smart Contracts.",
        "ticker_news": "ETH",
        "lien_x": "https://x.com/ethereum",
        "fallback_news": [
            {
                "title": "Scalabilité technique : Activité et frais sur les réseaux Layer 2", 
                "body": "Suivez l'évolution technique des chaînes secondaires (Arbitrum, Optimism, Base) et l'adoption des solutions de mise à l'échelle.",
                "url": "https://coinmarketcap.com/currencies/ethereum/#News"
            },
            {
                "title": "Finance Décentralisée : Volumes totaux verrouillés (TVL) et Staking", 
                "body": "Consultez les flux d'informations sur les smart contracts, la gouvernance et le rendement du staking institutionnel.",
                "url": "https://www.coindesk.com/price/ethereum/"
            }
        ]
    },
    "Solana (SOL)": {
        "tokenomics": "Inflation initiale décroissante stabilisée à 1.5% à long terme. 50% de chaque frais de transaction est détruit.",
        "roadmap": "Déploiement final du client de validation indépendant 'Firedancer' pour éliminer définitivement les pannes.",
        "sensibilite": "Actif à haut bêta (très volatil). Fortement dépendant de l'engouement du grand public et des volumes spéculatifs.",
        "ticker_news": "SOL",
        "lien_x": "https://x.com/solana",
        "fallback_news": [
            {
                "title": "Infrastructure Firedancer : Rapport de mise à niveau des validateurs", 
                "body": "Suivez le taux de déploiement du second validateur développé par Jump Crypto conçu pour maximiser le débit du réseau.",
                "url": "https://coinmarketcap.com/currencies/solana/#News"
            },
            {
                "title": "Activité Spéculative : Volumes d'échanges sur les DEX de Solana", 
                "body": "Suivez la création de liquidité brute et les volumes générés par les utilisateurs au jour le jour sur l'écosystème.",
                "url": "https://www.coindesk.com/price/solana/"
            }
        ]
    }
}

# --- FONCTIONS DE MISE EN CACHE PROTECTRICES ---
@st.cache_data(ttl=60)
def charger_donnees_prix(symbole):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbole}&interval=1d&limit=200"
    reponse = requests.get(url).json()
    colonnes = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_volume', 'Trades', 'Bids', 'Asks', 'Ignore']
    df = pd.DataFrame(reponse, columns=colonnes)
    df['Date'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[col] = pd.to_numeric(df[col])
    return df

@st.cache_data(ttl=600)
def charger_actualites(ticker):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        url_news = f"https://min-api.cryptocompare.com/data/v2/news/?categories={ticker}&lang=EN"
        reponse = requests.get(url_news, headers=headers, timeout=5) 
        if reponse.status_code == 200:
            res = reponse.json()
            return res.get('Data', [])[:4]
    except:
        pass
    return []

# --- SÉLECTION DE L'ACTIF ---
options_cryptos = {"Bitcoin (BTC)": "BTCUSDT", "Ethereum (ETH)": "ETHUSDT", "Solana (SOL)": "SOLUSDT"}
choix = st.selectbox("Sélectionne un actif à analyser :", list(options_cryptos.keys()))
symbole_api = options_cryptos[choix]
fiche = repo_fondamental[choix]

# --- PARAMÉTRAGE DES FLUX ---
df = charger_donnees_prix(symbole_api)

try:
    fng_res = requests.get("https://api.alternative.me/fng/?limit=1").json()
    fng_valeur = int(fng_res['data'][0]['value'])
    fng_statut = fng_res['data'][0]['value_classification']
except:
    fng_valeur, fng_statut = 50, "Neutre"

# --- ENGINE MATHÉMATIQUE (LES 4 PILIERS) ---
df['Moyenne_50'] = df['Close'].rolling(window=50).mean()
df['MA20'] = df['Close'].rolling(window=20).mean()
df['STD20'] = df['Close'].rolling(window=20).std()
df['Bollinger_Basse'] = df['MA20'] - (2 * df['STD20'])
df['Bollinger_Haute'] = df['MA20'] + (2 * df['STD20'])

delta = df['Close'].diff()
gain = delta.where(delta > 0, 0).rolling(window=14).mean()
perte = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
df['RSI'] = 100 - (100 / (1 + (gain / perte)))
df['Volume_Moyen'] = df['Volume'].rolling(window=20).mean()

infos = df.iloc[-1]
prix, rsi, b_basse, b_haute, ma50, volume_jour, volume_moyen = infos['Close'], infos['RSI'], infos['Bollinger_Basse'], infos['Bollinger_Haute'], infos['Moyenne_50'], infos['Volume'], infos['Volume_Moyen']

# Price Action
df['Is_Min'] = df['Low'] == df['Low'].rolling(window=15, center=True).min()
df['Is_Max'] = df['High'] == df['High'].rolling(window=15, center=True).max()
liste_supports = df[df['Is_Min']]['Low'].tail(3).tolist()
liste_resistances = df[df['Is_Max']]['High'].tail(3).tolist()

# --- BARRE LATÉRALE ---
st.sidebar.header("🧮 Gestion du Risque")
capital = st.sidebar.number_input("Capital total ($)", value=10000, step=500)
risque_pct = st.sidebar.slider("Risque par trade (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
stop_loss_suggere = liste_supports[-1] if liste_supports else prix * 0.95
stop_loss = st.sidebar.number_input("Prix du Stop Loss ($)", value=float(stop_loss_suggere))

st.sidebar.markdown("---")
st.sidebar.header("🏛️ Analyse Fondamentale")
statut_roadmap = st.sidebar.selectbox("Feuille de Route :", ["Neutre (Aucun impact)", "Favorable (+0.5 pt)", "Défavorable (-1.5 pt)"])
statut_politique = st.sidebar.selectbox("Contexte Légal/Politique :", ["Neutre (Aucun impact)", "Favorable (+0.5 pt)", "Défavorable (-1.5 pt)"])

st.sidebar.markdown("---")
st.sidebar.header("📱 Réseaux Sociaux")
st.sidebar.link_button(f"Consulter le flux X de {choix.split()[0]} ↗", fiche["lien_x"])

risque_dollars = capital * (risque_pct / 100)
distance_sl = ((prix - stop_loss) / prix) * 100
taille_position_dollars = risque_dollars / (distance_sl / 100) if distance_sl > 0 else 0
unites_a_acheter = taille_position_dollars / prix if prix > 0 else 0

st.sidebar.markdown("---")
st.sidebar.write(f"Perte max autorisée : **{risque_dollars:.2f} $**")
if distance_sl > 0:
    st.sidebar.info(f"👉 **Position recommandée :**\n\nAcheter pour : **{taille_position_dollars:,.2f} $**\n({unites_a_acheter:.4f} {choix.split()[0]})")

# --- CALCUL DU SCORE ---
cond_tendance = prix < ma50
cond_bollinger = prix <= b_basse
cond_rsi = rsi < 38
cond_volume = volume_jour > (1.5 * volume_moyen)
cond_macro_fng = fng_valeur < 30

score_technique = sum([cond_tendance, cond_bollinger, cond_rsi, cond_volume, cond_macro_fng])
score_final = float(score_technique)
if "Favorable" in statut_roadmap: score_final += 0.5
elif "Défavorable" in statut_roadmap: score_final -= 1.5
if "Favorable" in statut_politique: score_final += 0.5
elif "Défavorable" in statut_politique: score_final -= 1.5
score_final = max(0.0, min(5.0, score_final))

# --- RENDU DE L'INTERFACE VISUELLE ---
st.markdown(f"# 💰 {choix.split()[0]} : **{prix:,.2f} USD**")

c1, c2, c3, c4 = st.columns(4)
c1.metric(label="Prix Clôture 24h", value=f"{prix:,.2f} $")
c2.metric(label="RSI (Momentum)", value=f"{rsi:.1f}")
c3.metric(label="Objectif Bande Basse", value=f"{b_basse:,.2f} $")
c4.metric(label="Ratio Volume (Actuel/Moyen)", value=f"{volume_jour/volume_moyen:.2f}x")

if score_final >= 4: st.success(f"🔥 CONFLUENCE GLOBALE ULTIME (Score: {score_final}/5) : Zone d'achat institutionnelle majeure.")
elif score_final >= 2.5: st.warning(f"⚠️ SIGNAL MODÉRÉ (Score: {score_final}/5) : Configuration technique intéressante. Accumulation fractionnée possible.")
else: st.error(f"❌ SIGNAL NEUTRE OU DANGEREUX (Score: {score_final}/5) : Risque élevé ou absence de panique. Rester à l'écart.")

# --- LEXIQUE ---
with st.expander("📖 Guide de lecture et Lexique Technique"):
    st.markdown("""
    * **Ligne Cyan (MM50) :** Moyenne Mobile 50j (Tendance).
    * **Pointillés Verts (Bollinger Haute) :** Zone d'euphorie.
    * **Pointillés Rouges (Bollinger Basse) :** Zone de sous-évaluation statistique.
    """)

# --- GRAPHICS PLOTLY RE-VÉRIFIÉ ---
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Prix", hoverinfo="none"))

# MM50 avec explication réintégrée
fig.add_trace(go.Scatter(
    x=df['Date'], y=df['Moyenne_50'], line=dict(color='cyan', width=2), name="MM50",
    hovertemplate="<b>Tendance (MM50)</b><br>Prix moyen 50j : %{y:,.2f} $<br>➔ Filtre : Idéal d'acheter sous cette ligne.<extra></extra>"
))

# Bollinger Basse avec explication réintégrée
fig.add_trace(go.Scatter(
    x=df['Date'], y=df['Bollinger_Basse'], line=dict(color='rgba(231, 76, 60, 0.8)', dash='dash', width=1.5), name="Bande Basse",
    hovertemplate="<b>Volatilité (Bande Basse)</b><br>Seuil : %{y:,.2f} $<br>➔ Statut : Si le prix est ici, la baisse est statistiquement excessive.<extra></extra>"
))

# Bollinger Haute avec explication réintégrée
fig.add_trace(go.Scatter(
    x=df['Date'], y=df['Bollinger_Haute'], line=dict(color='rgba(46, 204, 113, 0.8)', dash='dash', width=1.5), name="Bande Haute",
    hovertemplate="<b>Volatilité (Bande Haute)</b><br>Seuil : %{y:,.2f} $<br>➔ Statut : Zone de surchauffe haussière. Éviter d'acheter ici.<extra></extra>"
))

if liste_supports:
    for i, sup in enumerate(liste_supports): fig.add_hline(y=sup, line_dash="dot", line_color="rgba(46, 204, 113, 0.4)", annotation_text=f"Support {i+1}")
if liste_resistances:
    for i, res in enumerate(liste_resistances): fig.add_hline(y=res, line_dash="dot", line_color="rgba(231, 76, 60, 0.4)", annotation_text=f"Resistance {i+1}")

fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=500, margin=dict(l=10, r=10, t=10, b=10), hovermode="x")
st.plotly_chart(fig, use_container_width=True)

# --- BLOC FONDAMENTAL ---
st.divider()
st.header("🌐 Analyse Fondamentale & Contexte Global")
col_m1, col_m2 = st.columns([1, 2])
col_m1.metric(label="Fear & Greed Index", value=f"{fng_valeur}/100", delta=fng_statut, delta_color="inverse")
col_m2.write("**Règle macro automatique :** Sentiment global intégré.")

f_col1, f_col2, f_col3 = st.columns(3)
f_col1.markdown(f"### 📊 Tokenomics & Offre\n{fiche['tokenomics']}")
f_col2.markdown(f"### 🗺️ Catalyseurs & Roadmap\n{fiche['roadmap']}")
f_col3.markdown(f"### 📈 Profil de Sensibilité\n{fiche['sensibilite']}")

# --- BLOC ACTUALITÉS ULTRA-STABLES ---
st.divider()
st.header(f"📰 Dernières Actualités Fondamentales : {choix.split()[0]}")

articles = charger_actualites(fiche['ticker_news'])

if not articles:
    articles = fiche["fallback_news"]
    st.caption("🔄 *Flux de secours actif : Redirection vers les plateformes d'analyse de fond en continu.*")

n_cols = st.columns(len(articles))
for idx, art in enumerate(articles):
    with n_cols[idx]:
        if art.get('imageurl'):
            st.image(art['imageurl'], use_container_width=True)
        st.markdown(f"#### {art['title']}")
        st.write(art['body'])
        if art.get('url'):
            st.link_button("Ouvrir le flux live ↗", art['url'])