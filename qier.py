# 第8章/streamlit_predict_v2.py
import streamlit as st  # 导入Streamlit库，用于构建Web应用
import pickle  # 导入pickle库，用于加载预训练模型
import pandas as pd  # 导入Pandas库，用于数据处理

# 设置页面的标题、图标和布局
st.set_page_config(
    page_title="企鹅分类器",  # 页面标题：显示在浏览器标签栏
    page_icon=":penguin:",    # 页面图标：企鹅emoji
    layout='wide'             # 布局模式：宽屏模式（默认是居中窄屏）
)

# 自定义CSS设置马卡龙浅蓝色背景（通过markdown嵌入HTML/CSS，实现页面样式美化）
st.markdown("""
    <style>
    /* 主页面背景 */
    [data-testid="stAppViewContainer"] {
        background-color: #E8F4F8;  /* 马卡龙浅蓝主色调 */
    }
    
    /* 侧边栏背景 */
    [data-testid="stSidebar"] {
        background-color: #D1E7DD;  /* 稍深一点的马卡龙蓝，与主背景区分 */
    }
    
    /* 表单区域背景 */
    [data-testid="stForm"] {
        background-color: #F0F8FB;  /* 更浅的马卡龙蓝，突出表单 */
        padding: 20px;
        border-radius: 10px;
    }
    
    /* 按钮样式优化，适配马卡龙风格 */
    [data-testid="baseButton-secondary"] {
        background-color: #B8D8E6;
        color: #2C3E50;
        border: none;
        border-radius: 8px;
    }
    
    [data-testid="baseButton-secondary"]:hover {
        background-color: #A0C4E2;  /* 按钮 hover 时的背景色 */
    }
    
    /* 标题文字颜色优化 */
    h1, h2, h3, h4 {
        color: #2C3E50;  /* 标题文字的深灰色 */
    }
    
    /* 普通文字颜色 */
    p, div, span {
        color: #34495E;  /* 普通文字的中灰色 */
    }
    </style>
    """, unsafe_allow_html=True)  # 允许执行HTML代码（Streamlit默认禁用，需显式开启）

# 使用侧边栏实现多页面显示效果（Streamlit的with语法：将内容包裹在侧边栏容器中）
with st.sidebar:
    st.image('images/rigth_logo.png', width=100)  # 侧边栏显示logo图片（width设置宽度为100像素）
    st.title('请选择页面')  # 侧边栏标题
    page = st.selectbox(
        "请选择页面", 
        ["简介页面", "预测分类页面"],  # 下拉选择框的选项
        label_visibility='collapsed'  # 隐藏选择框的label文字
    )  # 定义页面选择器，返回用户选择的页面名称

# 简介页面逻辑：当用户选择“简介页面”时执行
if page == "简介页面":
    st.title("企鹅分类器:penguin:")  # 页面标题（带企鹅emoji）
    st.header('数据集介绍')  # 二级标题
    st.markdown("""
帕尔默群岛企鹅数据集是用于数据探索和数据可视化的一个出色的数据集，也可以作为机器学习入门练习。
该数据集是由 Gorman 等收集，并发布在一个名为 palmerpenguins 的 R 语言包，可以对南极企鹅种类进行分类和研究。
该数据集记录了 344 行观测数据，包含 3 个不同物种的企鹅：阿德利企鹅、巴布亚企鹅和帽带企鹅的各种信息。
    """)  # 用markdown格式显示数据集说明
    st.header('三种企鹅的卡通图像')  # 二级标题
    st.image('images/penguins.png')  # 显示企鹅图片

# 预测分类页面逻辑：当用户选择“预测分类页面”时执行
elif page == "预测分类页面":
    st.header("预测企鹅分类")  # 二级标题
    st.markdown("这个 Web 应用是基于帕尔默群岛企鹅数据集构建的模型。只需输入 6 个信息，就可以预测企鹅的物种，使用下面的表单开始预测吧！")  # 功能说明
    
    # 该页面是3:1:2的列布局（用st.columns划分列，列表中的数字代表列宽比例）
    col_form, col, col_logo = st.columns([3, 1, 2])
    
    with col_form:  # 第一个列（占比3）：用于放表单
        # 运用表单和表单提交按钮（with st.form包裹表单元素，统一提交）
        with st.form('user_inputs'):  # 表单名称：user_inputs
            # 以下是用户输入控件：
            island = st.selectbox('企鹅栖息的岛屿', options=['托尔森岛', '比斯科群岛', '德里姆岛'])  # 下拉选择框（岛屿）
            sex = st.selectbox('性别', options=['雄性', '雌性'])  # 下拉选择框（性别）
            bill_length = st.number_input('喙的长度（毫米）', min_value=0.0)  # 数字输入框（喙长）
            bill_depth = st.number_input('喙的深度（毫米）', min_value=0.0)  # 数字输入框（喙深）
            flipper_length = st.number_input('翅膀的长度（毫米）', min_value=0.0)  # 数字输入框（翅长）
            body_mass = st.number_input('身体质量（克）', min_value=0.0)  # 数字输入框（体重）
            submitted = st.form_submit_button('预测分类')  # 表单提交按钮（点击后submitted为True）
        
        # 初始化数据预处理格式中与岛屿相关的变量（one-hot编码：将分类变量转为模型可识别的数值）
        island_biscoe, island_dream, island_torgerson = 0, 0, 0
        # 根据用户输入的岛屿数据更改对应的值
        if island == '比斯科群岛':
            island_biscoe = 1
        elif island == '德里姆岛':
            island_dream = 1
        elif island == '托尔森岛':
            island_torgerson = 1
        
        # 初始化数据预处理格式中与性别相关的变量（one-hot编码）
        sex_female, sex_male = 0, 0
        # 根据用户输入的性别数据更改对应的值
        if sex == '雌性':
            sex_female = 1
        elif sex == '雄性':
            sex_male = 1
        
        # 整理为模型可接收的格式化数据（按模型训练时的特征顺序排列）
        format_data = [
            bill_length, bill_depth, flipper_length, body_mass,
            island_dream, island_torgerson, island_biscoe, sex_male, sex_female
        ]
        
        # 使用pickle加载预训练的随机森林模型（rb：以二进制只读模式打开文件）
        with open('rfc_model.pkl', 'rb') as f:
            rfc_model = pickle.load(f)  # 加载模型到rfc_model变量
        
        # 使用pickle加载物种编码与名称的映射对象（用于将模型输出的数字编码转为物种名）
        with open('output_uniques.pkl', 'rb') as f:
            output_uniques_map = pickle.load(f)
        
        # 表单提交后执行预测（当用户点击“预测分类”按钮时）
        if submitted:
            # 构造与训练时一致的数据框，解决警告信息（用模型的feature_names_in_保证特征名匹配）
            format_data_df = pd.DataFrame(
                data=[format_data],  # 输入数据（一行）
                columns=rfc_model.feature_names_in_  # 特征名（与训练时一致）
            )
            # 使用模型对格式化后的数据进行预测，返回预测的类别代码
            predict_result_code = rfc_model.predict(format_data_df)
            # 将类别代码映射到具体的物种名称
            predict_result_species = output_uniques_map[predict_result_code][0]
            # 输出预测结果（加粗展示：用**包裹文本）
            st.write(f'根据您输入的数据，预测该企鹅的物种名称是：**{predict_result_species}**')
    
    with col_logo:  # 第三个列（占比2）：用于放图片
        if not submitted:
            # 未提交时显示logo
            st.image('images/rigth_logo.png', width=300)
        else:
            # 提交后显示对应企鹅物种的图片（根据预测结果拼接图片路径）
            st.image(f'images/{predict_result_species}.png', width=300)