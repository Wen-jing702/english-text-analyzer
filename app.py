import streamlit as st
from openai import OpenAI
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---------------------- 页面配置 ----------------------
st.set_page_config(page_title="英语课文结构分析工具", layout="wide")
st.title("📖 AI英语课文结构与衔接词分析工具")
st.markdown("### 上传课文图片 → AI自动分析结构 + 生成衔接词词云")

# ---------------------- API KEY ----------------------
# 从Streamlit Secrets安全读取（你后面在Streamlit里填）
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.warning("请在Streamlit Secrets中设置 OPENAI_API_KEY")
    st.stop()

# ---------------------- 上传课文图片 ----------------------
uploaded_file = st.file_uploader("上传课文图片（jpg/png）", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # 显示图片
    st.image(uploaded_file, caption="已上传的课文", use_column_width=True)

    # ---------------------- AI 分析文本 ----------------------
    with st.spinner("⌛ AI正在分析课文结构和衔接词..."):
        # 直接让GPT-4V分析图片
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请分析这张英语课文图片，完成以下任务：\n1. 提取课文完整文本\n2. 提炼文章写作结构（段落主题句+观点+支撑细节）\n3. 提取所有衔接词，按：递进/转折/因果/举例/总结分类，并给出例句"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{uploaded_file.getvalue().hex()}"}}
                    ]
                }
            ],
            max_tokens=2000
        )
        result = response.choices[0].message.content

    # ---------------------- 显示分析结果 ----------------------
    st.subheader("📋 课文结构与衔接词分析")
    st.markdown(result)

    # ---------------------- 提取衔接词 + 生成词云 ----------------------
    st.subheader("☁️ 衔接词互动词云")
    try:
        # 简单提取衔接词
        words = []
        for line in result.split("\n"):
            if any(key in line for key in ["递进", "转折", "因果", "举例", "总结"]):
                line = line.replace("：", ":").replace(",", " ")
                parts = line.split(":")[-1].strip()
                words.extend([w.strip() for w in parts.split() if w.strip()])

        # 生成词云
        if words:
            wc = WordCloud(
                width=800, height=400,
                background_color="white",
                font_path=None
            ).generate(" ".join(words))

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.info("未提取到足够衔接词，无法生成词云")
    except:
        st.info("词云生成失败")
