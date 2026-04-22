import streamlit as st
import pytesseract
from PIL import Image
import openai
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

# 1. 配置API和页面
st.set_page_config(page_title="AI课文读写分析工具", layout="wide")
openai.api_key = "你的API密钥"

# 2. 上传图片并OCR识别
uploaded_file = st.file_uploader("上传课文图片", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="上传的课文", use_column_width=True)
    
    # OCR提取文本
    text = pytesseract.image_to_string(image, lang='eng')
    st.subheader("识别出的课文文本")
    st.text_area("文本内容", text, height=200)

    # 3. AI提炼写作框架和衔接词
    with st.spinner("AI正在分析课文结构..."):
        prompt = f"""
        分析下面的议论文文本：
        1. 提炼文章写作框架，分段落列出主题句、核心观点和支撑细节；
        2. 提取所有衔接词，按功能分类（递进/转折/因果/举例/总结），并附上原文例句；
        文本：{text}
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        analysis = response.choices[0].message.content

    # 4. 展示写作框架
    st.subheader("📋 课文写作框架")
    st.markdown(analysis.split("衔接词分类")[0])

    # 5. 生成衔接词词云
    st.subheader("☁️ 衔接词互动词云")
    link_words = []
    # 从AI分析结果中提取衔接词（示例，可优化正则匹配）
    for line in analysis.splitlines():
        if any(cat in line for cat in ["递进", "转折", "因果", "举例", "总结"]):
            words = [w.strip() for w in line.split(":")[-1].split(",") if w.strip()]
            link_words.extend(words)
    
    if link_words:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(link_words))
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
