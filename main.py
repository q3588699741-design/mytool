import streamlit as st
import pandas as pd
from collections import defaultdict

# 页面基础配置
st.set_page_config(page_title="开奖历史数据全能统计工具", layout="wide")
st.title("📊 开奖记录全维度统计看板 (冷热总量 + 状态转移)")
st.caption("一键上传最新数据 ｜ 自动对齐排版 ｜ 绝不遮挡切断文字")

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
            
    total_records = len(parsed_data)
    
    if total_records < 2:
        st.error("❌ 表格内有效数据行数不足，无法进行全量特征统计！")
    else:
        # 定义全局标准集合
        all_tails = list(range(10))
        all_zodiacs = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
        
        st.write("---")
        st.header("🔥 新增：大盘总量冷热数据统计（按热度降序排列）")
        st.caption(f"当前表格总开奖期数：{total_records} 期")
        
        # ==========================================
        # 核心逻辑：计算整体冷热
        # ==========================================
        num_counts = defaultdict(int)
        tail_counts = defaultdict(int)
        zodiac_counts = defaultdict(int)
        
        for num, zodiac in parsed_data:
            num_counts[num] += 1
            tail_counts[num % 10] += 1
            zodiac_counts[zodiac] += 1
            
        # 三列并排布局展示总量冷热
        hot_col1, hot_col2, hot_col3 = st.columns(3)
        
        # 1. 号码冷热榜 (1-49)
        with hot_col1:
            st.subheader("🔢 号码冷热排行 (1-49)")
            num_hot_data = []
            for n in range(1, 50):
                cnt = num_counts[n]
                pct = (cnt / total_records * 100) if total_records > 0 else 0.0
                num_hot_data.append((n, cnt, pct))
            # 按次数降序，次数相同按号码数字升序
            num_hot_data.sort(key=lambda x: (-x[1], x[0]))
            
            num_md = "| 排名 | 号码 | 出现次数 | 占比概率 |\n| :---: | :---: | :---: | :---: |\n"
            for rank, (n, cnt, pct) in enumerate(num_hot_data, 1):
                num_str = f"**{n:02d}**" if rank <= 3 and cnt > 0 else f"{n:02d}"
                flag = "🔥" if rank <= 3 and cnt > 0 else ("❄️" if cnt == 0 else "")
                num_md += f"| {rank} | {num_str} {flag} | {cnt}次 | {pct:.1f}% |\n"
            st.markdown(num_md)
            
        # 2. 尾数冷热榜 (0-9)
        with hot_col2:
            st.subheader("🎯 尾数冷热排行 (0-9)")
            tail_hot_data = []
            for t in all_tails:
                cnt = tail_counts[t]
                pct = (cnt / total_records * 100) if total_records > 0 else 0.0
                tail_hot_data.append((t, cnt, pct))
            tail_hot_data.sort(key=lambda x: (-x[1], x[0]))
            
            tail_md = "| 排名 | 尾数 | 出现次数 | 占比概率 |\n| :---: | :---: | :---: | :---: |\n"
            for rank, (t, cnt, pct) in enumerate(tail_hot_data, 1):
                tail_str = f"**{t}尾**" if rank <= 3 and cnt > 0 else f"{t}尾"
                flag = "🔥" if rank <= 3 and cnt > 0 else ("❄️" if cnt == 0 else "")
                tail_md += f"| {rank} | {tail_str} {flag} | {cnt}次 | {pct:.1f}% |\n"
            st.markdown(tail_md)
            
        # 3. 生肖冷热榜 (12生肖)
        with hot_col3:
            st.subheader("🔮 生肖冷热排行")
            zodiac_hot_data = []
            for z in all_zodiacs:
                cnt = zodiac_counts[z]
                pct = (cnt / total_records * 100) if total_records > 0 else 0.0
                zodiac_hot_data.append((z, cnt, pct))
            zodiac_hot_data.sort(key=lambda x: (-x[1], all_zodiacs.index(x[0])))
            
            zodiac_md = "| 排名 | 生肖 | 出现次数 | 占比概率 |\n| :---: | :---: | :---: | :---: |\n"
            for rank, (z, cnt, pct) in enumerate(zodiac_hot_data, 1):
                zodiac_str = f"**{z}**" if rank <= 3 and cnt > 0 else z
                flag = "🔥" if rank <= 3 and cnt > 0 else ("❄️" if cnt == 0 else "")
                zodiac_md += f"| {rank} | {zodiac_str} {flag} | {cnt}次 | {pct:.1f}% |\n"
            st.markdown(zodiac_md)

        # ==========================================
        # 核心逻辑：计算前后行转换规律
        # ==========================================
        st.write("---")
        st.header("🔄 原有：前后行规律状态转移统计矩阵")
        
        tail_transitions = defaultdict(list)
        zodiac_transitions = defaultdict(list)
        
        for i in range(len(parsed_data) - 1):
            curr_tail = parsed_data[i][0] % 10
            next_tail = parsed_data[i+1][0] % 10
            tail_transitions[curr_tail].append(next_tail)
            
            curr_zodiac = parsed_data[i][1]
            next_zodiac = parsed_data[i+1][1]
            zodiac_transitions[curr_zodiac].append(next_zodiac)
            
        # 左右两列大布局展示状态转移
        trans_col1, trans_col2 = st.columns(2)
        
        # 4. 尾数转移矩阵
        with trans_col1:
            st.subheader("🔢 1. 尾数 0-9 后行尾数完整分布")
            tail_trans_md = "| 当前尾数 | 历史总计 | 下一行尾数概率分布 (降序排列) |\n| :---: | :---: | :--- |\n"
            
            for tail in range(10):
                nexts = tail_transitions[tail]
                total = len(nexts)
                counts = defaultdict(int)
                for n in nexts:
                    counts[n] += 1
                
                max_count = max(counts.values()) if counts else 0
                prob_parts = []
                for t in all_tails:
                    cnt = counts[t]
                    prob = (cnt / total * 100) if total > 0 else 0.0
                    prob_parts.append((t, cnt, prob))
                prob_parts.sort(key=lambda x: (-x[1], x[0]))
                
                formatted_parts = []
                for t, c, p in prob_parts:
                    if c == max_count and max_count > 0:
                        formatted_parts.append(f"**{t}尾: {p:.1f}%({c}次)**")
                    else:
                        formatted_parts.append(f"{t}尾: {p:.1f}%({c}次)")
                        
                prob_str = " ｜ ".join(formatted_parts)
                tail_trans_md += f"| **{tail}尾** | {total}次 | {prob_str} |\n"
            st.markdown(tail_trans_md, unsafe_allow_html=True)

        # 5. 生肖转移矩阵
        with trans_col2:
            st.subheader("🔮 2. 各生肖后行生肖完整分布")
            zodiac_trans_md = "| 当前生肖 | 历史总计 | 下一行生肖概率分布 (降序排列) |\n| :---: | :---: | :--- |\n"
            
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
                prob_parts.sort(key=lambda x: (-x[1], all_zodiacs.index(x[0])))
                
                formatted_parts = []
                for z, c, p in prob_parts:
                    if c == max_count and max_count > 0:
                        formatted_parts.append(f"**{z}: {p:.1f}%({c}次)**")
                    else:
                        formatted_parts.append(f"{z}: {p:.1f}%({c}次)")
                        
                prob_str = " ｜ ".join(formatted_parts)
                zodiac_trans_md += f"| **{zodiac}** | {total}次 | {prob_str} |\n"
            st.markdown(zodiac_trans_md, unsafe_allow_html=True)
