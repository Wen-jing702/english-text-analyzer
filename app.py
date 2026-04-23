import streamlit as st
import dashscope
from dashscope import MultiModalConversation
import base64

# ---------------------- 页面配置 ----------------------
st.set_page_config(page_title="英语课文结构分析工具", layout="wide")
st.title("📖 AI英语课文结构分析工具")
st.markdown("### 上传课文图片 → AI自动分析结构 + 生成思维导图")

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
    with st.spinner("⌛ AI正在分析课文结构..."):
        try:
            response = MultiModalConversation.call(
                model="qwen-vl-plus",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"text": "请分析这张英语课文图片，完成以下任务：\n1. 提取课文完整文本\n2. 提炼文章写作结构，以「思维导图」的层级形式呈现（用Markdown的多级列表格式，一级标题为文章主题，二级为段落主题，三级为观点/支撑细节，四级为关键信息/例子）\n3. 提取所有衔接词，按递进/转折/因果/举例/总结分类，并给出例句"},
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
    st.subheader("📋 课文完整文本与衔接词分析")
    st.markdown(result)

    # ---------------------- 提取并展示思维导图结构 ----------------------
    st.subheader("🧠 课文写作结构思维导图")
    st.info("下面是AI提炼的课文写作结构层级，可直接用于课堂板书或讲解")

    # 解析Markdown层级结构，展示为清晰的层级
    for line in result.split("\n"):
        if line.strip() == "":
            continue
        # 一级标题（文章主题）
        if line.startswith("# "):
            st.markdown(f"### {line[2:]}")
        # 二级标题（段落主题）
        elif line.startswith("## "):
            st.markdown(f"#### {line[3:]}")
        # 三级标题/列表项（观点/细节）
        elif line.startswith("### ") or line.startswith("- "):
            st.markdown(f"- {line.split(' ', 1)[1]}")
        # 四级列表项（关键信息/例子）
        elif line.startswith("  - "):
            st.markdown(f"  - {line.split(' ', 2)[2]}")
        elif line.startswith("    - "):
            st.markdown(f"    - {line.split(' ', 3)[3]}")
