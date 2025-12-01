import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import qrcode

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="VeriGrain Cloud", layout="wide", page_icon="🌾")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1 { color: #00FF00; font-family: 'Courier New'; text-align: center; }
    .stButton>button { 
        height: 60px; font-size: 18px; border-radius: 10px; 
        background-color: #00FF00; color: black; font-weight: bold; border: none; width: 100%;
    }
    .metric-card { background-color: #262730; padding: 15px; border-radius: 10px; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #262730; border-radius: 5px; color: white;}
    .stTabs [aria-selected="true"] { background-color: #00FF00; color: black; }
</style>
""", unsafe_allow_html=True)

# --- UNIVERSAL RICE DATABASE ---
PRESETS = [
    "Basmati (Premium)", 
    "Jasmine Rice", 
    "Sona Masoori", 
    "Ponni Rice", 
    "Matta / Parboiled",
    "Idli / Dosa Rice",
    "➕ DEFINE NEW VARIETY"
]

# --- LOAD BRAIN ---
@st.cache_resource
def load_model():
    return YOLO('best.pt')

try:
    model = load_model()
    model_status = "SYSTEM ONLINE"
    status_color = "green"
except:
    st.error("🚨 CRITICAL ERROR: 'best.pt' not found. Please upload it to GitHub.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2933/2933116.png", width=80)
    st.title("VeriGrain Cloud")
    st.markdown(f"**Status:** :{status_color}[{model_status}]")
    st.divider()

    # 1. MODE SELECTOR
    user_mode = st.radio("User Mode:", ["Consumer", "Industry Audit"])
    st.divider()
    
    # 2. UNIVERSAL VARIETY SELECTOR
    st.markdown("### 🍚 Calibration Standard")
    rice_selection = st.selectbox("Select Rice Variety:", PRESETS)
    
    # DYNAMIC LOGIC ENGINE
    if rice_selection == "➕ DEFINE NEW VARIETY":
        st.info("Manual Calibration Mode")
        target_shape = st.radio("What shape is this rice SUPPOSED to be?", 
                 ["Long Grain", "Medium Grain", "Short/Round Grain"])
        
        if target_shape == "Long Grain":
            logic = {"targets": ['premium'], "adulterants": ['mid', 'low']}
        elif target_shape == "Medium Grain":
            logic = {"targets": ['mid', 'medium'], "adulterants": ['low']}
        else:
            logic = {"targets": ['low'], "adulterants": []}
            
    else:
        # Load from Preset Database
        if "Basmati" in rice_selection or "Jasmine" in rice_selection:
            logic = {"targets": ['premium'], "adulterants": ['mid', 'low']}
        elif "Sona" in rice_selection or "Ponni" in rice_selection or "Matta" in rice_selection:
            logic = {"targets": ['mid', 'medium'], "adulterants": ['low']}
        else: # Idli/Dosa
            logic = {"targets": ['low', 'mid'], "adulterants": []}

    st.caption(f"Config: Expecting {logic['targets']}")
    st.divider()
    
    # 3. QR CONNECT (Updated for Cloud)
    st.markdown("### 📱 Mobile Connect")
    # Enter your Streamlit Cloud URL here once deployed
    app_url = st.text_input("Enter App URL for QR:", value="https://verigrain-live.streamlit.app")
    
    if app_url:
        img = qrcode.make(app_url)
        st.image(img.get_image(), caption="Scan to Open on Phone")

# --- MAIN INTERFACE ---
st.title("🌾 GRAIN AUDIT SYSTEM")
st.caption("AI-Powered Quality Control & Fraud Detection")

tab1, tab2 = st.tabs(["📸 LIVE SCANNER", "📂 UPLOAD BATCH"])
image_to_process = None

with tab1:
    st.info("Tap 'Take Photo' to audit a sample instantly.")
    camera_file = st.camera_input("Camera Input", label_visibility="collapsed")
    if camera_file: image_to_process = Image.open(camera_file)

with tab2:
    uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
    if uploaded_file: image_to_process = Image.open(uploaded_file)

# --- PROCESSING ENGINE ---
if image_to_process:
    st.divider()
    
    display_name = "Custom Variety" if "NEW" in rice_selection else rice_selection
    
    with st.spinner(f'Auditing against {display_name} Standards...'):
        # 1. RUN INFERENCE (Confidence 0.50)
        results = model(image_to_process, conf=0.50)
        
        # 2. EXTRACT & MAP DATA
        class_ids = results[0].boxes.cls.cpu().numpy()
        names = model.names
        
        target_count = 0
        other_count = 0
        broken_count = 0
        
        for i in class_ids:
            shape_name = names[int(i)]
            if shape_name == 'medium': shape_name = 'mid'
            
            # CHECK AGAINST DYNAMIC LOGIC
            if shape_name in logic['targets']:
                target_count += 1
            else:
                other_count += 1
                if shape_name == 'low': broken_count += 1
            
        total_grains = target_count + other_count

    # --- HALLUCINATION CHECK (10 GRAINS) ---
    if total_grains < 10:
        st.error("⛔ OBJECT NOT RECOGNIZED")
        st.warning(f"Only {total_grains} shapes detected. Valid audit requires 10+ grains.")
        res_plotted = results[0].plot()
        st.image(res_plotted, width=300, caption="Rejected Analysis")

    else:
        # 4. CALCULATE PURITY
        purity_score = (target_count / total_grains) * 100
        
        # 5. DISPLAY RESULTS
        res_plotted = results[0].plot()
        st.image(res_plotted, use_column_width=True, caption=f"Analyzed against: {display_name}")

        if user_mode == "Consumer":
            st.subheader(f"Quality Check: {display_name}")
            c1, c2 = st.columns(2)
            c1.metric("Total Grains", total_grains)
            c2.metric("Purity Score", f"{purity_score:.1f}%")
            
            if purity_score > 85:
                st.success("✅ EXCELLENT QUALITY. Matches Standards.")
            elif purity_score > 70:
                st.warning("⚠️ AVERAGE QUALITY. Mixed sizes detected.")
            else:
                st.error("❌ LOW QUALITY / ADULTERATED.")
                
        else: # Industry Mode
            st.subheader("🏭 Mill Audit Report")
            c1, c2, c3 = st.columns(3)
            c1.metric("Target Grain Count", target_count, "PASS")
            c2.metric("Wrong Variety", other_count - broken_count, "FAIL")
            c3.metric("Broken/Dust", broken_count, "CRITICAL")
            
            if purity_score < 90:
                st.error(f"⚠️ REJECT: Adulteration {(100-purity_score):.1f}% exceeds limit.")
            else:
                st.success("✅ CERTIFIED: Batch meets export standards.")