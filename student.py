# 导入所需库：
# streamlit：快速构建Web应用的核心库
# pandas：用于数据处理与分析
# plotly.express/graph_objects：创建交互式可视化图表
# numpy：数值计算工具
# datetime：处理日期时间
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# ---------------------- 全局配置：马卡龙淡蓝主题 + 统一样式 ----------------------
# 设置页面基础属性：标题、布局、侧边栏初始状态
st.set_page_config(
    page_title="学生成绩分析与预测系统",  # 浏览器标签页显示的标题
    layout="wide",  # 宽布局（充分利用页面空间）
    initial_sidebar_state="expanded"  # 侧边栏默认展开
)

# 注入全局CSS样式，自定义页面外观（统一主题风格、优化组件样式）
st.markdown("""
    <style>
    /* 页面基础样式 - 马卡龙淡蓝色主背景 */
    .stApp {
        background-color: #E6F4FF;  /* 主背景色：淡蓝 */
        color: #333333;  /* 文字主色：深灰（保证可读性） */
    }
    /* 侧边栏样式 - 稍深的淡蓝色 */
    .css-1d391kg, .stSidebar {
        background-color: #D1E7FF !important;
    }
    /* 标题样式 - 深蓝色更醒目 */
    h1, h2, h3, h4, h5 {
        color: #2D5B99;
        font-weight: 600;
    }
    /* 文本样式 - 深灰保证可读性 */
    p, div, span, li {
        color: #444444;
    }
    /* 卡片/分栏样式 - 白色背景+浅蓝边框（提升层次感） */
    .card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #B8D4EB;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* 技术架构栏样式 - 淡蓝背景（区分模块） */
    .tech-bar {
        background-color: #D1E7FF;
        padding: 15px;
        border-radius: 6px;
        text-align: center;
        height: 100%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* 按钮样式 - 柔和蓝色系（hover时加深） */
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 8px 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #357ABD;
    }
    /* 表单组件样式 - 白色背景+浅灰边框（统一风格） */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, 
    .stSlider>div>div>div, .stRadio>div>div {
        background-color: #FFFFFF;
        color: #333333;
        border: 1px solid #CCCCCC;
        border-radius: 4px;
    }
    /* 指标卡片样式 - 白色背景+浅蓝边框（突出关键数据） */
    .stMetric {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #B8D4EB;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* 展开栏样式 - 白色背景+浅蓝边框（优化内容容器） */
    .stExpander {
        background-color: #FFFFFF;
        border: 1px solid #B8D4EB;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* 滑块样式优化 - 调整滑块颜色与轨道色 */
    .stSlider .thumb {
        background-color: #4A90E2 !important;
    }
    .stSlider .track {
        background-color: #E0E0E0 !important;
    }
    /* 图片组件样式 - 圆角+阴影+居中（优化视觉效果） */
    .stImage > img {
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 10px 0;
        display: block;
        margin-left: auto;
        margin-right: auto; /* 图片居中显示 */
    }
    /* 图片说明文字样式 - 居中+深蓝色（配合图片） */
    .img-caption {
        text-align: center;
        color: #2D5B99;
        font-size: 14px;
        margin-top: 8px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)  # 允许解析HTML代码（使CSS生效）


# ---------------------- 全局变量：统一列名定义 ----------------------
# 定义数据列名的映射字典，避免硬编码、提升代码可维护性
COLUMNS = {
    "major": "专业",
    "gender": "性别",
    "midterm": "期中考试分数",
    "final": "期末考试分数",
    "study_hour": "每周学习时长（小时）",
    "attendance": "上课出勤率",
    "student_id": "学号"
}

# 本地图片路径配置：存储各功能模块所需的图片路径
LOCAL_IMAGES = {
    "preview": r"D:/streamlit_env/photo/功能预览图.png",  # 项目概述页的功能预览图
    "excellent": r"D:/streamlit_env/photo/很棒哦.jpg",     # 预测"优秀"时的鼓励图片
    "good": r"D:/streamlit_env/photo/继续努力.jpg",       # 预测"良好"时的鼓励图片
    "poor": r"D:/streamlit_env/photo/要加强学习.jpg"      # 预测"及格/不及格"时的鼓励图片
}


# ---------------------- 1. 数据加载函数 ----------------------
# @st.cache_data：缓存数据，避免重复加载（提升页面性能）
@st.cache_data
def load_local_data():
    """
    加载本地学生数据CSV文件，并处理异常情况
    返回：加载完成的学生数据DataFrame
    """
    csv_path = "student_data_adjusted_rounded.csv"  # 数据文件的本地路径
    try:
        # 读取CSV文件为DataFrame
        df = pd.read_csv(csv_path)
        # 检查数据是否包含所有必要列（避免后续代码报错）
        missing_cols = [col for col in COLUMNS.values() if col not in df.columns]
        if missing_cols:
            st.error(f"❌ CSV缺少必要列：{missing_cols}")  # 提示缺失列
            st.stop()  # 终止程序运行（避免后续错误）
        return df
    except FileNotFoundError:
        st.error(f"❌ 未找到CSV文件：{csv_path}")  # 提示文件不存在
        st.stop()
    except Exception as e:
        st.error(f"❌ 数据加载失败：{str(e)}")  # 提示其他加载错误
        st.stop()

# 调用数据加载函数，获取学生数据
df = load_local_data()


# ---------------------- 2. 侧边栏导航 ----------------------
# 设置侧边栏标题
st.sidebar.title("🎯 导航菜单")
# 创建侧边栏单选按钮，用于切换不同功能页面
page = st.sidebar.radio(
    "选择功能页面",  # 单选按钮的提示文字
    ["项目概述", "专业数据分析", "成绩预测"],  # 可选的功能页面列表
    index=0,  # 默认选中第一个页面（项目概述）
    key="main_nav"  # 组件唯一标识（避免与其他组件冲突）
)


# ---------------------- 3. 页面1：项目概述 ----------------------
if page == "项目概述":
    # 设置页面主标题
    st.title("📚 学生成绩分析与预测系统")
    st.markdown("---")  # 添加分隔线（视觉上区分模块）

    # 创建左右分栏（比例2:1）
    col_left, col_right = st.columns([2, 1])
    with col_left:  # 左侧栏：项目概述与核心功能
        # 使用自定义CSS的"card"样式包裹内容（提升美观度）
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 项目概述")
        # 展示项目基本信息（数据量、覆盖专业数、核心能力）
        st.write(f"""
        本系统基于 {len(df)} 条真实学生数据构建，覆盖 {len(df[COLUMNS['major']].unique())} 个专业，
        整合「学习时长、出勤率、期中成绩」等核心指标，实现多维度数据分析与期末成绩智能预测。
        """)
        
        st.markdown("#### ✨ 核心功能")
        # 列出系统的核心功能（简洁展示）
        st.markdown("""
        - 📊 多维度分析 | 🎯 精准洞察 | 📈 可视化呈现
        - 🤖 智能预测 | ⚠️ 风险预警 | 📝 个性化建议
        """)
        st.markdown('</div>', unsafe_allow_html=True)  # 关闭"card"样式
    
    with col_right:  # 右侧栏：功能预览图
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📸 功能预览")
        # 展示本地功能预览图（自适应容器宽度）
        st.image(LOCAL_IMAGES["preview"], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")  # 分隔线

    st.subheader("🎯 项目目标")
    # 创建3列布局，分别展示不同的项目目标
    goal_cols = st.columns(3)
    with goal_cols[0]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📊 数据可视化分析")
        st.markdown("整合数据、展示差异、挖掘影响因素")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with goal_cols[1]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 🎯 精准学情洞察")
        st.markdown("分析行为相关性、识别学生群体")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with goal_cols[2]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 🤖 智能成绩预测")
        st.markdown("预测成绩、预警风险、提供建议")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")  # 分隔线

    st.subheader("🔧 技术架构")
    # 创建4列布局，展示系统的技术栈
    tech_cols = st.columns(4)
    # 技术架构信息：（标题，描述）
    tech_info = [
        ("前端框架", "Streamlit<br>快速构建Web界面"),
        ("数据处理", "Pandas + NumPy<br>数据清洗与计算"),
        ("可视化", "Plotly<br>交互式图表展示"),
        ("预测模型", "Scikit-Learn<br>线性回归预测")
    ]
    # 循环生成每个技术栈的展示栏
    for idx, (title, desc) in enumerate(tech_info):
        with tech_cols[idx]:
            st.markdown('<div class="tech-bar">', unsafe_allow_html=True)
            st.markdown(f"**{title}**")  # 技术标题（加粗突出）
            st.markdown(desc, unsafe_allow_html=True)  # 技术描述（支持HTML换行）
            st.markdown('</div>', unsafe_allow_html=True)


# ---------------------- 4. 页面2：专业数据分析 ----------------------
elif page == "专业数据分析":
    st.title("📊 专业数据分析")
    # 展示数据来源与更新时间
    st.markdown(f"*基于 {len(df)} 条数据计算 | 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    st.markdown("---")  # 分隔线

    st.subheader("1. 👥 各专业性别分布")
    # 创建2列布局（图表+表格）
    gender_cols = st.columns([2, 1])
    # 按"专业+性别"分组，统计各组合的学生数量（缺失值填充为0）
    gender_count = df.groupby([COLUMNS['major'], COLUMNS['gender']]).size().unstack(fill_value=0)
    # 计算各专业的性别比例（按行求和后取占比）
    gender_ratio = gender_count.div(gender_count.sum(axis=1), axis=0).round(4)
    
    with gender_cols[0]:  # 左侧：性别比例分组柱状图
        fig_gender = go.Figure()
        # 添加"男性比例"柱状图
        fig_gender.add_trace(go.Bar(x=gender_ratio.index, y=gender_ratio["男"], name="男性比例", marker_color="#4A90E2", opacity=0.8))
        # 添加"女性比例"柱状图
        fig_gender.add_trace(go.Bar(x=gender_ratio.index, y=gender_ratio["女"], name="女性比例", marker_color="#FF6B8B", opacity=0.8))
        # 配置图表布局：分组显示、Y轴标题、百分比格式、高度、主题等
        fig_gender.update_layout(barmode="group", yaxis_title="比例", yaxis_tickformat=".2%", height=400, template="plotly_white", legend=dict(orientation="h", y=1.02, x=1))
        # 展示图表（自适应容器宽度）
        st.plotly_chart(fig_gender, use_container_width=True)
    
    with gender_cols[1]:  # 右侧：性别比例表格
        gender_table = gender_ratio.reset_index()
        # 将比例转换为"百分比+%"的格式（提升可读性）
        gender_table["男"] = (gender_table["男"] * 100).round(2).astype(str) + "%"
        gender_table["女"] = (gender_table["女"] * 100).round(2).astype(str) + "%"
        st.markdown("**各专业性别比例表**")
        # 展示表格（以"专业"为索引）
        st.dataframe(gender_table.set_index(COLUMNS['major']), use_container_width=True)

    st.markdown("---")  # 分隔线

    st.subheader("2. 📈 各专业核心学习指标")
    # 创建2列布局（图表+表格）
    study_cols = st.columns([2, 1])
    # 按"专业"分组，计算核心指标的平均值（保留2位小数）
    study_metrics = df.groupby(COLUMNS['major']).agg({
        COLUMNS['midterm']: "mean", COLUMNS['final']: "mean",
        COLUMNS['study_hour']: "mean", COLUMNS['attendance']: "mean"
    }).round(2).reset_index()
    
    with study_cols[0]:  # 左侧：期中/期末平均分折线图
        fig_study = go.Figure()
        # 添加"期中平均分数"折线
        fig_study.add_trace(go.Scatter(x=study_metrics[COLUMNS['major']], y=study_metrics[COLUMNS['midterm']], name="期中平均分数", line=dict(color="#2D5B99", width=3)))
        # 添加"期末平均分数"折线
        fig_study.add_trace(go.Scatter(x=study_metrics[COLUMNS['major']], y=study_metrics[COLUMNS['final']], name="期末平均分数", line=dict(color="#FF6B8B", width=3)))
        # 配置图表布局：Y轴标题、高度、主题等
        fig_study.update_layout(yaxis_title="平均分数", height=400, template="plotly_white", legend=dict(orientation="h", y=1.02, x=1))
        st.plotly_chart(fig_study, use_container_width=True)
    
    with study_cols[1]:  # 右侧：核心指标表格
        st.markdown("**各专业核心指标表**")
        # 展示表格（重命名列名，提升可读性）
        st.dataframe(
            study_metrics.set_index(COLUMNS['major']).rename(columns={
                COLUMNS['midterm']: "期中平均分数", COLUMNS['final']: "期末平均分数",
                COLUMNS['study_hour']: "每周平均学习时长", COLUMNS['attendance']: "平均上课出勤率"
            }),
            use_container_width=True
        )

    st.markdown("---")  # 分隔线

    st.subheader("3. 🕒 各专业上课出勤率")
    # 创建2列布局（图表+表格）
    attendance_cols = st.columns([2, 1])
    # 按"专业"分组，计算出勤率的平均值和样本数量（保留4位小数）
    attendance_metrics = df.groupby(COLUMNS['major']).agg({COLUMNS['attendance']: ["mean", "count"]}).round(4).reset_index()
    attendance_metrics.columns = [COLUMNS['major'], "平均上课出勤率", "样本数量"]  # 重命名列名
    
    with attendance_cols[0]:  # 左侧：出勤率柱状图（带颜色渐变）
        fig_attendance = px.bar(
            attendance_metrics, x=COLUMNS['major'], y="平均上课出勤率", color="平均上课出勤率",
            color_continuous_scale=px.colors.sequential.Blues, hover_data=["样本数量"],
            template="plotly_white", height=400
        )
        # 配置图表布局：Y轴标题、百分比格式、隐藏颜色刻度
        fig_attendance.update_layout(yaxis_title="平均上课出勤率", yaxis_tickformat=".2%", coloraxis_showscale=False)
        st.plotly_chart(fig_attendance, use_container_width=True)
    
    with attendance_cols[1]:  # 右侧：出勤率表格（含样本数）
        attendance_table = attendance_metrics.copy()
        # 将出勤率转换为"百分比+%"的格式
        attendance_table["平均上课出勤率"] = (attendance_table["平均上课出勤率"] * 100).round(2).astype(str) + "%"
        st.markdown("**各专业出勤率表（含样本数）**")
        st.dataframe(attendance_table.set_index(COLUMNS['major']), use_container_width=True)

    st.markdown("---")  # 分隔线

    st.subheader("4. 🔍 目标专业深度分析")
    # 下拉选择要分析的专业（默认选中"大数据管理"，若无则选第一个专业）
    target_major = st.selectbox(
        "选择要分析的专业",
        options=df[COLUMNS['major']].unique(),
        index=df[COLUMNS['major']].unique().tolist().index("大数据管理") if "大数据管理" in df[COLUMNS['major']].unique() else 0,
        key="target_major"
    )
    # 筛选出目标专业的学生数据
    major_data = df[df[COLUMNS['major']] == target_major].copy()
    
    st.markdown("#### 📊 核心指标概览")
    # 创建4列布局，展示目标专业的核心指标
    metric_cols = st.columns(4)
    with metric_cols[0]:
        # 展示"平均上课出勤率"（百分比格式，保留1位小数）
        st.metric("平均上课出勤率", f"{(major_data[COLUMNS['attendance']].mean() * 100).round(1)}%")
    with metric_cols[1]:
        # 展示"平均期末分数"（保留1位小数）
        st.metric("平均期末分数", f"{major_data[COLUMNS['final']].mean().round(1)} 分")
    with metric_cols[2]:
        # 计算并展示"期末通过率"（百分比格式，保留1位小数）
        pass_rate = (major_data[COLUMNS['final']] >= 60).sum() / len(major_data) * 100
        st.metric("期末通过率", f"{pass_rate.round(1)}%")
    with metric_cols[3]:
        # 展示"平均学习时长"（保留1位小数）
        st.metric("平均学习时长", f"{major_data[COLUMNS['study_hour']].mean().round(1)} 小时/周")
    
    st.markdown("#### 📉 数据分布详情")
    # 创建2列布局，展示目标专业的分数与学习时长分布
    dist_cols = st.columns(2)
    with dist_cols[0]:
        # 期末分数直方图（分15个区间）
        fig_score = px.histogram(major_data, x=COLUMNS['final'], nbins=15, color_discrete_sequence=["#4A90E2"], template="plotly_white", title=f"{target_major} - 期末分数分布")
        fig_score.update_layout(height=300)  # 设置图表高度
        st.plotly_chart(fig_score, use_container_width=True)
    
    with dist_cols[1]:
        # 学习时长箱线图（展示分布范围与异常值）
        fig_hour = px.box(major_data, y=COLUMNS['study_hour'], color_discrete_sequence=["#2D5B99"], template="plotly_white", title=f"{target_major} - 学习时长分布")
        fig_hour.update_layout(height=300)
        st.plotly_chart(fig_hour, use_container_width=True)


# ---------------------- 5. 页面3：成绩预测 ----------------------
else:
    st.title("🔮 期末成绩预测")
    st.markdown("---")
    # 提示用户输入信息的说明文字
    st.markdown("请输入学生的学习信息，系统将基于历史数据预测期末成绩并提供个性化建议")

    # 创建表单（提交后不自动清空内容）
    with st.form(key="prediction_form", clear_on_submit=False):
        # 第一行分栏：学号 + 每周学习时长
        col1, col2 = st.columns(2)
        with col1:
            # 学号输入框（默认值为"20230001"）
            student_id = st.text_input("学号", value="20230001", key="student_id_input")
        with col2:
            # 每周学习时长滑块（范围：数据的最小/最大值，默认值：数据平均值）
            pred_study_hour = st.slider(
                COLUMNS['study_hour'],
                min_value=int(df[COLUMNS['study_hour']].min()),
                max_value=int(df[COLUMNS['study_hour']].max()),
                value=int(df[COLUMNS['study_hour']].mean()),
                key="pred_study_hour"
            )

        # 第二行分栏：性别 + 上课出勤率
        col3, col4 = st.columns(2)
        with col3:
            # 性别单选按钮（选项：男/女）
            pred_gender = st.radio(COLUMNS['gender'], ["男", "女"], key="pred_gender")
        with col4:
            # 上课出勤率滑块（范围：数据的最小/最大值，默认值：数据平均值，步长0.01）
            pred_attendance = st.slider(
                COLUMNS['attendance'],
                min_value=round(df[COLUMNS['attendance']].min(), 2),
                max_value=round(df[COLUMNS['attendance']].max(), 2),
                value=round(df[COLUMNS['attendance']].mean(), 2),
                step=0.01,
                format="%.2f",
                key="pred_attendance"
            )

        # 第三行分栏：专业 + 期中考试分数
        col5, col6 = st.columns(2)
        with col5:
            # 专业下拉选择框（选项为数据中的所有专业）
            pred_major = st.selectbox(COLUMNS['major'], df[COLUMNS['major']].unique(), key="pred_major")
        with col6:
            # 期中考试分数滑块（范围：数据的最小/最大值，默认值：数据平均值）
            pred_midterm = st.slider(
                COLUMNS['midterm'],
                min_value=int(df[COLUMNS['midterm']].min()),
                max_value=int(df[COLUMNS['midterm']].max()),
                value=int(df[COLUMNS['midterm']].mean()),
                key="pred_midterm"
            )

        # 表单提交按钮（主按钮样式，自适应容器宽度）
        submit_btn = st.form_submit_button("🚀 预测期末成绩", type="primary", use_container_width=True)

    # 当用户点击提交按钮后，执行预测逻辑
    if submit_btn:
        # 期末成绩预测公式（基于历史数据拟合的线性模型）
        predicted_final = (
            0.65 * pred_midterm  # 期中成绩的权重
            + 18 * pred_attendance  # 出勤率的权重
            + 0.15 * pred_study_hour  # 每周学习时长的权重
            + 2.5  # 基础分（调整模型偏移）
        )
        # 将预测分数限制在0-100分之间，并保留1位小数
        predicted_final = max(0, min(100, round(predicted_final, 1)))

        st.markdown("---")
        # 展开栏展示预测结果（默认展开）
        with st.expander("📊 预测结果详情", expanded=True):
            st.success(f"### 预测期末成绩：{predicted_final} 分")  # 展示预测分数
            
            st.markdown("#### 📋 个性化学习建议")
            # 根据预测分数的不同区间，给出对应的学习建议
            if predicted_final >= 85:
                st.success("""
                ✅ 预测等级：优秀
                建议：保持当前学习节奏，可尝试参与学科竞赛、科研项目等拓展专业能力，
                重点突破高阶知识点，进一步提升竞争力。
                """)
                st.markdown("#### 💖 专属鼓励")
                st.image(LOCAL_IMAGES["excellent"], width=300)  # 展示"优秀"对应的鼓励图
                st.markdown('<p class="img-caption">很棒哦！继续保持🌟</p>', unsafe_allow_html=True)
                
            elif predicted_final >= 70:
                st.info("""
                ✅ 预测等级：良好
                建议：针对性复盘期中错题，聚焦薄弱知识点强化训练，
                每周可增加2-3小时学习时长，有望冲击优秀等级。
                """)
                st.markdown("#### 💪 专属鼓励")
                st.image(LOCAL_IMAGES["good"], width=300)  # 展示"良好"对应的鼓励图
                st.markdown('<p class="img-caption">继续努力！优秀就在前方🚀</p>', unsafe_allow_html=True)
                
            else:
                if predicted_final >= 60:
                    st.warning("""
                    ⚠️ 预测等级：及格
                    建议：立即提升上课出勤率至90%以上，每周学习时长增加至20小时以上，
                    重点复习期中低分章节，主动向老师/同学请教疑难问题。
                    """)
                else:
                    st.error("""
                    ❌ 预测等级：不及格风险
                    紧急建议：
                    1. 出勤率提升至95%以上，杜绝旷课/迟到；
                    2. 每天增加2小时专项学习时间；
                    3. 制定错题本，逐一攻克薄弱点；
                    4. 主动寻求老师一对一辅导。
                    """)
                st.markdown("#### 📝 专属鼓励")
                st.image(LOCAL_IMAGES["poor"], width=300)  # 展示"及格/不及格"对应的鼓励图
                st.markdown('<p class="img-caption">要加强学习啦！现在努力还不晚💡</p>', unsafe_allow_html=True)
            
            st.markdown("#### 📈 参考数据")
            # 筛选目标专业的参考数据
            ref_data = df[df[COLUMNS['major']] == pred_major]
            # 展示同专业的平均期末分数与通过率
            st.write(f"- 同专业平均期末分数：{ref_data[COLUMNS['final']].mean().round(1)} 分")
            st.write(f"- 同专业期末通过率：{((ref_data[COLUMNS['final']] >= 60).sum() / len(ref_data) * 100).round(1)}%")