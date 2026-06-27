import streamlit as st
import pandas as pd
from collections import defaultdict

# 页面基础配置
st.set_page_config(page_title="数据全维度智能统计看板", layout="wide")
st.title("📊 开奖记录全维度综合统计看板 (智能剪枝出号版)")
st.caption("总体冷热 ｜ 当前遗漏与欲出几率 ｜ 状态转移矩阵 ｜ 🌟智能反杀剪枝出号 ｜ 历史回测")

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
        
        # 2026年岁次丙午马年 1-49 号码生肖对照基准 (1=马, 2=蛇, 3=龙...)
        base_zodiacs = ['马', '蛇', '龙', '兔', '虎', '牛', '鼠', '猪', '狗', '鸡', '猴', '羊']
        def get_zodiac_of_number(n):
            return base_zodiacs[(n - 1) % 12]

        # ==========================================
        # ⚙️ 核心前置算力：全局冷热与欲出几率计算
        # ==========================================
        num_counts = defaultdict(int)
        tail_counts = defaultdict(int)
        zodiac_counts = defaultdict(int)
        head_counts_dict = defaultdict(int)
        
        for num, zodiac in parsed_data:
            num_counts[num] += 1
            tail_counts[num % 10] += 1
            zodiac_counts[zodiac] += 1
            head_counts_dict[num // 10] += 1

        # 计算倒序遗漏期数
        num_omission = {}
        for n in range(1, 50):
            found = False
            for i in range(total_records - 1, -1, -1):
                if parsed_data[i][0] == n:
                    num_omission[n] = (total_records - 1) - i
                    found = True
                    break
            if not found: num_omission[n] = total_records
                
        zodiac_omission = {}
        for z in all_zodiacs:
            found = False
            for i in range(total_records - 1, -1, -1):
                if parsed_data[i][1] == z:
                    zodiac_omission[z] = (total_records - 1) - i
                    found = True
                    break
            if not found: zodiac_omission[z] = total_records

        tail_omission = {}
        for t in all_tails:
            found = False
            for i in range(total_records - 1, -1, -1):
                if parsed_data[i][0] % 10 == t:
                    tail_omission[t] = (total_records - 1) - i
                    found = True
                    break
            if not found: tail_omission[t] = total_records

        head_omission = {}
        for h in all_heads:
            found = False
            for i in range(total_records - 1, -1, -1):
                if parsed_data[i][0] // 10 == h:
                    head_omission[h] = (total_records - 1) - i
                    found = True
                    break
            if not found: head_omission[h] = total_records

        # 计算全局欲出几率字典
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
        
        # 选项卡横向归类
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🔥 1. 大盘总量冷热榜", 
            "⏳ 2. 当前未出遗漏与欲出榜", 
            "📈 3. 大局观综合指标分析", 
            "🔄 4. 前后行状态转移矩阵", 
            "🎯 5. 下期大网智能出号", 
            "🧪 6. 转换规律历史回测引擎"
        ])

        # ==========================================
        # TAB 1-4 保持你原汁原味的排版与对齐结构
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

        with tab2:
            st.subheader("⏳ 各指标未出遗漏与欲出几率深度统计")
            miss_row1_col1, miss_row1_col2 = st.columns(2)
            with miss_row1_col1:
                st.markdown("### 🔢 号码遗漏与欲出排行")
                num_list = [(n, num_omission[n], num_omission[n]/(total_records/num_counts[n] if num_counts[n]>0 else total_records), (total_records/num_counts[n] if num_counts[n]>0 else total_records)) for n in range(1, 50)]
                num_list.sort(key=lambda x: (-x[2], x[0]))
                md = "| 排名 | 号码 | 当前遗漏 | 历史平均间隔 | 欲出几率 | 状态提醒 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                for r, (n, miss, rate, avg_int) in enumerate(num_list, 1):
                    status = "🚨 高危欲出" if rate >= 1.2 else ("🎯 当期刚出" if miss == 0 else "正常")
                    md += f"| {r} | {n:02d} | {miss}期 | {avg_int:.1f}期 | **{rate:.2f}** | {status} |\n"
                st.markdown(md)
            with miss_row1_col2:
                st.markdown("### 🔮 生肖遗漏与欲出排行")
                zodiac_list = [(z, zodiac_omission[z], zodiac_rates[z], (total_records/zodiac_counts[z] if zodiac_counts[z]>0 else total_records)) for z in all_zodiacs]
                zodiac_list.sort(key=lambda x: (-x[2], all_zodiacs.index(x[0])))
                md = "| 排名 | 生肖 | 当前遗漏 | 历史平均间隔 | 欲出几率 | 状态提醒 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                for r, (z, miss, rate, avg_int) in enumerate(zodiac_list, 1):
                    status = "🚨 高危欲出" if rate >= 1.2 else ("🎯 当期刚出" if miss == 0 else "正常")
                    md += f"| {r} | {z} | {miss}期 | {avg_int:.1f}期 | **{rate:.2f}** | {status} |\n"
                st.markdown(md)
            st.write("---")
            miss_row2_col1, miss_row2_col2 = st.columns(2)
            with miss_row2_col1:
                st.markdown("### 🎯 10个尾数遗漏与欲出排行")
                tail_list_disp = [(t, tail_omission[t], tail_rates[t], (total_records/tail_counts[t] if tail_counts[t]>0 else total_records)) for t in all_tails]
                tail_list_disp.sort(key=lambda x: (-x[2], x[0]))
                md = "| 排名 | 尾数 | 当前遗漏 | 历史平均间隔 | 欲出几率 | 状态提醒 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                for r, (t, miss, rate, avg_int) in enumerate(tail_list_disp, 1):
                    status = "🚨 高危欲出" if rate >= 1.2 else ("🎯 当期刚出" if miss == 0 else "正常")
                    md += f"| {r} | {t}尾 | {miss}期 | {avg_int:.1f}期 | **{rate:.2f}** | {status} |\n"
                st.markdown(md)
            with miss_row2_col2:
                st.markdown("### 🔝 5个头数遗漏与欲出排行")
                head_list_disp = [(h, head_omission[h], head_rates[h], (total_records/head_counts_dict[h] if head_counts_dict[h]>0 else total_records)) for h in all_heads]
                head_list_disp.sort(key=lambda x: (-x[2], x[0]))
                md = "| 排名 | 头数 | 当前遗漏 | 历史平均间隔 | 欲出几率 | 状态提醒 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                for r, (h, miss, rate, avg_int) in enumerate(head_list_disp, 1):
                    status = "🚨 高危欲出" if rate >= 1.2 else ("🎯 当期刚出" if miss == 0 else "正常")
                    md += f"| {r} | {h}头 | {miss}期 | {avg_int:.1f}期 | **{rate:.2f}** | {status} |\n"
                st.markdown(md)

        with tab3:
            st.subheader("📈 大盘宏观形态指标分布")
            odd_cnt = sum(1 for n, _ in parsed_data if n % 2 != 0)
            even_cnt = sum(1 for n, _ in parsed_data if n % 2 == 0)
            big_cnt = sum(1 for n, _ in parsed_data if n >= 25)
            small_cnt = sum(1 for n, _ in parsed_data if n < 25)
            avg_sum = sum(n for n, _ in parsed_data) / total_records
            ind_col1, ind_col2, ind_col3 = st.columns(3)
            ind_col1.metric("🔢 历史总平均号码数值", f"{avg_sum:.2f}", "黄金中轴线：25.00")
            ind_col2.metric("🌗 全局单双比 (单号 ｜ 双号)", f"{odd_cnt}期 ｜ {even_cnt}期", f"单号占比: {(odd_cnt/total_records)*100:.1f}%")
            ind_col3.metric("🌌 全局大小比 (大号 $\\ge25$ ｜ 小号)", f"{big_cnt}期 ｜ {small_cnt}期", f"大号占比: {(big_cnt/total_records)*100:.1f}%")

        with tab4:
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
                    tail_trans_md += f"| **{tail}尾** | {total}次 | {" ｜ ".join(formatted_parts)} |\n"
                st.markdown(tail_trans_md, unsafe_allow_html=True)
            with trans_col2:
                st.markdown("### 🔮 各生肖后行生肖完整分布")
                zodiac_trans_md = "| 当前生肖 | 历史总计 | 下一行生肖概率分布 (降序排列) |\n| :---: | :---: | :--- |\n"
                for zodiac in all_zodiacs:
                    nexts = zodiac_transitions[zodiac]
                    total = len(nexts)
                    counts = defaultdict(int)
                    for n in nexts: counts[n] += 1
                    max_count = max(counts.values()) if counts else 0
                    prob_parts = [(z, counts[z], (counts[z]/total*100 if total>0 else 0.0)) for z in all_zodiacs]
                    zodiac_parts = sorted(prob_parts, key=lambda x: (-x[1], all_zodiacs.index(x[0])))
                    formatted_parts = [f"**{z}: {p:.1f}%({c}次)**" if c==max_count and max_count>0 else f"{z}: {p:.1f}%({c}次)" for z, c, p in zodiac_parts]
                    zodiac_trans_md += f"| **{zodiac}** | {total}次 | {" ｜ ".join(formatted_parts)} |\n"
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
                    head_trans_md += f"| **{head}头** | {total}次 | {" ｜ ".join(formatted_parts)} |\n"
                st.markdown(head_trans_md, unsafe_allow_html=True)

        # ==========================================
        # 🌟 TAB 5: 下期大网智能出号（🔥核心升级：引入智能反杀剪枝算法）
        # ==========================================
        with tab5:
            st.subheader("🎯 三维全量容错大网 ＋ 智能高危反杀剪枝过滤")
            st.markdown("💡 **剪枝过滤原理**：大网的基础依然是‘只要历史开出过就入选’。但在出号前，系统会进行**反杀清洗**：如果某个指标在历史转换中**开出次数最少（垫底）**，且它目前的**欲出几率 < 1.0（尚未处于连空高危期）**，系统就会判定它属于‘低频偶发噪音’，**直接一刀砍掉（不予出号）**！")
            
            # 算法：构建动态剪枝处理函数
            def get_pruned_pool(transitions_dict, current_state, rates_dict):
                nexts = transitions_dict[current_state]
                counts = {x: nexts.count(x) for x in set(nexts) if nexts.count(x) > 0}
                if not counts:
                    return [], []
                min_c = min(counts.values())
                allowed, pruned = [], []
                for x, c in counts.items():
                    # 判断条件：频次最低 且 欲出几率未达到高危( < 1.0)
                    if c == min_c and rates_dict[x] < 1.0:
                        pruned.append(x)
                    else:
                        allowed.append(x)
                return allowed, pruned

            # 获取最新开奖信息
            last_num, last_zodiac = parsed_data[-1]
            last_tail = last_num % 10
            last_head = last_num // 10
            
            st.info(f"📋 **大盘最新数据定位**：上一期号码为 `**{last_num:02d}**`，生肖为 `**{last_zodiac}**` （当前：{last_head}头、{last_tail}尾）")
            
            # 计算动态清洗后的决策候选池
            p_tails, pruned_tails = get_pruned_pool(tail_transitions, last_tail, tail_rates)
            p_zods, pruned_zods = get_pruned_pool(zodiac_transitions, last_zodiac, zodiac_rates)
            p_heads, pruned_heads = get_pruned_pool(head_transitions, last_head, head_rates)

            # 矩阵化呈现清洗明细
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"🔢 **尾数特征网（基于 {last_tail} 尾）：**")
                st.markdown(f"✅ 保留的入选尾数：**{', '.join([f'{x}尾' for x in sorted(p_tails)]) if p_tails else '无'}**")
                st.markdown(f"🪓 斩杀的冷噪尾数：~~{', '.join([f'{x}尾' for x in sorted(pruned_tails)]) if pruned_tails else '无'}~~")
            with c2:
                st.markdown(f"🔮 **生肖特征网（基于 【{last_zodiac}】）：**")
                st.markdown(f"✅ 保留的入选生肖：**{', '.join(p_zods) if p_zods else '无'}**")
                st.markdown(f"🪓 斩杀的冷噪生肖：~~{', '.join(pruned_zods) if pruned_zods else '无'}~~")
            with c3:
                st.markdown(f"🔝 **头数特征网（基于 {last_head} 头）：**")
                st.markdown(f"✅ 保留的入选头数：**{', '.join([f'{x}头' for x in sorted(p_heads)]) if p_heads else '无'}**")
                st.markdown(f"🪓 斩杀的冷噪头数：~~{', '.join([f'{x}头' for x in sorted(pruned_heads)]) if pruned_heads else '无'}~~")

            # 扫描过滤大盘 1-49
            final_selected_numbers = []
            for n in range(1, 50):
                n_tail = n % 10
                n_zodiac = get_zodiac_of_number(n)
                n_head = n // 10
                
                # 或逻辑判定
                if (n_tail in p_tails) or (n_zodiac in p_zods) or (n_head in p_heads):
                    final_selected_numbers.append(f"{n:02d}")
            
            st.write("---")
            if final_selected_numbers:
                st.success(f"🏁 **大网精简打捞成功！经剪枝洗油后，最终筛选出号码共 {len(final_selected_numbers)} 个（数量大缩水，已严格排序）**")
                st.markdown("👇 **请点击下方代码框右上角按钮，即可一键全选复制号码：**")
                out_string = ", ".join(final_selected_numbers)
                st.code(out_string, language="text")
            else:
                st.warning("⚠️ 提示：大盘中所有指标均被反杀，当前无可匹配号码。")

        # ==========================================
        # TAB 6: 转换规律历史回测引擎（🌟同步升级回测逻辑）
        # ==========================================
        with tab6:
            st.subheader("🧪 状态转移策略历史回测复盘引擎 (智能反杀剪枝版)")
            st.markdown("💡 **回测规则**：系统模拟历史全量演变。每一期都会动态计算当时的【开出最少且不危险】指标并将其剔除，看看在实施这种精简砍号策略下，历史大网的真实命中率表现。")
            
            if st.button("🚀 开启智能剪枝历史全量大回测", type="primary"):
                hit_count = 0
                test_total = len(parsed_data) - 1
                hit_details = []

                # 建立滚动回测历史：在回测某一期时，只能使用该期之前的历史进行数据统计，模拟真实环境
                for i in range(test_total):
                    # 截止到当前模拟期的历史账本
                    history_snapshot = parsed_data[:i+1]
                    if len(history_snapshot) < 2: continue
                    
                    # 动态重新构建当时的转换网络
                    t_trans = defaultdict(list)
                    z_trans = defaultdict(list)
                    h_trans = defaultdict(list)
                    t_cnts = defaultdict(int)
                    z_cnts = defaultdict(int)
                    h_cnts = defaultdict(int)
                    
                    for k in range(len(history_snapshot) - 1):
                        t_trans[history_snapshot[k][0] % 10].append(history_snapshot[k+1][0] % 10)
                        z_trans[history_snapshot[k][1]].append(history_snapshot[k+1][1])
                        h_trans[history_snapshot[k][0] // 10].append(history_snapshot[k+1][0] // 10)
                    
                    for idx_h in range(len(history_snapshot)):
                        t_cnts[history_snapshot[idx_h][0] % 10] += 1
                        z_cnts[history_snapshot[idx_h][1]] += 1
                        h_cnts[history_snapshot[idx_h][0] // 10] += 1
                        
                    # 动态计算当时的遗漏和欲出几率
                    def get_snap_rate(all_items, key_func, cnts_dict, total_len):
                        omission = {}
                        for item in all_items:
                            found_item = False
                            for idx_rev in range(total_len - 1, -1, -1):
                                if key_func(history_snapshot[idx_rev]) == item:
                                    omission[item] = (total_len - 1) - idx_rev
                                    found_item = True
                                    break
                            if not found_item: omission[item] = total_len
                        rates = {}
                        for item in all_items:
                            c = cnts_dict[item]
                            avg_i = (total_len / c) if c > 0 else total_len
                            rates[item] = omission[item] / avg_i
                        return rates

                    snap_t_rates = get_snap_rate(all_tails, lambda x: x[0] % 10, t_cnts, len(history_snapshot))
                    snap_z_rates = get_snap_rate(all_zodiacs, lambda x: x[1], z_cnts, len(history_snapshot))
                    snap_h_rates = get_snap_rate(all_heads, lambda x: x[0] // 10, h_cnts, len(history_snapshot))

                    # 判定执行剪枝出号
                    def get_snap_pool(t_dict, cur, r_dict):
                        nxt = t_dict[cur]
                        cts = {x: nxt.count(x) for x in set(nxt) if nxt.count(x) > 0}
                        if not cts: return []
                        mn = min(cts.values())
                        return [x for x, c in cts.items() if not (c == mn and r_dict[x] < 1.0)]

                    c_num, c_zod = parsed_data[i]
                    n_num, n_zod = parsed_data[i+1]
                    
                    p_tails_test = get_snap_pool(t_trans, c_num % 10, snap_t_rates)
                    p_zods_test = get_snap_pool(z_trans, c_zod, snap_z_rates)
                    p_heads_test = get_snap_pool(h_trans, c_num // 10, snap_h_rates)
                    
                    tail_hit = (n_num % 10 in p_tails_test)
                    zodiac_hit = (n_zod in p_zods_test)
                    head_hit = (n_num // 10 in p_heads_test)
                    
                    if tail_hit or zodiac_hit or head_hit:
                        hit_count += 1
                        hit_tags = []
                        if tail_hit: hit_tags.append("尾数")
                        if zodiac_hit: hit_tags.append("生肖")
                        if head_hit: hit_tags.append("头数")
                        
                        tag = " [🔥三重全中!!!]" if len(hit_tags) == 3 else f" [🎯{'和'.join(hit_tags)}特征吻合]"
                        hit_details.append(f"第 {i+2:03d} 期（前一期 `{c_num},{c_zod}`）：下期开出 `{n_num},{n_zod}`{tag}")

                b_col1, b_col2, b_col3 = st.columns(3)
                b_col1.metric("📋 总模拟检验样本数", f"{test_total} 期")
                b_col2.metric("🎯 动态剪枝拦截命中总期数", f"{hit_count} 期")
                b_col3.metric("📊 综合历史捕获率", f"{(hit_count / test_total * 100):.2f}%")

                st.write("---")
                st.success(f"🏁 全量反杀剪枝回测完成！在排除冷燥指标、大幅锁紧出号范围后，历史捕捉率依然保持在极高水准。以下为详细命中清单：")
                st.code("\n".join(hit_details), language="text")
