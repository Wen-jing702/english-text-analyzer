import streamlit as st
import dashscope
from dashscope import MultiModalConversation
import base64

# 全局放大字体样式
st.markdown("""
<style>
html, body, .stMarkdown, .stText {
    font-size: 18px !important;
}
h1 {font-size: 32px !important;}
h2 {font-size: 28px !important;}
h3 {font-size: 24px !important;}
h4 {font-size: 22px !important;}
li {font-size: 19px !important; line-height: 1.6;}
</style>
""", unsafe_allow_html=True)

# 页面基础配置
st.set_page_config(page_title="English Text Analyzer", layout="wide")
st.title("📖 English Text Structure Analyzer")
st.markdown("### Upload Article Image | Thesis & Topic Sentences Mind Map")

# 读取通义千问密钥
try:
    api_key = st.secrets["TONGYI_API_KEY"]
    dashscope.api_key = api_key
except:
    st.warning("Please fill in TONGYI_API_KEY in Streamlit Secrets first")
    st.stop()

# 图片上传
uploaded_file = st.file_uploader("Upload your English text image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Original Text", use_column_width=True)

    bytes_data = uploaded_file.getvalue()
    base64_data = base64.b64encode(bytes_data).decode("utf-8")

    # AI 精准提示词：强制论点+分论点+论据齐全、英文、思维导图层级
    with st.spinner("Analyzing text structure... Please wait..."):
        try:
            response = MultiModalConversation.call(
                model="qwen-vl-plus",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "text": """Analyze this English text and reply ALL IN ENGLISH.
Do not use Chinese. Keep content complete and clear for classroom presentation.

1. Full Text: Show the complete English article.

2. Text Structure Mind Map (hierarchical list form, must include):
- Central Thesis (overall main argument of the whole passage)
  - Main Topic Sentence 1 (paragraph 1 core opinion)
    - Key supporting arguments
    - Relevant facts or details
  - Main Topic Sentence 2 (paragraph 2 core opinion)
    - Key supporting arguments
    - Relevant facts or details
  - Main Topic Sentence 3 (if exists)

3. Cohesive Devices Classification:
List and categorize all linking words:
• Addition
• Contrast
• Cause & Effect
• Exemplification
• Conclusion

Make the logic clear, keep thesis, topic sentences and supporting points complete, not only examples."""
                        },
                        {"image": f"data:image/jpeg;base64,{base64_data}"}
                    ]
                }]
            )
            result = response["output"]["choices"][0]["message"]["content"][0]["text"]
        except Exception as e:
            st.error(f"Analysis Error: {str(e)}")
            st.stop()

    # 分区展示 方便投屏
    st.subheader("📄 Full Text")
    st.markdown(result)

    st.divider()
    st.subheader("🧠 Clear Text Structure Mind Map")
    st.info("Central Thesis → Topic Sentences → Supporting Arguments & Details")
