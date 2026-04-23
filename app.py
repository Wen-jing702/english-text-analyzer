import streamlit as st
import dashscope
from dashscope import MultiModalConversation
import base64
from PIL import Image

# ---------------------- 全局字体放大，适配投屏 ----------------------
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

# ---------------------- 页面配置 ----------------------
st.set_page_config(page_title="English Teaching Suite", layout="wide")
st.title("📖 English Teaching Toolkit | Text Analysis & Essay Grader")
st.markdown("### Double Features: Analyze Model Text | Grade Student Essays")

# ---------------------- API Key 配置 ----------------------
try:
    api_key = st.secrets["TONGYI_API_KEY"]
    dashscope.api_key = api_key
except:
    st.warning("Please set TONGYI_API_KEY in Streamlit Secrets first")
    st.stop()

# ---------------------- 左右分栏布局 ----------------------
left_col, right_col = st.columns(2)

# ---------------------- 左侧功能：课文/范文分析 ----------------------
with left_col:
    st.header("📄 1. Text Structure Analysis")
    st.subheader("(Upload Model Text Image)")
    text_image = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"], key="text_img")

    if text_image is not None:
        st.image(text_image, caption="Uploaded Model Text", use_column_width=True)
        bytes_data = text_image.getvalue()
        base64_data = base64.b64encode(bytes_data).decode("utf-8")

        with st.spinner("Analyzing Structure..."):
            try:
                response = MultiModalConversation.call(
                    model="qwen-vl-plus",
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "text": """Analyze this English text image and output ALL IN ENGLISH.
1. Extract the full text accurately.
2. Generate a clear hierarchical mind map (Thesis → Topic Sentences → Supporting Details).
3. List key cohesive devices (Addition, Contrast, Cause, Effect, Example).
Make sure to keep COMPLETE thesis and topic sentences, not just examples.""",
                            },
                            {"image": f"data:image/jpeg;base64,{base64_data}"}
                        ]
                    }]
                )
                result = response["output"]["choices"][0]["message"]["content"][0]["text"]
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.stop()

        st.subheader("📋 Full Analysis")
        st.markdown(result)

# ---------------------- 右侧功能：作文图片批改 ----------------------
with right_col:
    st.header("✍️ 2. Student Essay Grader")
    st.subheader("(Upload Essay Image to Grade)")
    essay_image = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"], key="essay_img")
    total_score = st.slider("Set Total Score", min_value=20, max_value=100, value=100, step=10)

    if essay_image is not None:
        # 显示上传的作文图片
        st.image(essay_image, caption="Student Essay to Grade", use_column_width=True)
        
        # 转码图片
        bytes_data = essay_image.getvalue()
        base64_data = base64.b64encode(bytes_data).decode("utf-8")

        if st.button("🔎 Analyze & Grade Essay", type="primary"):
            with st.spinner("Reading Essay & Generating Feedback..."):
                try:
                    # 第一步：让AI识别图片中的作文文本
                    # 先提取文本
                    ocr_prompt = """Please accurately extract ALL English text from this image.
If there is any handwritten English or printed English, convert it to plain text exactly.
Do not add any comments, just output the pure text."""
                    
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

                    # 第二步：对提取的文本进行智能评分和建议
                    grading_prompt = f"""
You are an experienced English teacher. Grade the student's essay based on the extracted text.
Total Score: {total_score} points.

Evaluate strictly on these 5 dimensions:
1. Content & Relevance (How well is the topic covered?)
2. Structure & Coherence (Logical flow, paragraphing)
3. Language Accuracy (Grammar, spelling, punctuation)
4. Vocabulary Range (Word choice, variety)
5. Cohesion (Linking words, flow between sentences)

OUTPUT FORMAT (must be in English and large font for presentation):
- **Final Score**: [Score] / {total_score}
- **Strengths**: (3 brief points)
- **Areas to Improve**: (3 specific points with examples from the essay)
- **Revision Suggestions**: (List 3-5 key edits to make)
- **Revised Version**: (Rewrite the essay to a higher standard)

---
**Student Essay Text**:
{essay_text}
"""
                    # 调用大模型批改
                    grade_response = MultiModalConversation.call(
                        model="qwen-vl-plus",
                        messages=[{
                            "role": "user",
                            "content": [{"text": grading_prompt}]
                        }]
                    )
                    feedback = grade_response["output"]["choices"][0]["message"]["content"][0]["text"]

                except Exception as e:
                    st.error(f"Processing Error: {str(e)}")
                    st.stop()

            st.subheader("📊 Evaluation Report")
            st.markdown(feedback)
