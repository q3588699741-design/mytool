import streamlit as st
import pandas as pd
from collections import defaultdict
import traceback

# 页面基础配置
st.set_page_config(page_title="数据全维度智能统计看板", layout="wide")
st.title("📊 开奖记录全维度综合统计看板 (3头8尾黄金控码版)")
st.caption("最新总体冷热 ｜ 当前遗漏与欲出几率 ｜ 状态转移矩阵 ｜ 🎯狙击3头8尾出号 ｜ 🧪历史滚动回测")

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
            
            for i, (num, zodiac) in enumerate(parsed_data):
                num_indices[num].append(i)
                tail_indices[num % 10].append(i)
                zodiac_indices[zodiac].append(i)

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
                        num_last_omission[n] = idxs[-1] # 仅出现过一次，则是开头到这一期的距离
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

            # 计算状态转移数据
            tail_transitions = defaultdict(list)
            zodiac_transitions = defaultdict(list)
            head_transitions = defaultdict(list)
            for i in range(len(parsed_data) - 1):
                tail_transitions[parsed_data[i][0] % 10].append(parsed_data[i+1][0] % 10)
                zodiac_transitions[parsed_data[i][1]].append(parsed_data[i+1][1])
                head_transitions[parsed_data[i][0] // 10].append(parsed_data[i+1][0] // 10)

            st.write("---")
            
            # 5大功能选项卡
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🔥 1. 大盘总量冷热榜", 
                "⏳ 2. 当前未出遗漏与欲出榜", 
                "📈 3. 大局观综合指标分析", 
                "🔄 4. 前后行状态转移矩阵", 
                "🎯 5. 下期 3头8尾智能出号"
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

            # ==========================================
            # ⏳ TAB 2: 全面升级双重遗漏面板（号码、生肖、尾数）
            # ==========================================
            with tab2:
                st.subheader("⏳ 各指标未出当前遗漏与最近一次开出历史间隔深度统计")
                st.caption("提示：当前遗漏代表该项目前连空多少期；上次遗漏代表最近一次开出来的时候，它在历史里憋了多少期。")
                miss_col1, miss_col2, miss_col3 = st.columns(3)
                
                with miss_col1:
                    st.markdown("### 🔢 49个号码双重遗漏与欲出排行")
                    num_list = []
                    for n in range(1, 50):
                        miss = num_omission[n]
                        l_miss = num_last_omission[n]
                        rate = num_rates[n]
                        avg_int = (total_records / num_counts[n]) if num_counts[n] > 0 else total_records
                        num_list.append((n, miss, l_miss, avg_int, rate))
                    # 按照欲出几率降序排序
                    num_list.sort(key=lambda x: (-x[4], x[0]))
                    
                    md = "| 排名 | 号码 | 当前遗漏 | 上次遗漏 | 平均间隔 | 欲出几率 |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
                    for r, (n, miss, l_miss, avg_int, rate) in enumerate(num_list, 1):
                        md += f"| {r} | {n:02d} | **{miss}期** | {l_miss}期 | {avg_int:.1f}期 | **{rate:.2f}** |\n"
                    st.markdown(md)
                    
                with miss_col2:
                    st.markdown("### 🔮 12生肖双重遗漏与欲出排行")
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
                        md += f"| {r} | {z} | **{miss}期** | {l_miss}期 | {avg_int:.1f}期 | **{rate:.2f}** |\n"
                    st.markdown(md)
                    
                with miss_col3:
                    st.markdown("### 🎯 10个尾数双重遗漏与欲出排行")
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
                        md += f"| {r} | {t}尾 | **{miss}期** | {l_miss}期 | {avg_int:.1f}期 | **{rate:.2f}** |\n"
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
                ind_col3.metric("🌌 全局大小比 (大号 $\ge25$ ｜ 小号)", f"{big_cnt}期 ｜ {small_cnt}期", f"大号占比: {(big_cnt/total_records)*100:.1f}%")

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
                        # 前置转换，彻底隔离不同 Python 解释器的 f-string 引号语法差异
                        joined_tail_str = ' ｜ '.join(formatted_parts)
                        tail_trans_md += f"| **{tail}尾** | {total}次 | {joined_tail_str} |\n"
                    st.markdown(tail_trans_md, unsafe_allow_html=True)
                with trans_col2:
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
            # 🎯 TAB 5: 核心“3头8尾”联动控制台 (且逻辑)
            # ==========================================
            with tab5:
                st.subheader("🎯 黄金交叉战术：概率最高 3头 ＋ 概率最高 8尾 狙击面板")
                st.markdown("💡 **控码科学机制**：通过【并且 AND】交叉阻击，下期预测号码必须**同时属于**筛选出的 3个头数 和 8个尾数。这能将出号规模死死压死在 **24 个码以内**（最适合实战下网规模）。")
                
                # 获取最新一期
                last_num, last_zodiac = parsed_data[-1]
                last_tail = last_num % 10
                last_head = last_num // 10
                
                st.info(f"📋 **大盘最新数据定位**：上一期号码为 `**{last_num:02d}**` （当前转换引子：{last_head}头、{last_tail}尾）")
                
                # --- 算法：获取概率最高前 N 名的核心函数 ---
                def get_top_n_pool(transitions_dict, current_state, items_list, top_n):
                    nexts = transitions_dict[current_state]
                    counts = {x: nexts.count(x) for x in items_list}
                    sorted_items = sorted(items_list, key=lambda x: (-counts[x], items_list.index(x) if isinstance(x, str) else x))
                    final_pool = sorted_items[:top_n]
                    meta_info = {x: f"📈历史转换开出 {counts[x]} 次" for x in final_pool}
                    return final_pool, meta_info

                chosen_heads, head_meta = get_top_n_pool(head_transitions, last_head, all_heads, 3)
                chosen_tails, tail_meta = get_top_n_pool(tail_transitions, last_tail, all_tails, 8)
                
                # 规整打印指标名额
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"🔝 **胜率最高 3 头数精选池：**")
                    h_items = [f"**{x}头**({head_meta[x]})" for x in sorted(chosen_heads)]
                    joined_h_items = ' ｜ '.join(h_items)
                    st.markdown(f"➡️ 选中：{joined_h_items}")
                with c2:
                    st.markdown(f"🔢 **胜率最高 8 尾数精选池：**")
                    t_items = [f"**{x}尾**({tail_meta[x]})" for x in sorted(chosen_tails)]
                    joined_t_items = ' ｜ '.join(t_items)
                    st.markdown(f"➡️ 选中：{joined_t_items}")
                    
                # 计算 1-49 号码的且交集
                final_selected_numbers = []
                chosen_heads_set = set(chosen_heads)
                chosen_tails_set = set(chosen_tails)
                
                for n in range(1, 49 + 1):
                    if (n // 10 in chosen_heads_set) and (n % 10 in chosen_tails_set):
                        final_selected_numbers.append(f"{n:02d}")
                        
                st.write("---")
                if final_selected_numbers:
                    st.success(f"🏁 **3头8尾精准控码生成成功！本期共挑出 {len(final_selected_numbers)} 个号码（完美压制在24码黄金线上，已重排）：**")
                    st.markdown("👇 **请点击下方代码框右上角的图标，即可一键全选复制号码：**")
                    joined_final_nums = ", ".join(final_selected_numbers)
                    st.code(joined_final_nums, language="text")
                else:
                    st.warning("⚠️ 提示：当前转移频次下两部分没有产生交集。")

                # ==========================================
                # 🧪 “3头8尾”专属历史全量滚动回测引擎
                # ==========================================
                st.write("---")
                st.subheader("🧪 “3头8尾”策略专属历史全量滚动复盘回测")
                st.markdown("💡 **回测原理**：程序模拟历史上的每一期。每次都完全使用当时历史算出来的【最高3头 且 最高8尾】交叉拦截池。直接告诉你每期平均会吐出几个号，以及历史真实的双中拦截率！")
                
                if st.button("🚀 开启‘3头8尾且逻辑’历史大复盘", type="primary"):
                    try:
                        hit_count = 0
                        test_total = len(parsed_data) - 1
                        hit_details = []
                        all_sizes = []

                        for i in range(test_total):
                            history_snapshot = parsed_data[:i+1]
                            if len(history_snapshot) < 2: continue
                            
                            t_trans = defaultdict(list)
                            h_trans = defaultdict(list)
                            for k in range(len(history_snapshot) - 1):
                                t_trans[history_snapshot[k][0] % 10].append(history_snapshot[k+1][0] % 10)
                                h_trans[history_snapshot[k][0] // 10].append(history_snapshot[k+1][0] // 10)
                                
                            def get_snap_top_n(trans_dict, cur, items_list, top_n):
                                nxt = trans_dict[cur]
                                cts = {x: nxt.count(x) for x in items_list}
                                sorted_i = sorted(items_list, key=lambda x: (-cts[x], x))
                                return set(sorted_i[:top_n])

                            c_num, _ = parsed_data[i]
                            n_num, _ = parsed_data[i+1]
                            
                            snap_active_heads = get_snap_top_n(h_trans, c_num // 10, all_heads, 3)
                            snap_active_tails = get_snap_top_n(t_trans, c_num % 10, all_tails, 8)
                            
                            # 统计当前期数实际上吐出了几个号
                            snap_num_count = 0
                            for n in range(1, 50):
                                if (n // 10 in snap_active_heads) and (n % 10 in snap_active_tails):
                                    snap_num_count += 1
                            all_sizes.append(snap_num_count)
                            
                            # 判定是否拦截成功
                            head_hit = (n_num // 10 in snap_active_heads)
                            tail_hit = (n_num % 10 in snap_active_tails)
                            
                            if head_hit and tail_hit:
                                hit_count += 1
                                hit_details.append(f"第 {i+2:03d} 期（上期 `{c_num:02d}`）：下期开出 `{n_num:02d}` 🎯[精准狙击成功!] ｜ 本期大网覆盖了 {snap_num_count} 个号")

                        avg_size = sum(all_sizes) / len(all_sizes) if all_sizes else 0
                        b_col1, b_col2, b_col3 = st.columns(3)
                        b_col1.metric("📋 总模拟检验样本数", f"{test_total} 期")
                        b_col2.metric("📊 每期平均吐出号码", f"{avg_size:.1f} 个号", "稳定锁死在24码以内")
                        b_col3.metric("🎯 3头8尾真实捕获胜率", f"{(hit_count / test_total * 100):.2f}%")

                        st.write("---")
                        st.success(f"🏁 历史滚动回测复盘完成！清单明细如下：")
                        st.code("\n".join(hit_details), language="text")
                    except Exception as ex:
                        st.error(f"💥 回测内部运算发生错误: {ex}")
                        st.code(traceback.format_exc(), language="text")
    except Exception as global_ex:
        st.error(f"🚨 大盘核心数据解析时发生错误: {global_ex}")
        st.code(traceback.format_exc(), language="text")
