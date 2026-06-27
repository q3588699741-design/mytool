import streamlit as st
import pandas as pd
from collections import defaultdict

# 页面基础配置
st.set_page_config(page_title="数据全维度智能统计看板", layout="wide")
st.title("📊 开奖记录全维度综合统计看板 (全能出号版)")
st.caption("最新总体冷热 ｜ 当前遗漏与欲出几率 ｜ 大局观指标分析 ｜ 状态转移矩阵 ｜ 智能出号 ｜ 历史策略回测")

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
        all_heads = list(range(5)) # 0头到4头
        
        # 2026年岁次丙午马年 1-49 号码生肖对照基准 (1=马, 2=蛇, 3=龙...)
        base_zodiacs = ['马', '蛇', '龙', '兔', '虎', '牛', '鼠', '猪', '狗', '鸡', '猴', '羊']
        def get_zodiac_of_number(n):
            return base_zodiacs[(n - 1) % 12]
            
        st.write("---")
        
        # 🌟 核心排版：升级为 6 大功能 Tabs 选项卡，模块化平铺，绝不遮挡和切断文字
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🔥 1. 大盘总量冷热榜", 
            "⏳ 2. 当前未出遗漏与欲出榜", 
            "📈 3. 大局观综合指标分析", 
            "🔄 4. 前后行状态转移矩阵", 
            "🎯 5. 下期大网智能出号", 
            "🧪 6. 转换规律历史回测引擎"
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
        # TAB 2: 当前未出遗漏与欲出榜
        # ==========================================
        with tab2:
            st.subheader("⏳ 截止当前最新一期：遗漏期数与欲出几率深度统计")
            st.markdown("💡 **数学公式原理**：$$\\text{欲出几率} = \\frac{\\text{当前遗漏期数}}{\\text{历史平均出号间隔}}$$。当数值大于 **1.0** 时，意味着该指标连空时间已打破其历史平均频率，属于高概率回补区间。")
            
            # 各指标遗漏算法
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

            miss_row1_col1, miss_row1_col2 = st.columns(2)
            
            with miss_row1_col1:
                st.markdown("### 🔢 号码遗漏与欲出排行")
                num_list = []
                for n in range(1, 50):
                    miss = num_omission[n]
                    cnt = num_counts[n]
                    avg_interval = (total_records / cnt) if cnt > 0 else total_records
                    exp_rate = miss / avg_interval
                    num_list.append((n, miss, exp_rate, avg_interval))
                num_list.sort(key=lambda x: (-x[2], x[0]))
                
                md = "| 排名 | 号码 | 当前遗漏 | 历史平均间隔 | 欲出几率 | 状态提醒 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                for r, (n, miss, rate, avg_int) in enumerate(num_list, 1):
                    status = "🚨 高危欲出" if rate >= 1.2 else ("🎯 当期刚出" if miss == 0 else "正常")
                    md += f"| {r} | {n:02d} | {miss}期 | {avg_int:.1f}期 | **{rate:.2f}** | {status} |\n"
                st.markdown(md)
                
            with miss_row1_col2:
                st.markdown("### 🔮 生肖遗漏与欲出排行")
                zodiac_list = []
                for z in all_zodiacs:
                    miss = zodiac_omission[z]
                    cnt = zodiac_counts[z]
                    avg_interval = (total_records / cnt) if cnt > 0 else total_records
                    exp_rate = miss / avg_interval
                    zodiac_list.append((z, miss, exp_rate, avg_interval))
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
                tail_list = []
                for t in all_tails:
                    miss = tail_omission[t]
                    cnt = tail_counts[t]
                    avg_interval = (total_records / cnt) if cnt > 0 else total_records
                    exp_rate = miss / avg_interval
                    tail_list.append((t, miss, exp_rate, avg_interval))
                tail_list.sort(key=lambda x: (-x[2], x[0]))
                
                md = "| 排名 | 尾数 | 当前遗漏 | 历史平均间隔 | 欲出几率 | 状态提醒 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                for r, (t, miss, rate, avg_int) in enumerate(tail_list, 1):
                    status = "🚨 高危欲出" if rate >= 1.2 else ("🎯 当期刚出" if miss == 0 else "正常")
                    md += f"| {r} | {t}尾 | {miss}期 | {avg_int:.1f}期 | **{rate:.2f}** | {status} |\n"
                st.markdown(md)

            with miss_row2_col2:
                st.markdown("### 🔝 5个头数遗漏与欲出排行")
                head_counts_dict = defaultdict(int)
                for num, _ in parsed_data: head_counts_dict[num // 10] += 1
                    
                head_list = []
                for h in all_heads:
                    miss = head_omission[h]
                    cnt = head_counts_dict[h]
                    avg_interval = (total_records / cnt) if cnt > 0 else total_records
                    exp_rate = miss / avg_interval
                    head_list.append((h, miss, exp_rate, avg_interval))
                head_list.sort(key=lambda x: (-x[2], x[0]))
                
                md = "| 排名 | 头数 | 当前遗漏 | 历史平均间隔 | 欲出几率 | 状态提醒 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                for r, (h, miss, rate, avg_int) in enumerate(head_list, 1):
                    status = "🚨 高危欲出" if rate >= 1.2 else ("🎯 当期刚出" if miss == 0 else "正常")
                    md += f"| {r} | {h}头 | {miss}期 | {avg_int:.1f}期 | **{rate:.2f}** | {status} |\n"
                st.markdown(md)

        # ==========================================
        # TAB 3: 大局观综合指标分析
        # ==========================================
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

        # ==========================================
        # TAB 4: 前后行状态转移矩阵
        # ==========================================
        with tab4:
            st.subheader("🔄 纵向序列演变规律：当前行开出后，下一行开出什么的概率")
            
            tail_transitions = defaultdict(list)
            zodiac_transitions = defaultdict(list)
            head_transitions = defaultdict(list)
            
            for i in range(len(parsed_data) - 1):
                curr_tail = parsed_data[i][0] % 10
                next_tail = parsed_data[i+1][0] % 10
                tail_transitions[curr_tail].append(next_tail)
                
                curr_zodiac = parsed_data[i][1]
                next_zodiac = parsed_data[i+1][1]
                zodiac_transitions[curr_zodiac].append(next_zodiac)
                
                curr_head = parsed_data[i][0] // 10
                next_head = parsed_data[i+1][0] // 10
                head_transitions[curr_head].append(next_head)
                
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
                    for n in nexts: counts[n] += 1
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

            with trans_col3:
                st.markdown("### 🔝 头数 0-4 后行头数完整分布")
                head_trans_md = "| 当前头数 | 历史总计 | 下一行头数概率分布 (降序排列) |\n| :---: | :---: | :--- |\n"
                for head in range(5):
                    nexts = head_transitions[head]
                    total = len(nexts)
                    counts = defaultdict(int)
                    for n in nexts: counts[n] += 1
                    max_count = max(counts.values()) if counts else 0
                    prob_parts = []
                    for h in all_heads:
                        cnt = counts[h]
                        prob = (cnt / total * 100) if total > 0 else 0.0
                        prob_parts.append((h, cnt, prob))
                    prob_parts.sort(key=lambda x: (-x[1], x[0]))
                    
                    formatted_parts = []
                    for h, c, p in prob_parts:
                        if c == max_count and max_count > 0:
                            formatted_parts.append(f"**{h}头: {p:.1f}%({c}次)**")
                        else:
                            formatted_parts.append(f"{h}头: {p:.1f}%({c}次)")
                    head_trans_md += f"| **{head}头** | {total}次 | {" ｜ ".join(formatted_parts)} |\n"
                st.markdown(head_trans_md, unsafe_allow_html=True)

        # ==========================================
        # 🌟 TAB 5: 下期大网智能出号（✨新加入核心出号模块）
        # ==========================================
        with tab5:
            st.subheader("🎯 三维特征大网交叉：下期智能推荐号码生成器")
            st.markdown("💡 **出号逻辑**：系统自动读取目前表格最后一行（最新开奖），提取其尾数、生肖、头数。然后去转移概率表中找出这三项指标下期**最高频开出（含并列第一名）**的候选池，只要满足任意一项（或逻辑）的 1-49 号码，全部为你精准打捞出来。")
            
            # 先行计算最高频候选池
            best_tail_pred = {}
            for tail, nexts in tail_transitions.items():
                counts = defaultdict(int)
                for n in nexts: counts[n] += 1
                max_count = max(counts.values()) if counts else 0
                best_tail_pred[tail] = [t for t, c in counts.items() if c == max_count] if counts else []

            best_zodiac_pred = {}
            for zodiac, nexts in zodiac_transitions.items():
                counts = defaultdict(int)
                for n in nexts: counts[n] += 1
                max_count = max(counts.values()) if counts else 0
                best_zodiac_pred[zodiac] = [z for z, c in counts.items() if c == max_count] if counts else []

            best_head_pred = {}
            for head, nexts in head_transitions.items():
                counts = defaultdict(int)
                for n in nexts: counts[n] += 1
                max_count = max(counts.values()) if counts else 0
                best_head_pred[head] = [h for h, c in counts.items() if c == max_count] if counts else []

            # 获取表格里最后一期的最新数据
            last_num, last_zodiac = parsed_data[-1]
            last_tail = last_num % 10
            last_head = last_num // 10
            
            st.info(f"📋 **大盘最新数据定位**：上一期号码为 `**{last_num:02d}**`，生肖为 `**{last_zodiac}**` （即：{last_head}头、{last_tail}尾）")
            
            p_tails = best_tail_pred.get(last_tail, [])
            p_zods = best_zodiac_pred.get(last_zodiac, [])
            p_heads = best_head_pred.get(last_head, [])
            
            # 显示当前的决策池
            t_tips = "、".join([f"{x}尾" for x in sorted(p_tails)])
            z_tips = "、".join(p_zods)
            h_tips = "、".join([f"{x}头" for x in sorted(p_heads)])
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"🔢 历史规律：{last_tail}尾下期更易出 → **{t_tips}**")
            c2.markdown(f"🔮 历史规律：{last_zodiac}肖下期更易出 → **{z_tips}**")
            c3.markdown(f"🔝 历史规律：{last_head}头下期更易出 → **{h_tips}**")
            
            # 扫描大盘 1-49
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
                st.success(f"🏁 **全网打捞成功！同时满足上述任一特征的号码共 {len(final_selected_numbers)} 个（已从小到大严格排序）**")
                st.markdown("👇 **请点击下方文本框右上角的图标，即可一键全选复制号码：**")
                
                out_string = ", ".join(final_selected_numbers)
                st.code(out_string, language="text")
            else:
                st.warning("⚠️ 提示：大盘中没有符合要求的号码。")

        # ==========================================
        # TAB 6: 转换规律历史回测引擎
        # ==========================================
        with tab6:
            st.subheader("🧪 状态转移策略历史回测复盘引擎 (三维度或逻辑版)")
            st.markdown("💡 **回测规则**：系统模拟历史全量演变。只要下期的实际开奖结果落入【最高频尾数】**或者**【最高频生肖】**或者**【最高频头数】的任意一个目标池中，即算作拦截命中。")
            
            if st.button("🚀 开启三维特征全量历史大回测", type="primary"):
                hit_count = 0
                test_total = len(parsed_data) - 1
                hit_details = []

                for i in range(test_total):
                    c_num, c_zod = parsed_data[i]
                    n_num, n_zod = parsed_data[i+1]
                    
                    p_tails_test = best_tail_pred.get(c_num % 10, [])
                    p_zods_test = best_zodiac_pred.get(c_zod, [])
                    p_heads_test = best_head_pred.get(c_num // 10, [])
                    
                    tail_hit = (n_num % 10 in p_tails_test)
                    zodiac_hit = (n_zod in p_zods_test)
                    head_hit = (n_num // 10 in p_heads_test)
                    
                    if tail_hit or zodiac_hit or head_hit:
                        hit_count += 1
                        hit_tags = []
                        if tail_hit: hit_tags.append("尾数")
                        if zodiac_hit: hit_tags.append("生肖")
                        if head_hit: hit_tags.append("头数")
                        
                        if len(hit_tags) == 3:
                            tag = " [🔥三重全中!!!]"
                        else:
                            tag = f" [🎯仅{'和'.join(hit_tags)}中]"
                            
                        hit_details.append(f"第 {i+2:03d} 行（前一期 `{c_num},{c_zod}`）：下期开出 `{n_num},{n_zod}`{tag}")

                b_col1, b_col2, b_col3 = st.columns(3)
                b_col1.metric("📋 总模拟检验样本数", f"{test_total} 期")
                b_col2.metric("🎯 复合命中总期数 (满足任一)", f"{hit_count} 期")
                b_col3.metric("📊 综合历史捕获率 (三维或逻辑)", f"{(hit_count / test_total * 100):.2f}%")

                st.write("---")
                st.success(f"🏁 三维历史大回测完成！综合历史拦截胜率达 **{(hit_count / test_total * 100):.2f}%**。以下为命中明细清单：")
                st.code("\n".join(hit_details), language="text")
