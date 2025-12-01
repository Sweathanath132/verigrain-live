import streamlit as st
from ultralytics import YOLO
from PIL import Image, ImageOps
import numpy as np
import cv2
import qrcode
from fpdf import FPDF
from datetime import datetime

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

# --- PDF GENERATOR FUNCTION ---
def create_pdf(variety, total, pure, broken, score, status):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Header
    pdf.cell(190, 10, "VeriGrain Audit Certificate", 0, 1, 'C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(190, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'C')
    pdf.line(10, 30, 200, 30)
    
    # Report Details
    pdf.ln(15)
    pdf.set_font("Arial", '', 12)
    pdf.cell(50, 10, f"Target Standard:", 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"{variety}", 0, 1)
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(50, 10, f"Total Grains:", 0, 0)
    pdf.cell(100, 10, f"{total}", 0, 1)
    
    pdf.cell(50, 10, f"Pure Count:", 0, 0)
    pdf.cell(100, 10, f"{pure}", 0, 1)
    
    pdf.cell(50, 10, f"Mismatch/Defects:", 0, 0)
    pdf.cell(100, 10, f"{broken}", 0, 1)
    
    # Final Score Box
    pdf.ln(10)
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, pdf.get_y(), 190, 20, 'F')
    pdf.set_xy(15, pdf.get_y() + 5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(90, 10, f"SCORE: {score:.1f}%", 0, 0)
    pdf.cell(90, 10, f"STATUS: {status}", 0, 1, 'R')
    
    return pdf.output(dest='S').encode('latin-1')

# --- UNIVERSAL RICE DATABASE ---
RICE_STANDARDS = {
    "Basmati (Premium)": {
        "targets": ['premium'], 
        "adulterants": ['mid', 'low', 'medium'] 
    },
    "Sona Masoori / Daily Delight": {
        "targets": ['mid', 'medium', 'low'], 
        "adulterants": ['premium']
    },
    "Jasmine Rice": {
        "targets": ['premium'], 
        "adulterants": ['mid', 'low']
    },
    "Ponni Rice": {
        "targets": ['mid', 'medium'], 
        "adulterants": ['low', 'premium']
    },
    "Idli / Dosa Rice": {
        "targets": ['low', 'mid', 'medium'], 
        "adulterants": ['premium']
    }
}
PRESETS = list(RICE_STANDARDS.keys()) + ["➕ DEFINE NEW VARIETY"]

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
        logic = RICE_STANDARDS[rice_selection]

    st.caption(f"Config: Accepting {logic['targets']}")
    st.divider()
    
    # 3. AUTOMATIC QR CODE
    st.markdown("### 📱 Mobile Connect")
    # REPLACE WITH YOUR ACTUAL DEPLOYED URL
    app_url = "https://verigrain-live-c4h7lputvhvdhfxqcymq4j.streamlit.app/" 
    
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
    
    # 1. FIX MEMORY CRASH & ROTATION (The Critical Fix)
    image_to_process = ImageOps.exif_transpose(image_to_process) # Fixes rotated phone pics
    image_to_process.thumbnail((1024, 1024)) # Resizes huge images to safe size
    
    display_name = "Custom Variety" if "NEW" in rice_selection else rice_selection
    
    with st.spinner(f'Auditing against {display_name} Standards...'):
        # 2. RUN INFERENCE (Confidence 0.50)
        results = model(image_to_process, conf=0.50)
        
        # 3. EXTRACT & MAP DATA
        class_ids = results[0].boxes.cls.cpu().numpy()
        names = model.names
        
        target_count = 0
        adulterant_count = 0
        
        for i in class_ids:
            shape_name = names[int(i)]
            if shape_name == 'medium': shape_name = 'mid'
            
            # CHECK AGAINST DYNAMIC LOGIC
            if shape_name in logic['targets']:
                target_count += 1
            else:
                adulterant_count += 1
            
        total_grains = target_count + adulterant_count

    # --- HALLUCINATION CHECK (10 GRAINS) ---
    if total_grains < 10:
        st.error("⛔ OBJECT NOT RECOGNIZED")
        st.warning(f"Only {total_grains} shapes detected. Valid audit requires 10+ grains.")
        st.image(image_to_process, width=300, caption="Rejected Image")

    else:
        # 4. CALCULATE METRICS
        purity_score = (target_count / total_grains) * 100
        adulteration_pct = 100 - purity_score
        
        # 5. DISPLAY RESULTS
        res_plotted = results[0].plot()
        st.image(res_plotted, use_column_width=True, caption=f"Analyzed against: {display_name}")

        if user_mode == "Consumer":
            st.subheader(f"Quality Check: {display_name}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Grains", total_grains)
            c2.metric("✅ Pure Grains", f"{target_count} ({purity_score:.1f}%)")
            c3.metric("❌ Mismatch/Broken", f"{adulterant_count} ({adulteration_pct:.1f}%)")
            
            st.divider()
            
            if purity_score > 85:
                status_text = "APPROVED"
                st.success("✅ VERDICT: EXCELLENT QUALITY")
                st.balloons()
            elif purity_score > 70:
                status_text = "AVERAGE"
                st.warning("⚠️ VERDICT: AVERAGE QUALITY (Mixed Sizes)")
            else:
                status_text = "REJECTED"
                st.error("❌ VERDICT: LOW QUALITY / MISMATCH")
                
        else: # Industry Mode
            st.subheader("🏭 Mill Audit Report")
            c1, c2 = st.columns(2)
            c1.metric("Target Variety Count", target_count, "PASS")
            c2.metric("Contaminants / Broken", adulterant_count, "FAIL")
            
            st.write(f"**Detailed Breakdown:**")
            st.progress(purity_score/100, text=f"Purity: {purity_score:.1f}%")
            
            if purity_score < 90:
                status_text = "REJECTED"
                st.error(f"⚠️ REJECT: Adulteration {adulteration_pct:.1f}% exceeds limit.")
            else:
                status_text = "APPROVED"
                st.success("✅ CERTIFIED: Batch meets export standards.")

        # --- DOWNLOAD CERTIFICATE BUTTON ---
        st.write("---")
        pdf_data = create_pdf(display_name, total_grains, target_count, adulterant_count, purity_score, status_text)
        st.download_button(
            label="📄 Download Official Audit Certificate (PDF)",
            data=pdf_data,
            file_name=f"VeriGrain_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
