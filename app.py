import streamlit as st
from ultralytics import YOLO
from PIL import Image, ImageOps, ImageDraw, ImageFont
import numpy as np
import cv2
import qrcode
from fpdf import FPDF
from datetime import datetime
import io

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
</style>
""", unsafe_allow_html=True)

# --- PDF GENERATOR ---
def create_pdf(variety, total, pure, broken, score, status):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "VeriGrain Audit Certificate", 0, 1, 'C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(190, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1, 'C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(15)
    pdf.set_font("Arial", '', 12)
    pdf.cell(100, 10, f"Target Standard: {variety}", 0, 1)
    pdf.cell(100, 10, f"Total Sample: {total} grains", 0, 1)
    pdf.cell(100, 10, f"Pure Count: {pure}", 0, 1)
    pdf.cell(100, 10, f"Defects: {broken}", 0, 1)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(100, 10, f"FINAL SCORE: {score:.1f}% ({status})", 0, 1)
    return pdf.output(dest='S').encode('latin-1')

# --- VIRAL CARD GENERATOR ---
def create_viral_card(orig_img, analyzed_img_arr, score, status, total, broken):
    width, height = 800, 1000
    card = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(card)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 60)
        font_main = ImageFont.truetype("arial.ttf", 40)
    except:
        font_title = ImageFont.load_default()
        font_main = ImageFont.load_default()

    draw.rectangle([(0,0), (width, 120)], fill="#0E1117")
    draw.text((30, 30), "VeriGrain Audit Report", fill="#00FF00", font=font_title)
    
    orig_img = orig_img.resize((350, 350))
    analyzed_pil = Image.fromarray(analyzed_img_arr[:, :, ::-1]).resize((350, 350))
    
    card.paste(orig_img, (25, 150))
    card.paste(analyzed_pil, (425, 150))
    
    draw.text((25, 510), "Original Sample", fill="black", font=font_main)
    draw.text((425, 510), "AI Detection", fill="black", font=font_main)
    
    draw.rectangle([(25, 580), (775, 900)], outline="black", width=3)
    draw.text((50, 600), f"PURITY SCORE: {score:.1f}%", fill="black", font=font_main)
    
    color = "green" if "APPROVED" in status else "red"
    draw.text((50, 660), f"STATUS: {status}", fill=color, font=font_main)
    draw.text((50, 720), f"Total Grains: {total}", fill="black", font=font_main)
    draw.text((50, 780), f"Defects Found: {broken}", fill="black", font=font_main)
    
    draw.rectangle([(0, 920), (width, 1000)], fill="#EEEEEE")
    draw.text((150, 940), "Scanned via VeriGrain AI Cloud", fill="gray", font=font_main)
    
    return card

# --- UNIVERSAL RICE DATABASE ---
PRESETS = [
    "Basmati (Premium)", "Jasmine Rice", "Sona Masoori", "Ponni Rice", 
    "Matta / Parboiled", "Idli / Dosa Rice", "➕ DEFINE NEW VARIETY"
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
    st.error("🚨 CRITICAL ERROR: 'best.pt' not found on GitHub.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2933/2933116.png", width=80)
    st.title("VeriGrain Cloud")
    st.markdown(f"**Status:** :{status_color}[{model_status}]")
    st.divider()
    user_mode = st.radio("User Mode:", ["Consumer", "Industry Audit"])
    st.divider()
    rice_selection = st.selectbox("Select Rice Variety:", PRESETS)
    
    if rice_selection == "➕ DEFINE NEW VARIETY":
        st.info("Manual Calibration")
        target_shape = st.radio("Expected Shape:", ["Long Grain", "Medium Grain", "Short/Round Grain"])
        if target_shape == "Long Grain": logic = {"targets": ['premium'], "adulterants": ['mid', 'low']}
        elif target_shape == "Medium Grain": logic = {"targets": ['mid', 'medium'], "adulterants": ['low']}
        else: logic = {"targets": ['low'], "adulterants": []}
    else:
        # DB MAPPING
        if "Basmati" in rice_selection or "Jasmine" in rice_selection: 
            logic = {"targets": ['premium'], "adulterants": ['mid', 'low']}
        elif "Sona" in rice_selection or "Ponni" in rice_selection or "Matta" in rice_selection: 
            logic = {"targets": ['mid', 'medium'], "adulterants": ['low']}
        else: # Idli/Dosa
            logic = {"targets": ['low', 'mid'], "adulterants": []}

    st.divider()
    # QR CODE
    app_url = "https://verigrain-live-c4h7lputvhvdhfxqcymq4j.streamlit.app" 
    img = qrcode.make(app_url)
    st.image(img.get_image(), caption="Scan to Open on Phone")

# --- MAIN APP ---
st.title("🌾 GRAIN AUDIT SYSTEM")
tab1, tab2 = st.tabs(["📸 LIVE SCANNER", "📂 UPLOAD BATCH"])
image_to_process = None

with tab1:
    camera_file = st.camera_input("Camera Input", label_visibility="collapsed")
    if camera_file: image_to_process = Image.open(camera_file)

with tab2:
    uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
    if uploaded_file: image_to_process = Image.open(uploaded_file)

# --- PROCESS IMAGE ---
if image_to_process:
    st.divider()
    
    image_to_process = ImageOps.exif_transpose(image_to_process)
    image_to_process.thumbnail((1024, 1024))
    
    display_name = "Custom Variety" if "NEW" in rice_selection else rice_selection
    
    with st.spinner(f'Auditing...'):
        results = model(image_to_process, conf=0.50)
        class_ids = results[0].boxes.cls.cpu().numpy()
        names = model.names
        target_count = 0
        broken_count = 0
        
        for i in class_ids:
            shape_name = names[int(i)]
            if shape_name == 'medium': shape_name = 'mid'
            if shape_name in logic['targets']: target_count += 1
            else: broken_count += 1
        total_grains = target_count + broken_count

    if total_grains < 10:
        st.error("⛔ OBJECT NOT RECOGNIZED: Need 10+ grains.")
        st.image(image_to_process, width=300)
    else:
        purity_score = (target_count / total_grains) * 100
        res_plotted = results[0].plot()
        st.image(res_plotted, use_column_width=True, caption=f"Analyzed: {display_name}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Total", total_grains)
        c2.metric("Pure", f"{target_count}")
        c3.metric("Score", f"{purity_score:.1f}%")
        
        if purity_score > 85: 
            status_text = "APPROVED"
            st.success("✅ BATCH APPROVED")
        else: 
            status_text = "REJECTED"
            st.error("❌ BATCH REJECTED")

        # --- SHARING SECTION (UPDATED) ---
        st.write("---")
        st.subheader("📢 Share Results")
        
        # 1. CREATE CARD
        viral_card = create_viral_card(image_to_process, res_plotted, purity_score, status_text, total_grains, broken_count)
        
        # 2. SAVE TO BUFFER
        buf = io.BytesIO()
        viral_card.save(buf, format="JPEG")
        byte_im = buf.getvalue()
        
        # 3. SHARE WORKFLOW
        st.info("💡 To share the image on WhatsApp: Download the Report Card first, then click 'Share Text' and attach the image.")
        
        col_dl, col_wa = st.columns(2)
        
        col_dl.download_button(
            label="1️⃣ Download Report Card Image",
            data=byte_im,
            file_name="VeriGrain_Card.jpg",
            mime="image/jpeg",
        )
        
        whatsapp_msg = f"I scanned this rice with VeriGrain! Score: {purity_score:.1f}% ({status_text}). Check yours here: https://verigrain-live.streamlit.app"
        col_wa.link_button("2️⃣ Share Text on WhatsApp", f"https://wa.me/?text={whatsapp_msg}")
        
        st.image(viral_card, width=300, caption="Preview of Report Card")

        if user_mode == "Industry Audit":
            st.write("---")
            pdf_data = create_pdf(display_name, total_grains, target_count, broken_count, purity_score, status_text)
            st.download_button("📄 Download Audit Certificate (PDF)", data=pdf_data, file_name="Audit.pdf", mime="application/pdf")
