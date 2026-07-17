import streamlit as st
import pandas as pd
from collections import defaultdict
import traceback

# 页面基础配置
st.set_page_config(page_title="数据全维度智能统计看板", layout="wide")
st.title("📊 开奖记录全维度综合统计看板 (方案B阶梯对冲版)")
st.caption("最新总体冷热 ｜ 当前双重遗漏与欲出几率 ｜ 纵向状态转移矩阵 ｜ 🎯方案B阶梯注码筛选")

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
            
            # 维持清爽的四大选项卡切换
            tab1, tab2, tab3, tab4 = st.tabs([
                "🔥 1. 大盘总量冷热榜", 
                "⏳ 2. 当前未出遗漏与欲出榜", 
                "🔄 3. 前后行状态转移矩阵",
                "🎯 4. 方案B阶梯注码筛选"
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
            # ⏳ TAB 2: 当前未出遗漏与欲出榜
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

            # ==========================================
            # 🔄 TAB 3: 前后行状态转移矩阵
            # ==========================================
            with tab3:
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
            # 🎯 TAB 4: 🛠 *修正运行版* 方案B阶梯式注码分类
            # ==========================================
            with tab4:
                st.subheader("🛡 资金风险防火墙：方案 B 阶梯式重合度自动分类对冲面板")
                st.markdown("💡 **实战阶梯对冲买法机制**：根据三个大池的条件交叉，程序自动对1-49所有号码进行阶梯分类。")
                
                # 1. 前置算出三大触发池
                triggered_nums = []
                for n in range(1, 50):
                    if (num_rates[n] >= 0.4) or (num_omission[n] >= num_last_omission[n]):
                        triggered_nums.append(n)
                
                triggered_tails = []
                for t in all_tails:
                    if (tail_rates[t] >= 0.4) or (tail_omission[t] >= tail_last_omission[t]):
                        triggered_tails.append(t)
                
                triggered_zodiacs = []
                for z in all_zodiacs:
                    if (zodiac_rates[z] >= 0.4) or (zodiac_omission[z] >= zodiac_last_omission[z]):
                        triggered_zodiacs.append(z)
                
                # 2. 转换为集合提速
                t_nums_set = set(triggered_nums)
                t_tails_set = set(triggered_tails)
                t_zods_set = set(triggered_zodiacs)
                
                # 3. 扫描分类 1-49
                triple_overlap_list = []
                double_overlap_list = []
                single_overlap_list = []
                
                for n in range(1, 50):
                    c1 = n in t_nums_set
                    c2 = (n % 10) in t_tails_set
                    c3 = get_zodiac_of_number(n) in t_zods_set
                    
                    match_count = sum([c1, c2, c3])
                    num_str = f"{n:02d}"
                    
                    if match_count == 3:
                        triple_overlap_list.append(num_str)
                    elif match_count == 2:
                        double_overlap_list.append(num_str)
                    elif match_count == 1:
                        single_overlap_list.append(num_str)
                        
                # 4. 前端分栏输出
                c_b1, c_b2, c_b3 = st.columns(3)
                
                with c_b1:
                    st.markdown("### 🔥 三重号 (重注突击队)")
                    st.caption("🎯 **入选标准**：同时在号码池、尾数池、生肖池满足变盘特征。建议分配**最高额度注码**！")
                    if triple_overlap_list:
                        st.info(f"📋 本期共有核心重叠：{len(triple_overlap_list)} 个码")
                        st.code(", ".join(triple_overlap_list), language="text")
                    else:
                        st.warning("暂无号码触发三重交集")
                        
                with c_b2:
                    st.markdown("### 📈 双重号 (中注主力军)")
                    st.caption("🌗 **入选标准**：恰好踩中其中任意两个方案。建议分配**中等额度注码**！")
                    if double_overlap_list:
                        st.success(f"📋 本期共有次级重叠：{len(double_overlap_list)} 个码")
                        st.code(", ".join(double_overlap_list), language="text")
                    else:
                        st.info("暂无号码触发双重交集")
                        
                with c_b3:
                    st.markdown("### 🛡 单重号 (轻注防守卫)")
                    st.caption("❄ **入选标准**：仅单边踩中一个特征。建议分配**最低限度额度**作为兜底！")
                    if single_overlap_list:
                        st.text(f"📋 本期共有孤立外围：{len(single_overlap_list)} 个码")
                        st.code(", ".join(single_overlap_list), language="text")
                    else:
                        st.info("没有单重孤立码")

    except Exception as global_ex:
        st.error(f"🚨 大盘核心数据解析时发生错误: {global_ex}")
        st.code(traceback.format_exc(), language="text")
