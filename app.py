import streamlit as st
import dashscope
from dashscope import MultiModalConversation
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64

# ---------------------- 页面配置 ----------------------
st.set_page_config(page_title="英语课文结构分析工具", layout="wide")
st.title("📖 AI英语课文结构与衔接词分析工具")
st.markdown("### 上传课文图片 → AI自动分析结构 + 生成衔接词词云")

# ---------------------- API KEY 设置 ----------------------
try:
    api_key = st.secrets["TONGYI_API_KEY"]
    dashscope.api_key = api_key
except:
    st.warning("请在Streamlit Secrets中正确设置 TONGYI_API_KEY")
    st.stop()

# ---------------------- 上传课文图片 ----------------------
uploaded_file = st.file_uploader("上传课文图片（jpg/png）", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # 显示图片
    st.image(uploaded_file, caption="已上传的课文", use_column_width=True)

    # 图片转 base64
    bytes_data = uploaded_file.getvalue()
    base64_data = base64.b64encode(bytes_data).decode("utf-8")

    # ---------------------- AI 分析 ----------------------
    with st.spinner("⌛ AI正在分析课文..."):
        try:
            response = MultiModalConversation.call(
                model="qwen-vl-plus",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"text": "请分析这张英语课文图片，完成以下任务：\n1. 提取课文完整文本\n2. 提炼文章写作结构（主题句+观点+细节）\n3. 提取所有衔接词，按递进/转折/因果/举例/总结分类，并给出例句"},
                            {"image": f"data:image/jpeg;base64,{base64_data}"}
                        ]
                    }
                ]
            )
            result = response["output"]["choices"][0]["message"]["content"][0]["text"]
        except Exception as e:
            st.error(f"AI调用出错：{str(e)}")
            st.stop()

    # ---------------------- 显示结果 ----------------------
    st.subheader("📋 课文结构与衔接词分析")
    st.markdown(result)

    # ---------------------- 词云生成 ----------------------
    st.subheader("☁️ 衔接词词云")
    try:
        words = []
        for line in result.split("\n"):
            if any(key in line for key in ["递进", "转折", "因果", "举例", "总结"]):
                line = line.replace("：", ":").replace(",", " ")
                parts = line.split(":")[-1].strip()
                words.extend([w.strip() for w in parts.split() if w.strip()])

        if words:
            wc = WordCloud(
                width=800, height=400,
                background_color="white"
            ).generate(" ".join(words))

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.info("未提取到足够衔接词，无法生成词云")
    except:
        st.info("词云生成失败")
