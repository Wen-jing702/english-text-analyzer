import streamlit as st
import dashscope
from dashscope import MultiModalConversation
import base64

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
st.set_page_config(page_title="English Text & Essay Analyzer", layout="wide")
st.title("📖 English Text Structure + Student Essay Grader")
st.markdown("### Upload Article Image → Analyze Structure | Paste Essay → Get Score & Suggestions")

# ---------------------- API Key ----------------------
try:
    api_key = st.secrets["TONGYI_API_KEY"]
    dashscope.api_key = api_key
except:
    st.warning("Please fill in TONGYI_API_KEY in Streamlit Secrets first")
    st.stop()

# ---------------------- 分栏布局：左边课文分析，右边作文批改 ----------------------
col1, col2 = st.columns(2)

# ---------------------- 左侧：课文结构分析 ----------------------
with col1:
    st.header("1. Text Structure Analysis")
    uploaded_file = st.file_uploader("Upload the model text/image", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Original Text", use_column_width=True)

        bytes_data = uploaded_file.getvalue()
        base64_data = base64.b64encode(bytes_data).decode("utf-8")

        with st.spinner("Analyzing text structure..."):
            try:
                response = MultiModalConversation.call(
                    model="qwen-vl-plus",
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "text": """Analyze this English text and reply ALL IN ENGLISH.
Do not use Chinese. Keep content complete for classroom presentation.

1. Full Text: Show the complete English article.

2. Text Structure Mind Map (hierarchical list):
- Central Thesis (main argument)
  - Main Topic Sentence 1 (paragraph 1 core idea)
    - Supporting arguments
    - Relevant details/examples
  - Main Topic Sentence 2 (paragraph 2 core idea)
    - Supporting arguments
    - Relevant details/examples
  - Main Topic Sentence 3 (if exists)

3. Cohesive Devices Classification:
List and categorize all linking words:
• Addition
• Contrast
• Cause & Effect
• Exemplification
• Conclusion"""
                            },
                            {"image": f"data:image/jpeg;base64,{base64_data}"}
                        ]
                    }]
                )
                result = response["output"]["choices"][0]["message"]["content"][0]["text"]
            except Exception as e:
                st.error(f"Analysis Error: {str(e)}")
                st.stop()

        st.subheader("📄 Full Text & Structure")
        st.markdown(result)

        st.divider()
        st.subheader("🧠 Text Structure Mind Map")
        st.info("Central Thesis → Topic Sentences → Supporting Details")

# ---------------------- 右侧：学生作文智能批改 ----------------------
with col2:
    st.header("2. Student Essay Grader")
    essay = st.text_area("Paste the student's essay here:", height=400, placeholder="Enter the essay to grade...")
    max_score = st.slider("Total Score", min_value=20, max_value=100, value=100, step=10)

    if st.button("Grade Essay", type="primary") and essay:
        with st.spinner("Grading and giving suggestions..."):
            try:
                # 作文批改指令：多维度评分+建议
                prompt = f"""Grade this student's English essay (out of {max_score} points).
Evaluate from these dimensions:
1. Content & Thesis (relevance, completeness, clear main idea)
2. Structure & Organization (logical flow, paragraphing, use of topic sentences)
3. Language Accuracy (grammar, spelling, punctuation errors)
4. Cohesion & Coherence (use of linking words, logical connections)
5. Vocabulary & Expression (word choice, variety, appropriateness)

Output format:
1. Final Score: [score]/[{max_score}]
2. Strengths: (3-4 bullet points)
3. Areas to Improve: (3-4 bullet points with specific examples from the essay)
4. Detailed Suggestions & Revisions: (specific edits and a revised version of the essay)

Student Essay:
{essay}
"""
                response = MultiModalConversation.call(
                    model="qwen-vl-plus",
                    messages=[{
                        "role": "user",
                        "content": [{"text": prompt}]
                    }]
                )
                feedback = response["output"]["choices"][0]["message"]["content"][0]["text"]
            except Exception as e:
                st.error(f"Grading Error: {str(e)}")
                st.stop()

        st.subheader("📊 Essay Evaluation Report")
        st.markdown(feedback)
