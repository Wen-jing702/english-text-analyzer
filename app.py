import streamlit as st
import dashscope
from dashscope import MultiModalConversation
import base64

# ---------------------- Page Config ----------------------
st.set_page_config(page_title="Text Structure Analysis", layout="wide")
st.title("📖 English Text Structure & Cohesion Analyzer")
st.markdown("### Upload Text Image → Auto Structure + Mind Map (English)")

# ---------------------- API Key ----------------------
try:
    api_key = st.secrets["TONGYI_API_KEY"]
    dashscope.api_key = api_key
except:
    st.warning("Please set TONGYI_API_KEY in Streamlit Secrets")
    st.stop()

# ---------------------- Upload Image ----------------------
uploaded_file = st.file_uploader("Upload an image (JPG/PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Text", use_column_width=True)
    
    bytes_data = uploaded_file.getvalue()
    base64_data = base64.b64encode(bytes_data).decode("utf-8")

    # ---------------------- AI Analysis (FULL ENGLISH) ----------------------
    with st.spinner("Analyzing text structure..."):
        try:
            response = MultiModalConversation.call(
                model="qwen-vl-plus",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "text": """Analyze this English text image and output ONLY IN ENGLISH:
1. Extract full text
2. Show TEXT STRUCTURE IN HIERARCHICAL MIND MAP (use -, ---, ---- for levels: Main Idea → Supporting Ideas → Details → Examples)
3. List ALL cohesive devices: Addition, Contrast, Cause/Effect, Example, Conclusion"""
                        },
                        {"image": f"data:image/jpeg;base64,{base64_data}"}
                    ]
                }]
            )
            result = response["output"]["choices"][0]["message"]["content"][0]["text"]
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.stop()

    # ---------------------- Show Full Analysis ----------------------
    st.subheader("📋 Full Analysis")
    st.markdown(result)

    # ---------------------- English Mind Map Section ----------------------
    st.subheader("🧠 Text Structure Mind Map (English)")
    st.markdown("""
    **Structure Style:**
    - Main Idea
      - Key Point 1
        - Detail
        - Example
      - Key Point 2
        - Detail
    """)
