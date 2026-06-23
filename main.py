import streamlit as st
import pandas as pd
from collections import defaultdict

# 页面基础配置
st.set_page_config(page_title="开奖历史数据统计工具", layout="wide")
st.title("📊 开奖记录序列特征全量统计工具 (纯净对齐版)")
st.caption("专注前后行状态转移统计 ｜ 规整对齐 ｜ 全量不遮挡")

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
    
    # 清洗并解析数据
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
            
        # 左右两列大布局
        col1, col2 = st.columns(2)
        
        # --- 模块一：尾数矩阵生成 ---
        with col1:
            st.subheader("🔢 1. 尾数 0-9 后行尾数完整分布")
            
            # 动态构建排版精美的 Markdown 表格
            tail_md = "| 当前尾数 | 历史总计 | 下一行尾数概率分布 (从高到低降序排列) |\n| :---: | :---: | :--- |\n"
            
            for tail in range(10):
                nexts = tail_transitions[tail]
                total = len(nexts)
                counts = defaultdict(int)
                for n in nexts:
                    counts[n] += 1
                
                # 获取最高频次，用于加粗对比
                max_count = max(counts.values()) if counts else 0
                
                prob_parts = []
                for t in all_tails:
                    cnt = counts[t]
                    prob = (cnt / total * 100) if total > 0 else 0.0
                    prob_parts.append((t, cnt, prob))
                
                # 降序排序
                prob_parts.sort(key=lambda x: (-x[1], x[0]))
                
                # 格式化文本格式（全角符号 ｜ 防止破坏 Markdown 结构）
                formatted_parts = []
                for t, c, p in prob_parts:
                    if c == max_count and max_count > 0:
                        # 历史最高频：加粗高亮显眼展示
                        formatted_parts.append(f"**{t}尾: {p:.1f}%({c}次)**")
                    else:
                        formatted_parts.append(f"{t}尾: {p:.1f}%({c}次)")
                        
                prob_str = " ｜ ".join(formatted_parts)
                tail_md += f"| **{tail}尾** | {total}次 | {prob_str} |\n"
                
            st.markdown(tail_md, unsafe_allow_html=True)

        # --- 模块二：生肖矩阵生成 ---
        with col2:
            st.subheader("🔮 2. 各生肖后行生肖完整分布")
            
            # 动态构建排版精美的 Markdown 表格
            zodiac_md = "| 当前生肖 | 历史总计 | 下一行生肖概率分布 (从高到低降序排列) |\n| :---: | :---: | :--- |\n"
            
            for zodiac in all_zodiacs:
                nexts = zodiac_transitions[zodiac]
                total = len(nexts)
                counts = defaultdict(int)
                for n in nexts:
                    counts[n] += 1
                    
                max_count = max(counts.values()) if counts else 0
                
                prob_parts = []
                for z in all_zodiacs:
                    cnt = counts[z]
                    prob = (cnt / total * 100) if total > 0 else 0.0
                    prob_parts.append((z, cnt, prob))
                
                # 降序排序
                prob_parts.sort(key=lambda x: (-x[1], all_zodiacs.index(x[0])))
                
                formatted_parts = []
                for z, c, p in prob_parts:
                    if c == max_count and max_count > 0:
                        formatted_parts.append(f"**{z}: {p:.1f}%({c}次)**")
                    else:
                        formatted_parts.append(f"{z}: {p:.1f}%({c}次)")
                        
                prob_str = " ｜ ".join(formatted_parts)
                zodiac_md += f"| **{zodiac}** | {total}次 | {prob_str} |\n"
                
            st.markdown(zodiac_md, unsafe_allow_html=True)
