import streamlit as st
import pandas as pd
from collections import defaultdict

# 页面基础配置
st.set_page_config(page_title="数据全维度智能统计看板", layout="wide")
st.title("📊 记录全维度综合统计看板 (终极算力版)")
st.caption("最新总体冷热 ｜ 当前遗漏与欲出几率 ｜ 大局观指标分析 ｜ 状态转移矩阵 ｜ 历史策略回测")

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
        all_heads = list(range(5))
        
        st.write("---")
        
        # 🌟 核心排版：扩展为 5 大功能 Tabs 选项卡，界面干净规整，绝不遮挡文字
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔥 1. 大盘总量冷热榜", 
            "⏳ 2. 当前未出遗漏与欲出榜", 
            "📈 3. 大局观综合指标分析",
            "🔄 4. 前后行状态转移矩阵",
            "🧪 5. 转换规律历史回测引擎"
        ])

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
        # TAB 2: 当前未出遗漏与欲出榜（🌟引入欲出几率模型）
        # ==========================================
        with tab2:
            st.subheader("⏳ 截止当前最新一期：遗漏期数与欲出几率深度统计")
            st.markdown("💡 **数学公式原理**：$$\\text{欲出几率} = \\frac{\\text{当前遗漏期数}}{\\text{历史平均出号间隔}}$$。当数值大于 **1.0** 时，意味着该指标连空时间已打破其历史平均频率，属于高概率回补区间。")
            
            # 1. 号码遗漏与欲出
            num_omission = {}
            for n in range(1, 49 + 1):
                found = False
                for i in range(total_records - 1, -1, -1):
                    if parsed_data[i][0] == n:
                        num_omission[n] = (total_records - 1) - i
                        found = True
                        break
                if not found:
                    num_omission[n] = total_records
                    
            # 2. 生肖遗漏与欲出
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

            # 3. 尾数遗漏与欲出
            tail_omission = {}
            for t in all_tails:
                found = False
                for i in range(total_records - 1, -1, -1):
                    if parsed_data[i][0] % 10 == t:
                        tail_omission[t] = (total_records - 1) - i
                        found = True
                        break
                if not found:
                    tail_omission[t] = total_records

            # 4. 头数遗漏与欲出
            head_omission = {}
            for h in all_heads:
                found = False
                for i in range(total_records - 1, -1, -1):
                    if parsed_data[i][0] // 10 == h:
                        head_omission[h] = (total_records - 1) - i
                        found = True
                        break
                if not found:
                    head_omission[h] = total_records

            # 渲染双行两列对齐布局
            miss_row1_col1, miss_row1_col2 = st.columns(2)
            
            with miss_row1_col1:
                st.markdown("### 🔢 号码遗漏与欲出排行")
                # 按照欲出几率降序排序
                num_list = []
                for n in range(1, 50):
                    miss = num_omission[n]
                    cnt = num_counts[n]
                    avg_interval = (total_records / cnt) if cnt > 0 else total_records
                    exp_rate = miss / avg_interval
                    num_list.append((n, miss, exp_rate))
                num_list.sort(key=lambda x: (-x[2], x[0]))
                
                md = "| 排名 | 号码 | 当前遗漏 | 历史平均间隔 | 欲出几率 | 状态提醒 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                for r, (n, miss, rate) in enumerate(num_list, 1):
                    status = "🚨 高危欲出" if rate >= 1.2 else ("🎯 当期刚出" if miss == 0 else "正常")
                    md += f"| {r} | {n:02d} | {miss}期 | {avg_interval:.1f}期 | **{rate:.2f}** | {status} |\n"
                st.markdown(md)
                
            with miss_row1_col2:
                st.markdown("### 🔮 生肖遗漏与欲出排行")
                zodiac_list = []
                for z in all_zodiacs:
                    miss = zodiac_omission[z]
                    cnt = zodiac_counts[z]
                    avg_interval = (total_records / cnt) if cnt > 0 else total_records
                    exp_rate = miss / avg_interval
                    zodiac_list.append((z, miss, exp_rate))
                zodiac_list.sort(key=lambda x: (-x[2], all_zodiacs.index(x[0])))
                
                md = "| 排名 | 生肖 | 当前遗漏 | 历史平均间隔 | 欲出几率 | 状态提醒 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                for r, (z, miss, rate) in enumerate(zodiac_list, 1):
                    status = "🚨 高危欲出" if rate >= 1.2 else ("🎯 当期刚出" if miss == 0 else "正常")
                    md += f"| {r} | {z} | {miss}期 | {avg_interval:.1f}期 | **{rate:.2f}** | {status} |\n"
                st.markdown(md)

            st.write("---")
            miss_row2_col1, miss_row2_col2 = st.columns(2)

            with miss_row2_col1:
                st.markdown("### 🎯 10个尾数遗漏与欲出排行")
                tail_list = []
                for t in all_tails:
                    miss = tail_omission[t]
                    cnt = tail_counts[t]
                    avg_interval = (total_records / cnt) if cnt > 0 else total_records
                    exp_rate = miss / avg_interval
                    tail_list.append((t, miss, exp_rate))
                tail_list.sort(key=lambda x: (-x[2], x[0]))
                
                md = "| 排名 | 尾数 | 当前遗漏 | 历史平均间隔 | 欲出几率 | 状态提醒 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                for r, (t, miss, rate) in enumerate(tail_list, 1):
                    status = "🚨 高危欲出" if rate >= 1.2 else ("🎯 当期刚出" if miss == 0 else "正常")
                    md += f"| {r} | {t}尾 | {miss}期 | {avg_interval:.1f}期 | **{rate:.2f}** | {status} |\n"
                st.markdown(md)

            with miss_row2_col2:
                st.markdown("### 🔝 5个头数遗漏与欲出排行")
                head_counts_dict = defaultdict(int)
                for num, _ in parsed_data:
                    head_counts_dict[num // 10] += 1
                    
                head_list = []
                for h in all_heads:
                    miss = head_omission[h]
                    cnt = head_counts_dict[h]
                    avg_interval = (total_records / cnt) if cnt > 0 else total_records
                    exp_rate = miss / avg_interval
                    head_list.append((h, miss, exp_rate))
                head_list.sort(key=lambda x: (-x[2], x[0]))
                
                md = "| 排名 | 头数 | 当前遗漏 | 历史平均间隔 | 欲出几率 | 状态提醒 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                for r, (h, miss, rate) in enumerate(head_list, 1):
                    status = "🚨 高危欲出" if rate >= 1.2 else ("🎯 当期刚出" if miss == 0 else "正常")
                    md += f"| {r} | {h}头 | {miss}期 | {avg_interval:.1f}期 | **{rate:.2f}** | {status} |\n"
                st.markdown(md)

        # ==========================================
        # TAB 3: 大局观综合指标分析（✨全新功能模块）
        # ==========================================
        with tab3:
            st.subheader("📈 大盘宏观形态指标分布")
            st.caption("通过观测全局偏好比例，防止选号偏离统计大盘。")
            
            # 计算宏观比例
            odd_cnt = sum(1 for n, _ in parsed_data if n % 2 != 0)
            even_cnt = sum(1 for n, _ in parsed_data if n % 2 == 0)
            big_cnt = sum(1 for n, _ in parsed_data if n >= 25)
            small_cnt = sum(1 for n, _ in parsed_data if n < 25)
            avg_sum = sum(n for n, _ in parsed_data) / total_records
            
            ind_col1, ind_col2, ind_col3 = st.columns(3)
            ind_col1.metric("🔢 历史总平均号码数值", f"{avg_sum:.2f}", "黄金中轴线线：25.00")
            ind_col2.metric("🌗 全局单双比 (单号 ｜ 双号)", f"{odd_cnt}期 ｜ {even_cnt}期", f"单号占比: {(odd_cnt/total_records)*100:.1f}%")
            ind_col3.metric("🌌 全局大小比 (大号 $\\ge24$ ｜ 小号)", f"{big_cnt}期 ｜ {small_cnt}期", f"大号占比: {(big_cnt/total_records)*100:.1f}%")

        # ==========================================
        # TAB 4: 前后行状态转移矩阵
        # ==========================================
        with tab3 or tab4: # 保持原转移逻辑
            if "tab4" in locals() or "tab4" in globals():
                current_tab = tab4
            else:
                current_tab = tab3
                
        with current_tab:
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

        # ==========================================
        # TAB 5: 转换规律历史回测引擎（✨全新黑科技模块）
        # ==========================================
        with tab5:
            st.subheader("🧪 状态转移策略历史回测复盘引擎")
            st.markdown("说明：点击下方按钮后，系统会模拟在历史所有期数中，每次都采用**当前尾数下期最高频尾数（含并列） 且 当前生肖下期最高频生肖（含并列）**的复合池进行全量对答案判定。")
            
            if st.button("🚀 开启全量历史大回测", type="primary"):
                # 重新计算各最高频候选集
                best_tail_pred = {}
                for tail, nexts in tail_transitions.items():
                    counts = defaultdict(int)
                    for n in nexts: counts[n] += 1
                    max_count = max(counts.values())
                    best_tail_pred[tail] = [t for t, c in counts.items() if c == max_count]

                best_zodiac_pred = {}
                for zodiac, nexts in zodiac_transitions.items():
                    counts = defaultdict(int)
                    for n in nexts: counts[n] += 1
                    max_count = max(counts.values())
                    best_zodiac_pred[zodiac] = [z for z, c in counts.items() if c == max_count]

                # 回测循环
                hit_count = 0
                test_total = len(parsed_data) - 1
                hit_details = []

                for i in range(test_total):
                    c_num, c_zod = parsed_data[i]
                    n_num, n_zod = parsed_data[i+1]
                    
                    p_tails = best_tail_pred.get(c_num % 10, [])
                    p_zods = best_zodiac_pred.get(c_zod, [])
                    
                    if (n_num % 10 in p_tails) and (n_zod in p_zods):
                        hit_count += 1
                        hit_details.append(f"第 {i+2} 行（基于第 {i+1} 行 `{c_num},{c_zod}` 预测）：成功抓获下一期 `{n_num},{n_zod}` 🎯")

                # 结果大屏渲染
                b_col1, b_col2, b_col3 = st.columns(3)
                b_col1.metric("📋 总模拟检验样本数", f"{test_total} 期")
                b_col2.metric("🎯 完美双中总期数", f"{hit_count} 期")
                b_col3.metric("📊 综合历史命中率", f"{(hit_count / test_total * 100):.2f}%")

                st.write("---")
                st.success(f"🏁 历史大回测完成！当前数据下该特征的实战拦截率为 **{(hit_count / test_total * 100):.2f}%**。以下为完美的双命中期数明细：")
                st.code("\n".join(hit_details), language="text")
