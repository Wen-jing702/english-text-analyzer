import streamlit as st
import dashscope
from dashscope import MultiModalConversation
import base64

# 全局放大字体 适配课堂投屏
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

# 页面配置
st.set_page_config(page_title="Student Essay Grader", layout="wide")
st.title("✍️ Student Essay Image Grading Tool")
st.markdown("### Upload student essay photo → Auto score + comments + revision advice")

# 读取API密钥
try:
    api_key = st.secrets["TONGYI_API_KEY"]
    dashscope.api_key = api_key
except:
    st.warning("Please set TONGYI_API_KEY in Streamlit Secrets first")
    st.stop()

# 只保留作文图片批改功能
st.header("Upload Student Essay Image")
essay_image = st.file_uploader("Choose image (jpg/png/jpeg)", type=["jpg", "png", "jpeg"])
total_score = st.slider("Total Score", min_value=20, max_value=100, value=100, step=10)

if essay_image is not None:
    st.image(essay_image, caption="Student Essay", use_column_width=True)

    bytes_data = essay_image.getvalue()
    base64_data = base64.b64encode(bytes_data).decode("utf-8")

    if st.button("🔎 Analyze & Grade Essay", type="primary"):
        with st.spinner("Reading and grading essay..."):
            # 第一步：提取图片里的英文作文
            ocr_prompt = """Extract all English text from this image exactly.
Only output the pure essay text, no extra comments."""

            ocr_response = MultiModalConversation.call(
                model="qwen-vl-plus",
                messages=[{
                    "role": "user",
                    "content": [
                        {"text": ocr_prompt},
                        {"image": f"data:image/jpeg;base64,{base64_data}"}
                    ]
                }]
            )
            essay_text = ocr_response["output"]["choices"][0]["message"]["content"][0]["text"]

            # 第二步：多维度评分点评
            grade_prompt = f"""You are a professional English teacher.
Grade this student essay out of {total_score} points.

Evaluate in 5 dimensions:
1. Content & Theme
2. Structure & Logic
3. Grammar & Accuracy
4. Cohesive Devices
5. Vocabulary & Expression

Output all in English, use clear layout for classroom projection:
- Final Score: ___ / {total_score}
- Strengths
- Weaknesses & Specific Errors
- Detailed Revision Suggestions
- Polished Revised Essay

Student Essay:
{essay_text}
"""

            grade_res = MultiModalConversation.call(
                model="qwen-vl-plus",
                messages=[{
                    "role": "user",
                    "content": [{"text": grade_prompt}]
                }]
            )
            feedback = grade_res["output"]["choices"][0]["message"]["content"][0]["text"]

        st.subheader("📊 Essay Evaluation Report")
        st.markdown(feedback)
