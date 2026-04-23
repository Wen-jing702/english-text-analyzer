import streamlit as st
import dashscope
from dashscope import MultiModalConversation
import base64

# ---------------------- 页面配置 ----------------------
st.set_page_config(page_title="Text Structure Analysis", layout="wide")
st.title("📖 English Text Structure & Cohesive Devices Analyzer")
st.markdown("### Upload a text image → AI generates THESIS + TOPIC SENTENCES + SUPPORTING DETAILS")

# ---------------------- API Key ----------------------
try:
    api_key = st.secrets["TONGYI_API_KEY"]
    dashscope.api_key = api_key
except:
    st.warning("Please set TONGYI_API_KEY in Streamlit Secrets")
    st.stop()

# ---------------------- 上传图片 ----------------------
uploaded_file = st.file_uploader("Upload text image (JPG/PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Text", use_column_width=True)
    
    bytes_data = uploaded_file.getvalue()
    base64_data = base64.b64encode(bytes_data).decode("utf-8")

    # ---------------------- AI 分析指令（严格保留论点） ----------------------
    with st.spinner("Analyzing text structure..."):
        try:
            response = MultiModalConversation.call(
                model="qwen-vl-plus",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "text": """Analyze this English text image strictly in ENGLISH.
Output 3 parts clearly:

1. FULL TEXT
Extract the full essay/article exactly.

2. TEXT STRUCTURE MIND MAP (KEEP ALL THESE LEVELS)
- CENTRAL THESIS (main argument of the whole text)
  - TOPIC SENTENCE 1 (main idea of paragraph 1)
    - Supporting Point 1
    - Supporting Point 2
    - Example/Evidence
  - TOPIC SENTENCE 2 (main idea of paragraph 2)
    - Supporting Point 1
    - Supporting Point 2
    - Example/Evidence
  - TOPIC SENTENCE 3 (if any)
    - Supporting details

3. COHESIVE DEVICES CLASSIFICATION
List all linking words:
- Addition
- Contrast
- Cause & Effect
- Example
- Conclusion"""
                        },
                        {"image": f"data:image/jpeg;base64,{base64_data}"}
                    ]
                }]
            )
            result = response["output"]["choices"][0]["message"]["content"][0]["text"]
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            st.stop()

    # ---------------------- 显示完整分析结果 ----------------------
    st.subheader("📋 Complete Analysis")
    st.markdown(result)

    # ---------------------- 思维导图标题 ----------------------
    st.subheader("🧠 Text Structure Mind Map")
    st.success("Central Thesis → Topic Sentences → Supporting Points → Examples")
