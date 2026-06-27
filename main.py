import streamlit as st
import pandas as pd
from collections import defaultdict

# 页面基础配置
st.set_page_config(page_title="数据全维度智能统计看板", layout="wide")
st.title("📊 全维度综合统计看板")
st.caption("最新总量冷热 ｜ 当前期数遗漏 ｜ 状态转移矩阵 ｜ 规整对齐排版")

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
        st.error("❌ 表格内有效数据行数不足，无法进行数据统计！")
    else:
        # 定义全局标准集合
        all_tails = list(range(10))
        all_zodiacs = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
        
        st.write("---")
        
        # 🌟 核心排版优化：使用 Tabs 将三大功能进行横向归类，界面极度整齐
        tab1, tab2, tab3 = st.tabs(["🔥 1. 大盘总量冷热榜", "⏳ 2. 当前未出遗漏榜", "🔄 3. 前后行状态转移矩阵"])

        # ==========================================
        # TAB 1: 大盘总量冷热榜
        # ==========================================
        with tab1:
            st.subheader("📊 整体出现次数总计（按频率从高到低排列）")
            
            num_counts = defaultdict(int)
            tail_counts = defaultdict(int)
            zodiac_counts = defaultdict(int)
            
            for num, zodiac in parsed_data:
                num_counts[num] += 1
                tail_counts[num % 10] += 1
                zodiac_counts[zodiac] += 1
                
            hot_col1, hot_col2, hot_col3 = st.columns(3)
            
            # 1. 号码冷热
            with hot_col1:
                st.markdown("### 🔢 号码冷热排行 (1-49)")
                num_hot_data = []
                for n in range(1, 50):
                    cnt = num_counts[n]
                    pct = (cnt / total_records * 100) if total_records > 0 else 0.0
                    num_hot_data.append((n, cnt, pct))
                num_hot_data.sort(key=lambda x: (-x[1], x[0]))
                
                num_md = "| 排名 | 号码 | 出现次数 | 占比概率 |\n| :---: | :---: | :---: | :---: |\n"
                for rank, (n, cnt, pct) in enumerate(num_hot_data, 1):
                    num_str = f"**{n:02d}**" if rank <= 3 and cnt > 0 else f"{n:02d}"
                    flag = "🔥" if rank <= 3 and cnt > 0 else ("❄️" if cnt == 0 else "")
                    num_md += f"| {rank} | {num_str} {flag} | {cnt}次 | {pct:.1f}% |\n"
                st.markdown(num_md)
                
            # 2. 尾数冷热
            with hot_col2:
                st.markdown("### 🎯 尾数冷热排行 (0-9)")
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
                
            # 3. 生肖冷热
            with hot_col3:
                st.markdown("### 🔮 生肖冷热排行")
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
        # TAB 2: 当前未出遗漏榜（✨新增加核心模块）
        # ==========================================
        with tab2:
            st.subheader("⏳ 截止当前最新一期：各指标未出遗漏期数统计（按遗漏时间降序排列）")
            st.caption("提示：遗漏期数越大代表该指标越久没有开出；遗漏为 0 表示上期（最新一期）刚刚开出。")
            
            # --- 算法：倒序扫描计算遗漏 ---
            # 1. 号码遗漏计算
            num_omission = {}
            for n in range(1, 50):
                found = False
                for i in range(total_records - 1, -1, -1):
                    if parsed_data[i][0] == n:
                        num_omission[n] = (total_records - 1) - i
                        found = True
                        break
                if not found:
                    num_omission[n] = total_records # 整个历史都没出现过
                    
            # 2. 生肖遗漏计算
            zodiac_omission = {}
            for z in all_zodiacs:
                found = False
                for i in range(total_records - 1, -1, -1):
                    if parsed_data[i][1] == z:
                        zodiac_omission[z] = (total_records - 1) - i
                        found = True
                        break
                if not found:
                    zodiac_omission[z] = total_records

            # 两列并排排版
            miss_col1, miss_col2 = st.columns(2)
            
            with miss_col1:
                st.markdown("### 🔢 49个号码当前遗漏排行")
                # 排序：遗漏期数从大到小，遗漏一样按号码从小到大
                sorted_num_miss = sorted(num_omission.items(), key=lambda x: (-x[1], x[0]))
                
                num_miss_md = "| 排名 | 号码 | 当前已连空（遗漏） | 状态提醒 |\n| :---: | :---: | :---: | :---: |\n"
                for rank, (n, miss) in enumerate(sorted_num_miss, 1):
                    status = "⚠️ 超级冷码" if miss >= 10 else ("🎯 当期刚出" if miss == 0 else "正常")
                    n_str = f"**{n:02d}**" if miss >= 10 or miss == 0 else f"{n:02d}"
                    num_miss_md += f"| {rank} | {n_str} | **{miss}** 期未出 | {status} |\n"
                st.markdown(num_miss_md)
                
            with miss_col2:
                st.markdown("### 🔮 12生肖当前遗漏排行")
                # 排序：遗漏期数从大到小
                sorted_zodiac_miss = sorted(zodiac_omission.items(), key=lambda x: (-x[1], all_zodiacs.index(x[0])))
                
                zodiac_miss_md = "| 排名 | 生肖 | 当前已连空（遗漏） | 状态提醒 |\n| :---: | :---: | :---: | :---: |\n"
                for rank, (z, miss) in enumerate(sorted_zodiac_miss, 1):
                    status = "⚠️ 超级冷肖" if miss >= 5 else ("🎯 当期刚出" if miss == 0 else "正常")
                    z_str = f"**{z}**" if miss >= 5 or miss == 0 else z
                    zodiac_miss_md += f"| {rank} | {z_str} | **{miss}** 期未出 | {status} |\n"
                st.markdown(zodiac_miss_md)

        # ==========================================
        # TAB 3: 前后行状态转移矩阵
        # ==========================================
        with tab3:
            st.subheader("🔄 纵向序列演变规律：当前行开出后，下一行开出什么的概率")
            
            tail_transitions = defaultdict(list)
            zodiac_transitions = defaultdict(list)
            
            for i in range(len(parsed_data) - 1):
                curr_tail = parsed_data[i][0] % 10
                next_tail = parsed_data[i+1][0] % 10
                tail_transitions[curr_tail].append(next_tail)
                
                curr_zodiac = parsed_data[i][1]
                next_zodiac = parsed_data[i+1][1]
                zodiac_transitions[curr_zodiac].append(next_zodiac)
                
            trans_col1, trans_col2 = st.columns(2)
            
            # 尾数转移
            with trans_col1:
                st.markdown("### 🔢 尾数 0-9 后行尾数完整分布")
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
                    tail_trans_md += f"| **{tail}尾** | {total}次 | {" ｜ ".join(formatted_parts)} |\n"
                st.markdown(tail_trans_md, unsafe_allow_html=True)

            # 生肖转移
            with trans_col2:
                st.markdown("### 🔮 各生肖后行生肖完整分布")
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
                    zodiac_trans_md += f"| **{zodiac}** | {total}次 | {" ｜ ".join(formatted_parts)} |\n"
                st.markdown(zodiac_trans_md, unsafe_allow_html=True)
