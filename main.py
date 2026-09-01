import streamlit as st
import pandas as pd
from collections import defaultdict
import numpy as np
import traceback

# 页面基础配置
st.set_page_config(page_title="数据全维度智能统计看板", layout="wide")
st.title("📊 开奖记录全维度综合统计看板 (滑动选功能+动态实时胜率版)")
st.caption("最新总体冷热 ｜ 当前双重遗漏与欲出几率 ｜ 空间分区与四季五行七段 ｜ 纵向状态转移 ｜ 🎯选号与杀号 ｜ 🧊冷热遗漏分层")

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

            # 生肖空间形态、四季、五行与七段数体系定义
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

            five_elements = {
                '金行': [4, 5, 12, 13, 26, 27, 34, 35, 42, 43],
                '木行': [8, 9, 16, 17, 24, 25, 38, 39, 46, 47],
                '水行': [1, 14, 15, 22, 23, 30, 31, 44, 45],
                '火行': [2, 3, 10, 11, 18, 19, 32, 33, 40, 41, 48, 49],
                '土行': [6, 7, 20, 21, 28, 29, 36, 37]
            }

            seven_segments = {
                '1段': list(range(1, 8)),
                '2段': list(range(8, 15)),
                '3段': list(range(15, 22)),
                '4段': list(range(22, 29)),
                '5段': list(range(29, 36)),
                '6段': list(range(36, 43)),
                '7段': list(range(43, 50))
            }

            # 基础出现总数统计
            num_counts = defaultdict(int)
            tail_counts = defaultdict(int)
            zodiac_counts = defaultdict(int)
            head_counts_dict = defaultdict(int)
            zone_counts = defaultdict(int)
            season_counts = defaultdict(int)
            element_counts = defaultdict(int)
            segment_counts = defaultdict(int)
            
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
                for e_name, e_nums in five_elements.items():
                    if num in e_nums:
                        element_counts[e_name] += 1
                for seg_name, seg_nums in seven_segments.items():
                    if num in seg_nums:
                        segment_counts[seg_name] += 1

            # 🛠️ 建立全量位置索引
            num_indices = defaultdict(list)
            tail_indices = defaultdict(list)
            zodiac_indices = defaultdict(list)
            head_indices = defaultdict(list)
            zone_indices = defaultdict(list)
            season_indices = defaultdict(list)
            element_indices = defaultdict(list)
            segment_indices = defaultdict(list)
            
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
                for e_name, e_nums in five_elements.items():
                    if num in e_nums:
                        element_indices[e_name].append(i)
                for seg_name, seg_nums in seven_segments.items():
                    if num in seg_nums:
                        segment_indices[seg_name].append(i)

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

            # 6. 四季生肖双重遗漏与欲出几率
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

            # 7. 五行属性双重遗漏与欲出几率
            element_omission = {}
            element_last_omission = {}
            element_rates = {}
            for e_name in five_elements:
                idxs = element_indices[e_name]
                if idxs:
                    element_omission[e_name] = (total_records - 1) - idxs[-1]
                    element_last_omission[e_name] = idxs[-1] - idxs[-2] - 1 if len(idxs) >= 2 else idxs[-1]
                else:
                    element_omission[e_name] = total_records
                    element_last_omission[e_name] = 0
                cnt = element_counts[e_name]
                avg_int = (total_records / cnt) if cnt > 0 else total_records
                element_rates[e_name] = element_omission[e_name] / avg_int

            # 8. 七段数双重遗漏与欲出几率
            segment_omission = {}
            segment_last_omission = {}
            segment_rates = {}
            for seg_name in seven_segments:
                idxs = segment_indices[seg_name]
                if idxs:
                    segment_omission[seg_name] = (total_records - 1) - idxs[-1]
                    segment_last_omission[seg_name] = idxs[-1] - idxs[-2] - 1 if len(idxs) >= 2 else idxs[-1]
                else:
                    segment_omission[seg_name] = total_records
                    segment_last_omission[seg_name] = 0
                cnt = segment_counts[seg_name]
                avg_int = (total_records / cnt) if cnt > 0 else total_records
                segment_rates[seg_name] = segment_omission[seg_name] / avg_int

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

            # =========================================================================
            # ⚡ 核心引擎：针对上传表格执行【全量动态滚动回测】，毫秒级计算各策略真实胜率
            # =========================================================================
            start_backtest_idx = min(30, max(2, total_records // 5))
            test_periods_count = 0

            hits_dyn_f4 = 0
            hits_dyn_or = 0
            hits_dyn_seasons = 0
            hits_dyn_elements = 0
            hits_dyn_segments = 0
            hits_dyn_layers = 0
            kill_success_dyn_top15 = 0

            pool_dyn_f4 = []
            pool_dyn_or = []
            pool_dyn_seasons = []
            pool_dyn_elements = []
            pool_dyn_segments = []
            pool_dyn_layers = []

            for i in range(start_backtest_idx, total_records - 1):
                hist_sub = parsed_data[:i+1]
                h_len = len(hist_sub)
                n_num, n_zod = parsed_data[i+1]
                
                sub_num_idx = defaultdict(list)
                sub_tail_idx = defaultdict(list)
                sub_zod_idx = defaultdict(list)
                sub_z2_idx = defaultdict(list)
                sub_z3_idx = defaultdict(list)
                sub_sea_idx = defaultdict(list)
                sub_elem_idx = defaultdict(list)
                sub_seg_idx = defaultdict(list)
                
                sub_num_cnt = defaultdict(int)
                sub_tail_cnt = defaultdict(int)
                sub_zod_cnt = defaultdict(int)
                
                for idx_s, (s_num, s_zod) in enumerate(hist_sub):
                    sub_num_idx[s_num].append(idx_s)
                    sub_tail_idx[s_num % 10].append(idx_s)
                    sub_zod_idx[s_zod].append(idx_s)
                    sub_num_cnt[s_num] += 1
                    sub_tail_cnt[s_num % 10] += 1
                    sub_zod_cnt[s_zod] += 1
                    for zn, zl in zodiac_zones_2.items():
                        if s_zod in zl: sub_z2_idx[zn].append(idx_s)
                    for zn, zl in zodiac_zones_3.items():
                        if s_zod in zl: sub_z3_idx[zn].append(idx_s)
                    for sn, sl in zodiac_seasons.items():
                        if s_zod in sl: sub_sea_idx[sn].append(idx_s)
                    for en, el in five_elements.items():
                        if s_num in el: sub_elem_idx[en].append(idx_s)
                    for sgn, sgl in seven_segments.items():
                        if s_num in sgl: sub_seg_idx[sgn].append(idx_s)
                        
                def get_sub_inf(idx_map, keys):
                    trig = set()
                    for k in keys:
                        idxs = idx_map[k]
                        cur_m = (h_len - 1 - idxs[-1]) if idxs else h_len
                        last_m = (idxs[-1] - idxs[-2] - 1) if len(idxs) >= 2 else (idxs[-1] if idxs else 0)
                        if cur_m >= last_m: trig.add(k)
                    return trig

                sub_zod_om = {z: (h_len - 1 - sub_zod_idx[z][-1]) if sub_zod_idx[z] else h_len for z in all_zodiacs}
                sub_zod_last = {z: (sub_zod_idx[z][-1] - sub_zod_idx[z][-2] - 1) if len(sub_zod_idx[z]) >= 2 else (sub_zod_idx[z][-1] if sub_zod_idx[z] else 0) for z in all_zodiacs}
                sub_tail_om = {t: (h_len - 1 - sub_tail_idx[t][-1]) if sub_tail_idx[t] else h_len for t in all_tails}
                sub_tail_last = {t: (sub_tail_idx[t][-1] - sub_tail_idx[t][-2] - 1) if len(sub_tail_idx[t]) >= 2 else (sub_tail_idx[t][-1] if sub_tail_idx[t] else 0) for t in all_tails}
                sub_num_om = {n: (h_len - 1 - sub_num_idx[n][-1]) if sub_num_idx[n] else h_len for n in range(1, 50)}
                sub_num_last = {n: (sub_num_idx[n][-1] - sub_num_idx[n][-2] - 1) if len(sub_num_idx[n]) >= 2 else (sub_num_idx[n][-1] if sub_num_idx[n] else 0) for n in range(1, 50)}

                sub_zod_rates = {z: sub_zod_om[z] / ((h_len / sub_zod_cnt[z]) if sub_zod_cnt[z] > 0 else h_len) for z in all_zodiacs}
                sub_tail_rates = {t: sub_tail_om[t] / ((h_len / sub_tail_cnt[t]) if sub_tail_cnt[t] > 0 else h_len) for t in all_tails}
                sub_num_rates = {n: sub_num_om[n] / ((h_len / sub_num_cnt[n]) if sub_num_cnt[n] > 0 else h_len) for n in range(1, 50)}

                # 1. 回测功能四
                sub_f4 = []
                for n in range(1, 50):
                    t = n % 10
                    z = get_zodiac_of_number(n)
                    r1_rem = (sub_zod_rates[z] < 0.4) and (sub_zod_om[z] < sub_zod_last[z])
                    r2_rem = (sub_tail_rates[t] < 0.4) and (sub_tail_om[t] < sub_tail_last[t])
                    can_res = (sub_zod_om[z] >= sub_zod_last[z]) or (sub_tail_om[t] >= sub_tail_last[t])
                    if (r1_rem or r2_rem) and not can_res: continue
                    sub_f4.append(n)
                if n_num in sub_f4: hits_dyn_f4 += 1
                pool_dyn_f4.append(len(sub_f4))
                
                # 2. 回测杀15码安全率
                sub_scores = []
                for n in range(1, 50):
                    t = n % 10
                    z = get_zodiac_of_number(n)
                    sc = 0.35 * sub_zod_rates[z] + 0.35 * sub_tail_rates[t] + 0.30 * sub_num_rates[n]
                    if sub_zod_om[z] < sub_zod_last[z]: sc -= 0.15
                    if sub_tail_om[t] < sub_tail_last[t]: sc -= 0.15
                    if sub_num_om[n] < sub_num_last[n]: sc -= 0.10
                    sub_scores.append((n, sc))
                sub_scores.sort(key=lambda x: (x[1], x[0]))
                sub_top15_kill = set([x[0] for x in sub_scores[:15]])
                if n_num not in sub_top15_kill: kill_success_dyn_top15 += 1
                
                # 3. 回测空间形态OR
                sub_trig_z2 = get_sub_inf(sub_z2_idx, zodiac_zones_2.keys())
                sub_trig_z3 = get_sub_inf(sub_z3_idx, zodiac_zones_3.keys())
                sub_zods_or = set([z for zn in sub_trig_z2 for z in zodiac_zones_2[zn]]).union([z for zn in sub_trig_z3 for z in zodiac_zones_3[zn]])
                sub_nums_or = [n for n in range(1, 50) if get_zodiac_of_number(n) in sub_zods_or]
                if n_num in sub_nums_or: hits_dyn_or += 1
                pool_dyn_or.append(len(sub_nums_or))
                
                # 4. 回测四季生肖
                sub_trig_sea = get_sub_inf(sub_sea_idx, zodiac_seasons.keys())
                sub_zods_sea = set([z for sn in sub_trig_sea for z in zodiac_seasons[sn]])
                sub_nums_sea = [n for n in range(1, 50) if get_zodiac_of_number(n) in sub_zods_sea]
                if n_num in sub_nums_sea: hits_dyn_seasons += 1
                pool_dyn_seasons.append(len(sub_nums_sea))
                
                # 5. 回测五行属性
                sub_trig_elem = get_sub_inf(sub_elem_idx, five_elements.keys())
                sub_nums_elem = sorted(list(set([n for en in sub_trig_elem for n in five_elements[en]])))
                if n_num in sub_nums_elem: hits_dyn_elements += 1
                pool_dyn_elements.append(len(sub_nums_elem))
                
                # 6. 回测七段数
                sub_trig_seg = get_sub_inf(sub_seg_idx, seven_segments.keys())
                sub_nums_seg = sorted(list(set([n for sgn in sub_trig_seg for n in seven_segments[sgn]])))
                if n_num in sub_nums_seg: hits_dyn_segments += 1
                pool_dyn_segments.append(len(sub_nums_seg))
                
                # 7. 回测冷热分层
                sub_nums_lay = []
                for n in range(1, 50):
                    om = sub_num_om[n]
                    is_inf = om >= sub_num_last[n]
                    rate = sub_num_rates[n]
                    if om <= 25: sub_nums_lay.append(n)
                    elif 26 <= om <= 50 and (is_inf or rate >= 0.40): sub_nums_lay.append(n)
                    elif 51 <= om <= 100 and is_inf: sub_nums_lay.append(n)
                if n_num in sub_nums_lay: hits_dyn_layers += 1
                pool_dyn_layers.append(len(sub_nums_lay))
                
                test_periods_count += 1

            # 计算动态胜率百分比
            rate_f4 = (hits_dyn_f4 / test_periods_count * 100) if test_periods_count > 0 else 0.0
            rate_kill15 = (kill_success_dyn_top15 / test_periods_count * 100) if test_periods_count > 0 else 0.0
            rate_or = (hits_dyn_or / test_periods_count * 100) if test_periods_count > 0 else 0.0
            rate_seasons = (hits_dyn_seasons / test_periods_count * 100) if test_periods_count > 0 else 0.0
            rate_elements = (hits_dyn_elements / test_periods_count * 100) if test_periods_count > 0 else 0.0
            rate_segments = (hits_dyn_segments / test_periods_count * 100) if test_periods_count > 0 else 0.0
            rate_layers = (hits_dyn_layers / test_periods_count * 100) if test_periods_count > 0 else 0.0

            # =========================================================================
            # 🎛️ 功能导航体系：用【滑动选择器】代替翻页，并实时动态绑定最新胜率
            # =========================================================================
            st.write("---")
            
            func_options = [
                "1. 🔥 大盘总量冷热统计",
                "2. ⏳ 当前双重遗漏与欲出",
                "3. 🔄 前后行状态转移矩阵",
                f"4. 🎯 拐点特赦智能选号 【胜率: {rate_f4:.1f}%】",
                f"5. ❌ 综合反向杀15码 【安全率: {rate_kill15:.1f}%】",
                f"6. ⚡ 空间形态拐点选号 【胜率: {rate_or:.1f}%】",
                f"7. 🌸 四季生肖拐点选号 【胜率: {rate_seasons:.1f}%】",
                f"8. 🪙 五行属性拐点选号 【胜率: {rate_elements:.1f}%】",
                f"9. 🔢 七段数拐点选号 【胜率: {rate_segments:.1f}%】",
                f"10. 🧊 冷热遗漏分层控码 【胜率: {rate_layers:.1f}%】"
            ]

            selected_func = st.select_slider(
                "🎛️ **请左右滑动选择要查看的统计或预测功能模块（各模型已自动根据上传表格计算最新动态历史胜率）：**",
                options=func_options,
                value=func_options[3] # 默认定位在功能四
            )

            st.write("---")

            # ==========================================
            # 功能 1: 大盘总量冷热榜
            # ==========================================
            if selected_func.startswith("1."):
                st.subheader("📊 整体出现次数总计 (全量大盘分析)")
                hot_col1, hot_col2, hot_col3 = st.columns(3)
                with hot_col1:
                    st.markdown("### 🔢 号码冷热排行 (1-49)")
                    num_hot_data = [(n, num_counts[n], (num_counts[n]/total_records*100 if total_records>0 else 0.0)) for n in range(1, 50)]
                    num_hot_data.sort(key=lambda x: (-x[1], x[0]))
                    md = "| 排名 | 号码 | 出现次数 | 占比概率 |\\n| :---: | :---: | :---: | :---: |\\n"
                    for rank, (n, cnt, pct) in enumerate(num_hot_data, 1):
                        num_str = f"**{n:02d}**" if rank <= 3 and cnt > 0 else f"{n:02d}"
                        flag = "🔥" if rank <= 3 and cnt > 0 else ("❄️" if cnt == 0 else "")
                        md += f"| {rank} | {num_str} {flag} | {cnt}次 | {pct:.1f}% |\\n"
                    st.markdown(md)
                with hot_col2:
                    st.markdown("### 🎯 尾数冷热排行 (0-9)")
                    tail_hot_data = [(t, tail_counts[t], (tail_counts[t]/total_records*100 if total_records>0 else 0.0)) for t in all_tails]
                    tail_hot_data.sort(key=lambda x: (-x[1], x[0]))
                    md = "| 排名 | 尾数 | 出现次数 | 占比概率 |\\n| :---: | :---: | :---: | :---: |\\n"
                    for rank, (t, cnt, pct) in enumerate(tail_hot_data, 1):
                        tail_str = f"**{t}尾**" if rank <= 3 and cnt > 0 else f"{t}尾"
                        flag = "🔥" if rank <= 3 and cnt > 0 else ("❄️" if cnt == 0 else "")
                        md += f"| {rank} | {tail_str} {flag} | {cnt}次 | {pct:.1f}% |\\n"
                    st.markdown(md)
                with hot_col3:
                    st.markdown("### 🔮 生肖冷热排行")
                    zodiac_hot_data = [(z, zodiac_counts[z], (zodiac_counts[z]/total_records*100 if total_records>0 else 0.0)) for z in all_zodiacs]
                    zodiac_hot_data.sort(key=lambda x: (-x[1], all_zodiacs.index(x[0])))
                    md = "| 排名 | 生肖 | 出现次数 | 占比概率 |\\n| :---: | :---: | :---: | :---: |\\n"
                    for rank, (z, cnt, pct) in enumerate(zodiac_hot_data, 1):
                        zodiac_str = f"**{z}**" if rank <= 3 and cnt > 0 else z
                        flag = "🔥" if rank <= 3 and cnt > 0 else ("❄️" if cnt == 0 else "")
                        md += f"| {rank} | {zodiac_str} {flag} | {cnt}次 | {pct:.1f}% |\\n"
                    st.markdown(md)

            # ==========================================
            # 功能 2: 当前未出遗漏与欲出榜
            # ==========================================
            elif selected_func.startswith("2."):
                st.subheader("⏳ 各指标未出当前遗漏与最近一次开出历史间隔深度统计")
                st.caption("💡 **标注说明**：带有 **🚨 警报** 代表【当前遗漏 $\\\\ge$ 上次遗漏】（触底拐点）；带有 **🔥 火焰** 代表【欲出几率 $\\\\ge$ 0.40】（高热度区）！")
                
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
                    md = "| 排名 | 号码 | 当前遗漏 | 上次遗漏 | 平均间隔 | 欲出几率 |\\n| :---: | :---: | :---: | :---: | :---: | :---: |\\n"
                    for r, (n, miss, l_miss, avg_int, rate) in enumerate(num_list, 1):
                        is_inflection = (miss >= l_miss)
                        is_high_rate = (rate >= 0.4)
                        tags = (" 🚨" if is_inflection else "") + (" 🔥" if is_high_rate else "")
                        n_str = f"**{n:02d}**{tags}" if (is_inflection or is_high_rate) else f"{n:02d}"
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        rate_str = f"**{rate:.2f}** 🔥" if is_high_rate else f"{rate:.2f}"
                        md += f"| {r} | {n_str} | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | {rate_str} |\\n"
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
                    md = "| 排名 | 生肖 | 当前遗漏 | 上次遗漏 | 平均间隔 | 欲出几率 |\\n| :---: | :---: | :---: | :---: | :---: | :---: |\\n"
                    for r, (z, miss, l_miss, avg_int, rate) in enumerate(zodiac_list, 1):
                        is_inflection = (miss >= l_miss)
                        is_high_rate = (rate >= 0.4)
                        tags = (" 🚨" if is_inflection else "") + (" 🔥" if is_high_rate else "")
                        z_str = f"**{z}**{tags}" if (is_inflection or is_high_rate) else z
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        rate_str = f"**{rate:.2f}** 🔥" if is_high_rate else f"{rate:.2f}"
                        md += f"| {r} | {z_str} | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | {rate_str} |\\n"
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
                    md = "| 排名 | 尾数 | 当前遗漏 | 上次遗漏 | 平均间隔 | 欲出几率 |\\n| :---: | :---: | :---: | :---: | :---: | :---: |\\n"
                    for r, (t, miss, l_miss, avg_int, rate) in enumerate(tail_list_disp, 1):
                        is_inflection = (miss >= l_miss)
                        is_high_rate = (rate >= 0.4)
                        tags = (" 🚨" if is_inflection else "") + (" 🔥" if is_high_rate else "")
                        t_str = f"**{t}尾**{tags}" if (is_inflection or is_high_rate) else f"{t}尾"
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        rate_str = f"**{rate:.2f}** 🔥" if is_high_rate else f"{rate:.2f}"
                        md += f"| {r} | {t_str} | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | {rate_str} |\\n"
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
                    md = "| 排名 | 头数 | 当前遗漏 | 上次遗漏 | 平均间隔 | 欲出几率 |\\n| :---: | :---: | :---: | :---: | :---: | :---: |\\n"
                    for r, (h, miss, l_miss, avg_int, rate) in enumerate(head_list_disp, 1):
                        is_inflection = (miss >= l_miss)
                        is_high_rate = (rate >= 0.4)
                        tags = (" 🚨" if is_inflection else "") + (" 🔥" if is_high_rate else "")
                        h_str = f"**{h}头**{tags}" if (is_inflection or is_high_rate) else f"{h}头"
                        miss_str = f"**{miss}期** ⚡" if is_inflection else f"{miss}期"
                        rate_str = f"**{rate:.2f}** 🔥" if is_high_rate else f"{rate:.2f}"
                        md += f"| {r} | {h_str} | {miss_str} | {l_miss}期 | {avg_int:.1f}期 | {rate_str} |\\n"
                    st.markdown(md)

                st.write("---")
                st.subheader("🔮 空间形态 / 四季生肖 / 五行属性 / 七段数 遗漏与欲出深度统计")
                zone_col1, zone_col2, zone_col3, zone_col4, zone_col5 = st.columns(5)
                with zone_col1:
                    st.markdown("### 🌗 二分空间 (上下区)")
                    z2_list = [(zn, zone_counts[zn], zone_omission[zn], zone_last_omission[zn], zone_rates[zn]) for zn in zodiac_zones_2]
                    z2_list.sort(key=lambda x: -x[4])
                    z2_md = "| 分区 | 遗漏 | 上次 | 欲出 |\\n| :---: | :---: | :---: | :---: |\\n"
                    for zn, cnt, miss, l_miss, rate in z2_list:
                        is_inf = (miss >= l_miss)
                        tags = (" 🚨" if is_inf else "") + (" 🔥" if rate>=0.4 else "")
                        z2_md += f"| **{zn}**{tags} | **{miss}**⚡ | {l_miss} | **{rate:.2f}** |\\n" if is_inf else f"| {zn}{tags} | {miss} | {l_miss} | {rate:.2f} |\\n"
                    st.markdown(z2_md)
                with zone_col2:
                    st.markdown("### 🧭 三分空间 (左中右区)")
                    z3_list = [(zn, zone_counts[zn], zone_omission[zn], zone_last_omission[zn], zone_rates[zn]) for zn in zodiac_zones_3]
                    z3_list.sort(key=lambda x: -x[4])
                    z3_md = "| 分区 | 遗漏 | 上次 | 欲出 |\\n| :---: | :---: | :---: | :---: |\\n"
                    for zn, cnt, miss, l_miss, rate in z3_list:
                        is_inf = (miss >= l_miss)
                        tags = (" 🚨" if is_inf else "") + (" 🔥" if rate>=0.4 else "")
                        z3_md += f"| **{zn}**{tags} | **{miss}**⚡ | {l_miss} | **{rate:.2f}** |\\n" if is_inf else f"| {zn}{tags} | {miss} | {l_miss} | {rate:.2f} |\\n"
                    st.markdown(z3_md)
                with zone_col3:
                    st.markdown("### 🌸 四季生肖")
                    season_list = [(sn, season_counts[sn], season_omission[sn], season_last_omission[sn], season_rates[sn]) for sn in zodiac_seasons]
                    season_list.sort(key=lambda x: -x[4])
                    season_md = "| 季肖 | 遗漏 | 上次 | 欲出 |\\n| :---: | :---: | :---: | :---: |\\n"
                    for sn, cnt, miss, l_miss, rate in season_list:
                        is_inf = (miss >= l_miss)
                        tags = (" 🚨" if is_inf else "") + (" 🔥" if rate>=0.4 else "")
                        season_md += f"| **{sn}**{tags} | **{miss}**⚡ | {l_miss} | **{rate:.2f}** |\\n" if is_inf else f"| {sn}{tags} | {miss} | {l_miss} | {rate:.2f} |\\n"
                    st.markdown(season_md)
                with zone_col4:
                    st.markdown("### 🪙 五行属性")
                    element_list = [(en, element_counts[en], element_omission[en], element_last_omission[en], element_rates[en]) for en in five_elements]
                    element_list.sort(key=lambda x: -x[4])
                    element_md = "| 五行 | 遗漏 | 上次 | 欲出 |\\n| :---: | :---: | :---: | :---: |\\n"
                    for en, cnt, miss, l_miss, rate in element_list:
                        is_inf = (miss >= l_miss)
                        tags = (" 🚨" if is_inf else "") + (" 🔥" if rate>=0.4 else "")
                        element_md += f"| **{en}**{tags} | **{miss}**⚡ | {l_miss} | **{rate:.2f}** |\\n" if is_inf else f"| {en}{tags} | {miss} | {l_miss} | {rate:.2f} |\\n"
                    st.markdown(element_md)
                with zone_col5:
                    st.markdown("### 🔢 七段数")
                    segment_list = [(sgn, segment_counts[sgn], segment_omission[sgn], segment_last_omission[sgn], segment_rates[sgn]) for sgn in seven_segments]
                    segment_list.sort(key=lambda x: -x[4])
                    segment_md = "| 段数 | 遗漏 | 上次 | 欲出 |\\n| :---: | :---: | :---: | :---: |\\n"
                    for sgn, cnt, miss, l_miss, rate in segment_list:
                        is_inf = (miss >= l_miss)
                        tags = (" 🚨" if is_inf else "") + (" 🔥" if rate>=0.4 else "")
                        segment_md += f"| **{sgn}**{tags} | **{miss}**⚡ | {l_miss} | **{rate:.2f}** |\\n" if is_inf else f"| {sgn}{tags} | {miss} | {l_miss} | {rate:.2f} |\\n"
                    st.markdown(segment_md)

            # ==========================================
            # 功能 3: 前后行状态转移矩阵
            # ==========================================
            elif selected_func.startswith("3."):
                st.subheader("🔄 纵向序列演变规律概率分布")
                trans_col1, trans_col2, trans_col3 = st.columns(3)
                with trans_col1:
                    st.markdown("### 🔢 尾数 0-9 后行尾数完整分布")
                    tail_trans_md = "| 当前尾数 | 历史总计 | 下一行尾数概率分布 (降序排列) |\\n| :---: | :---: | :--- |\\n"
                    for tail in range(10):
                        nexts = tail_transitions[tail]
                        total = len(nexts)
                        counts = defaultdict(int)
                        for n in nexts: counts[n] += 1
                        max_count = max(counts.values()) if counts else 0
                        prob_parts = [(t, counts[t], (counts[t]/total*100 if total>0 else 0.0)) for t in all_tails]
                        prob_parts.sort(key=lambda x: (-x[1], x[0]))
                        formatted_parts = [f"**{t}尾: {p:.1f}%({c}次)**" if c==max_count and max_count>0 else f"{t}尾: {p:.1f}%({c}次)" for t, c, p in prob_parts]
                        tail_trans_md += f"| **{tail}尾** | {total}次 | {' ｜ '.join(formatted_parts)} |\\n"
                    st.markdown(tail_trans_md, unsafe_allow_html=True)

                with trans_col2:
                    st.markdown("### 🔮 12生肖 后行生肖完整分布")
                    zodiac_trans_md = "| 当前生肖 | 历史总计 | 下一行生肖概率分布 (降序排列) |\\n| :---: | :---: | :--- |\\n"
                    for z in all_zodiacs:
                        nexts = zodiac_transitions[z]
                        total = len(nexts)
                        counts = defaultdict(int)
                        for n in nexts: counts[n] += 1
                        max_count = max(counts.values()) if counts else 0
                        prob_parts = [(nz, counts[nz], (counts[nz]/total*100 if total>0 else 0.0)) for nz in all_zodiacs]
                        prob_parts.sort(key=lambda x: (-x[1], all_zodiacs.index(x[0])))
                        formatted_parts = [f"**{nz}: {p:.1f}%({c}次)**" if c==max_count and max_count>0 else f"{nz}: {p:.1f}%({c}次)" for nz, c, p in prob_parts]
                        zodiac_trans_md += f"| **{z}** | {total}次 | {' ｜ '.join(formatted_parts)} |\\n"
                    st.markdown(zodiac_trans_md, unsafe_allow_html=True)

                with trans_col3:
                    st.markdown("### 🔝 头数 0-4 后行头数完整分布")
                    head_trans_md = "| 当前头数 | 历史总计 | 下一行头数概率分布 (降序排列) |\\n| :---: | :---: | :--- |\\n"
                    for head in range(5):
                        nexts = head_transitions[head]
                        total = len(nexts)
                        counts = defaultdict(int)
                        for n in nexts: counts[n] += 1
                        max_count = max(counts.values()) if counts else 0
                        prob_parts = [(h, counts[h], (counts[h]/total*100 if total>0 else 0.0)) for h in all_heads]
                        prob_parts.sort(key=lambda x: (-x[1], x[0]))
                        formatted_parts = [f"**{h}头: {p:.1f}%({c}次)**" if c==max_count and max_count>0 else f"{h}头: {p:.1f}%({c}次)" for h, c, p in prob_parts]
                        head_trans_md += f"| **{head}头** | {total}次 | {' ｜ '.join(formatted_parts)} |\\n"
                    st.markdown(head_trans_md, unsafe_allow_html=True)

            # ==========================================
            # 功能 4: 🎯 剔除与拐点特赦智能选号
            # ==========================================
            elif selected_func.startswith("4."):
                st.subheader("🎯 智能精选选号（欲出率剔除 + 遗漏拐点特赦）")
                
                # 动态胜率展示卡
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                kpi1.metric("📈 动态历史综合胜率", f"{rate_f4:.2f}%")
                kpi2.metric("✅ 历史命中期数", f"{hits_dyn_f4} / {test_periods_count} 期")
                kpi3.metric("🔢 平均每期码数", f"{np.mean(pool_dyn_f4):.1f} 码")
                kpi4.metric("🛡️ 平均排除死码", f"{49 - np.mean(pool_dyn_f4):.1f} 码")
                
                st.markdown("""
                💡 **最新过滤逻辑**：
                1. **删除**：欲出率 < 40% 且 本次遗漏 < 上次遗漏 的生肖对应号码；
                2. **删除**：欲出率 < 40% 且 本次遗漏 < 上次遗漏 的尾数对应号码；
                3. **特赦恢复**：被上述剔除规则标记的号码中，只要其 **生肖** 或 **尾数** 满足【本次遗漏 $\\\\ge$ 上次遗漏】，强制予以特赦恢复保留！
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
                st.code(", ".join(formatted_nums) if formatted_nums else "暂无符合条件号码", language="text")
                st.write("---")

            # ==========================================
            # 功能 5: ❌ 综合分析反向杀号 (精选 15 码)
            # ==========================================
            elif selected_func.startswith("5."):
                st.subheader("❌ 综合概率模型：精选最不可能出现的 15 个号码 (反向杀号池)")
                
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("🛡️ 15杀码历史安全排除率", f"{rate_kill15:.2f}%")
                kpi2.metric("🎯 成功避坑期数", f"{kill_success_dyn_top15} / {test_periods_count} 期")
                kpi3.metric("🚫 固定每期排除码数", "15 码 (固定)")

                st.markdown("""
                💡 **计算模型**：融合【生肖欲出率(35%) + 尾数欲出率(35%) + 号码欲出率(30%)】三维权重，
                并对未触底拐点（当前遗漏 < 上次遗漏）的弱势指标执行智能扣分，精准筛选出全盘概率势能最低的 **15 个危险冷杂码**。
                """)
                
                exclusion_scores = []
                for n in range(1, 50):
                    t = n % 10
                    z = get_zodiac_of_number(n)
                    score = 0.35 * zodiac_rates[z] + 0.35 * tail_rates[t] + 0.30 * num_rates[n]
                    if zodiac_omission[z] < zodiac_last_omission[z]: score -= 0.15
                    if tail_omission[t] < tail_last_omission[t]: score -= 0.15
                    if num_omission[n] < num_last_omission[n]: score -= 0.10
                    exclusion_scores.append((n, score, zodiac_rates[z], tail_rates[t], num_rates[n], z, t))
                
                exclusion_scores.sort(key=lambda x: (x[1], x[0]))
                top_15_tuples = exclusion_scores[:15]
                top_15_nums = sorted([x[0] for x in top_15_tuples])
                formatted_top_15 = [f"{x:02d}" for x in top_15_nums]
                
                st.write("---")
                st.error(f"🚫 **【综合分析反向杀号池】本期精选最不可能开出的 15 个号码（已按从小到大重排）：**")
                st.markdown("👇 **实战极简配置：请点击右上方小图标全选复制，直接用于排除/杀号：**")
                st.code(", ".join(formatted_top_15), language="text")
                st.write("---")
                
                st.markdown("### 🔍 15 个杀码的定量参数与扣分明细表")
                details_md = "| 排名 | 杀码 | 生肖/尾数 | 综合风险分 | 生肖欲出率 | 尾数欲出率 | 号码欲出率 |\\n| :---: | :---: | :---: | :---: | :---: | :---: | :---: |\\n"
                for rank, (n, sc, z_r, t_r, n_r, z, t) in enumerate(top_15_tuples, 1):
                    details_md += f"| {rank} | **{n:02d}** | {z} / {t}尾 | **{sc:.3f}** | {z_r:.2f} | {t_r:.2f} | {n_r:.2f} |\\n"
                st.markdown(details_md)

            # ==========================================
            # 功能 6: ⚡ 生肖空间形态拐点选号
            # ==========================================
            elif selected_func.startswith("6."):
                st.subheader("⚡ 生肖空间形态分区（带闪电拐点）智能号码提取引擎")
                
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                kpi1.metric("🛡️ 空间OR包抄动态胜率", f"{rate_or:.2f}%")
                kpi2.metric("✅ 历史命中期数", f"{hits_dyn_or} / {test_periods_count} 期")
                kpi3.metric("🔢 平均涵盖码数", f"{np.mean(pool_dyn_or):.1f} 码")
                kpi4.metric("🏆 空间AND核心命中率", f"{(hits_and / test_periods_count * 100) if test_periods_count>0 else 0:.1f}%")

                st.markdown("""
                💡 **空间形态选号逻辑**：
                * 自动扫描功能二中 **上下区（二分空间）** 与 **左中右区（三分空间）** 的遗漏触底状态；
                * 提取触发 **【当前遗漏 $\\\\ge$ 上次遗漏】（即带 ⚡ 闪电标记）** 的分区所覆盖的全部生肖，并自动反查打捞对应的 1-49 特码。
                """)
                
                triggered_z2_zones = [zn for zn in zodiac_zones_2 if zone_omission[zn] >= zone_last_omission[zn]]
                z2_zodiacs_set = set([z for zn in triggered_z2_zones for z in zodiac_zones_2[zn]])
                z2_nums = sorted([n for n in range(1, 50) if get_zodiac_of_number(n) in z2_zodiacs_set])
                
                triggered_z3_zones = [zn for zn in zodiac_zones_3 if zone_omission[zn] >= zone_last_omission[zn]]
                z3_zodiacs_set = set([z for zn in triggered_z3_zones for z in zodiac_zones_3[zn]])
                z3_nums = sorted([n for n in range(1, 50) if get_zodiac_of_number(n) in z3_zodiacs_set])
                
                strict_zodiacs_set = z2_zodiacs_set.intersection(z3_zodiacs_set)
                strict_nums = sorted([n for n in range(1, 50) if get_zodiac_of_number(n) in strict_zodiacs_set])
                
                combined_zodiacs_set = z2_zodiacs_set.union(z3_zodiacs_set)
                combined_nums = sorted([n for n in range(1, 50) if get_zodiac_of_number(n) in combined_zodiacs_set])
                
                st.write("---")
                st.success(f"🏆 **【双区交集超级核心池】（二分闪电 ∩ 三分闪电 严格交集）共 {len(strict_nums)} 个特码：**")
                st.caption(f"🎯 **涵盖核心生肖**：`{'、'.join(sorted(list(strict_zodiacs_set)))}` ｜ 码数极度浓缩，适合精准重击！")
                st.code(", ".join([f"{x:02d}" for x in strict_nums]) if strict_nums else "暂无交集特码", language="text")
                st.write("---")
                
                c_z1, c_z2, c_z3 = st.columns(3)
                with c_z1:
                    st.markdown(f"🌗 **二分空间(上下区)闪电池 ({len(z2_nums)} 码)**")
                    st.caption(f"🚨 触发分区：{', '.join(triggered_z2_zones) if triggered_z2_zones else '无'}")
                    st.code(", ".join([f"{x:02d}" for x in z2_nums]) if z2_nums else "无", language="text")
                with c_z2:
                    st.markdown(f"🧭 **三分空间(左中右)闪电池 ({len(z3_nums)} 码)**")
                    st.caption(f"🚨 触发分区：{', '.join(triggered_z3_zones) if triggered_z3_zones else '无'}")
                    st.code(", ".join([f"{x:02d}" for x in z3_nums]) if z3_nums else "无", language="text")
                with c_z3:
                    st.markdown(f"🛡️ **空间形态全包抄池(OR并集) ({len(combined_nums)} 码)**")
                    st.caption(f"🔮 涵盖生肖：`{'、'.join(sorted(list(combined_zodiacs_set)))}`")
                    st.code(", ".join([f"{x:02d}" for x in combined_nums]) if combined_nums else "无", language="text")

            # ==========================================
            # 功能 7: 🌸 四季生肖拐点选号
            # ==========================================
            elif selected_func.startswith("7."):
                st.subheader("🌸 四季生肖（春夏秋冬）触底拐点智能选号引擎")
                
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("🌸 动态历史综合胜率", f"{rate_seasons:.2f}%")
                kpi2.metric("✅ 历史命中期数", f"{hits_dyn_seasons} / {test_periods_count} 期")
                kpi3.metric("🔢 平均涵盖码数", f"{np.mean(pool_dyn_seasons):.1f} 码")

                st.markdown("""
                💡 **四季生肖拐点逻辑**：
                * 自动扫描功能二中 **春肖 (虎兔龙)**、**夏肖 (蛇马羊)**、**秋肖 (猴鸡狗)**、**冬肖 (猪鼠牛)** 的遗漏触底状态；
                * 提取触发 **【当前遗漏 $\\\\ge$ 上次遗漏】（即带 ⚡ 闪电标记）** 的季节肖，并自动反查打捞该季节所对应的全部特码。
                """)
                
                triggered_seasons = [sn for sn in zodiac_seasons if season_omission[sn] >= season_last_omission[sn]]
                season_zodiacs_set = set([z for sn in triggered_seasons for z in zodiac_seasons[sn]])
                season_selected_nums = sorted([n for n in range(1, 50) if get_zodiac_of_number(n) in season_zodiacs_set])
                
                st.write("---")
                st.success(f"🏆 **【四季闪电拐点精选全包池】本期共命中 {len(triggered_seasons)} 个季节肖，精选特码共 {len(season_selected_nums)} 个：**")
                st.caption(f"🚨 **本期触发闪电的季节肖**：`{', '.join(triggered_seasons) if triggered_seasons else '暂无'}` ｜ 涵盖生肖：`{'、'.join(sorted(list(season_zodiacs_set)))}`")
                st.markdown("👇 **请点击下方代码框右上角的小图标，即可秒级全选复制到剪贴板：**")
                st.code(", ".join([f"{x:02d}" for x in season_selected_nums]) if season_selected_nums else "暂无触发号码", language="text")
                st.write("---")
                
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

            # ==========================================
            # 功能 8: 🪙 五行属性拐点选号
            # ==========================================
            elif selected_func.startswith("8."):
                st.subheader("🪙 五行属性（金木水火土）触底拐点智能选号引擎")
                
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("🪙 动态历史综合胜率", f"{rate_elements:.2f}%")
                kpi2.metric("✅ 历史命中期数", f"{hits_dyn_elements} / {test_periods_count} 期")
                kpi3.metric("🔢 平均涵盖码数", f"{np.mean(pool_dyn_elements):.1f} 码")

                st.markdown("""
                💡 **五行属性拐点选号逻辑**：
                * 自动扫描功能二中 **金行**、**木行**、**水行**、**火行**、**土行** 的双重遗漏与触底状态；
                * 自动提取触发 **【当前遗漏 $\\\\ge$ 上次遗漏】（即带 ⚡ 闪电标记）** 的五行属性，并自动打包输出对应属性的全部特码。
                """)
                
                triggered_elements = [en for en in five_elements if element_omission[en] >= element_last_omission[en]]
                element_selected_nums = sorted(list(set([n for en in triggered_elements for n in five_elements[en]])))
                
                st.write("---")
                st.success(f"🏆 **【五行闪电拐点精选全包池】本期共命中 {len(triggered_elements)} 个五行属性，精选特码共 {len(element_selected_nums)} 个：**")
                st.caption(f"🚨 **本期触发闪电的五行**：`{', '.join(triggered_elements) if triggered_elements else '暂无'}` ｜ 占比覆盖率：`{len(element_selected_nums)/49*100:.1f}%`")
                st.markdown("👇 **请点击下方代码框右上角的小图标，即可秒级全选复制到剪贴板：**")
                st.code(", ".join([f"{x:02d}" for x in element_selected_nums]) if element_selected_nums else "暂无触发号码", language="text")
                st.write("---")
                
                ec1, ec2, ec3, ec4, ec5 = st.columns(5)
                with ec1:
                    is_jin = '金行' in triggered_elements
                    st.markdown(f"🪙 **金行 {'🚨 ⚡' if is_jin else ''}**")
                    st.caption(f"当前: **{element_omission['金行']}期** ｜ 上次: {element_last_omission['金行']}期")
                    st.code(", ".join([f"{x:02d}" for x in five_elements['金行']]), language="text")
                with ec2:
                    is_mu = '木行' in triggered_elements
                    st.markdown(f"🌲 **木行 {'🚨 ⚡' if is_mu else ''}**")
                    st.caption(f"当前: **{element_omission['木行']}期** ｜ 上次: {element_last_omission['木行']}期")
                    st.code(", ".join([f"{x:02d}" for x in five_elements['木行']]), language="text")
                with ec3:
                    is_shui = '水行' in triggered_elements
                    st.markdown(f"💧 **水行 {'🚨 ⚡' if is_shui else ''}**")
                    st.caption(f"当前: **{element_omission['水行']}期** ｜ 上次: {element_last_omission['水行']}期")
                    st.code(", ".join([f"{x:02d}" for x in five_elements['水行']]), language="text")
                with ec4:
                    is_huo = '火行' in triggered_elements
                    st.markdown(f"🔥 **火行 {'🚨 ⚡' if is_huo else ''}**")
                    st.caption(f"当前: **{element_omission['火行']}期** ｜ 上次: {element_last_omission['火行']}期")
                    st.code(", ".join([f"{x:02d}" for x in five_elements['火行']]), language="text")
                with ec5:
                    is_tu = '土行' in triggered_elements
                    st.markdown(f"⛰️ **土行 {'🚨 ⚡' if is_tu else ''}**")
                    st.caption(f"当前: **{element_omission['土行']}期** ｜ 上次: {element_last_omission['土行']}期")
                    st.code(", ".join([f"{x:02d}" for x in five_elements['土行']]), language="text")

            # ==========================================
            # 功能 9: 🔢 七段数拐点选号
            # ==========================================
            elif selected_func.startswith("9."):
                st.subheader("🔢 七段数（每段7码等分）触底拐点智能选号引擎")
                
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("🔢 动态历史综合胜率", f"{rate_segments:.2f}%")
                kpi2.metric("✅ 历史命中期数", f"{hits_dyn_segments} / {test_periods_count} 期")
                kpi3.metric("🔢 平均涵盖码数", f"{np.mean(pool_dyn_segments):.1f} 码")

                st.markdown("""
                💡 **七段数拐点选号逻辑**：
                * 自动扫描功能二中 **1段(01-07)** 至 **7段(43-49)** 的双重遗漏与触底状态；
                * 自动提取触发 **【当前遗漏 $\\\\ge$ 上次遗漏】（即带 ⚡ 闪电标记）** 的段数，并自动打包输出对应段数的全部特码。
                """)
                
                triggered_segments = [sgn for sgn in seven_segments if segment_omission[sgn] >= segment_last_omission[sgn]]
                segment_selected_nums = sorted(list(set([n for sgn in triggered_segments for n in seven_segments[sgn]])))
                
                st.write("---")
                st.success(f"🏆 **【七段数闪电拐点精选全包池】本期共命中 {len(triggered_segments)} 个段数，精选特码共 {len(segment_selected_nums)} 个：**")
                st.caption(f"🚨 **本期触发闪电的段数**：`{', '.join(triggered_segments) if triggered_segments else '暂无'}` ｜ 占比覆盖率：`{len(segment_selected_nums)/49*100:.1f}%`")
                st.markdown("👇 **请点击下方代码框右上角的小图标，即可秒级全选复制到剪贴板：**")
                st.code(", ".join([f"{x:02d}" for x in segment_selected_nums]) if segment_selected_nums else "暂无触发号码", language="text")
                st.write("---")
                
                seg_cols = st.columns(7)
                for idx, sgn in enumerate(seven_segments):
                    with seg_cols[idx]:
                        is_seg_inf = sgn in triggered_segments
                        st.markdown(f"**{sgn} {'🚨 ⚡' if is_seg_inf else ''}**")
                        st.caption(f"遗漏: **{segment_omission[sgn]}期**")
                        st.caption(f"上次: {segment_last_omission[sgn]}期")
                        st.code(", ".join([f"{x:02d}" for x in seven_segments[sgn]]), language="text")

            # ==========================================
            # 功能 10: 🧊 冷热遗漏分层控码选号
            # ==========================================
            elif selected_func.startswith("10."):
                st.subheader("🧊 五层冷热遗漏梯级选号与杀号引擎")
                
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                kpi1.metric("🧊 动态历史综合胜率", f"{rate_layers:.2f}%")
                kpi2.metric("✅ 历史命中期数", f"{hits_dyn_layers} / {test_periods_count} 期")
                kpi3.metric("🔢 平均涵盖码数", f"{np.mean(pool_dyn_layers):.1f} 码")
                kpi4.metric("🛡️ 平均排除死码", f"{49 - np.mean(pool_dyn_layers):.1f} 码")

                st.markdown("""
                💡 **五层冷热梯度控码逻辑**：
                * 🔴 **第 1 层：热码回补层 (遗漏 0 - 10 期)** ── 全额保留（防守高频连开）
                * 🟠 **第 2 层：温热黄金层 (遗漏 11 - 25 期)** ── 全额保留（主力爆发地带）
                * 🟡 **第 3 层：常态温冷层 (遗漏 26 - 50 期)** ── 优选具备触底拐点($\\\\ge$上次)或高欲出率($\\\\ge 0.40$)的号码
                * 🔵 **第 4 层：深度冷码层 (遗漏 51 - 100 期)** ── 仅特赦具备触底拐点($\\\\ge$上次)的号码
                * ⚪ **第 5 层：极限大冷层 (遗漏 100+ 期)** ── 全额排除剔除（天然杀号区）
                """)
                
                tier_1 = [] # 0-10
                tier_2 = [] # 11-25
                tier_3 = [] # 26-50
                tier_4 = [] # 51-100
                tier_5 = [] # 100+
                
                for n in range(1, 50):
                    om = num_omission[n]
                    last_om = num_last_omission[n]
                    rate = num_rates[n]
                    z = get_zodiac_of_number(n)
                    is_inf = om >= last_om
                    info = (n, z, om, last_om, rate, is_inf)
                    
                    if om <= 10: tier_1.append(info)
                    elif 11 <= om <= 25: tier_2.append(info)
                    elif 26 <= om <= 50: tier_3.append(info)
                    elif 51 <= om <= 100: tier_4.append(info)
                    else: tier_5.append(info)
                
                layer_selected = []
                layer_removed = []
                
                for x in tier_1 + tier_2: layer_selected.append(x[0])
                for x in tier_3:
                    if x[5] or (x[4] >= 0.40): layer_selected.append(x[0])
                    else: layer_removed.append(x[0])
                for x in tier_4:
                    if x[5]: layer_selected.append(x[0])
                    else: layer_removed.append(x[0])
                for x in tier_5: layer_removed.append(x[0])
                    
                layer_selected.sort()
                layer_removed.sort()
                
                st.write("---")
                st.success(f"🏆 **【冷热遗漏分层精选全包池】本期符合分层策略号码共 {len(layer_selected)} 个（已按由小到大重排）：**")
                st.caption(f"🎯 **分层覆盖率**：`{len(layer_selected)/49*100:.1f}%` ｜ 稳健控制在 40 码以下主力区间！")
                st.markdown("👇 **请点击下方代码框右上角的小图标，即可秒级全选复制到剪贴板：**")
                st.code(", ".join([f"{x:02d}" for x in layer_selected]) if layer_selected else "无", language="text")
                
                st.error(f"❄️ **【冷热分层剔除死码池】本期排除的大冷/弱势死码共 {len(layer_removed)} 个：**")
                st.code(", ".join([f"{x:02d}" for x in layer_removed]) if layer_removed else "无", language="text")
                st.write("---")
                
                st.markdown("### 🔍 5 大遗漏梯级大盘分布与号码明细")
                t_col1, t_col2, t_col3, t_col4, t_col5 = st.columns(5)
                with t_col1:
                    st.markdown(f"🔴 **第1层: 热码回补 ({len(tier_1)}码)**")
                    st.caption("遗漏 0-10 期 ｜ 全包保留")
                    t1_nums = [f"{x[0]:02d}" for x in tier_1]
                    st.code(", ".join(t1_nums) if t1_nums else "无", language="text")
                with t_col2:
                    st.markdown(f"🟠 **第2层: 温热黄金 ({len(tier_2)}码)**")
                    st.caption("遗漏 11-25 期 ｜ 全包保留")
                    t2_nums = [f"{x[0]:02d}" for x in tier_2]
                    st.code(", ".join(t2_nums) if t2_nums else "无", language="text")
                with t_col3:
                    st.markdown(f"🟡 **第3层: 常态温冷 ({len(tier_3)}码)**")
                    st.caption("遗漏 26-50 期 ｜ 优选拐点/高欲出")
                    t3_nums = [f"{x[0]:02d}" for x in tier_3]
                    st.code(", ".join(t3_nums) if t3_nums else "无", language="text")
                with t_col4:
                    st.markdown(f"🔵 **第4层: 深度冷码 ({len(tier_4)}码)**")
                    st.caption("遗漏 51-100 期 ｜ 仅特赦拐点⚡")
                    t4_nums = [f"{x[0]:02d}" for x in tier_4]
                    st.code(", ".join(t4_nums) if t4_nums else "无", language="text")
                with t_col5:
                    st.markdown(f"⚪ **第5层: 极限大冷 ({len(tier_5)}码)**")
                    st.caption("遗漏 100+ 期 ｜ 全额排除剔除")
                    t5_nums = [f"{x[0]:02d}" for x in tier_5]
                    st.code(", ".join(t5_nums) if t5_nums else "无", language="text")

    except Exception as global_ex:
        st.error(f"🚨 大盘核心数据解析时发生错误: {global_ex}")
        st.code(traceback.format_exc(), language="text")
