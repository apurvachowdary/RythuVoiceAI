
import streamlit as st
import requests
from datetime import datetime
from gnani.tts import GnaniTTSClient


# -------------------- PAGE CONFIGURATION --------------------

st.set_page_config(
    page_title="RythuVoiceAI | రైతు వాయిస్ AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------- GNANI CLIENTS --------------------

@st.cache_resource
def get_gnani_clients():
    api_key = st.secrets["GNANI_API_KEY"]
    tts_client = GnaniTTSClient(api_key=api_key)
    return tts_client


# -------------------- GNANI PRISMA V3 SPEECH TO TEXT --------------------

def transcribe_with_prisma_v3(
    audio_bytes,
    filename,
    language_code,
    mime_type="audio/wav"
):
    api_key = st.secrets["GNANI_API_KEY"]

    response = requests.post(
        "https://api.vachana.ai/stt/v3",
        headers={
            "X-API-Key-ID": api_key
        },
        files={
            "audio_file": (
                filename,
                audio_bytes,
                mime_type
            )
        },
        data={
            "model": "prisma-v3.0",
            "language_code": language_code
        },
        timeout=60
    )

    if response.status_code == 504:
        raise RuntimeError(
            "Gnani Prisma timed out. Please try again with a shorter recording."
        )

    if not response.ok:
        try:
            error_details = response.json()
        except ValueError:
            error_details = response.text

        raise RuntimeError(
            f"Gnani STT error {response.status_code}: {error_details}"
        )

    result = response.json()

    if not result.get("success"):
        raise RuntimeError(
            str(result.get("error", "Speech recognition failed"))
        )

    return (
        result.get("transcript")
        or result.get("text")
        or ""
    )


# -------------------- LANGUAGE + DISTRICT DATA --------------------

DISTRICTS = {
    "Alluri Sitarama Raju": "అల్లూరి సీతారామ రాజు",
    "Anakapalli": "అనకాపల్లి",
    "Anantapur": "అనంతపురం",
    "Annamayya": "అన్నమయ్య",
    "Bapatla": "బాపట్ల",
    "Chittoor": "చిత్తూరు",
    "Dr. B.R. Ambedkar Konaseema": "డా. బి.ఆర్. అంబేద్కర్ కోనసీమ",
    "East Godavari": "తూర్పు గోదావరి",
    "Eluru": "ఏలూరు",
    "Guntur": "గుంటూరు",
    "Kakinada": "కాకినాడ",
    "Krishna": "కృష్ణా",
    "Kurnool": "కర్నూలు",
    "Nandyal": "నంద్యాల",
    "NTR": "ఎన్‌టీఆర్",
    "Palnadu": "పల్నాడు",
    "Prakasam": "ప్రకాశం",
    "SPSR Nellore": "ఎస్‌పీఎస్‌ఆర్ నెల్లూరు",
    "Sri Sathya Sai": "శ్రీ సత్యసాయి",
    "Srikakulam": "శ్రీకాకుళం",
    "Tirupati": "తిరుపతి",
    "Visakhapatnam": "విశాఖపట్నం",
    "Vizianagaram": "విజయనగరం",
    "West Godavari": "పశ్చిమ గోదావరి",
    "YSR Kadapa": "వైఎస్ఆర్ కడప",
}


# -------------------- CROP INFORMATION --------------------

CROPS = {
    "Rice": {
        "te": "వరి",
        "season": ("Kharif and Rabi", "ఖరీఫ్ మరియు రబీ"),
        "soil": (
            "Clayey or clay-loam soil with good water retention.",
            "నీటిని నిల్వ ఉంచే బంకమట్టి లేదా బంకమట్టి-లోమ్ నేల అనుకూలం."
        ),
        "water": (
            "Keep adequate water during important growth stages; avoid unnecessary flooding.",
            "ముఖ్యమైన పెరుగుదల దశల్లో తగినంత నీరు ఇవ్వండి; అవసరం లేకుండా పొలంలో నీరు నిల్వ చేయవద్దు."
        ),
        "fertilizer": (
            "Use soil-test recommendations. Apply nutrients in split doses as advised by the local agriculture officer.",
            "నేల పరీక్ష ఆధారంగా ఎరువులు వాడండి. స్థానిక వ్యవసాయ అధికారుల సూచన మేరకు విడతలుగా వేయండి."
        ),
        "pests": (
            "Watch for stem borer, leaf folder and planthoppers.",
            "కాండం తొలిచే పురుగు, ఆకుముడత పురుగు, దాటే పురుగులను గమనించండి."
        ),
        "tips": (
            "Use certified seed, maintain field drainage and inspect the crop weekly.",
            "ధృవీకరించిన విత్తనాలు వాడండి, పొలంలో నీటి పారుదల సరిగా ఉంచండి, వారానికి ఒకసారి పంటను పరిశీలించండి."
        ),
    },

    "Cotton": {
        "te": "పత్తి",
        "season": ("Mainly Kharif", "ప్రధానంగా ఖరీఫ్"),
        "soil": (
            "Well-drained black or red loamy soil.",
            "నీరు నిల్వ ఉండని నల్లరేగడి లేదా ఎర్ర లోమ్ నేల."
        ),
        "water": (
            "Avoid waterlogging; irrigate based on soil moisture and crop stage.",
            "నీరు నిల్వ ఉండకుండా చూడండి; నేల తేమ, పంట దశ ఆధారంగా నీరు పెట్టండి."
        ),
        "fertilizer": (
            "Base fertilizer quantity on soil testing and local recommendations.",
            "నేల పరీక్ష మరియు స్థానిక సిఫార్సుల ఆధారంగా ఎరువుల మోతాదు నిర్ణయించండి."
        ),
        "pests": (
            "Monitor for bollworms, whitefly and sucking pests.",
            "కాయ తొలిచే పురుగులు, తెల్లదోమ, రసం పీల్చే పురుగులను గమనించండి."
        ),
        "tips": (
            "Use recommended spacing and scout the field regularly before choosing pest control.",
            "సిఫార్సు చేసిన మొక్కల దూరం పాటించండి; పురుగు మందు ఎంచుకునే ముందు పొలాన్ని తరచూ పరిశీలించండి."
        ),
    },

    "Chilli": {
        "te": "మిరప",
        "season": (
            "Kharif and Rabi, depending on region",
            "ప్రాంతాన్ని బట్టి ఖరీఫ్ మరియు రబీ"
        ),
        "soil": (
            "Well-drained fertile loam soil.",
            "సారవంతమైన, నీరు నిల్వ ఉండని లోమ్ నేల."
        ),
        "water": (
            "Provide uniform moisture; avoid both drought stress and waterlogging.",
            "సమానమైన తేమ ఉండేలా చూడండి; ఎండబారడం, నీరు నిల్వ ఉండడం రెండింటినీ నివారించండి."
        ),
        "fertilizer": (
            "Follow soil-test-based nutrient recommendations.",
            "నేల పరీక్ష ఆధారంగా పోషకాలు అందించండి."
        ),
        "pests": (
            "Check for thrips, mites, aphids and fruit borers.",
            "తామర పురుగులు, నల్లులు, పేనుబంక, కాయ తొలిచే పురుగులను గమనించండి."
        ),
        "tips": (
            "Use healthy seedlings and remove severely affected plant parts safely.",
            "ఆరోగ్యమైన నారును నాటండి; తీవ్రంగా దెబ్బతిన్న మొక్క భాగాలను సురక్షితంగా తొలగించండి."
        ),
    },

    "Tomato": {
        "te": "టమాటా",
        "season": (
            "Can be grown in suitable seasons with local guidance",
            "స్థానిక సూచనలతో అనుకూలమైన సీజన్లలో సాగు చేయవచ్చు"
        ),
        "soil": (
            "Well-drained sandy loam to clay loam soil.",
            "నీరు నిల్వ ఉండని ఇసుక-లోమ్ నుంచి బంక-లోమ్ నేల."
        ),
        "water": (
            "Maintain even soil moisture; avoid wetting foliage where possible.",
            "నేలలో తేమ సమంగా ఉంచండి; సాధ్యమైనంతవరకు ఆకులు తడవకుండా నీరు పెట్టండి."
        ),
        "fertilizer": (
            "Use soil-test results and split nutrient applications as advised.",
            "నేల పరీక్ష ఫలితాల ఆధారంగా, సూచించిన విధంగా విడతలుగా ఎరువులు వేయండి."
        ),
        "pests": (
            "Monitor for fruit borer, whitefly and leaf miner.",
            "కాయ తొలిచే పురుగు, తెల్లదోమ, ఆకుతొలిచే పురుగులను గమనించండి."
        ),
        "tips": (
            "Stake plants if needed, rotate crops and remove diseased debris.",
            "అవసరమైతే మొక్కలకు కర్రల ఆధారం ఇవ్వండి; పంట మార్పిడి చేయండి; వ్యాధిగ్రస్త అవశేషాలను తొలగించండి."
        ),
    },

    "Maize": {
        "te": "మొక్కజొన్న",
        "season": (
            "Kharif and Rabi, depending on irrigation",
            "నీటి సదుపాయాన్ని బట్టి ఖరీఫ్ మరియు రబీ"
        ),
        "soil": (
            "Well-drained loamy soil.",
            "నీరు నిల్వ ఉండని లోమ్ నేల."
        ),
        "water": (
            "Pay special attention to irrigation around flowering and grain filling.",
            "పూత దశ, గింజ నిండే దశల్లో నీటిపై ప్రత్యేక శ్రద్ధ పెట్టండి."
        ),
        "fertilizer": (
            "Apply nutrients according to soil test and local package of practices.",
            "నేల పరీక్ష మరియు స్థానిక సాగు పద్ధతుల ప్రకారం ఎరువులు వేయండి."
        ),
        "pests": (
            "Scout for fall armyworm and stem borer.",
            "కత్తెర పురుగు, కాండం తొలిచే పురుగులను గమనించండి."
        ),
        "tips": (
            "Use quality seed, timely sowing and field monitoring.",
            "నాణ్యమైన విత్తనాలు వాడండి, సరైన సమయంలో విత్తండి, పొలాన్ని క్రమం తప్పకుండా పరిశీలించండి."
        ),
    },

    "Groundnut": {
        "te": "వేరుశనగ",
        "season": (
            "Kharif and Rabi/summer where suitable",
            "అనుకూల ప్రాంతాల్లో ఖరీఫ్ మరియు రబీ/వేసవి"
        ),
        "soil": (
            "Loose, well-drained sandy loam soil.",
            "గుల్లగా ఉండే, నీరు నిల్వ ఉండని ఇసుక-లోమ్ నేల."
        ),
        "water": (
            "Avoid waterlogging; moisture is important during pegging and pod development.",
            "నీరు నిల్వ ఉండకుండా చూడండి; ఊడలు దిగే, కాయలు అభివృద్ధి చెందే దశల్లో తేమ అవసరం."
        ),
        "fertilizer": (
            "Follow soil-test-based recommendations, including calcium where locally advised.",
            "నేల పరీక్ష ఆధారంగా, స్థానికంగా సూచిస్తే కాల్షియంతో సహా ఎరువులు వాడండి."
        ),
        "pests": (
            "Monitor leaf miner, tobacco caterpillar and soil pests.",
            "ఆకు తొలిచే పురుగు, పొగాకు లద్దె పురుగు, నేల పురుగులను గమనించండి."
        ),
        "tips": (
            "Use treated quality seed and harvest at suitable maturity.",
            "శుద్ధి చేసిన నాణ్యమైన విత్తనాలు వాడండి; సరైన పరిపక్వతకు కోత కోయండి."
        ),
    },

    "Sugarcane": {
        "te": "చెరకు",
        "season": (
            "Planting season varies by region",
            "నాటే కాలం ప్రాంతాన్ని బట్టి మారుతుంది"
        ),
        "soil": (
            "Deep, fertile and well-drained soil.",
            "లోతైన, సారవంతమైన, నీరు నిల్వ ఉండని నేల."
        ),
        "water": (
            "Irrigate according to soil moisture and weather; ensure drainage.",
            "నేల తేమ, వాతావరణాన్ని బట్టి నీరు పెట్టండి; నీటి పారుదల ఉండాలి."
        ),
        "fertilizer": (
            "Use soil testing and recommendations from the local sugarcane/agriculture office.",
            "నేల పరీక్ష చేసి స్థానిక చెరకు/వ్యవసాయ అధికారుల సిఫార్సులు పాటించండి."
        ),
        "pests": (
            "Watch for early shoot borer, internode borer and scale insects.",
            "మొలక దశ కాండం తొలిచే పురుగు, కణుపుల తొలిచే పురుగు, పొలుసు పురుగులను గమనించండి."
        ),
        "tips": (
            "Use healthy setts, proper spacing and timely earthing up.",
            "ఆరోగ్యమైన చెరకు ముచ్చెలు వాడండి; సరైన దూరం పాటించి, సరైన సమయంలో మట్టి ఎత్తండి."
        ),
    },
}


# -------------------- LANGUAGE TEXT --------------------

TEXT = {
    "English": {
        "tagline": "Smart farming guidance in your language",
        "dashboard": "Dashboard",
        "crop": "Crop Information",
        "assistant": "Farmer Help Desk",
        "disease": "Leaf Image Check",
        "weather": "Weather Planner",
        "market": "Market Information",
        "about": "About Project",
        "district": "Select your district",
        "welcome": "Welcome to RythuVoiceAI",
        "welcome_sub": "A simple digital farming guide designed for farmers in Andhra Pradesh.",
        "services": "Available modules",
        "crop_title": "Crop Information Guide",
        "choose_crop": "Choose a crop",
        "season": "Growing season",
        "soil": "Suitable soil",
        "water": "Water management",
        "fertilizer": "Fertilizer guidance",
        "pests": "Pests to monitor",
        "tips": "Good farming practices",
        "ask": "Ask a farming question",
        "ask_hint": "Example: How can I manage pests in tomato?",
        "get_answer": "Get guidance",
        "answer": "Suggested guidance",
        "image_title": "Upload a crop or leaf image",
        "upload": "Choose an image",
        "image_note": "This prototype previews your image only. It does not diagnose a disease.",
        "weather_note": "Live weather data is not connected in this prototype. Check the IMD forecast or local agriculture office before irrigation or spraying.",
        "market_note": "Live mandi prices are not connected yet. Verify today's price with the official e-NAM portal or your local market committee.",
        "about_text": "RythuVoiceAI is a bilingual prototype intended to make basic crop information easier to access for Andhra Pradesh farmers.",
        "prototype": "Prototype status",
        "working": "Working: bilingual interface, AP district selection, crop guide, offline FAQ and image preview.",
        "planned": "Not connected yet: trained disease-recognition model, live weather API and live market-price feed.",
        "select_district": "Selected district",
        "faq_none": "Please enter a question first.",
        "faq_unknown": "I do not have a verified answer for that question in this offline demo. Please contact your local Agriculture Officer or KVK before applying any pesticide or fertilizer.",
        "disclaimer": "General guidance only. Follow soil-test results and advice from your local Agriculture Officer/KVK for field-specific decisions.",
    },

    "తెలుగు": {
        "tagline": "మీ భాషలో స్మార్ట్ వ్యవసాయ సమాచారం",
        "dashboard": "డ్యాష్‌బోర్డ్",
        "crop": "పంట సమాచారం",
        "assistant": "రైతు సహాయ కేంద్రం",
        "disease": "ఆకు చిత్ర పరిశీలన",
        "weather": "వాతావరణ ప్రణాళిక",
        "market": "మార్కెట్ సమాచారం",
        "about": "ప్రాజెక్ట్ గురించి",
        "district": "మీ జిల్లాను ఎంచుకోండి",
        "welcome": "రైతు వాయిస్ AI కి స్వాగతం",
        "welcome_sub": "ఆంధ్రప్రదేశ్ రైతుల కోసం రూపొందించిన సులభమైన డిజిటల్ వ్యవసాయ మార్గదర్శి.",
        "services": "అందుబాటులో ఉన్న విభాగాలు",
        "crop_title": "పంటల సమాచారం",
        "choose_crop": "పంటను ఎంచుకోండి",
        "season": "సాగు కాలం",
        "soil": "అనుకూలమైన నేల",
        "water": "నీటి యాజమాన్యం",
        "fertilizer": "ఎరువుల సూచనలు",
        "pests": "గమనించాల్సిన పురుగులు",
        "tips": "మంచి సాగు పద్ధతులు",
        "ask": "వ్యవసాయ ప్రశ్న అడగండి",
        "ask_hint": "ఉదాహరణ: టమాటాలో పురుగులను ఎలా నియంత్రించాలి?",
        "get_answer": "సూచనలు పొందండి",
        "answer": "సూచించిన సమాచారం",
        "image_title": "పంట లేదా ఆకు చిత్రాన్ని అప్‌లోడ్ చేయండి",
        "upload": "చిత్రాన్ని ఎంచుకోండి",
        "image_note": "ఈ నమూనా మీ చిత్రాన్ని మాత్రమే చూపిస్తుంది. ఇది వ్యాధిని నిర్ధారించదు.",
        "weather_note": "ఈ నమూనాలో ప్రత్యక్ష వాతావరణ సమాచారం అనుసంధానం కాలేదు. నీరు పెట్టడం లేదా మందు పిచికారీకి ముందు IMD సూచనలు లేదా స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి.",
        "market_note": "ప్రత్యక్ష మార్కెట్ ధరలు ఇంకా అనుసంధానం కాలేదు. నేటి ధరను అధికారిక e-NAM లేదా స్థానిక మార్కెట్ కమిటీ వద్ద నిర్ధారించుకోండి.",
        "about_text": "రైతు వాయిస్ AI అనేది ఆంధ్రప్రదేశ్ రైతులకు ప్రాథమిక పంట సమాచారాన్ని సులభంగా అందించడానికి రూపొందించిన ద్విభాషా నమూనా ప్రాజెక్ట్.",
        "prototype": "ప్రాజెక్ట్ ప్రస్తుత స్థితి",
        "working": "పనిచేస్తున్నవి: తెలుగు/ఇంగ్లీష్ ఇంటర్‌ఫేస్, ఏపీ జిల్లా ఎంపిక, పంటల సమాచారం, ఆఫ్‌లైన్ ప్రశ్నోత్తరాలు, చిత్ర ప్రివ్యూ.",
        "planned": "ఇంకా అనుసంధానం కానివి: శిక్షణ పొందిన వ్యాధి గుర్తింపు మోడల్, ప్రత్యక్ష వాతావరణ API, మార్కెట్ ధరలు.",
        "select_district": "ఎంచుకున్న జిల్లా",
        "faq_none": "ముందుగా మీ ప్రశ్నను నమోదు చేయండి.",
        "faq_unknown": "ఈ ఆఫ్‌లైన్ నమూనాలో ఈ ప్రశ్నకు ధృవీకరించిన సమాధానం లేదు. పురుగు మందు లేదా ఎరువు వాడే ముందు స్థానిక వ్యవసాయ అధికారి లేదా కృషి విజ్ఞాన కేంద్రాన్ని సంప్రదించండి.",
        "disclaimer": "ఇవి సాధారణ సూచనలు మాత్రమే. మీ పొలానికి సంబంధించిన నిర్ణయాల కోసం నేల పరీక్ష ఫలితాలు మరియు స్థానిక వ్యవసాయ అధికారి/KVK సూచనలు పాటించండి.",
    },
}


def tr(key):
    return TEXT[language].get(key, key)


# -------------------- SIDEBAR --------------------

st.sidebar.markdown("## 🌱 RythuVoiceAI")
st.sidebar.caption("రైతు వాయిస్ AI")

language = st.sidebar.selectbox(
    "Language / భాష",
    ["English", "తెలుగు"],
    index=0,
)

district_names = list(DISTRICTS.keys())

district = st.sidebar.selectbox(
    tr("district"),
    district_names,
    format_func=lambda x: (
        f"{x} — {DISTRICTS[x]}"
        if language == "తెలుగు"
        else x
    ),
)

st.sidebar.markdown("---")

pages = [
    tr("dashboard"),
    tr("crop"),
    tr("assistant"),
    tr("disease"),
    tr("weather"),
    tr("market"),
    tr("about"),
]

page = st.sidebar.radio("Navigation / మెనూ", pages)

st.sidebar.caption(
    f"{tr('select_district')}: "
    f"{DISTRICTS[district] if language == 'తెలుగు' else district}"
)


# -------------------- HEADER + DESIGN --------------------

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f4fbf4 0%, #ffffff 42%);
    }

    section[data-testid="stSidebar"] {
        background: #eaf5e9;
    }

    .hero {
        padding: 1.25rem 1.5rem;
        border-radius: 18px;
        background: linear-gradient(110deg,#14532d,#27834a);
        color: white;
        margin-bottom: 1rem;
    }

    .hero h1 {
        color: white;
        margin: 0;
    }

    .hero p {
        color: #e8f5e9;
        margin: .35rem 0 0 0;
    }

    .small-note {
        color: #64748b;
        font-size: .9rem;
    }

    div[data-testid="stMetric"] {
        background: #f0f8f0;
        border: 1px solid #d7ead7;
        padding: 12px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="hero">
        <h1>🌱 {tr("welcome")}</h1>
        <p>{tr("welcome_sub")}</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# -------------------- DASHBOARD --------------------

if page == tr("dashboard"):

    st.subheader(tr("services"))

    cols = st.columns(3)

    cards = [
        ("🌾", tr("crop"), "Crop growing guidance / పంటల సాగు సమాచారం"),
        ("💬", tr("assistant"), "Basic offline answers / ప్రాథమిక సమాధానాలు"),
        ("🍃", tr("disease"), "Upload and preview / చిత్రాన్ని అప్‌లోడ్ చేయండి"),
        ("🌦️", tr("weather"), "Weather planning note / వాతావరణ సూచన"),
        ("📈", tr("market"), "Market information note / మార్కెట్ సమాచారం"),
        (
            "📍",
            tr("district"),
            DISTRICTS[district] if language == "తెలుగు" else district
        ),
    ]

    for i, (emoji, title, desc) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(f"### {emoji} {title}")
            st.caption(desc)

    st.info(
        f"{tr('select_district')}: "
        f"**{DISTRICTS[district] if language == 'తెలుగు' else district}**"
    )

    st.caption(tr("disclaimer"))


# -------------------- CROP GUIDE --------------------

elif page == tr("crop"):

    st.subheader(tr("crop_title"))

    crop = st.selectbox(
        tr("choose_crop"),
        list(CROPS.keys()),
        format_func=lambda x: (
            f"{x} — {CROPS[x]['te']}"
            if language == "తెలుగు"
            else x
        ),
    )

    data = CROPS[crop]

    st.markdown(
        f"## 🌱 {CROPS[crop]['te'] if language == 'తెలుగు' else crop}"
    )

    for key in [
        "season",
        "soil",
        "water",
        "fertilizer",
        "pests",
        "tips",
    ]:
        en, te = data[key]

        st.markdown(f"**{tr(key)}**")
        st.write(te if language == "తెలుగు" else en)

    st.caption(tr("disclaimer"))


# -------------------- FARMER HELP DESK --------------------

elif page == tr("assistant"):

    st.subheader(tr("assistant"))

    tts_client = get_gnani_clients()

    language_code = "te-IN" if language == "తెలుగు" else "en-IN"

    st.markdown("### 🎤 Voice Question / వాయిస్ ప్రశ్న")

    st.info(
        "English and Telugu voice recognition are available. "
        "Keep your recording under 30 seconds. / "
        "ఇంగ్లీష్ మరియు తెలుగు వాయిస్ గుర్తింపు అందుబాటులో ఉన్నాయి. "
        "30 సెకన్లలోపు రికార్డ్ చేయండి."
    )

    audio_input = st.audio_input(
        "Record your question / మీ ప్రశ్నను రికార్డ్ చేయండి"
    )

    if audio_input is not None:

        if st.button(
            "Convert Speech to Text / మాటలను టెక్స్ట్‌గా మార్చండి"
        ):

            try:

                with st.spinner("Recognizing your speech..."):

                    recognized_text = transcribe_with_prisma_v3(
                        audio_input.getvalue(),
                        getattr(audio_input, "name", "farmer_question.wav"),
                        language_code,
                        getattr(audio_input, "type", None) or "audio/wav"
                    )

                if recognized_text.strip():

                    st.session_state["voice_question"] = recognized_text
                    st.session_state["farmer_question_input"] = recognized_text

                    st.success("Speech recognized successfully!")

                    st.write("**Recognized Text / గుర్తించిన వచనం:**")
                    st.write(recognized_text)

                else:

                    st.warning(
                        "No speech was recognized. Please try again."
                    )

            except Exception as e:

                st.error(f"Speech recognition failed: {e}")

    # -------------------- QUESTION INPUT --------------------

    if "farmer_question_input" not in st.session_state:
        st.session_state["farmer_question_input"] = st.session_state.get(
            "voice_question", ""
        )

    question = st.text_area(
        tr("ask"),
        placeholder=tr("ask_hint"),
        height=110,
        key="farmer_question_input",
    )

    # -------------------- GET GUIDANCE --------------------

    if st.button(tr("get_answer"), type="primary"):

        q = question.lower().strip()

        if not q:

            st.warning(tr("faq_none"))

        else:

            if any(
                word in q
                for word in ["yellow", "పసుపు", "ఆకులు పసుపు"]
            ):

                en = (
                    "Yellow leaves can have several causes, including "
                    "nutrient deficiency, excess water, poor drainage or pests. "
                    "Check older and newer leaves, soil moisture and the roots. "
                    "A soil test and local field inspection are best before "
                    "applying fertilizer."
                )

                te = (
                    "ఆకులు పసుపు రంగులోకి మారడానికి పోషకాల లోపం, అధిక నీరు, "
                    "నీటి పారుదల లోపం లేదా పురుగులు కారణం కావచ్చు. "
                    "పాత/కొత్త ఆకులు, నేల తేమ, వేర్లను పరిశీలించండి. "
                    "ఎరువులు వేయడానికి ముందు నేల పరీక్ష చేయించి స్థానిక "
                    "నిపుణుడిని సంప్రదించండి."
                )

            elif any(
                word in q
                for word in [
                    "tomato",
                    "టమాట",
                    "మిరప",
                    "chilli",
                    "chili",
                ]
            ):

                en = (
                    "Inspect the underside of leaves and growing tips for "
                    "whiteflies, thrips and mites. Remove heavily affected "
                    "plant parts where practical, avoid excessive nitrogen, "
                    "and ask your local Agriculture Officer/KVK to identify "
                    "the pest before selecting a registered control."
                )

                te = (
                    "ఆకుల అడుగు భాగం, కొత్త చిగుళ్లపై తెల్లదోమ, తామర పురుగులు, "
                    "నల్లులు ఉన్నాయా చూడండి. తీవ్రంగా దెబ్బతిన్న భాగాలను "
                    "సాధ్యమైనంతవరకు తొలగించండి. అధిక నత్రజని ఎరువులు "
                    "నివారించండి. మందు ఎంచుకునే ముందు స్థానిక వ్యవసాయ "
                    "అధికారి/KVK ద్వారా పురుగును గుర్తించండి."
                )

            elif any(
                word in q
                for word in [
                    "water",
                    "irrigation",
                    "నీరు",
                    "నీటిపారుదల",
                ]
            ):

                en = (
                    "Irrigation depends on crop, soil type, crop stage and "
                    "recent rainfall. Check soil moisture before watering "
                    "and make sure excess water can drain away. Avoid a "
                    "fixed schedule for every field."
                )

                te = (
                    "నీటి అవసరం పంట, నేల రకం, పంట దశ, ఇటీవలి వర్షాలపై "
                    "ఆధారపడి ఉంటుంది. నీరు పెట్టే ముందు నేల తేమను "
                    "పరిశీలించండి; అదనపు నీరు బయటకు వెళ్లేలా చూడండి. "
                    "అన్ని పొలాలకు ఒకే సమయ పట్టికను అనుసరించవద్దు."
                )

            elif any(
                word in q
                for word in [
                    "fertilizer",
                    "manure",
                    "ఎరువు",
                    "ఎరువులు",
                ]
            ):

                en = (
                    "Do not choose fertilizer only by guesswork. Get a soil "
                    "test and follow the crop- and district-specific "
                    "recommendation from the Agriculture Department. "
                    "Apply the recommended dose at the correct crop stages."
                )

                te = (
                    "ఊహతో మాత్రమే ఎరువులు ఎంచుకోవద్దు. నేల పరీక్ష చేయించి "
                    "వ్యవసాయ శాఖ సూచించిన పంట, ప్రాంతానికి తగిన మోతాదును "
                    "సరైన దశల్లో వేయండి."
                )

            elif any(
                word in q
                for word in [
                    "rice",
                    "paddy",
                    "వరి",
                    "ధాన్యం",
                ]
            ):

                en = (
                    "For rice, use certified seed, maintain good field "
                    "drainage and monitor regularly for stem borer, leaf "
                    "folder and planthoppers. Follow local recommendations "
                    "for nursery, spacing, water and fertilizer."
                )

                te = (
                    "వరి సాగులో ధృవీకరించిన విత్తనాలు వాడండి, పొలంలో నీటి "
                    "పారుదల సరిగా ఉంచండి. కాండం తొలిచే పురుగు, ఆకుముడత "
                    "పురుగు, దాటే పురుగులను గమనించండి. నారు, దూరం, నీరు, "
                    "ఎరువుల విషయంలో స్థానిక సూచనలు పాటించండి."
                )

            else:

                en = TEXT["English"]["faq_unknown"]
                te = TEXT["తెలుగు"]["faq_unknown"]

            st.session_state["farmer_answer"] = (
                te if language == "తెలుగు" else en
            )

            st.session_state["farmer_answer_language"] = language_code

    # -------------------- DISPLAY ANSWER --------------------

    if "farmer_answer" in st.session_state:

        answer_text = st.session_state["farmer_answer"]

        st.markdown(f"**{tr('answer')}**")
        st.success(answer_text)

        if st.button("🔊 Speak Answer / సమాధానం వినండి"):

            try:

                with st.spinner("Generating voice..."):

                    audio_bytes = tts_client.synthesize(
                        answer_text,
                        voice="Pranav",
                        model="timbre-v2.5",
                        language=st.session_state["farmer_answer_language"],
                    )

                st.audio(audio_bytes, format="audio/wav")

            except Exception as e:

                st.error(f"Voice generation failed: {e}")

        st.caption(
            "Offline FAQ prototype — not a generative AI model / "
            "ఆఫ్‌లైన్ నమూనా — జనరేటివ్ AI మోడల్ కాదు"
        )

    st.caption(tr("disclaimer"))


# -------------------- IMAGE PREVIEW --------------------

elif page == tr("disease"):

    st.subheader(tr("image_title"))

    st.warning(tr("image_note"))

    uploaded = st.file_uploader(
        tr("upload"),
        type=["jpg", "jpeg", "png", "webp"],
    )

    if uploaded:

        left, right = st.columns([1.2, 1])

        with left:

            st.image(
                uploaded,
                caption=uploaded.name,
                use_container_width=True,
            )

        with right:

            st.markdown("**Image details / చిత్ర వివరాలు**")

            st.write(f"File: {uploaded.name}")
            st.write(f"Size: {uploaded.size / 1024:.1f} KB")
            st.write(f"Type: {uploaded.type}")

            st.info(
                "No disease prediction is performed. "
                "Do not spray pesticide based only on this page."
            )

    else:

        st.info(
            "Upload a clear leaf image in good lighting. / "
            "మంచి వెలుతురులో తీసిన స్పష్టమైన ఆకు చిత్రాన్ని అప్‌లోడ్ చేయండి."
        )


# -------------------- WEATHER --------------------

elif page == tr("weather"):

    st.subheader(tr("weather"))

    st.write(
        f"**{tr('select_district')}:** "
        f"{DISTRICTS[district] if language == 'తెలుగు' else district}"
    )

    st.info(tr("weather_note"))

    st.markdown(
        "**Useful official source / అధికారిక సమాచారం:** "
        "[India Meteorological Department (IMD)]"
        "(https://mausam.imd.gov.in/)"
    )


# -------------------- MARKET --------------------

elif page == tr("market"):

    st.subheader(tr("market"))

    commodities = {
        "Rice": "వరి",
        "Cotton": "పత్తి",
        "Chilli": "మిరప",
        "Maize": "మొక్కజొన్న",
        "Groundnut": "వేరుశనగ",
        "Tomato": "టమాటా",
    }

    commodity = st.selectbox(
        "Commodity / పంట",
        list(commodities),
        format_func=lambda x: (
            f"{x} — {commodities[x]}"
            if language == "తెలుగు"
            else x
        ),
    )

    st.write(
        f"Selected: **"
        f"{commodities[commodity] if language == 'తెలుగు' else commodity}"
        f"**"
    )

    st.info(tr("market_note"))

    st.markdown(
        "**Official source / అధికారిక వెబ్‌సైట్:** "
        "[e-NAM](https://www.enam.gov.in/web/)"
    )


# -------------------- ABOUT PROJECT --------------------

elif page == tr("about"):

    st.subheader(tr("about"))

    st.write(tr("about_text"))

    st.markdown("### " + tr("prototype"))

    st.success(tr("working"))

    st.warning(tr("planned"))

    st.markdown("**Technology / సాంకేతికత:** Python, Streamlit")

    st.markdown("**State focus / రాష్ట్రం:** Andhra Pradesh / ఆంధ్రప్రదేశ్")

    st.caption(
        f"Prototype prepared on {datetime.now().strftime('%d %b %Y')}."
    )

    st.caption(tr("disclaimer"))


# -------------------- FOOTER --------------------

st.markdown("---")

st.caption(
    "🌱 RythuVoiceAI • Andhra Pradesh farming information prototype "
    "• రైతు వాయిస్ AI"
)
