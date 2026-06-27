import streamlit as st
import pandas as pd
from collections import defaultdict

# 页面基础配置
st.set_page_config(page_title="数据全维度智能统计看板", layout="wide")
st.title("📊 开奖记录全维度综合统计看板 (前6名精选+高危护航版)")
st.caption("最新总体冷热 ｜ 当前遗漏与欲出几率 ｜ 状态转移矩阵 ｜ 🎯前6名+高危补回智能出号 ｜ 🧪策略历史回测")

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
        
        for num, zodiac in parsed_data:
            num_counts[num] += 1
            tail_counts[num % 10] += 1
            zodiac_counts[zodiac] += 1

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

        # 计算状态转移数据
        tail_transitions = defaultdict(list)
        zodiac_transitions = defaultdict(list)
        for i in range(len(parsed_data) - 1):
            tail_transitions[parsed_data[i][0] % 10].append(parsed_data[i+1][0] % 10)
            zodiac_transitions[parsed_data[i][1]].append(parsed_data[i+1][1])

        st.write("---")
        
        # 选项卡横向归类 (砍掉头数，合并为 5 个大标签)
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔥 1. 大盘总量冷热榜", 
            "⏳ 2. 当前未出遗漏与欲出榜", 
            "📈 3. 大局观综合指标分析", 
            "🔄 4. 前后行状态转移矩阵", 
            "🎯 5. 下期大网智能出号"
        ])

        # ==========================================
        # TAB 1: 大盘总量冷热榜
        # ==========================================
        with tab1:
            st.subheader("📊 整体出现次数总计（按频率从高到低排列）")
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
        # TAB 2: 当前未出遗漏与欲出榜 (对齐优化)
        # ==========================================
        with tab2:
            st.subheader("⏳ 各指标未出遗漏与欲出几率深度统计")
            miss_col1, miss_col2, miss_col3 = st.columns(3)
            with miss_col1:
                st.markdown("### 🔢 号码遗漏与欲出排行")
                num_list = [(n, num_omission[n], num_omission[n]/(total_records/num_counts[n] if num_counts[n]>0 else total_records), (total_records/num_counts[n] if num_counts[n]>0 else total_records)) for n in range(1, 50)]
                num_list.sort(key=lambda x: (-x[2], x[0]))
                md = "| 排名 | 号码 | 当前遗漏 | 历史平均间隔 | 欲出几率 |\n| :---: | :---: | :---: | :---: | :---: |\n"
                for r, (n, miss, rate, avg_int) in enumerate(num_list, 1):
                    md += f"| {r} | {n:02d} | {miss}期 | {avg_int:.1f}期 | **{rate:.2f}** |\n"
                st.markdown(md)
            with miss_col2:
                st.markdown("### 🔮 生肖遗漏与欲出排行")
                zodiac_list = [(z, zodiac_omission[z], zodiac_rates[z], (total_records/zodiac_counts[z] if zodiac_counts[z]>0 else total_records)) for z in all_zodiacs]
                zodiac_list.sort(key=lambda x: (-x[2], all_zodiacs.index(x[0])))
                md = "| 排名 | 生肖 | 当前遗漏 | 历史平均间隔 | 欲出几率 |\n| :---: | :---: | :---: | :---: | :---: |\n"
                for r, (z, miss, rate, avg_int) in enumerate(zodiac_list, 1):
                    md += f"| {r} | {z} | {miss}期 | {avg_int:.1f}期 | **{rate:.2f}** |\n"
                st.markdown(md)
            with miss_col3:
                st.markdown("### 🎯 10个尾数遗漏与欲出排行")
                tail_list_disp = [(t, tail_omission[t], tail_rates[t], (total_records/tail_counts[t] if tail_counts[t]>0 else total_records)) for t in all_tails]
                tail_list_disp.sort(key=lambda x: (-x[2], x[0]))
                md = "| 排名 | 尾数 | 当前遗漏 | 历史平均间隔 | 欲出几率 |\n| :---: | :---: | :---: | :---: | :---: |\n"
                for r, (t, miss, rate, avg_int) in enumerate(tail_list_disp, 1):
                    md += f"| {r} | {t}尾 | {miss}期 | {avg_int:.1f}期 | **{rate:.2f}** |\n"
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
        # TAB 4: 前后行状态转移矩阵 (双列纯净版)
        # ==========================================
        with tab4:
            st.subheader("🔄 纵向序列演变规律概率分布")
            trans_col1, trans_col2 = st.columns(2)
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

        # ==========================================
        # 🌟 TAB 5: 下期大网智能出号 + 🧪 滚动回测引擎 (合并单页联动)
        # ==========================================
        with tab5:
            st.subheader("🎯 前 6 名转换池（含并列） ＋ 🚨冷皇高危护航特赦模型")
            
            # --- 算法：获取前六名及高危特赦的核心处理函数 ---
            def get_advanced_pool(transitions_dict, current_state, rates_dict, items_list):
                nexts = transitions_dict[current_state]
                counts = {x: nexts.count(x) for x in items_list}
                
                # 排序获取前六名划分界线
                sorted_items = sorted(items_list, key=lambda x: (-counts[x], items_list.index(x) if isinstance(x, str) else x))
                cutoff_count = counts[sorted_items[5]] # 第六名的开出次数
                
                top_6_pool = [x for x in items_list if counts[x] >= cutoff_count]
                pruned_pool = [x for x in items_list if x not in top_6_pool]
                
                # 特赦补回逻辑：只要没进前六名，但欲出几率 >= 1.0 强制补回
                rescued_pool = [x for x in pruned_pool if rates_dict[x] >= 1.0]
                final_active = top_6_pool + rescued_pool
                return top_6_pool, rescued_pool, cutoff_count

            # 获取最新一期数据
            last_num, last_zodiac = parsed_data[-1]
            last_tail = last_num % 10
            
            st.info(f"📋 **大盘最新数据定位**：上一期开奖号码为 `**{last_num:02d}**`，对应生肖为 `**{last_zodiac}**` （当前线索：{last_tail}尾）")
            
            # 动态运算
            top6_t, rescue_t, cut_line_t = get_advanced_pool(tail_transitions, last_tail, tail_rates, all_tails)
            top6_z, rescue_z, cut_line_z = get_advanced_pool(zodiac_transitions, last_zodiac, zodiac_rates, all_zodiacs)
            
            # 排版渲染明细
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"🔢 **尾数预测网（基于 {last_tail} 尾，第6名门槛：{cut_line_t}次）：**")
                t_display = [f"**{x}尾**" for x in top6_t] + [f"**{x}尾**(🚨高危特赦补回)" for x in rescue_t]
                st.markdown(f"✅ 最终入选尾数：{' 、 '.join(t_display) if t_display else '无'}")
            with c2:
                st.markdown(f"🔮 **生肖预测网（基于 【{last_zodiac}】，第6名门槛：{cut_line_z}次）：**")
                z_display = [f"**{x}**" for x in top6_z] + [f"**{x}**(🚨高危特赦补回)" for x in rescue_z]
                st.markdown(f"✅ 最终入选生肖：{' 、 '.join(z_display) if z_display else '无'}")
                
            # 执行 1-49 号码筛网 (或逻辑)
            final_selected_numbers = []
            active_tails_set = set(top6_t + rescue_t)
            active_zods_set = set(top6_z + rescue_z)
            
            for n in range(1, 50):
                if (n % 10 in active_tails_set) or (get_zodiac_of_number(n) in active_zods_set):
                    final_selected_numbers.append(f"{n:02d}")
                    
            st.write("---")
            if final_selected_numbers:
                st.success(f"🏁 **全量精选打捞完成！当前双特征‘前6名或高危’号码共 {len(final_selected_numbers)} 个（已数字从小到大对齐排列）**")
                st.markdown("👇 **请点击下方代码框右上角的图标，即可一键全选复制号码：**")
                st.code(", ".join(final_selected_numbers), language="text")
            else:
                st.warning("⚠️ 提示：无匹配号码。")

            # ==========================================
            # 🧪 转换规律历史回测引擎 (嵌入页底作为附加高级验证)
            # ==========================================
            st.write("---")
            st.subheader("🧪 附加验证：该“前6名+高危补回”策略历史全量滚动回测引擎")
            st.markdown("💡 **回测机制**：系统模拟历史上的每一期。每次都严格采用当时的【前6名（含并列）或高危特赦】指标进行布网。只要下期的实际开奖 尾数 或者 生肖 任意一个被大网包含，即判定命中！")
            
            if st.button("🚀 开启‘前6名+高危护航’策略历史全量大回测", type="primary"):
                hit_count = 0
                test_total = len(parsed_data) - 1
                hit_details = []

                # 建立高精度滚动历史回测循环
                for i in range(test_total):
                    history_snapshot = parsed_data[:i+1]
                    if len(history_snapshot) < 2: continue
                    
                    # 1. 重构当时的转移数据
                    t_trans = defaultdict(list)
                    z_trans = defaultdict(list)
                    t_cnts = defaultdict(int)
                    z_cnts = defaultdict(int)
                    
                    for k in range(len(history_snapshot) - 1):
                        t_trans[history_snapshot[k][0] % 10].append(history_snapshot[k+1][0] % 10)
                        z_trans[history_snapshot[k][1]].append(history_snapshot[k+1][1])
                    for idx_h in range(len(history_snapshot)):
                        t_cnts[history_snapshot[idx_h][0] % 10] += 1
                        z_cnts[history_snapshot[idx_h][1]] += 1
                        
                    # 2. 重构当时的欲出几率
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

                    # 3. 执行当时的“前6名+特赦”算法
                    def get_snap_advanced_pool(t_dict, cur, r_dict, items_list):
                        nxt = t_dict[cur]
                        cts = {x: nxt.count(x) for x in items_list}
                        sorted_i = sorted(items_list, key=lambda x: (-cts[x], items_list.index(x) if isinstance(x, str) else x))
                        cut_c = cts[sorted_i[5]]
                        t6 = [x for x in items_list if cts[x] >= cut_c]
                        rsc = [x for x in items_list if x not in t6 and r_dict[x] >= 1.0]
                        return set(t6 + rsc)

                    c_num, c_zod = parsed_data[i]
                    n_num, n_zod = parsed_data[i+1]
                    
                    snap_active_tails = get_snap_advanced_pool(t_trans, c_num % 10, snap_t_rates, all_tails)
                    snap_active_zods = get_snap_advanced_pool(z_trans, c_zod, snap_z_rates, all_zodiacs)
                    
                    tail_hit = (n_num % 10 in snap_active_tails)
                    zodiac_hit = (n_zod in snap_active_zods)
                    
                    if tail_hit or zodiac_hit:
                        hit_count += 1
                        tag = " [🔥双重全中!]" if (tail_hit and zodiac_hit) else (" [🎯仅尾数中]" if tail_hit else " [🎯仅生肖中]")
                        hit_details.append(f"第 {i+2:03d} 期（前一期 `{c_num},{c_zod}`）：下期开出 `{n_num},{n_zod}`{tag}")

                # 回测总成绩看板
                b_col1, b_col2, b_col3 = st.columns(3)
                b_col1.metric("📋 总模拟检验样本数", f"{test_total} 期")
                b_col2.metric("🎯 优化策略复合拦截总期数", f"{hit_count} 期")
                b_col3.metric("📊 综合历史捕获率", f"{(hit_count / test_total * 100):.2f}%")

                st.write("---")
                st.success(f"🏁 历史滚动回测复盘完成！精细剪枝后，大网号码数量大幅缩减的同时，大盘整体捕获胜率依然稳健。以下为完美捕获明细清单：")
                st.code("\n".join(hit_details), language="text")
