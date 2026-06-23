import streamlit as st
import pandas as pd
from collections import defaultdict

# 页面基础配置
st.set_page_config(page_title="开奖特征自动统计工具", layout="wide")
st.title("📊 开奖记录序列特征自动统计与推荐工具 (通用兼容版)")
st.caption("支持一键上传最新的中奖记录表格，全自动双重概率池对齐交叉预测")

# 1. 配置文件上传组件
uploaded_file = st.file_uploader("👉 请上传最新的开奖记录表格 (支持 .csv 或 .xlsx 格式)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # 2. 自动兼容读取 CSV 或 Excel
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, header=None)
    else:
        try:
            df = pd.read_excel(uploaded_file, header=None)
        except ImportError:
            st.error("❌ 检查到您的电脑缺少 Excel 解析组件，请在终端/命令行运行：`pip install openpyxl` 后重新启动程序。")
            st.stop()
    
    # 清洗并解析数据 (默认第一列为号码，第二列为生肖)
    df = df.dropna()
    parsed_data = []
    for idx, row in df.iterrows():
        try:
            num = int(row[0])
            zodiac = str(row[1]).strip()
            parsed_data.append((num, zodiac))
        except:
            continue
            
    if len(parsed_data) < 2:
        st.error("❌ 表格内有效数据行数不足，无法进行前后行规律统计！")
    else:
        # 定义全局标准集合
        all_tails = list(range(10))
        all_zodiacs = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
        
        # 2026年岁次丙午马年 1-49 号码生肖对照基准 (1=马, 2=蛇, 3=龙...)
        base_zodiacs = ['马', '蛇', '龙', '兔', '虎', '牛', '鼠', '猪', '狗', '鸡', '猴', '羊']
        def get_zodiac_of_number(n):
            return base_zodiacs[(n - 1) % 12]

        # 3. 核心统计逻辑：前后行状态转移
        tail_transitions = defaultdict(list)
        zodiac_transitions = defaultdict(list)
        
        for i in range(len(parsed_data) - 1):
            curr_tail = parsed_data[i][0] % 10
            next_tail = parsed_data[i+1][0] % 10
            tail_transitions[curr_tail].append(next_tail)
            
            curr_zodiac = parsed_data[i][1]
            next_zodiac = parsed_data[i+1][1]
            zodiac_transitions[curr_zodiac].append(next_zodiac)
            
        # 创建两列布局展示完整分布表
        col1, col2 = st.columns(2)
        
        # --- 模块一：尾数概率计算 ---
        tail_table_data = []
        for tail in range(10):
            nexts = tail_transitions[tail]
            total = len(nexts)
            counts = defaultdict(int)
            for n in nexts:
                counts[n] += 1
            
            prob_parts = []
            for t in all_tails:
                cnt = counts[t]
                prob = (cnt / total * 100) if total > 0 else 0.0
                prob_parts.append((t, cnt, prob))
            prob_parts.sort(key=lambda x: (-x[1], x[0]))
            prob_str = ", ".join([f"{t}尾: {p:.1f}%({c}次)" for t, c, p in prob_parts])
            
            tail_table_data.append({
                "当前尾数": f"{tail}尾",
                "历史出现总计": f"{total}次",
                "下一行尾数完整分布 (降序排列)": prob_str
            })
            
        with col1:
            st.subheader("🔢 1. 尾数 0-9 后各尾数完整概率分布")
            st.dataframe(pd.DataFrame(tail_table_data), use_container_width=True)

        # --- 模块二：生肖概率计算 ---
        zodiac_table_data = []
        for zodiac in all_zodiacs:
            nexts = zodiac_transitions[zodiac]
            total = len(nexts)
            counts = defaultdict(int)
            for n in nexts:
                counts[n] += 1
            
            prob_parts = []
            for z in all_zodiacs:
                cnt = counts[z]
                prob = (cnt / total * 100) if total > 0 else 0.0
                prob_parts.append((z, cnt, prob))
            prob_parts.sort(key=lambda x: (-x[1], all_zodiacs.index(x[0])))
            prob_str = ", ".join([f"{z}: {p:.1f}%({c}次)" for z, c, p in prob_parts])
            
            zodiac_table_data.append({
                "当前生肖": zodiac,
                "历史出现总计": f"{total}次",
                "下一行生肖完整分布 (降序排列)": prob_str
            })
            
        with col2:
            st.subheader("🔮 2. 各生肖后各生肖完整概率分布")
            st.dataframe(pd.DataFrame(zodiac_table_data), use_container_width=True)

        # --- 模块三：自动交叉对齐号码推荐 ---
        st.write("---")
        st.subheader("🎯 3. 下期精准双条件重合号码预测")
        
        # 模式选择器
        predict_mode = st.radio(
            "🛠️ **请选择预测合并模式：**",
            ["⚡ 精选模式（智能控码：按综合热度从高到低，精准锁定前 5 个最强交叉码）",
             "🔥 容错模式（大网拦截：只要历史出现过、概率 > 0% 的条件全部组合）"],
            index=0
        )
        
        # 获取最新开奖数据
        last_num, last_zodiac = parsed_data[-1]
        last_tail = last_num % 10
        
        st.markdown(f"📋 **最新一期（表格最后一行）**：号码 `**{last_num}**` ，生肖 `**{last_zodiac}**`（尾数 `{last_tail}`）")
        
        # 计算 1-49 所有号码的联合得分
        number_scores = []
        for n in range(1, 50):
            n_tail = n % 10
            n_zodiac = get_zodiac_of_number(n)
            
            t_count = tail_transitions[last_tail].count(n_tail)
            z_count = zodiac_transitions[last_zodiac].count(n_zodiac)
            
            combined_score = t_count * z_count
            number_scores.append((n, combined_score))
            
        # 根据模式筛选号码
        matched_numbers = []
        if "精选模式" in predict_mode:
            number_scores.sort(key=lambda x: (-x[1], x[0]))
            top_5 = number_scores[:5]
            matched_numbers = [f"{item[0]:02d}" for item in top_5]
            matched_numbers.sort()
            mode_title = "精选模式（联合热度最高的前 5 码）"
        else:
            matched_numbers = [f"{item[0]:02d}" for item in number_scores if item[1] > 0]
            matched_numbers.sort()
            mode_title = "容错模式（所有曾经出现过的组合）"
        
        # 格式化输出
        if matched_numbers:
            st.success(f"🏁 **最终筛选：【{mode_title}】共为您选出 {len(matched_numbers)} 个号码（已按顺序排列）**")
            st.markdown("👇 **请点击下方代码框右上角的图标，即可一键复制全部号码：**")
            
            copy_string = ", ".join(matched_numbers)
            st.code(copy_string, language="text")
        else:
            st.warning("⚠️ 提示：没有匹配的号码。")
