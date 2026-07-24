import streamlit as st
import pandas as pd
from collections import defaultdict
import traceback

# 页面基础配置
st.set_page_config(page_title="数据全维度智能统计看板", layout="wide")
st.title("📊 开奖记录全维度综合统计看板 (拐点视觉高亮版)")
st.caption("最新总体冷热 ｜ 当前双重遗漏与欲出几率 ｜ 纵向状态转移矩阵 ｜ 🎯精准剔除+拐点特赦智能控码")

# 1. 配置文件上传组件
uploaded_file = st.file_uploader("👉 请上传最新的开奖记录表格 (支持 .csv 或 .xlsx 格式)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # 2. 自动兼容读取 CSV 或 Excel
    if uploaded_file.name.endswith('.csv'):
        try:
            df = pd.read_csv(uploaded_file, header=None)
        except Exception as e:
            st.error(f"❌ 读取 CSV 表格失败: {e}")
            st.stop()
    else:
        try:
            df = pd.read_excel(uploaded_file, header=None)
        except ImportError:
            st.error("❌ 检查到您的电脑缺少 Excel 解析组件，请在终端/命令行运行：`pip install openpyxl` 后重新启动程序。")
            st.stop()
        except Exception as e:
            st.error(f"❌ 读取 Excel 表格失败: {e}")
            st.stop()
    
    try:
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
            all_heads = list(range(5)) # 0头到4头
            
            # 2026年岁次丙午马年 1-49 号码生肖对照基准
            base_zodiacs = ['马', '蛇', '龙', '兔', '虎', '牛', '鼠', '猪', '狗', '鸡', '猴', '羊']
            def get_zodiac_of_number(n):
                return base_zodiacs[(n - 1) % 12]

            # 号码出现总数统计
            num_counts = defaultdict(int)
            tail_counts = defaultdict(int)
            zodiac_counts = defaultdict(int)
            head_counts_dict = defaultdict(int)
            
            for num, zodiac in parsed_data:
                num_counts[num] += 1
                tail_counts[num % 10] += 1
                zodiac_counts[zodiac] += 1
                head_counts_dict[num // 10] += 1

            # 🛠️ 建立全量位置索引，用于精准提炼“当前遗漏”与“上次遗漏（最近开出间隔）”
            num_indices = defaultdict(list)
            tail_indices = defaultdict(list)
            zodiac_indices = defaultdict(list)
            head_indices = defaultdict(list)
            
            for i, (num, zodiac) in enumerate(parsed_data):
                num_indices[num].append(i)
                tail_indices[num % 10].append(i)
                zodiac_indices[zodiac].append(i)
                head_indices[num // 10].append(i)

            # 1. 号码双重遗漏计算
            num_omission = {}
            num_last_omission = {}
            for n in range(1, 50):
                idxs = num_indices[n]
                if idxs:
                    num_omission[n] = (total_records - 1) - idxs[-1]
                    if len(idxs) >= 2:
                        num_last_omission[n] = idxs[-1] - idxs[-2] - 1
                    else:
                        num_last_omission[n] = idxs[-1]
                else:
                    num_omission[n] = total_records
                    num_last_omission[n] = 0

            # 2. 生肖双重遗漏计算
            zodiac_omission = {}
            zodiac_last_omission = {}
            for z in all_zodiacs:
                idxs = zodiac_indices[z]
                if idxs:
                    zodiac_omission[z] = (total_records - 1) - idxs[-1]
                    if len(idxs) >= 2:
                        zodiac_last_omission[z] = idxs[-1] - idxs[-2] - 1
                    else:
                        zodiac_last_omission[z] = idxs[-1]
                else:
                    zodiac_omission[z] = total_records
                    zodiac_last_omission[z] = 0

            # 3. 尾数双重遗漏计算
            tail_omission = {}
            tail_last_omission = {}
            for t in all_tails:
                idxs = tail_indices[t]
                if idxs:
                    tail_omission[t] = (total_records - 1) - idxs[-1]
                    if len(idxs) >= 2:
                        tail_last_omission[t] = idxs[-1] - idxs[-2] - 1
                    else:
                        tail_last_omission[t] = idxs[-1]
                else:
                    tail_omission[t] = total_records
                    tail_last_omission[t] = 0

            # 4. 头数双重遗漏计算
            head_omission = {}
            head_last_omission = {}
            for h in all_heads:
                idxs = head_indices[h]
                if idxs:
                    head_omission[h] = (total_records - 1) - idxs[-1]
                    if len(idxs) >= 2:
                        head_last_omission[h] = idxs[-1] - idxs[-2] - 1
                    else:
                        head_last_omission[h] = idxs[-1]
                else:
                    head_omission[h] = total_records
                    head_last_omission[h] = 0

            # 计算全局欲出几率
            tail_rates = {}
            for t in all_tails:
                cnt = tail_counts[t]
                avg_int = (total_records / cnt) if cnt > 0 else total_records
                tail_rates[t] = tail_omission[t] / avg_int

            zodiac_rates = {}
            for z in all_zodiacs:
                cnt = zodiac_counts[z]
                avg_int = (total_records / cnt) if cnt > 0 else total_records
                zodiac_rates[z] = zodiac_omission[z] / avg_int

            num_rates = {}
            for n in range(1, 50):
                cnt = num_counts[n]
                avg_int = (total_records / cnt) if cnt > 0 else total_records
                num_rates[n] = num_omission[n] / avg_int

            head_rates = {}
            for h in all_heads:
                cnt = head_counts_dict[h]
                avg_int = (total_records / cnt) if cnt > 0 else total_records
                head_rates[h] = head_omission[h] / avg_int

            # 计算状态转移数据
            tail_transitions = defaultdict(list)
            zodiac_transitions = defaultdict(list)
            head_transitions = defaultdict(list)
            for i in range(len(parsed_data) - 1):
                tail_transitions[parsed_data[i][0] % 10].append(parsed_data[i+1][0] % 10)
                zodiac_transitions[parsed_data[i][1]].append(parsed_data[i+1][1])
                head_transitions[parsed_data[i][0] // 10].append(parsed_data[i+1][0] // 10)

            st.write("---")
            
            # 简洁直观的四大板块
            tab1, tab2, tab3, tab4 = st.tabs([
                "🔥 1. 大盘总量冷热榜", 
                "⏳ 2. 当前未出遗漏与欲出榜", 
                "🔄 3. 前后行状态转移矩阵",
                "🎯 4. 剔除与拐点特赦智能选号"
            ])

            # ==========================================
            # TAB 1: 大盘总量冷热榜
            # ==========================================
            with tab1:
                st.subheader("📊 整体出现次数总计")
                hot_col1, hot_col2, hot_col3 = st.columns(3)
                with hot_col1:
                    st.markdown("### 🔢 号码冷热排行 (1-49)")
                    num_hot_data = [(n, num_counts[n], (num_counts[n]/total_records*100 if total_records>0 else 0.0)) for n in range(1, 50)]
                    num_hot_data.sort(key=lambda x: (-x[1], x[0]))
                    md = "| 排名 | 号码 | 出现次数 | 占比概率 |\n| :---: | :---: | :---: | :---: |\n"
                    for rank, (n, cnt, pct) in enumerate(num_hot_data, 1):
                        num_str = f"**{n:02d}**" if rank <= 3 and cnt > 0 else f"{n:02d}"
                        flag = "🔥" if rank <= 3 and cnt > 0 else ("❄️" if cnt == 0 else "")
                        md += f"| {rank} | {num_str} {flag} | {cnt}次 | {pct:.1f}% |\n"
                    st.markdown(md)
                with hot_col2:
                    st.markdown("### 🎯 尾数冷热排行 (0-9)")
                    tail_hot_data = [(t, tail_counts[t], (tail_counts[t]/total_records*100 if total_records>0 else 0.0)) for t in all_tails]
                    tail_hot_data.sort(key=lambda x: (-x[1], x[0]))
                    md = "| 排名 | 尾数 | 出现次数 | 占比概率 |\n| :---: | :---: | :---: | :---: |\n"
                    for rank, (t, cnt, pct) in enumerate(tail_hot_data, 1):
                        tail_str = f"**{t}尾**" if rank <= 3 and cnt > 0 else f"{t}尾"
                        flag = "🔥" if rank <= 3 and cnt > 0 else ("❄️" if cnt == 0 else "")
                        md += f"| {rank} | {tail_str} {flag} | {cnt}次 | {pct:.1f}% |\n"
                    st.markdown(md)
                with hot_col3:
                    st.markdown("### 🔮 生肖冷热排行")
                    zodiac_hot_data = [(z, zodiac_counts[z], (zodiac_counts[z]/total_records*100 if total_records>0 else 0.0)) for z in all_zodiacs]
                    zodiac_hot_data.sort(key=lambda x: (-x[1], all_zodiacs.index(x[0])))
                    md = "| 排名 | 生肖 | 出现次数 | 占比概率 |\n| :---: | :---: | :---: | :---: |\n"
                    for rank, (z, cnt, pct) in enumerate(zodiac_hot_data, 1):
                        zodiac_str = f"**{z}**" if rank <= 3 and cnt > 0 else z
                        flag = "🔥" if rank <= 3 and cnt > 0 else ("❄️" if cnt == 0 else "")
                        md += f"| {rank} | {zodiac_str} {flag} | {cnt}次 | {pct:.1f}% |\n"
                    st.markdown(md)

            # ==========================================
            # ⏳ TAB 2: 当前未出遗漏与欲出榜 (✨带 🚨 拐点高亮版)
            # ==========================================
            with tab2:
                st.subheader("⏳ 各指标未出当前遗漏与最近一次开出历史间隔深度统计")
                st.caption("💡 **直观标注说明**：带有 **🚨 警报** 与 **⚡ 闪电标记** 的项目，代表其【当前遗漏 $\ge$ 上次遗漏】，已触发遗漏拐点！")
                miss_col1, miss_col2, miss_col3, miss_col4 = st.columns(4)
                
                with miss_col1:
                    st.markdown("### 🔢 49个号码遗漏与欲出")
                    num_list = []
                    for n in range(1, 50):
                        miss = num_omission[n]
                        l_miss = num_last_omission[n]
                        rate = num_rates[n]
                        avg_int = (total_records / num_counts[n]) if num_counts[n] > 0 else total_records
                        num_list.append((n, miss, l_miss, avg_int, rate))
                    num_list.sort(key=lambda x: (-x[4], x[0]))
                    
                    md = "| 排名 | 号码 | 当前遗漏 | 上次遗漏 | 平均间隔 | 欲出几率 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                    for r, (n, miss, l_miss, avg_int, rate) in enumerate(num_list, 1):
                        is_inflection = (miss >= l_miss)
                        n_str = f"**{n:02d}** 🚨" if is_inflection else f"{n:02d}"
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        md += f"| {r} | {n_str} | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | **{rate:.2f}** |\n"
                    st.markdown(md)
                    
                with miss_col2:
                    st.markdown("### 🔮 12生肖遗漏与欲出")
                    zodiac_list = []
                    for z in all_zodiacs:
                        miss = zodiac_omission[z]
                        l_miss = zodiac_last_omission[z]
                        rate = zodiac_rates[z]
                        avg_int = (total_records / zodiac_counts[z]) if zodiac_counts[z] > 0 else total_records
                        zodiac_list.append((z, miss, l_miss, avg_int, rate))
                    zodiac_list.sort(key=lambda x: (-x[4], all_zodiacs.index(x[0])))
                    
                    md = "| 排名 | 生肖 | 当前遗漏 | 上次遗漏 | 平均间隔 | 欲出几率 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                    for r, (z, miss, l_miss, avg_int, rate) in enumerate(zodiac_list, 1):
                        is_inflection = (miss >= l_miss)
                        z_str = f"**{z}** 🚨" if is_inflection else z
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        md += f"| {r} | {z_str} | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | **{rate:.2f}** |\n"
                    st.markdown(md)
                    
                with miss_col3:
                    st.markdown("### 🎯 10个尾数遗漏与欲出")
                    tail_list_disp = []
                    for t in all_tails:
                        miss = tail_omission[t]
                        l_miss = tail_last_omission[t]
                        rate = tail_rates[t]
                        avg_int = (total_records / tail_counts[t]) if tail_counts[t] > 0 else total_records
                        tail_list_disp.append((t, miss, l_miss, avg_int, rate))
                    tail_list_disp.sort(key=lambda x: (-x[4], x[0]))
                    
                    md = "| 排名 | 尾数 | 当前遗漏 | 上次遗漏 | 平均间隔 | 欲出几率 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                    for r, (t, miss, l_miss, avg_int, rate) in enumerate(tail_list_disp, 1):
                        is_inflection = (miss >= l_miss)
                        t_str = f"**{t}尾** 🚨" if is_inflection else f"{t}尾"
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        md += f"| {r} | {t_str} | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | **{rate:.2f}** |\n"
                    st.markdown(md)

                with miss_col4:
                    st.markdown("### 🔝 5个头数遗漏与欲出")
                    head_list_disp = []
                    for h in all_heads:
                        miss = head_omission[h]
                        l_miss = head_last_omission[h]
                        rate = head_rates[h]
                        avg_int = (total_records / head_counts_dict[h]) if head_counts_dict[h] > 0 else total_records
                        head_list_disp.append((h, miss, l_miss, avg_int, rate))
                    head_list_disp.sort(key=lambda x: (-x[4], x[0]))
                    
                    md = "| 排名 | 头数 | 当前遗漏 | 上次遗漏 | 平均间隔 | 欲出几率 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                    for r, (h, miss, l_miss, avg_int, rate) in enumerate(head_list_disp, 1):
                        is_inflection = (miss >= l_miss)
                        h_str = f"**{h}头** 🚨" if is_inflection else f"{h}头"
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        md += f"| {r} | {h_str} | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | **{rate:.2f}** |\n"
                    st.markdown(md)

            # ==========================================
            # 🔄 TAB 3: 前后行状态转移矩阵
            # ==========================================
            with tab3:
                st.subheader("🔄 纵向序列演变规律概率分布")
                trans_col1, trans_col2, trans_col3 = st.columns(3)
                
                with trans_col1:
                    st.markdown("### 🔢 尾数 0-9 后行尾数完整分布")
                    tail_trans_md = "| 当前尾数 | 历史总计 | 下一行尾数概率分布 (降序排列) |\n| :---: | :---: | :--- |\n"
                    for tail in range(10):
                        nexts = tail_transitions[tail]
                        total = len(nexts)
                        counts = defaultdict(int)
                        for n in nexts: counts[n] += 1
                        max_count = max(counts.values()) if counts else 0
                        prob_parts = [(t, counts[t], (counts[t]/total*100 if total>0 else 0.0)) for t in all_tails]
                        prob_parts.sort(key=lambda x: (-x[1], x[0]))
                        formatted_parts = [f"**{t}尾: {p:.1f}%({c}次)**" if c==max_count and max_count>0 else f"{t}尾: {p:.1f}%({c}次)" for t, c, p in prob_parts]
                        joined_tail_str = ' ｜ '.join(formatted_parts)
                        tail_trans_md += f"| **{tail}尾** | {total}次 | {joined_tail_str} |\n"
                    st.markdown(tail_trans_md, unsafe_allow_html=True)

                with trans_col2:
                    st.markdown("### 🔮 12生肖 后行生肖完整分布")
                    zodiac_trans_md = "| 当前生肖 | 历史总计 | 下一行生肖概率分布 (降序排列) |\n| :---: | :---: | :--- |\n"
                    for z in all_zodiacs:
                        nexts = zodiac_transitions[z]
                        total = len(nexts)
                        counts = defaultdict(int)
                        for n in nexts: counts[n] += 1
                        max_count = max(counts.values()) if counts else 0
                        prob_parts = [(nz, counts[nz], (counts[nz]/total*100 if total>0 else 0.0)) for nz in all_zodiacs]
                        prob_parts.sort(key=lambda x: (-x[1], all_zodiacs.index(x[0])))
                        formatted_parts = [f"**{nz}: {p:.1f}%({c}次)**" if c==max_count and max_count>0 else f"{nz}: {p:.1f}%({c}次)" for nz, c, p in prob_parts]
                        joined_zodiac_str = ' ｜ '.join(formatted_parts)
                        zodiac_trans_md += f"| **{z}** | {total}次 | {joined_zodiac_str} |\n"
                    st.markdown(zodiac_trans_md, unsafe_allow_html=True)

                with trans_col3:
                    st.markdown("### 🔝 头数 0-4 后行头数完整分布")
                    head_trans_md = "| 当前头数 | 历史总计 | 下一行头数概率分布 (降序排列) |\n| :---: | :---: | :--- |\n"
                    for head in range(5):
                        nexts = head_transitions[head]
                        total = len(nexts)
                        counts = defaultdict(int)
                        for n in nexts: counts[n] += 1
                        max_count = max(counts.values()) if counts else 0
                        prob_parts = [(h, counts[h], (counts[h]/total*100 if total>0 else 0.0)) for h in all_heads]
                        prob_parts.sort(key=lambda x: (-x[1], x[0]))
                        formatted_parts = [f"**{h}头: {p:.1f}%({c}次)**" if c==max_count and max_count>0 else f"{h}头: {p:.1f}%({c}次)" for h, c, p in prob_parts]
                        joined_head_str = ' ｜ '.join(formatted_parts)
                        head_trans_md += f"| **{head}头** | {total}次 | {joined_head_str} |\n"
                    st.markdown(head_trans_md, unsafe_allow_html=True)

            # ==========================================
            # 🎯 TAB 4: ✨ 剔除与拐点特赦智能选号引擎
            # ==========================================
            with tab4:
                st.subheader("🎯 智能精选选号（欲出率剔除 + 遗漏拐点特赦）")
                st.markdown("""
                💡 **最新过滤逻辑**：
                1. **删除**：欲出率 < 40% 且 本次遗漏 < 上次遗漏 的生肖对应号码；
                2. **删除**：欲出率 < 40% 且 本次遗漏 < 上次遗漏 的尾数对应号码；
                3. **特赦恢复**：被上述剔除规则标记的号码中，只要其 **生肖** 或 **尾数** 满足【本次遗漏 $\ge$ 上次遗漏】，强制予以特赦恢复保留！
                """)
                
                selected_numbers = []
                for n in range(1, 50):
                    t = n % 10
                    z = get_zodiac_of_number(n)
                    
                    # 规则 1：生肖欲出率 < 0.4 且 本次遗漏 < 上次遗漏
                    r1_remove = (zodiac_rates[z] < 0.4) and (zodiac_omission[z] < zodiac_last_omission[z])
                    
                    # 规则 2：尾数欲出率 < 0.4 且 本次遗漏 < 上次遗漏
                    r2_remove = (tail_rates[t] < 0.4) and (tail_omission[t] < tail_last_omission[t])
                    
                    # 规则 3：特赦恢复条件（生肖本次遗漏 >= 上次遗漏 OR 尾数本次遗漏 >= 上次遗漏）
                    can_restore = (zodiac_omission[z] >= zodiac_last_omission[z]) or (tail_omission[t] >= tail_last_omission[t])
                    
                    # 判定逻辑：被规则1或规则2标记删除，且无法被规则3恢复 -> 剔除；否则保留
                    if (r1_remove or r2_remove) and not can_restore:
                        continue # 被删除，不收入选号网
                    else:
                        selected_numbers.append(n)
                
                selected_numbers.sort() # 严格从小到大按顺序排列
                formatted_nums = [f"{x:02d}" for x in selected_numbers]
                
                st.write("---")
                st.success(f"🏆 **【特赦恢复精选网】本期符合条件的号码共 {len(formatted_nums)} 个（已按由小到大重排）：**")
                st.markdown("👇 **请点击下方代码框右上角的小图标，即可秒级全选复制到剪贴板：**")
                
                if formatted_nums:
                    st.code(", ".join(formatted_nums), language="text")
                else:
                    st.info("提示：当前数据周期内没有符合条件的号码。")
                st.write("---")

    except Exception as global_ex:
        st.error(f"🚨 大盘核心数据解析时发生错误: {global_ex}")
        st.code(traceback.format_exc(), language="text")
