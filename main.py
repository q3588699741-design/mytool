import streamlit as st
import pandas as pd
from collections import defaultdict
import traceback

# 页面基础配置
st.set_page_config(page_title="数据全维度智能统计看板", layout="wide")
st.title("📊 开奖记录全维度综合统计看板 (含四季生肖拐点选号版)")
st.caption("最新总体冷热 ｜ 当前双重遗漏与欲出几率 ｜ 空间分区与四季生肖 ｜ 纵向状态转移 ｜ 🎯选号与杀号 ｜ ⚡空间形态 ｜ 🌸四季拐点")

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

            # 生肖空间形态与四季体系定义
            zodiac_zones_2 = {
                '上区': ['马', '蛇', '龙', '兔', '虎', '牛'],
                '下区': ['鼠', '猪', '狗', '鸡', '猴', '羊']
            }
            zodiac_zones_3 = {
                '左区': ['马', '兔', '鼠', '鸡'],
                '中区': ['蛇', '虎', '猪', '猴'],
                '右区': ['龙', '牛', '狗', '羊']
            }
            zodiac_seasons = {
                '春肖': ['虎', '兔', '龙'],
                '夏肖': ['蛇', '马', '羊'],
                '秋肖': ['猴', '鸡', '狗'],
                '冬肖': ['猪', '鼠', '牛']
            }
            all_zones = {**zodiac_zones_2, **zodiac_zones_3}

            # 基础出现总数统计
            num_counts = defaultdict(int)
            tail_counts = defaultdict(int)
            zodiac_counts = defaultdict(int)
            head_counts_dict = defaultdict(int)
            zone_counts = defaultdict(int)
            season_counts = defaultdict(int)
            
            for num, zodiac in parsed_data:
                num_counts[num] += 1
                tail_counts[num % 10] += 1
                zodiac_counts[zodiac] += 1
                head_counts_dict[num // 10] += 1
                for z_name, z_list in all_zones.items():
                    if zodiac in z_list:
                        zone_counts[z_name] += 1
                for s_name, s_list in zodiac_seasons.items():
                    if zodiac in s_list:
                        season_counts[s_name] += 1

            # 🛠️ 建立全量位置索引
            num_indices = defaultdict(list)
            tail_indices = defaultdict(list)
            zodiac_indices = defaultdict(list)
            head_indices = defaultdict(list)
            zone_indices = defaultdict(list)
            season_indices = defaultdict(list)
            
            for i, (num, zodiac) in enumerate(parsed_data):
                num_indices[num].append(i)
                tail_indices[num % 10].append(i)
                zodiac_indices[zodiac].append(i)
                head_indices[num // 10].append(i)
                for z_name, z_list in all_zones.items():
                    if zodiac in z_list:
                        zone_indices[z_name].append(i)
                for s_name, s_list in zodiac_seasons.items():
                    if zodiac in s_list:
                        season_indices[s_name].append(i)

            # 1. 号码双重遗漏
            num_omission = {}
            num_last_omission = {}
            for n in range(1, 50):
                idxs = num_indices[n]
                if idxs:
                    num_omission[n] = (total_records - 1) - idxs[-1]
                    num_last_omission[n] = idxs[-1] - idxs[-2] - 1 if len(idxs) >= 2 else idxs[-1]
                else:
                    num_omission[n] = total_records
                    num_last_omission[n] = 0

            # 2. 生肖双重遗漏
            zodiac_omission = {}
            zodiac_last_omission = {}
            for z in all_zodiacs:
                idxs = zodiac_indices[z]
                if idxs:
                    zodiac_omission[z] = (total_records - 1) - idxs[-1]
                    zodiac_last_omission[z] = idxs[-1] - idxs[-2] - 1 if len(idxs) >= 2 else idxs[-1]
                else:
                    zodiac_omission[z] = total_records
                    zodiac_last_omission[z] = 0

            # 3. 尾数双重遗漏
            tail_omission = {}
            tail_last_omission = {}
            for t in all_tails:
                idxs = tail_indices[t]
                if idxs:
                    tail_omission[t] = (total_records - 1) - idxs[-1]
                    tail_last_omission[t] = idxs[-1] - idxs[-2] - 1 if len(idxs) >= 2 else idxs[-1]
                else:
                    tail_omission[t] = total_records
                    tail_last_omission[t] = 0

            # 4. 头数双重遗漏
            head_omission = {}
            head_last_omission = {}
            for h in all_heads:
                idxs = head_indices[h]
                if idxs:
                    head_omission[h] = (total_records - 1) - idxs[-1]
                    head_last_omission[h] = idxs[-1] - idxs[-2] - 1 if len(idxs) >= 2 else idxs[-1]
                else:
                    head_omission[h] = total_records
                    head_last_omission[h] = 0

            # 5. 生肖空间分区双重遗漏与欲出几率
            zone_omission = {}
            zone_last_omission = {}
            zone_rates = {}
            for z_name in all_zones:
                idxs = zone_indices[z_name]
                if idxs:
                    zone_omission[z_name] = (total_records - 1) - idxs[-1]
                    zone_last_omission[z_name] = idxs[-1] - idxs[-2] - 1 if len(idxs) >= 2 else idxs[-1]
                else:
                    zone_omission[z_name] = total_records
                    zone_last_omission[z_name] = 0
                
                cnt = zone_counts[z_name]
                avg_int = (total_records / cnt) if cnt > 0 else total_records
                zone_rates[z_name] = zone_omission[z_name] / avg_int

            # 6. 四季生肖双重遗漏与欲出几率 (✨新增)
            season_omission = {}
            season_last_omission = {}
            season_rates = {}
            for s_name in zodiac_seasons:
                idxs = season_indices[s_name]
                if idxs:
                    season_omission[s_name] = (total_records - 1) - idxs[-1]
                    season_last_omission[s_name] = idxs[-1] - idxs[-2] - 1 if len(idxs) >= 2 else idxs[-1]
                else:
                    season_omission[s_name] = total_records
                    season_last_omission[s_name] = 0
                
                cnt = season_counts[s_name]
                avg_int = (total_records / cnt) if cnt > 0 else total_records
                season_rates[s_name] = season_omission[s_name] / avg_int

            # 计算全局欲出几率
            tail_rates = {t: tail_omission[t] / ((total_records / tail_counts[t]) if tail_counts[t] > 0 else total_records) for t in all_tails}
            zodiac_rates = {z: zodiac_omission[z] / ((total_records / zodiac_counts[z]) if zodiac_counts[z] > 0 else total_records) for z in all_zodiacs}
            num_rates = {n: num_omission[n] / ((total_records / num_counts[n]) if num_counts[n] > 0 else total_records) for n in range(1, 50)}
            head_rates = {h: head_omission[h] / ((total_records / head_counts_dict[h]) if head_counts_dict[h] > 0 else total_records) for h in all_heads}

            # 计算状态转移数据
            tail_transitions = defaultdict(list)
            zodiac_transitions = defaultdict(list)
            head_transitions = defaultdict(list)
            for i in range(len(parsed_data) - 1):
                tail_transitions[parsed_data[i][0] % 10].append(parsed_data[i+1][0] % 10)
                zodiac_transitions[parsed_data[i][1]].append(parsed_data[i+1][1])
                head_transitions[parsed_data[i][0] // 10].append(parsed_data[i+1][0] // 10)

            st.write("---")
            
            # 七大核心板块
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "🔥 1. 大盘总量冷热榜", 
                "⏳ 2. 当前未出遗漏与欲出榜", 
                "🔄 3. 前后行状态转移矩阵",
                "🎯 4. 剔除与拐点特赦智能选号",
                "❌ 5. 综合分析反向杀号 (15码)",
                "⚡ 6. 空间形态拐点选号",
                "🌸 7. 四季生肖拐点选号"
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
                    md = "| 排名 | 尾数 | 出现次数 | 占比概率 |\n| :---: | :---: |\n"
                    for rank, (t, cnt, pct) in enumerate(tail_hot_data, 1):
                        tail_str = f"**{t}尾**" if rank <= 3 and cnt > 0 else f"{t}尾"
                        flag = "🔥" if rank <= 3 and cnt > 0 else ("❄️" if cnt == 0 else "")
                        md += f"| {rank} | {tail_str} {flag} | {cnt}次 | {pct:.1f}% |\n"
                    st.markdown(md)
                with hot_col3:
                    st.markdown("### 🔮 生肖冷热排行")
                    zodiac_hot_data = [(z, zodiac_counts[z], (zodiac_counts[z]/total_records*100 if total_records>0 else 0.0)) for z in all_zodiacs]
                    zodiac_hot_data.sort(key=lambda x: (-x[1], all_zodiacs.index(x[0])))
                    md = "| 排名 | 生肖 | 出现次数 | 占比概率 |\n| :---: | :---: |\n"
                    for rank, (z, cnt, pct) in enumerate(zodiac_hot_data, 1):
                        zodiac_str = f"**{z}**" if rank <= 3 and cnt > 0 else z
                        flag = "🔥" if rank <= 3 and cnt > 0 else ("❄️" if cnt == 0 else "")
                        md += f"| {rank} | {zodiac_str} {flag} | {cnt}次 | {pct:.1f}% |\n"
                    st.markdown(md)

            # ==========================================
            # ⏳ TAB 2: 当前未出遗漏与欲出榜 (含四季生肖)
            # ==========================================
            with tab2:
                st.subheader("⏳ 各指标未出当前遗漏与最近一次开出历史间隔深度统计")
                st.caption("💡 **标注说明**：带有 **🚨 警报** 代表【当前遗漏 $\ge$ 上次遗漏】（触底拐点）；带有 **🔥 火焰** 代表【欲出几率 $\ge$ 0.40】（高热度区）！")
                
                # 第一层：号码 / 生肖 / 尾数 / 头数
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
                        is_high_rate = (rate >= 0.4)
                        tags = ""
                        if is_inflection: tags += " 🚨"
                        if is_high_rate: tags += " 🔥"
                        n_str = f"**{n:02d}**{tags}" if (is_inflection or is_high_rate) else f"{n:02d}"
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        rate_str = f"**{rate:.2f}** 🔥" if is_high_rate else f"{rate:.2f}"
                        md += f"| {r} | {n_str} | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | {rate_str} |\n"
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
                        is_high_rate = (rate >= 0.4)
                        tags = ""
                        if is_inflection: tags += " 🚨"
                        if is_high_rate: tags += " 🔥"
                        z_str = f"**{z}**{tags}" if (is_inflection or is_high_rate) else z
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        rate_str = f"**{rate:.2f}** 🔥" if is_high_rate else f"{rate:.2f}"
                        md += f"| {r} | {z_str} | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | {rate_str} |\n"
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
                        is_high_rate = (rate >= 0.4)
                        tags = ""
                        if is_inflection: tags += " 🚨"
                        if is_high_rate: tags += " 🔥"
                        t_str = f"**{t}尾**{tags}" if (is_inflection or is_high_rate) else f"{t}尾"
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        rate_str = f"**{rate:.2f}** 🔥" if is_high_rate else f"{rate:.2f}"
                        md += f"| {r} | {t_str} | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | {rate_str} |\n"
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
                        is_high_rate = (rate >= 0.4)
                        tags = ""
                        if is_inflection: tags += " 🚨"
                        if is_high_rate: tags += " 🔥"
                        h_str = f"**{h}头**{tags}" if (is_inflection or is_high_rate) else f"{h}头"
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        rate_str = f"**{rate:.2f}** 🔥" if is_high_rate else f"{rate:.2f}"
                        md += f"| {r} | {h_str} | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | {rate_str} |\n"
                    st.markdown(md)

                # 第二层：生肖空间分区与四季生肖形态深度统计 (3 栏展示)
                st.write("---")
                st.subheader("🔮 生肖形态分区（上下区 / 左中右区 / 春夏秋冬四季肖）遗漏与欲出深度统计")
                zone_col1, zone_col2, zone_col3 = st.columns(3)
                
                with zone_col1:
                    st.markdown("### 🌗 生肖二分空间 (上下区)")
                    z2_list = []
                    for z_name, z_members in zodiac_zones_2.items():
                        miss = zone_omission[z_name]
                        l_miss = zone_last_omission[z_name]
                        rate = zone_rates[z_name]
                        cnt = zone_counts[z_name]
                        avg_int = (total_records / cnt) if cnt > 0 else total_records
                        z2_list.append((z_name, "、".join(z_members), cnt, miss, l_miss, avg_int, rate))
                    z2_list.sort(key=lambda x: -x[6])
                    
                    z2_md = "| 排名 | 分区名称 | 包含生肖 | 历史开出 | 当前遗漏 | 上次遗漏 | 平均间隔 | 欲出几率 |\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
                    for r, (zn, zm, cnt, miss, l_miss, avg_int, rate) in enumerate(z2_list, 1):
                        is_inflection = (miss >= l_miss)
                        is_high_rate = (rate >= 0.4)
                        tags = ""
                        if is_inflection: tags += " 🚨"
                        if is_high_rate: tags += " 🔥"
                        zn_str = f"**{zn}**{tags}" if (is_inflection or is_high_rate) else zn
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        rate_str = f"**{rate:.2f}** 🔥" if is_high_rate else f"{rate:.2f}"
                        z2_md += f"| {r} | {zn_str} | `{zm}` | {cnt}次 | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | {rate_str} |\n"
                    st.markdown(z2_md)
                    
                with zone_col2:
                    st.markdown("### 🧭 生肖三分空间 (左中右区)")
                    z3_list = []
                    for z_name, z_members in zodiac_zones_3.items():
                        miss = zone_omission[z_name]
                        l_miss = zone_last_omission[z_name]
                        rate = zone_rates[z_name]
                        cnt = zone_counts[z_name]
                        avg_int = (total_records / cnt) if cnt > 0 else total_records
                        z3_list.append((z_name, "、".join(z_members), cnt, miss, l_miss, avg_int, rate))
                    z3_list.sort(key=lambda x: -x[6])
                    
                    z3_md = "| 排名 | 分区名称 | 包含生肖 | 历史开出 | 当前遗漏 | 上次遗漏 | 平均间隔 | 欲出几率 |\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
                    for r, (zn, zm, cnt, miss, l_miss, avg_int, rate) in enumerate(z3_list, 1):
                        is_inflection = (miss >= l_miss)
                        is_high_rate = (rate >= 0.4)
                        tags = ""
                        if is_inflection: tags += " 🚨"
                        if is_high_rate: tags += " 🔥"
                        zn_str = f"**{zn}**{tags}" if (is_inflection or is_high_rate) else zn
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        rate_str = f"**{rate:.2f}** 🔥" if is_high_rate else f"{rate:.2f}"
                        z3_md += f"| {r} | {zn_str} | `{zm}` | {cnt}次 | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | {rate_str} |\n"
                    st.markdown(z3_md)

                with zone_col3:
                    st.markdown("### 🌸 四季生肖空间 (春夏秋冬)")
                    season_list = []
                    for s_name, s_members in zodiac_seasons.items():
                        miss = season_omission[s_name]
                        l_miss = season_last_omission[s_name]
                        rate = season_rates[s_name]
                        cnt = season_counts[s_name]
                        avg_int = (total_records / cnt) if cnt > 0 else total_records
                        season_list.append((s_name, "、".join(s_members), cnt, miss, l_miss, avg_int, rate))
                    season_list.sort(key=lambda x: -x[6])
                    
                    season_md = "| 排名 | 季节肖 | 包含生肖 | 历史开出 | 当前遗漏 | 上次遗漏 | 平均间隔 | 欲出几率 |\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
                    for r, (sn, sm, cnt, miss, l_miss, avg_int, rate) in enumerate(season_list, 1):
                        is_inflection = (miss >= l_miss)
                        is_high_rate = (rate >= 0.4)
                        tags = ""
                        if is_inflection: tags += " 🚨"
                        if is_high_rate: tags += " 🔥"
                        sn_str = f"**{sn}**{tags}" if (is_inflection or is_high_rate) else sn
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        rate_str = f"**{rate:.2f}** 🔥" if is_high_rate else f"{rate:.2f}"
                        season_md += f"| {r} | {sn_str} | `{sm}` | {cnt}次 | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | {rate_str} |\n"
                    st.markdown(season_md)

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
                    
                    r1_remove = (zodiac_rates[z] < 0.4) and (zodiac_omission[z] < zodiac_last_omission[z])
                    r2_remove = (tail_rates[t] < 0.4) and (tail_omission[t] < tail_last_omission[t])
                    can_restore = (zodiac_omission[z] >= zodiac_last_omission[z]) or (tail_omission[t] >= tail_last_omission[t])
                    
                    if (r1_remove or r2_remove) and not can_restore:
                        continue
                    else:
                        selected_numbers.append(n)
                
                selected_numbers.sort()
                formatted_nums = [f"{x:02d}" for x in selected_numbers]
                
                st.write("---")
                st.success(f"🏆 **【特赦恢复精选网】本期符合条件的号码共 {len(formatted_nums)} 个（已按由小到大重排）：**")
                st.markdown("👇 **请点击下方代码框右上角的小图标，即可秒级全选复制到剪贴板：**")
                
                if formatted_nums:
                    st.code(", ".join(formatted_nums), language="text")
                else:
                    st.info("提示：当前数据周期内没有符合条件的号码。")
                st.write("---")

            # ==========================================
            # ❌ TAB 5: ✨ 综合分析反向杀号 (精选 15 码)
            # ==========================================
            with tab5:
                st.subheader("❌ 综合概率模型：精选最不可能出现的 15 个号码 (反向杀号池)")
                st.markdown("""
                💡 **计算模型**：融合【生肖欲出率(35%) + 尾数欲出率(35%) + 号码欲出率(30%)】三维权重，
                并对未触底拐点（当前遗漏 < 上次遗漏）的弱势指标执行智能扣分，精准筛选出全盘概率势能最低的 **15 个危险冷杂码**。
                """)
                
                exclusion_scores = []
                for n in range(1, 50):
                    t = n % 10
                    z = get_zodiac_of_number(n)
                    
                    score = 0.35 * zodiac_rates[z] + 0.35 * tail_rates[t] + 0.30 * num_rates[n]
                    
                    if zodiac_omission[z] < zodiac_last_omission[z]:
                        score -= 0.15
                    if tail_omission[t] < tail_last_omission[t]:
                        score -= 0.15
                    if num_omission[n] < num_last_omission[n]:
                        score -= 0.10
                        
                    exclusion_scores.append((n, score, zodiac_rates[z], tail_rates[t], num_rates[n], z, t))
                
                exclusion_scores.sort(key=lambda x: (x[1], x[0]))
                
                top_15_tuples = exclusion_scores[:15]
                top_15_nums = [x[0] for x in top_15_tuples]
                top_15_nums.sort()
                formatted_top_15 = [f"{x:02d}" for x in top_15_nums]
                
                st.write("---")
                st.error(f"🚫 **【综合分析反向杀号池】本期精选最不可能开出的 15 个号码（已按从小到大重排）：**")
                st.markdown("👇 **实战极简配置：请点击右上方小图标全选复制，直接用于排除/杀号：**")
                
                st.code(", ".join(formatted_top_15), language="text")
                st.write("---")
                
                st.markdown("### 🔍 15 个杀码的定量参数与扣分明细表")
                details_md = "| 排名 | 杀码 | 生肖/尾数 | 综合风险分 | 生肖欲出率 | 尾数欲出率 | 号码欲出率 |\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
                for rank, (n, sc, z_r, t_r, n_r, z, t) in enumerate(top_15_tuples, 1):
                    details_md += f"| {rank} | **{n:02d}** | {z} / {t}尾 | **{sc:.3f}** | {z_r:.2f} | {t_r:.2f} | {n_r:.2f} |\n"
                st.markdown(details_md)

            # ==========================================
            # ⚡ TAB 6: ✨ 生肖空间形态拐点选号
            # ==========================================
            with tab6:
                st.subheader("⚡ 生肖空间形态分区（带闪电拐点）智能号码提取引擎")
                st.markdown("""
                💡 **空间形态选号逻辑**：
                * 自动扫描功能二中 **上下区（二分空间）** 与 **左中右区（三分空间）** 的遗漏触底状态；
                * 提取触发 **【当前遗漏 $\ge$ 上次遗漏】（即带 ⚡ 闪电标记）** 的分区所覆盖的全部生肖，并自动反查打捞对应的 1-49 特码。
                """)
                
                # 1. 抓取带闪电的二分空间 (上下区)
                triggered_z2_zones = [zn for zn in zodiac_zones_2 if zone_omission[zn] >= zone_last_omission[zn]]
                z2_zodiacs_set = set()
                for zn in triggered_z2_zones:
                    z2_zodiacs_set.update(zodiac_zones_2[zn])
                
                z2_nums = [n for n in range(1, 50) if get_zodiac_of_number(n) in z2_zodiacs_set]
                z2_nums.sort()
                
                # 2. 抓取带闪电的三分空间 (左中右区)
                triggered_z3_zones = [zn for zn in zodiac_zones_3 if zone_omission[zn] >= zone_last_omission[zn]]
                z3_zodiacs_set = set()
                for zn in triggered_z3_zones:
                    z3_zodiacs_set.update(zodiac_zones_3[zn])
                
                z3_nums = [n for n in range(1, 50) if get_zodiac_of_number(n) in z3_zodiacs_set]
                z3_nums.sort()
                
                # 3. 计算双区重叠核心交集 (AND) 与 综合并集 (OR)
                strict_zodiacs_set = z2_zodiacs_set.intersection(z3_zodiacs_set)
                strict_nums = [n for n in range(1, 50) if get_zodiac_of_number(n) in strict_zodiacs_set]
                strict_nums.sort()
                
                combined_zodiacs_set = z2_zodiacs_set.union(z3_zodiacs_set)
                combined_nums = [n for n in range(1, 50) if get_zodiac_of_number(n) in combined_zodiacs_set]
                combined_nums.sort()
                
                st.write("---")
                st.success(f"🏆 **【双区交集超级核心池】（二分闪电 ∩ 三分闪电 严格交集）共 {len(strict_nums)} 个特码：**")
                st.caption(f"🎯 **涵盖核心生肖**：`{'、'.join(sorted(list(strict_zodiacs_set)))}` ｜ 属于双重空间形态共振区，码数极度浓缩，适合精准重击！")
                if strict_nums:
                    st.code(", ".join([f"{x:02d}" for x in strict_nums]), language="text")
                else:
                    st.info("提示：本期二分与三分闪电分区无重合交集生肖。")
                st.write("---")
                
                c_z1, c_z2, c_z3 = st.columns(3)
                
                with c_z1:
                    st.markdown(f"🌗 **二分空间(上下区)闪电池 ({len(z2_nums)} 码)**")
                    st.caption(f"🚨 **触发分区**：{', '.join(triggered_z2_zones) if triggered_z2_zones else '无'}")
                    st.caption(f"🔮 **涵盖生肖**：`{'、'.join(sorted(list(z2_zodiacs_set)))}`")
                    if z2_nums:
                        st.code(", ".join([f"{x:02d}" for x in z2_nums]), language="text")
                    else:
                        st.info("暂无二分区触发闪电")
                        
                with c_z2:
                    st.markdown(f"🧭 **三分空间(左中右)闪电池 ({len(z3_nums)} 码)**")
                    st.caption(f"🚨 **触发分区**：{', '.join(triggered_z3_zones) if triggered_z3_zones else '无'}")
                    st.caption(f"🔮 **涵盖生肖**：`{'、'.join(sorted(list(z3_zodiacs_set)))}`")
                    if z3_nums:
                        st.code(", ".join([f"{x:02d}" for x in z3_nums]), language="text")
                    else:
                        st.info("暂无三分区触发闪电")
                        
                with c_z3:
                    st.markdown(f"🛡️ **空间形态全包抄池(OR并集) ({len(combined_nums)} 码)**")
                    st.caption("🌐 **入选标准**：满足任意一个带闪电分区的生肖特码")
                    st.caption(f"🔮 **涵盖生肖**：`{'、'.join(sorted(list(combined_zodiacs_set)))}`")
                    if combined_nums:
                        st.code(", ".join([f"{x:02d}" for x in combined_nums]), language="text")
                    else:
                        st.info("暂无空间形态号码")

            # ==========================================
            # 🌸 TAB 7: ✨ 四季生肖拐点选号 (🔥功能七全新上线)
            # ==========================================
            with tab7:
                st.subheader("🌸 四季生肖（春夏秋冬）触底拐点智能选号引擎")
                st.markdown("""
                💡 **四季生肖拐点逻辑**：
                * 自动扫描功能二中 **春肖 (虎兔龙)**、**夏肖 (蛇马羊)**、**秋肖 (猴鸡狗)**、**冬肖 (猪鼠牛)** 的遗漏触底状态；
                * 提取触发 **【当前遗漏 $\ge$ 上次遗漏】（即带 ⚡ 闪电标记）** 的季节肖，并自动反查打捞该季节所对应的全部特码。
                """)
                
                # 抓取带闪电的季节肖
                triggered_seasons = [sn for sn in zodiac_seasons if season_omission[sn] >= season_last_omission[sn]]
                season_zodiacs_set = set()
                for sn in triggered_seasons:
                    season_zodiacs_set.update(zodiac_seasons[sn])
                
                season_selected_nums = [n for n in range(1, 50) if get_zodiac_of_number(n) in season_zodiacs_set]
                season_selected_nums.sort()
                
                st.write("---")
                st.success(f"🏆 **【四季闪电拐点精选全包池】本期共命中 {len(triggered_seasons)} 个季节肖，精选特码共 {len(season_selected_nums)} 个：**")
                st.caption(f"🚨 **本期触发闪电的季节肖**：`{', '.join(triggered_seasons) if triggered_seasons else '暂无'}` ｜ 涵盖生肖：`{'、'.join(sorted(list(season_zodiacs_set)))}`")
                st.markdown("👇 **请点击下方代码框右上角的小图标，即可秒级全选复制到剪贴板：**")
                
                if season_selected_nums:
                    st.code(", ".join([f"{x:02d}" for x in season_selected_nums]), language="text")
                else:
                    st.info("提示：本期四季生肖中暂无分区触发遗漏拐点。")
                st.write("---")
                
                # 四季生肖分栏独立展示
                st.markdown("### 🔍 四季生肖各自状态与对应特码库")
                sc1, sc2, sc3, sc4 = st.columns(4)
                
                with sc1:
                    is_spr = '春肖' in triggered_seasons
                    spr_nums = [n for n in range(1, 50) if get_zodiac_of_number(n) in zodiac_seasons['春肖']]
                    st.markdown(f"🌱 **春肖 (虎兔龙) {'🚨 ⚡' if is_spr else ''}**")
                    st.caption(f"当前遗漏: **{season_omission['春肖']}期** ｜ 上次: {season_last_omission['春肖']}期")
                    st.code(", ".join([f"{x:02d}" for x in spr_nums]), language="text")
                    
                with sc2:
                    is_sum = '夏肖' in triggered_seasons
                    sum_nums = [n for n in range(1, 50) if get_zodiac_of_number(n) in zodiac_seasons['夏肖']]
                    st.markdown(f"☀️ **夏肖 (蛇马羊) {'🚨 ⚡' if is_sum else ''}**")
                    st.caption(f"当前遗漏: **{season_omission['夏肖']}期** ｜ 上次: {season_last_omission['夏肖']}期")
                    st.code(", ".join([f"{x:02d}" for x in sum_nums]), language="text")
                    
                with sc3:
                    is_aut = '秋肖' in triggered_seasons
                    aut_nums = [n for n in range(1, 50) if get_zodiac_of_number(n) in zodiac_seasons['秋肖']]
                    st.markdown(f"🍂 **秋肖 (猴鸡狗) {'🚨 ⚡' if is_aut else ''}**")
                    st.caption(f"当前遗漏: **{season_omission['秋肖']}期** ｜ 上次: {season_last_omission['秋肖']}期")
                    st.code(", ".join([f"{x:02d}" for x in aut_nums]), language="text")
                    
                with sc4:
                    is_win = '冬肖' in triggered_seasons
                    win_nums = [n for n in range(1, 50) if get_zodiac_of_number(n) in zodiac_seasons['冬肖']]
                    st.markdown(f"❄️ **冬肖 (猪鼠牛) {'🚨 ⚡' if is_win else ''}**")
                    st.caption(f"当前遗漏: **{season_omission['冬肖']}期** ｜ 上次: {season_last_omission['冬肖']}期")
                    st.code(", ".join([f"{x:02d}" for x in win_nums]), language="text")

    except Exception as global_ex:
        st.error(f"🚨 大盘核心数据解析时发生错误: {global_ex}")
        st.code(traceback.format_exc(), language="text")
