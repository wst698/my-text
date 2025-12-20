# 导入所需库
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os  # 用于路径校验和容错

# ---------------------- 全局配置：仅保留基础页面设置 ----------------------
st.set_page_config(
    page_title="学生成绩分析与预测系统",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- 全局变量：统一列名定义 ----------------------
COLUMNS = {
    "major": "专业",
    "gender": "性别",
    "midterm": "期中考试分数",
    "final": "期末考试分数",
    "study_hour": "每周学习时长（小时）",
    "attendance": "上课出勤率",
    "student_id": "学号"
}

# 🔥 核心修改：匹配截图中的photo文件夹路径（本地+云端相对路径）
# 要求：需将photo文件夹上传到GitHub仓库根目录
LOCAL_IMAGES = {
    "preview": "photo/功能预览图.png",
    "excellent": "photo/很棒哦.jpg",  # 截图中对应的文件名
    "good": "photo/继续努力.jpg",
    "poor": "photo/要加强学习.jpg"
}

# 侧边栏调试：检查云端photo文件夹是否存在
st.sidebar.markdown("### 📝 路径调试（云端）")
st.sidebar.write("仓库根目录内容：", os.listdir("."))
if os.path.exists("photo"):
    st.sidebar.write("photo文件夹内容：", os.listdir("photo"))
else:
    st.sidebar.warning("❌ 未找到photo文件夹！")

# ---------------------- 1. 数据加载函数 ----------------------
@st.cache_data
def load_local_data():
    """加载本地学生数据CSV文件，并处理异常情况"""
    csv_path = "student_data_adjusted_rounded.csv"
    try:
        df = pd.read_csv(csv_path)
        missing_cols = [col for col in COLUMNS.values() if col not in df.columns]
        if missing_cols:
            st.error(f"❌ CSV缺少必要列：{missing_cols}")
            st.stop()
        return df
    except FileNotFoundError:
        st.error(f"❌ 未找到CSV文件：{csv_path}")
        st.stop()
    except Exception as e:
        st.error(f"❌ 数据加载失败：{str(e)}")
        st.stop()

df = load_local_data()

# ---------------------- 2. 侧边栏导航 ----------------------
st.sidebar.title("🎯 导航菜单")
page = st.sidebar.radio(
    "选择功能页面",
    ["项目概述", "专业数据分析", "成绩预测"],
    index=0,
    key="main_nav"
)

# ---------------------- 3. 页面1：项目概述 ----------------------
if page == "项目概述":
    st.title("📚 学生成绩分析与预测系统")
    st.markdown("---")

    # 创建左右分栏
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("📋 项目概述")
        st.write(f"""
        本系统基于 {len(df)} 条真实学生数据构建，覆盖 {len(df[COLUMNS['major']].unique())} 个专业，
        整合「学习时长、出勤率、期中成绩」等核心指标，实现多维度数据分析与期末成绩智能预测。
        """)
        
        st.markdown("#### ✨ 核心功能")
        st.markdown("""
        - 📊 多维度分析 | 🎯 精准洞察 | 📈 可视化呈现
        - 🤖 智能预测 | ⚠️ 风险预警 | 📝 个性化建议
        """)
    
    with col_right:
        st.subheader("📸 功能预览")
        # 容错处理：图片不存在时显示提示
        if os.path.exists(LOCAL_IMAGES["preview"]):
            st.image(LOCAL_IMAGES["preview"], use_container_width=True)
        else:
            st.warning(f"⚠️ 功能预览图缺失：{LOCAL_IMAGES['preview']}")
            st.info("请检查GitHub仓库的photo文件夹是否上传该图片")

    st.markdown("---")

    st.subheader("🎯 项目目标")
    goal_cols = st.columns(3)
    with goal_cols[0]:
        st.markdown("#### 📊 数据可视化分析")
        st.markdown("整合数据、展示差异、挖掘影响因素")
    
    with goal_cols[1]:
        st.markdown("#### 🎯 精准学情洞察")
        st.markdown("分析行为相关性、识别学生群体")
    
    with goal_cols[2]:
        st.markdown("#### 🤖 智能成绩预测")
        st.markdown("预测成绩、预警风险、提供建议")

    st.markdown("---")

    st.subheader("🔧 技术架构")
    tech_cols = st.columns(4)
    tech_info = [
        ("前端框架", "Streamlit\n快速构建Web界面"),
        ("数据处理", "Pandas + NumPy\n数据清洗与计算"),
        ("可视化", "Plotly\n交互式图表展示"),
        ("预测模型", "Scikit-Learn\n线性回归预测")
    ]
    for idx, (title, desc) in enumerate(tech_info):
        with tech_cols[idx]:
            st.markdown(f"**{title}**")
            st.markdown(desc)

# ---------------------- 4. 页面2：专业数据分析 ----------------------
elif page == "专业数据分析":
    st.title("📊 专业数据分析")
    st.markdown(f"*基于 {len(df)} 条数据计算 | 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    st.markdown("---")

    st.subheader("1. 👥 各专业性别分布")
    gender_cols = st.columns([2, 1])
    gender_count = df.groupby([COLUMNS['major'], COLUMNS['gender']]).size().unstack(fill_value=0)
    gender_ratio = gender_count.div(gender_count.sum(axis=1), axis=0).round(4)
    
    with gender_cols[0]:
        fig_gender = go.Figure()
        fig_gender.add_trace(go.Bar(x=gender_ratio.index, y=gender_ratio["男"], name="男性比例", marker_color="#4A90E2", opacity=0.8))
        fig_gender.add_trace(go.Bar(x=gender_ratio.index, y=gender_ratio["女"], name="女性比例", marker_color="#FF6B8B", opacity=0.8))
        fig_gender.update_layout(barmode="group", yaxis_title="比例", yaxis_tickformat=".2%", height=400, template="plotly_white", legend=dict(orientation="h", y=1.02, x=1))
        st.plotly_chart(fig_gender, use_container_width=True)
    
    with gender_cols[1]:
        gender_table = gender_ratio.reset_index()
        gender_table["男"] = (gender_table["男"] * 100).round(2).astype(str) + "%"
        gender_table["女"] = (gender_table["女"] * 100).round(2).astype(str) + "%"
        st.markdown("**各专业性别比例表**")
        st.dataframe(gender_table.set_index(COLUMNS['major']), use_container_width=True)

    st.markdown("---")

    st.subheader("2. 📈 各专业核心学习指标")
    study_cols = st.columns([2, 1])
    study_metrics = df.groupby(COLUMNS['major']).agg({
        COLUMNS['midterm']: "mean", COLUMNS['final']: "mean",
        COLUMNS['study_hour']: "mean", COLUMNS['attendance']: "mean"
    }).round(2).reset_index()
    
    with study_cols[0]:
        fig_study = go.Figure()
        fig_study.add_trace(go.Scatter(x=study_metrics[COLUMNS['major']], y=study_metrics[COLUMNS['midterm']], name="期中平均分数", line=dict(color="#2D5B99", width=3)))
        fig_study.add_trace(go.Scatter(x=study_metrics[COLUMNS['major']], y=study_metrics[COLUMNS['final']], name="期末平均分数", line=dict(color="#FF6B8B", width=3)))
        fig_study.update_layout(yaxis_title="平均分数", height=400, template="plotly_white", legend=dict(orientation="h", y=1.02, x=1))
        st.plotly_chart(fig_study, use_container_width=True)
    
    with study_cols[1]:
        st.markdown("**各专业核心指标表**")
        st.dataframe(
            study_metrics.set_index(COLUMNS['major']).rename(columns={
                COLUMNS['midterm']: "期中平均分数", COLUMNS['final']: "期末平均分数",
                COLUMNS['study_hour']: "每周平均学习时长", COLUMNS['attendance']: "平均上课出勤率"
            }),
            use_container_width=True
        )

    st.markdown("---")

    st.subheader("3. 🕒 各专业上课出勤率")
    attendance_cols = st.columns([2, 1])
    attendance_metrics = df.groupby(COLUMNS['major']).agg({COLUMNS['attendance']: ["mean", "count"]}).round(4).reset_index()
    attendance_metrics.columns = [COLUMNS['major'], "平均上课出勤率", "样本数量"]
    
    with attendance_cols[0]:
        fig_attendance = px.bar(
            attendance_metrics, x=COLUMNS['major'], y="平均上课出勤率", color="平均上课出勤率",
            color_continuous_scale=px.colors.sequential.Blues, hover_data=["样本数量"],
            template="plotly_white", height=400
        )
        fig_attendance.update_layout(yaxis_title="平均上课出勤率", yaxis_tickformat=".2%", coloraxis_showscale=False)
        st.plotly_chart(fig_attendance, use_container_width=True)
    
    with attendance_cols[1]:
        attendance_table = attendance_metrics.copy()
        attendance_table["平均上课出勤率"] = (attendance_table["平均上课出勤率"] * 100).round(2).astype(str) + "%"
        st.markdown("**各专业出勤率表（含样本数）**")
        st.dataframe(attendance_table.set_index(COLUMNS['major']), use_container_width=True)

    st.markdown("---")

    st.subheader("4. 🔍 目标专业深度分析")
    target_major = st.selectbox(
        "选择要分析的专业",
        options=df[COLUMNS['major']].unique(),
        index=df[COLUMNS['major']].unique().tolist().index("大数据管理") if "大数据管理" in df[COLUMNS['major']].unique() else 0,
        key="target_major"
    )
    major_data = df[df[COLUMNS['major']] == target_major].copy()
    
    st.markdown("#### 📊 核心指标概览")
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("平均上课出勤率", f"{(major_data[COLUMNS['attendance']].mean() * 100).round(1)}%")
    with metric_cols[1]:
        st.metric("平均期末分数", f"{major_data[COLUMNS['final']].mean().round(1)} 分")
    with metric_cols[2]:
        pass_rate = (major_data[COLUMNS['final']] >= 60).sum() / len(major_data) * 100
        st.metric("期末通过率", f"{pass_rate.round(1)}%")
    with metric_cols[3]:
        st.metric("平均学习时长", f"{major_data[COLUMNS['study_hour']].mean().round(1)} 小时/周")
    
    st.markdown("#### 📉 数据分布详情")
    dist_cols = st.columns(2)
    with dist_cols[0]:
        fig_score = px.histogram(major_data, x=COLUMNS['final'], nbins=15, color_discrete_sequence=["#4A90E2"], template="plotly_white", title=f"{target_major} - 期末分数分布")
        fig_score.update_layout(height=300)
        st.plotly_chart(fig_score, use_container_width=True)
    
    with dist_cols[1]:
        fig_hour = px.box(major_data, y=COLUMNS['study_hour'], color_discrete_sequence=["#2D5B99"], template="plotly_white", title=f"{target_major} - 学习时长分布")
        fig_hour.update_layout(height=300)
        st.plotly_chart(fig_hour, use_container_width=True)

# ---------------------- 5. 页面3：成绩预测 ----------------------
else:
    st.title("🔮 期末成绩预测")
    st.markdown("---")
    st.markdown("请输入学生的学习信息，系统将基于历史数据预测期末成绩并提供个性化建议")

    with st.form(key="prediction_form", clear_on_submit=False):
        # 第一行分栏
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.text_input("学号", value="20230001", key="student_id_input")
        with col2:
            pred_study_hour = st.slider(
                COLUMNS['study_hour'],
                min_value=int(df[COLUMNS['study_hour']].min()),
                max_value=int(df[COLUMNS['study_hour']].max()),
                value=int(df[COLUMNS['study_hour']].mean()),
                key="pred_study_hour"
            )

        # 第二行分栏
        col3, col4 = st.columns(2)
        with col3:
            pred_gender = st.radio(COLUMNS['gender'], ["男", "女"], key="pred_gender")
        with col4:
            pred_attendance = st.slider(
                COLUMNS['attendance'],
                min_value=round(df[COLUMNS['attendance']].min(), 2),
                max_value=round(df[COLUMNS['attendance']].max(), 2),
                value=round(df[COLUMNS['attendance']].mean(), 2),
                step=0.01,
                format="%.2f",
                key="pred_attendance"
            )

        # 第三行分栏
        col5, col6 = st.columns(2)
        with col5:
            pred_major = st.selectbox(COLUMNS['major'], df[COLUMNS['major']].unique(), key="pred_major")
        with col6:
            pred_midterm = st.slider(
                COLUMNS['midterm'],
                min_value=int(df[COLUMNS['midterm']].min()),
                max_value=int(df[COLUMNS['midterm']].max()),
                value=int(df[COLUMNS['midterm']].mean()),
                key="pred_midterm"
            )

        submit_btn = st.form_submit_button("🚀 预测期末成绩", type="primary", use_container_width=True)

    if submit_btn:
        # 预测公式
        predicted_final = (
            0.65 * pred_midterm
            + 18 * pred_attendance
            + 0.15 * pred_study_hour
            + 2.5
        )
        predicted_final = max(0, min(100, round(predicted_final, 1)))

        st.markdown("---")
        with st.expander("📊 预测结果详情", expanded=True):
            st.success(f"### 预测期末成绩：{predicted_final} 分")
            
            st.markdown("#### 📋 个性化学习建议")
            if predicted_final >= 85:
                st.success("""
                ✅ 预测等级：优秀
                建议：保持当前学习节奏，可尝试参与学科竞赛、科研项目等拓展专业能力，
                重点突破高阶知识点，进一步提升竞争力。
                """)
                st.markdown("#### 💖 专属鼓励")
                if os.path.exists(LOCAL_IMAGES["excellent"]):
                    st.image(LOCAL_IMAGES["excellent"], width=300)
                else:
                    st.warning(f"⚠️ 鼓励图片缺失：{LOCAL_IMAGES['excellent']}")
                st.markdown("很棒哦！继续保持🌟")
                
            elif predicted_final >= 70:
                st.info("""
                ✅ 预测等级：良好
                建议：针对性复盘期中错题，聚焦薄弱知识点强化训练，
                每周可增加2-3小时学习时长，有望冲击优秀等级。
                """)
                st.markdown("#### 💪 专属鼓励")
                if os.path.exists(LOCAL_IMAGES["good"]):
                    st.image(LOCAL_IMAGES["good"], width=300)
                else:
                    st.warning(f"⚠️ 鼓励图片缺失：{LOCAL_IMAGES['good']}")
                st.markdown("继续努力！优秀就在前方🚀")
                
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
                if os.path.exists(LOCAL_IMAGES["poor"]):
                    st.image(LOCAL_IMAGES["poor"], width=300)
                else:
                    st.warning(f"⚠️ 鼓励图片缺失：{LOCAL_IMAGES['poor']}")
                st.markdown("要加强学习啦！现在努力还不晚💡")
            
            st.markdown("#### 📈 参考数据")
            ref_data = df[df[COLUMNS['major']] == pred_major]
            st.write(f"- 同专业平均期末分数：{ref_data[COLUMNS['final']].mean().round(1)} 分")
            st.write(f"- 同专业期末通过率：{((ref_data[COLUMNS['final']] >= 60).sum() / len(ref_data) * 100).round(1)}%")