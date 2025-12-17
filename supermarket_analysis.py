import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ---------------------- 1. 页面配置 ----------------------
st.set_page_config(page_title="销售仪表板", layout="wide")
st.title("销售仪表板")


# ---------------------- 2. 模拟销售数据 ----------------------
def generate_sample_data():
    # 城市/顾客类型/性别/产品类型选项
    cities = ["太原", "临汾", "大同", "长治"]
    customer_types = ["会员用户", "普通用户"]
    genders = ["男性", "女性"]
    product_types = ["食品饮料", "运动旅行", "电子配件", "时尚配饰", "家居生活", "健康美容"]
    
    # 生成1000条模拟数据
    np.random.seed(42)
    data = {
        "city": np.random.choice(cities, 1000),
        "customer_type": np.random.choice(customer_types, 1000),
        "gender": np.random.choice(genders, 1000),
        "hour": np.random.randint(0, 24, 1000),  # 小时（0-23）
        "product_type": np.random.choice(product_types, 1000),
        "sales": np.random.randint(100, 1000, 1000),  # 单销售额
        "rating": np.random.randint(5, 10, 1000)  # 评分（5-9）
    }
    df = pd.DataFrame(data)
    return df

# 加载数据
df = generate_sample_data()


# ---------------------- 3. 侧边栏：筛选控件 ----------------------
with st.sidebar:
    st.subheader("请筛选数据：")
    
    # 城市筛选
    selected_cities = st.multiselect(
        "请选择城市：",
        options=df["city"].unique(),
        default=["太原", "临汾", "大同"]  # 默认选中示例中的城市
    )
    
    # 顾客类型筛选
    selected_types = st.multiselect(
        "请选择顾客类型：",
        options=df["customer_type"].unique(),
        default=df["customer_type"].unique()
    )
    
    # 性别筛选
    selected_genders = st.multiselect(
        "请选择性别：",
        options=df["gender"].unique(),
        default=df["gender"].unique()
    )


# ---------------------- 4. 筛选数据 ----------------------
df_filtered = df[
    (df["city"].isin(selected_cities)) &
    (df["customer_type"].isin(selected_types)) &
    (df["gender"].isin(selected_genders))
]


# ---------------------- 5. 计算核心指标 ----------------------
total_sales = df_filtered["sales"].sum()
avg_rating = df_filtered["rating"].mean().round(1)
avg_per_order = (total_sales / len(df_filtered)).round(2)


# ---------------------- 6. 指标卡片展示 ----------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.write("总销售额：")
    st.subheader(f"RMB¥{total_sales:,.0f}")
with col2:
    st.write("顾客评分的平均值：")
    st.subheader(f"{avg_rating} ⭐⭐⭐⭐⭐⭐⭐")  # 7星对应7.0分
with col3:
    st.write("每单的平均销售额：")
    st.subheader(f"RMB¥{avg_per_order:,.2f}")


# ---------------------- 7. 图表展示（核心修改：添加马卡龙浅蓝颜色） ----------------------
st.divider()  # 分隔线
col_chart1, col_chart2 = st.columns(2)

# 定义马卡龙浅蓝的色值（可根据喜好微调）
MACARON_LIGHT_BLUE = "#A8D1E7"

# 按小时划分的销售额
with col_chart1:
    st.write("按小时划分的销售额")
    hour_sales = df_filtered.groupby("hour")["sales"].sum().reset_index()
    st.bar_chart(
        hour_sales, 
        x="hour", 
        y="sales", 
        use_container_width=True,
        color=MACARON_LIGHT_BLUE  # 设置马卡龙浅蓝
    )

# 按产品类型划分的销售额
with col_chart2:
    st.write("按产品类型划分的销售额")
    product_sales = df_filtered.groupby("product_type")["sales"].sum().sort_values(ascending=False).reset_index()
    st.bar_chart(
        product_sales, 
        x="product_type", 
        y="sales", 
        use_container_width=True,
        color=MACARON_LIGHT_BLUE  # 设置马卡龙浅蓝
    )


# ---------------------- 8. 数据表格展示 ----------------------
st.divider()
st.subheader("销售数据详情表")
st.dataframe(
    df_filtered,
    use_container_width=True,
    column_config={
        "sales": st.column_config.NumberColumn("销售额", format="¥%d"),
        "rating": st.column_config.NumberColumn("顾客评分")
    }
)