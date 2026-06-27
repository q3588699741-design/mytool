import streamlit as st
import pandas as pd
from collections import defaultdict
import traceback

# 页面基础配置
st.set_page_config(page_title="数据全维度智能统计看板", layout="wide")
st.title("📊 开奖记录全维度综合统计看板 (安全诊断双模版)")
st.caption("最新总体冷热 ｜ 当前遗漏与欲出几率 ｜ 状态转移矩阵 ｜ 🎯固定6+6多维智能出号 ｜ 🧪历史滚动回测")

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
            
            # 2026年岁次丙午马年 1-49 号码生肖对照基准
            base_zodiacs = ['马', '蛇', '龙', '兔', '虎', '牛', '鼠', '猪', '狗', '鸡', '猴', '羊']
            def get_zodiac_of_number(n):
                return base_zodiacs[(n - 1) % 12]

            # 号码出现总数统计
            num_counts = defaultdict(int)
            tail_counts = defaultdict(int)
            zodiac_counts = defaultdict(int)
            
            for num, zodiac in parsed_data:
                num_counts[num] += 1
                tail_counts[num % 10] += 1
                zodiac_counts[zodiac] += 1

            # 计算倒序遗漏期数
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

            # 计算状态转移数据
            tail_transitions = defaultdict(list)
            zodiac_transitions = defaultdict(list)
            for i in range(len(parsed_data) - 1):
                tail_transitions[parsed_data[i][0] % 10].append(parsed_data[i+1][0] % 10)
                zodiac_transitions[parsed_data[i][1]].append(parsed_data[i+1][1])

            st.write("---")
            
            # 5大功能选项卡
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🔥 1. 大盘总量冷热榜", 
                "⏳ 2. 当前未出遗漏与欲出榜", 
                "📈 3. 大局观综合指标分析", 
                "🔄 4. 前后行状态转移矩阵", 
                "🎯 5. 下期智能锁码出号"
            ])

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
            # 🎯 TAB 5: 核心选号控制台
            # ==========================================
            with tab5:
                st.subheader("🎛️ 策略过滤器：严格定容 6尾 + 6生肖 选号面板")
                
                combine_mode = st.radio(
                    "🛠️ **请选择交叉组合战术：**",
                    ["⚡ 严格精选模式（并且 AND）：号码必须同时属于精选尾数和生肖！【强力收紧：预计每期 10-15 码】", 
                     "🔥 广撒网容错模式（或者 OR）：号码只要满足尾数或生肖中任意一项即可！【大网拦截：预计每期 37 码】"],
                    index=0
                )
                
                def get_strict_6_pool(transitions_dict, current_state, rates_dict, items_list):
                    nexts = transitions_dict[current_state]
                    counts = {x: nexts.count(x) for x in items_list}
                    high_risk = [x for x in items_list if rates_dict[x] >= 1.0]
                    normal = [x for x in items_list if x not in high_risk]
                    high_risk_sorted = sorted(high_risk, key=lambda x: (-counts[x], items_list.index(x) if isinstance(x, str) else x))
                    normal_sorted = sorted(normal, key=lambda x: (-counts[x], items_list.index(x) if isinstance(x, str) else x))
                    combined = high_risk_sorted + normal_sorted
                    final_6 = combined[:6]
                    meta_info = {x: ("🚨高危必选" if x in high_risk else f"📈概率入选({counts[x]}次)") for x in final_6}
                    return final_6, meta_info

                last_num, last_zodiac = parsed_data[-1]
                last_tail = last_num % 10
                
                st.info(f"📋 **大盘最新数据定位**：上一期号码为 `**{last_num:02d}**`，生肖为 `**{last_zodiac}**` （当前转换线索：{last_tail}尾）")
                
                chosen_tails, tail_meta = get_strict_6_pool(tail_transitions, last_tail, tail_rates, all_tails)
                chosen_zods, zod_meta = get_strict_6_pool(zodiac_transitions, last_zodiac, zodiac_rates, all_zodiacs)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"🔢 **精选 6 尾数构成清单：**")
                    t_items = [f"**{x}尾**({tail_meta[x]})" for x in sorted(chosen_tails)]
                    st.markdown(f"➡️ 最终入选：{' ｜ '.join(t_items)}")
                with c2:
                    st.markdown(f"🔮 **精选 6 生肖构成清单：**")
                    z_items = [f"**{x}**({zod_meta[x]})" for x in sorted(chosen_zods, key=lambda x: all_zodiacs.index(x))]
                    st.markdown(f"➡️ 最终入选：{' ｜ '.join(z_items)}")
                    
                # 执行 1-49 号码精准筛网
                final_selected_numbers = []
                chosen_tails_set = set(chosen_tails)
                chosen_zods_set = set(chosen_zods)
                
                for n in range(1, 50):
                    tail_match = (n % 10 in chosen_tails_set)
                    zod_match = (get_zodiac_of_number(n) in chosen_zods_set)
                    
                    if "严格精选模式" in combine_mode:
                        if tail_match and zod_match:
                            final_selected_numbers.append(f"{n:02d}")
                    else:
                        if tail_match or zod_match:
                            final_selected_numbers.append(f"{n:02d}")
                        
                st.write("---")
                if final_selected_numbers:
                    st.success(f"🏁 **号码计算成功！在当前选定战术下，本期共生成号码 {len(final_selected_numbers)} 个（已数字从小到大重排）**")
                    st.markdown("👇 **请点击下方代码框右上角的图标，即可一键全选复制号码：**")
                    st.code(", ".join(final_selected_numbers), language="text")
                else:
                    st.warning("⚠️ 提示：在【且】逻辑极限收紧下，本期刚好没有交集重合的号码，建议切回【或】模式查阅基准。")

                # ==========================================
                # 🧪 转换规律历史滚动回测引擎 (带防御拦截)
                # ==========================================
                st.write("---")
                st.subheader("🧪 历史滚动实战模拟复盘（随上方选择模式实时自动适配）")
                
                if st.button("🚀 依据上方勾选的模式，开启全量历史大回测", type="primary"):
                    try:
                        hit_count = 0
                        test_total = len(parsed_data) - 1
                        hit_details = []
                        all_sizes = []

                        for i in range(test_total):
                            history_snapshot = parsed_data[:i+1]
                            if len(history_snapshot) < 2: continue
                            
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
                            snap_z_rates = get_snap_rate(all_zodiacs, lambda x: x
