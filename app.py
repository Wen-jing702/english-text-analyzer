import streamlit as st
import dashscope
from dashscope import MultiModalConversation
import base64

# 全局放大字体 适配教室投屏展示
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
st.set_page_config(page_title="Guangdong Gaokao Letter Grader", layout="wide")
st.title("✍️ 广东高考英语建议信 作文评分工具")
st.markdown("### 上传作文照片 → 固定满分15分 严格按高考标准打分点评")

# 加载通义千问API密钥
try:
    api_key = st.secrets["TONGYI_API_KEY"]
    dashscope.api_key = api_key
except:
    st.warning("请先在 Streamlit Secrets 配置 TONGYI_API_KEY")
    st.stop()

# 固定满分15分，取消手动滑块
FULL_SCORE = 15

# 上传学生建议信作文图片
st.header("上传学生建议信作文图片")
essay_image = st.file_uploader("选择图片 jpg / png / jpeg", type=["jpg", "png", "jpeg"])

if essay_image is not None:
    st.image(essay_image, caption="待评学生建议信", use_column_width=True)

    bytes_data = essay_image.getvalue()
    base64_data = base64.b64encode(bytes_data).decode("utf-8")

    if st.button("🔎 按广东高考标准评分并点评", type="primary"):
        with st.spinner("正在识别作文 + 严格按高考标准阅卷评分..."):
            # 第一步：精准提取图片中作文文字
            ocr_prompt = """Extract all handwritten or printed English text from this image exactly.
Only output the pure letter text, no extra explanation, no translation."""

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

            # 第二步：严格广东高考建议信评分标准 固定满分15分
            grade_prompt = f"""You are an experienced English examiner for Guangdong Gaokao.
Grade this student's **advice letter** strictly following **Guangdong Gaokao English scoring criteria**.
The full score is fixed at {FULL_SCORE} points, score objectively and strictly.

Evaluate by these fixed dimensions for Gaokao advice letter:
1. Task Completion: Greeting, purpose statement, complete advice points, proper ending and letter format.
2. Content & Relevance: On-topic, reasonable suggestions, complete key points, no irrelevant content.
3. Text Structure & Layout: Standard letter format, clear paragraph division, logical beginning-body-ending.
4. Cohesion & Logical Connection: Proper use of linking words, smooth logical connection between sentences and paragraphs.
5. Grammar & Sentence Structure: Tense accuracy, sentence variety, use of simple and compound sentences, number of grammar errors.
6. Vocabulary & Expression: Accurate word choice, proper collocation, avoidance of Chinglish.
7. Spelling & Punctuation: Correct spelling, capitalization and punctuation rules.

Output all in clear English, keep strict, fair and objective like real Gaokao marking.
Follow this fixed output structure:

- Final Gaokao Score: ___ / {FULL_SCORE}
- Gaokao Level Assessment: (High / Medium / Low level under 15-point standard)
- Strengths (accord with Guangdong Gaokao scoring rules)
- Main Problems & Specific Errors
- Detailed Revision Advice for Gaokao
- Polished Gaokao-level Revised Version

Student Advice Letter Text:
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

        st.subheader("📊 广东高考标准 15分制 作文评分报告")
        st.markdown(feedback)
