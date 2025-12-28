

 **VeriGrain: AI-Powered Rice Quality Auditing**

**VeriGrain** is a cloud-native solution designed to combat **Intra-Varietal Adulteration** in the rice supply chain.pptx]. By utilizing advanced computer vision, it replaces expensive industrial hardware with a low-cost, mobile-accessible auditing tool capable of quantifying purity in real-time.pptx].

 **🚀 Key Innovations**

 **1. Solving the Occlusion Problem**

Standard AI models fail when grains overlap in a pile.pptx]. VeriGrain implements **YOLOv8 Instance Segmentation** to generate precise pixel-level masks for every individual grain.pptx]. This allows for exact counting and segregation even in dense samples.pptx].

### **2. Universal Dynamic Logic Layer (Patentable)**

Most AI models are rigid; a model trained for Basmati will fail on Idli rice.pptx]. Our system **decouples the AI detection from the grading context**.pptx]. A single model detects physical shapes, while our dynamic logic layer applies the specific "Pass/Fail" criteria based on the user's selected rice variety.pptx].

---

 **📊 Performance Metrics**

* **mAP@50 (Accuracy):** 94.6%.pptx]
* **Recall (Contaminant Detection):** 0.98.pptx]
* **Inference Speed:** ~180ms (Cloud CPU).pptx]

---

 **🛠️ Tech Stack**

* **Model:** YOLOv8-Nano Segmentation.pptx]
* **Training:** Google Colab (NVIDIA T4 GPU).pptx]
* **Deployment:** Streamlit Community Cloud.pptx]
* **Language:** Python 3.9+.pptx]

---

 **📂 Methodology**

1. **Dataset Engineering:** Created a custom dataset with 12 levels of contamination (4% to 48%) using **Smart Polygon Masks** for high-precision morphology training.pptx].
2. **Model Evolution:** Evaluated Custom CNNs and MobileNetV2 before pivoting to YOLOv8 to achieve individual grain quantification.pptx].
3. **Logic Integration:** Developed a proprietary Python backend to calculate **Purity Scores** and **Estimated Financial Loss**.pptx].
4. **Robustness:** Implemented the **"10-Grain Rule"** to automatically reject non-grain images and prevent model hallucinations.pptx].

---

 **💻 How to Use**

1. **Access:** Open the VeriGrain web app via the provided URL or QR code.pptx].
2. **Select Variety:** Choose the target rice variety (e.g., Basmati).pptx].
3. **Capture/Upload:** Take a top-down photo of the grain sample on a non-reflective background.pptx].
4. **Audit:** View the live segmentation, Purity Score, and financial impact report.pptx].

---

 **⚖️ License & Contact**

Developed by the VeriGrain Team lead by swathanath  at **SMVITM, Bantakal**.
For inquiries regarding the **Universal Dynamic Logic** patent or technical collaboration, please contact the project guide and swathanath 
