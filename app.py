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
st.markdown("### 上传作文照片 → 严格按广东高考评分标准打分 + 专业修改建议")

# 加载通义千问API密钥
try:
    api_key = st.secrets["TONGYI_API_KEY"]
    dashscope.api_key = api_key
except:
    st.warning("请先在 Streamlit Secrets 配置 TONGYI_API_KEY")
    st.stop()

# 作文上传与总分设置（高考常用满分25分）
st.header("上传学生建议信作文图片")
essay_image = st.file_uploader("选择图片 jpg / png / jpeg", type=["jpg", "png", "jpeg"])
total_score = st.slider("作文满分设置（广东高考建议信满分25）", min_value=10, max_value=25, value=25, step=1)

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

            # 第二步：严格按照广东高考英语建议信评分标准阅卷
            grade_prompt = f"""You are an experienced English examiner for Guangdong Gaokao.
Grade this student's **advice letter** strictly following **Guangdong Gaokao English scoring criteria**, total score out of {total_score}.

Evaluate strictly by these fixed dimensions for Gaokao formal letter:
1. Task Completion (是否完成写作任务：问候、表明来意、给出具体建议、结尾客套、格式完整)
2. Content & Relevance (内容切题、建议合理、要点齐全、无无关内容)
3. Text Structure & Layout (书信格式、段落划分、逻辑层次、开头-主体-结尾结构)
4. Cohesion & Logical Connection (衔接词使用、句间段间逻辑连贯、行文流畅度)
5. Grammar & Sentence Structure (时态、语态、句式多样性、复合句使用、语法错误多少)
6. Vocabulary & Expression (词汇准确、高级词汇运用、搭配地道、中式英语程度)
7. Spelling & Punctuation (单词拼写、大小写、标点规范)

Output all comments in clear English, keep objective, strict and fair as real Gaokao marking.
Use clear structure below:

- Final Gaokao Score: ___ / {total_score}
- Gaokao Level Assessment: (High / Medium / Low level according to Guangdong standard)
- Strengths (match Gaokao scoring standard)
- Main Problems & Errors (list specific mistakes in the letter)
- Detailed Revision Advice (follow Gaokao requirement)
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

        st.subheader("📊 广东高考标准 作文评分报告")
        st.markdown(feedback)
