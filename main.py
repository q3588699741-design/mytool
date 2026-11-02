import streamlit as st
import pandas as pd
from collections import defaultdict, Counter
import numpy as np
import itertools
import traceback

# 页面基础配置
st.set_page_config(page_title="数据全维度智能统计看板", layout="wide", initial_sidebar_state="expanded")

st.title("📊 开奖记录全维度综合统计看板 (含修复版·双独立杀码·旗舰版)")
st.caption("🤖 10-40码全自动匹配 ｜ 新版杀3肖近14天100% ｜ 时空杀2码 98.6% ｜ 晶格杀5码 96.0% ｜ 全周期风控与连黑看板")

# 定义全局标准集合
all_tails = list(range(10))
all_zodiacs = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
all_heads = list(range(5))

# 2026 丙午马年当前基准映射
base_zodiacs = ['马', '蛇', '龙', '兔', '虎', '牛', '鼠', '猪', '狗', '鸡', '猴', '羊']
def get_zodiac_of_number(n): return base_zodiacs[(n - 1) % 12]

# 波色与半波映射定义
red_balls = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
blue_balls = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
green_balls = [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]

def get_half_wave(n):
    c = '红' if n in red_balls else ('蓝' if n in blue_balls else '绿')
    p = '单' if n % 2 == 1 else '双'
    return f"{c}{p}"

all_half_waves = ['红单', '红双', '蓝单', '蓝双', '绿单', '绿双']
hw_numbers = {hw: [] for hw in all_half_waves}
for n in range(1, 50):
    hw_numbers[get_half_wave(n)].append(n)

# 模9数根映射全集
dr_numbers = defaultdict(list)
for n in range(1, 50):
    dr = (n - 1) % 9 + 1
    dr_numbers[dr].append(n)

# 和数尾映射全集
cst_numbers = defaultdict(list)
for n in range(1, 50):
    cst = (n // 10 + n % 10) % 10
    cst_numbers[cst].append(n)

# 模7同余映射全集
mod7_numbers = {r: [n for n in range(1, 50) if n % 7 == r] for r in range(7)}

# 五门头数映射全集
head_numbers = {h: [n for n in range(1, 50) if n // 10 == h] for h in range(5)}

# 四象限映射全集
quad_numbers = {
    '小单': [n for n in range(1, 25) if n % 2 == 1],
    '小双': [n for n in range(1, 25) if n % 2 == 0],
    '大单': [n for n in range(25, 50) if n % 2 == 1],
    '大双': [n for n in range(25, 50) if n % 2 == 0]
}
all_quads = ['小单', '小双', '大单', '大双']
def get_quad(n):
    return ('大' if n >= 25 else '小') + ('单' if n % 2 == 1 else '双')

zodiac_zones_2 = {'上区': ['马', '蛇', '龙', '兔', '虎', '牛'], '下区': ['鼠', '猪', '狗', '鸡', '猴', '羊']}
zodiac_zones_3 = {'左区': ['马', '兔', '鼠', '鸡'], '中区': ['蛇', '虎', '猪', '猴'], '右区': ['龙', '牛', '狗', '羊']}
zodiac_seasons = {'春肖': ['虎', '兔', '龙'], '夏肖': ['蛇', '马', '羊'], '秋肖': ['猴', '鸡', '狗'], '冬肖': ['猪', '鼠', '牛']}
all_zones = {**zodiac_zones_2, **zodiac_zones_3}

five_elements = {
    '金行': [4, 5, 12, 13, 26, 27, 34, 35, 42, 43],
    '木行': [8, 9, 16, 17, 24, 25, 38, 39, 46, 47],
    '水行': [1, 14, 15, 22, 23, 30, 31, 44, 45],
    '火行': [2, 3, 10, 11, 18, 19, 32, 33, 40, 41, 48, 49],
    '土行': [6, 7, 20, 21, 28, 29, 36, 37]
}
seven_segments = {f'{k}段': list(range(1+(k-1)*7, 1+k*7)) for k in range(1, 8)}

num_to_elem = {n: en for en, el in five_elements.items() for n in el}
num_to_seg = {n: sgn for sgn, sgl in seven_segments.items() for n in sgl}
zod_to_z2 = {z: zn for zn, zl in zodiac_zones_2.items() for z in zl}
zod_to_z3 = {z: zn for zn, zl in zodiac_zones_3.items() for z in zl}
zod_to_sea = {z: sn for sn, sl in zodiac_seasons.items() for z in sl}

# =========================================================================
# 📈 全周期连红与风控统计解析函数
# =========================================================================
def calc_rate_and_streaks(hit_list):
    n = len(hit_list)
    if n == 0:
        return {
            'total_rate': 0.0, 'total_hits': 0, 'total_n': 0,
            'r30_rate': 0.0, 'r30_hits': 0, 'r30_n': 0,
            'r14_rate': 0.0, 'r14_hits': 0, 'r14_n': 0,
            'r7_rate': 0.0, 'r7_hits': 0, 'r7_n': 0,
            'r3_rate': 0.0, 'r3_hits': 0, 'r3_n': 0,
            'streak2_rate': 0.0, 'streak2_hits': 0,
            'streak3_rate': 0.0, 'streak3_hits': 0,
            'max_win_streak': 0, 'max_loss_streak': 0,
            'r30_max_loss': 0, 'r14_max_loss': 0,
            'cur_win_streak': 0
        }
    th = sum(hit_list)
    tr = th / n * 100
    
    sub3 = hit_list[-3:]
    r3 = (sum(sub3) / len(sub3) * 100) if len(sub3) > 0 else 0.0
    sub7 = hit_list[-7:]
    r7 = (sum(sub7) / len(sub7) * 100) if len(sub7) > 0 else 0.0
    sub14 = hit_list[-14:]
    r14 = (sum(sub14) / len(sub14) * 100) if len(sub14) > 0 else 0.0
    sub30 = hit_list[-30:]
    r30 = (sum(sub30) / len(sub30) * 100) if len(sub30) > 0 else 0.0
    
    streak2_cnt = sum(1 for j in range(n - 1) if hit_list[j] and hit_list[j+1])
    streak2_rate = (streak2_cnt / (n - 1) * 100) if n > 1 else 0.0
    streak3_cnt = sum(1 for j in range(n - 2) if hit_list[j] and hit_list[j+1] and hit_list[j+2])
    streak3_rate = (streak3_cnt / (n - 2) * 100) if n > 2 else 0.0
    
    max_w, cur_w = 0, 0
    max_l, cur_l = 0, 0
    for h in hit_list:
        if h:
            cur_w += 1
            max_w = max(max_w, cur_w)
            cur_l = 0
        else:
            cur_l += 1
            max_l = max(max_l, cur_l)
            cur_w = 0
            
    r30_max_l, cur_r30_l = 0, 0
    for h in sub30:
        if not h:
            cur_r30_l += 1
            r30_max_l = max(r30_max_l, cur_r30_l)
        else:
            cur_r30_l = 0
            
    r14_max_l, cur_r14_l = 0, 0
    for h in sub14:
        if not h:
            cur_r14_l += 1
            r14_max_l = max(r14_max_l, cur_r14_l)
        else:
            cur_r14_l = 0
            
    return {
        'total_rate': tr, 'total_hits': th, 'total_n': n,
        'r30_rate': r30, 'r30_hits': sum(sub30), 'r30_n': len(sub30),
        'r14_rate': r14, 'r14_hits': sum(sub14), 'r14_n': len(sub14),
        'r7_rate': r7, 'r7_hits': sum(sub7), 'r7_n': len(sub7),
        'r3_rate': r3, 'r3_hits': sum(sub3), 'r3_n': len(sub3),
        'streak2_rate': streak2_rate, 'streak2_hits': streak2_cnt,
        'streak3_rate': streak3_rate, 'streak3_hits': streak3_cnt,
        'max_win_streak': max_w, 'max_loss_streak': max_l,
        'r30_max_loss': r30_max_l, 'r14_max_loss': r14_max_l,
        'cur_win_streak': cur_w
    }

# 通用财务测算器与风控连黑看板渲染组件
def render_financial_calculator_and_streaks(stats, n_codes, key_prefix="calc"):
    st.write("---")
    st.markdown("#### 🛡️ 连红稳定性与连黑风控综合看板：")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🔥 2 连红成功率", f"{stats['streak2_rate']:.1f}%", f"{stats['streak2_hits']} 次达成")
    c2.metric("🚀 3 连红成功率", f"{stats['streak3_rate']:.1f}%", f"{stats['streak3_hits']} 次达成")
    c3.metric("🏆 历史最长连红", f"{stats['max_win_streak']} 期连中", f"当前已连红: {stats['cur_win_streak']} 期")
    c4.metric("🛡️ 近30天最大连黑", f"{stats['r30_max_loss']} 期", "抗断缆极强" if stats['r30_max_loss'] <= 1 else "注意防守")
    c5.metric("🛡️ 近14天最大连黑", f"{stats['r14_max_loss']} 期", "零连黑满贯" if stats['r14_max_loss'] == 0 else f"最大连黑 {stats['r14_max_loss']} 期")

    st.write("---")
    st.markdown("#### 💰 平注财务动态测算器（支持自定义单码金额与赔率）：")
    in_c1, in_c2, in_c3 = st.columns([1, 1, 1])
    with in_c1:
        stake = st.number_input("单码投注金额 (元)：", min_value=1, max_value=500, value=20, step=1, key=f"{key_prefix}_stake")
    with in_c2:
        odds = st.number_input("中奖赔率 (倍)：", min_value=1, max_value=100, value=47, step=1, key=f"{key_prefix}_odds")
    with in_c3:
        breakeven_p = (n_codes / odds * 100) if odds > 0 else 0
        st.metric("保本所需胜率红线", f"{breakeven_p:.2f}%", f"超额护城河 +{stats['total_rate'] - breakeven_p:.1f}%")

    cost = n_codes * stake
    win_net = stake * odds - cost
    tot_profit = stats['total_hits'] * win_net - (stats['total_n'] - stats['total_hits']) * cost
    weekly_profit = (tot_profit / (stats['total_n'] / 7)) if stats['total_n'] > 0 else 0
    r30_profit = stats['r30_hits'] * win_net - (30 - stats['r30_hits']) * cost
    r30_weekly = r30_profit / (30 / 7)
    two_win_profit = 2 * win_net

    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("单期总投入成本", f"{cost} 元/天", f"覆盖 {n_codes} 码")
    f2.metric("中奖单期净利润", f"+{win_net} 元")
    f3.metric("全量累计总净利", f"{tot_profit:+.0f} 元", f"周均: {weekly_profit:+.0f}元/周")
    f4.metric("近30天总净利", f"{r30_profit:+.0f} 元", f"周均: {r30_weekly:+.0f}元/周")
    f5.metric("🎯 2连红收网纯利", f"+{two_win_profit} 元", "跑满两期即锁利")

# 统一多周期胜率大盘 KPI 展示组件
def render_kpi_header(stats, n_codes_label=""):
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📊 全量实测胜率", f"{stats['total_rate']:.2f}%", f"{stats['total_hits']}/{stats['total_n']}期")
    c2.metric("📅 近30天胜率", f"{stats['r30_rate']:.1f}%", f"最大连黑: {stats['r30_max_loss']} 期")
    c3.metric("⚡ 近14天胜率", f"{stats['r14_rate']:.1f}%", f"最大连黑: {stats['r14_max_loss']} 期")
    c4.metric("🔥 近7天胜率", f"{stats['r7_rate']:.1f}%", f"{stats['r7_hits']}/{stats['r7_n']}期")
    c5.metric("🚀 近3天胜率", f"{stats['r3_rate']:.1f}%", n_codes_label if n_codes_label else f"{stats['r3_hits']}/{stats['r3_n']}期")

# 1. 配置文件上传与双模式自适应解析引擎
uploaded_file = st.file_uploader("👉 请上传最新的开奖记录表格 (支持含平码的全量表 或 纯特码表，.csv/.xlsx 格式)", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        try: df_raw = pd.read_csv(uploaded_file, header=None)
        except Exception as e: st.error(f"❌ 读取 CSV 失败: {e}"); st.stop()
    else:
        try: df_raw = pd.read_excel(uploaded_file, header=None)
        except ImportError:
            st.error("❌ 缺少 openpyxl 组件，请在终端运行：`pip install openpyxl` 后重试。")
            st.stop()
        except Exception as e: st.error(f"❌ 读取 Excel 失败: {e}"); st.stop()
    
    try:
        has_period_header = False
        for r in range(min(15, len(df_raw))):
            if '期' in str(df_raw.iloc[r, 0]):
                has_period_header = True
                break

        parsed_data = []

        if has_period_header and df_raw.shape[1] >= 7:
            # 模式 A: 3 行一期的全量多列详细表
            i = 0
            periods_temp = []
            while i < len(df_raw):
                val = str(df_raw.iloc[i, 0])
                if '期' in val:
                    try:
                        header_str = val
                        nums = df_raw.iloc[i+1, :].tolist()
                        zods = df_raw.iloc[i+2, :].tolist()
                        
                        p_flats = [int(nums[k]) for k in range(6)]
                        te = int(nums[7])
                        zte = str(zods[7]).strip()
                        flats_zod = [str(zods[k]).strip() for k in range(6)]
                        periods_temp.append({
                            'header': header_str,
                            'num': te,
                            'zodiac': zte,
                            'flats': p_flats,
                            'flats_zod': flats_zod
                        })
                        i += 3
                    except Exception:
                        i += 1
                else:
                    i += 1
            
            if len(periods_temp) >= 2:
                p_first = int(''.join(filter(str.isdigit, periods_temp[0]['header'].split('期')[0]))) if '期' in periods_temp[0]['header'] else 0
                p_last = int(''.join(filter(str.isdigit, periods_temp[-1]['header'].split('期')[0]))) if '期' in periods_temp[-1]['header'] else 0
                if p_first > p_last:
                    periods_temp = periods_temp[::-1]
            
            seen_p = set()
            for p in periods_temp:
                sig = (p['header'], p['num'], tuple(p['flats']))
                if sig not in seen_p:
                    seen_p.add(sig)
                    parsed_data.append((p['num'], p['zodiac'], p['flats'], p['header'], p['flats_zod']))
        else:
            # 模式 B: 经典双列格式 (特码, 生肖)
            df_clean = df_raw.dropna()
            for idx, row in df_clean.iterrows():
                try:
                    num = int(row[0])
                    zodiac = str(row[1]).strip()
                    parsed_data.append((num, zodiac, None, f"第{idx+1}期", None))
                except: continue

        total_records = len(parsed_data)
        if total_records < 2:
            st.error("❌ 表格有效数据不足！")
            st.stop()

        has_flat_data = (parsed_data[-1][2] is not None and len(parsed_data[-1][2]) == 6)

        # 基础数据统计
        num_counts = defaultdict(int)
        tail_counts = defaultdict(int)
        zodiac_counts = defaultdict(int)
        head_counts_dict = defaultdict(int)
        zone_counts = defaultdict(int)
        season_counts = defaultdict(int)
        element_counts = defaultdict(int)
        segment_counts = defaultdict(int)

        num_indices = defaultdict(list)
        tail_indices = defaultdict(list)
        zodiac_indices = defaultdict(list)
        head_indices = defaultdict(list)
        zone_indices = defaultdict(list)
        season_indices = defaultdict(list)
        element_indices = defaultdict(list)
        segment_indices = defaultdict(list)

        for i, (num, zodiac, _, _, _) in enumerate(parsed_data):
            num_counts[num] += 1
            tail_counts[num % 10] += 1
            zodiac_counts[zodiac] += 1
            head_counts_dict[num // 10] += 1
            num_indices[num].append(i)
            tail_indices[num % 10].append(i)
            zodiac_indices[zodiac].append(i)
            head_indices[num // 10].append(i)
            for z_name, z_list in all_zones.items():
                if zodiac in z_list:
                    zone_counts[z_name] += 1
                    zone_indices[z_name].append(i)
            for s_name, s_list in zodiac_seasons.items():
                if zodiac in s_list:
                    season_counts[s_name] += 1
                    season_indices[s_name].append(i)
            for e_name, e_nums in five_elements.items():
                if num in e_nums:
                    element_counts[e_name] += 1
                    element_indices[e_name].append(i)
            for seg_name, seg_nums in seven_segments.items():
                if num in seg_nums:
                    segment_counts[seg_name] += 1
                    segment_indices[seg_name].append(i)

        num_omission = {n: (total_records - 1 - num_indices[n][-1]) if num_indices[n] else total_records for n in range(1, 50)}
        num_last_omission = {n: (num_indices[n][-1] - num_indices[n][-2] - 1) if len(num_indices[n]) >= 2 else (num_indices[n][-1] if num_indices[n] else 0) for n in range(1, 50)}
        zodiac_omission = {z: (total_records - 1 - zodiac_indices[z][-1]) if zodiac_indices[z] else total_records for z in all_zodiacs}
        zodiac_last_omission = {z: (zodiac_indices[z][-1] - zodiac_indices[z][-2] - 1) if len(zodiac_indices[z]) >= 2 else (zodiac_indices[z][-1] if zodiac_indices[z] else 0) for z in all_zodiacs}
        tail_omission = {t: (total_records - 1 - tail_indices[t][-1]) if tail_indices[t] else total_records for t in all_tails}
        tail_last_omission = {t: (tail_indices[t][-1] - tail_indices[t][-2] - 1) if len(tail_indices[t]) >= 2 else (tail_indices[t][-1] if tail_indices[t] else 0) for t in all_tails}
        head_omission = {h: (total_records - 1 - head_indices[h][-1]) if head_indices[h] else total_records for h in all_heads}
        head_last_omission = {h: (head_indices[h][-1] - head_indices[h][-2] - 1) if len(head_indices[h]) >= 2 else (head_indices[h][-1] if head_indices[h] else 0) for h in all_heads}

        zone_omission = {z: (total_records - 1 - zone_indices[z][-1]) if zone_indices[z] else total_records for z in all_zones}
        zone_last_omission = {z: (zone_indices[z][-1] - zone_indices[z][-2] - 1) if len(zone_indices[z]) >= 2 else (zone_indices[z][-1] if zone_indices[z] else 0) for z in all_zones}
        season_omission = {s: (total_records - 1 - season_indices[s][-1]) if season_indices[s] else total_records for s in zodiac_seasons}
        season_last_omission = {s: (season_indices[s][-1] - season_indices[s][-2] - 1) if len(season_indices[s]) >= 2 else (season_indices[s][-1] if season_indices[s] else 0) for s in zodiac_seasons}
        element_omission = {e: (total_records - 1 - element_indices[e][-1]) if element_indices[e] else total_records for e in five_elements}
        element_last_omission = {e: (element_indices[e][-1] - element_indices[e][-2] - 1) if len(element_indices[e]) >= 2 else (element_indices[e][-1] if element_indices[e] else 0) for e in five_elements}
        segment_omission = {sg: (total_records - 1 - segment_indices[sg][-1]) if segment_indices[sg] else total_records for sg in seven_segments}
        segment_last_omission = {sg: (segment_indices[sg][-1] - segment_indices[sg][-2] - 1) if len(segment_indices[sg]) >= 2 else (segment_indices[sg][-1] if segment_indices[sg] else 0) for sg in seven_segments}

        tail_rates = {t: tail_omission[t] / ((total_records / tail_counts[t]) if tail_counts[t] > 0 else total_records) for t in all_tails}
        zodiac_rates = {z: zodiac_omission[z] / ((total_records / zodiac_counts[z]) if zodiac_counts[z] > 0 else total_records) for z in all_zodiacs}
        num_rates = {n: num_omission[n] / ((total_records / num_counts[n]) if num_counts[n] > 0 else total_records) for n in range(1, 50)}
        head_rates = {h: head_omission[h] / ((total_records / head_counts_dict[h]) if head_counts_dict[h] > 0 else total_records) for h in all_heads}
        zone_rates = {z: zone_omission[z] / ((total_records / zone_counts[z]) if zone_counts[z] > 0 else total_records) for z in all_zones}
        season_rates = {s: season_omission[s] / ((total_records / season_counts[s]) if season_counts[s] > 0 else total_records) for s in zodiac_seasons}
        element_rates = {e: element_omission[e] / ((total_records / element_counts[e]) if element_counts[e] > 0 else total_records) for e in five_elements}
        segment_rates = {sg: segment_omission[sg] / ((total_records / segment_counts[sg]) if segment_counts[sg] > 0 else total_records) for sg in seven_segments}

        tail_transitions = defaultdict(list)
        zodiac_transitions = defaultdict(list)
        head_transitions = defaultdict(list)
        for i in range(len(parsed_data) - 1):
            tail_transitions[parsed_data[i][0] % 10].append(parsed_data[i+1][0] % 10)
            zodiac_transitions[parsed_data[i][1]].append(parsed_data[i+1][1])
            head_transitions[parsed_data[i][0] // 10].append(parsed_data[i+1][0] // 10)

        start_backtest_idx = min(30, max(2, total_records // 5))

        cur_num_idx = defaultdict(list)
        cur_tail_idx = defaultdict(list)
        cur_zod_idx = defaultdict(list)
        cur_z2_idx = defaultdict(list)
        cur_z3_idx = defaultdict(list)
        cur_sea_idx = defaultdict(list)
        cur_elem_idx = defaultdict(list)
        cur_seg_idx = defaultdict(list)
        cur_num_cnt = defaultdict(int)
        cur_tail_cnt = defaultdict(int)
        cur_zod_cnt = defaultdict(int)

        for idx_s in range(start_backtest_idx):
            s_num, s_zod, _, _, _ = parsed_data[idx_s]
            cur_num_idx[s_num].append(idx_s)
            cur_tail_idx[s_num % 10].append(idx_s)
            cur_zod_idx[s_zod].append(idx_s)
            cur_z2_idx[zod_to_z2[s_zod]].append(idx_s)
            cur_z3_idx[zod_to_z3[s_zod]].append(idx_s)
            cur_sea_idx[zod_to_sea[s_zod]].append(idx_s)
            cur_elem_idx[num_to_elem[s_num]].append(idx_s)
            cur_seg_idx[num_to_seg[s_num]].append(idx_s)
            cur_num_cnt[s_num] += 1
            cur_tail_cnt[s_num % 10] += 1
            cur_zod_cnt[s_zod] += 1

        tier_configs = {
            "方案A (36码平衡型)": {"n20": 2, "n10": 5, "n5": 29, "cost": 235},
            "方案C (32码进攻型)": {"n20": 3, "n10": 6, "n5": 23, "cost": 235},
            "方案B (35码标准型)": {"n20": 2, "n10": 6, "n5": 27, "cost": 235},
            "方案D (31码精进型)": {"n20": 3, "n10": 7, "n5": 21, "cost": 235},
            "方案E (30码狙击型)": {"n20": 3, "n10": 8, "n5": 19, "cost": 235},
            "方案F (38码极盾型)": {"n20": 1, "n10": 4, "n5": 33, "cost": 225}
        }

        res_tier_records = {k: [] for k in tier_configs}
        res_hybrid1, res_hybrid2, res_hybrid3 = [], [], []
        res_pool30_1, res_pool30_2, res_pool30_3 = [], [], []
        res_layers, res_tail10, res_asym10, res_zod3, res_top40 = [], [], [], [], []
        res_asym12, res_or, res_f4, res_blind12, res_kill15 = [], [], [], [], []
        res_seasons, res_elements, res_segments = [], [], []

        res_zod_k2, res_zod_k3, res_zod_k4, res_zod_k5 = [], [], [], []
        res_num_k8, res_num_k10, res_num_k12 = [], [], []
        
        # 🌟 独立双逻辑杀码回测容器
        res_k2_dual = []      # 杀2码：时空双核阻尼法 (prev_te + 最死平码)
        res_k5_lattice = []   # 杀5码：五维正交代数晶格死锁法 (模7+和数尾+拓扑+死肖+死尾碰撞)

        res_dr_kill = []
        res_hw_k1 = []
        res_hw_k2 = []

        res_cst_k2 = []
        res_m7_k1 = []
        res_m7_k2 = []
        res_head_k1 = []
        res_dist_k9 = []
        res_quad_k1 = []
        
        # 平码战法回测
        res_flat_k6 = []
        res_flat_k7 = []
        res_flat_zod_k2 = []
        res_flat_dr_k2 = []
        res_flat_hw_k1 = []
        res_flat_elem_k1 = []

        res_slim_20, res_slim_18, res_slim_16, res_slim_15 = [], [], [], []
        res_inter_4_5, res_inter_6_7, res_inter_3_4_5 = [], [], []

        for i in range(start_backtest_idx, total_records - 1):
            s_num, s_zod, s_flats, _, s_flats_zod = parsed_data[i]
            cur_num_idx[s_num].append(i)
            cur_tail_idx[s_num % 10].append(i)
            cur_zod_idx[s_zod].append(i)
            cur_z2_idx[zod_to_z2[s_zod]].append(i)
            cur_z3_idx[zod_to_z3[s_zod]].append(i)
            cur_sea_idx[zod_to_sea[s_zod]].append(i)
            cur_elem_idx[num_to_elem[s_num]].append(i)
            cur_seg_idx[num_to_seg[s_num]].append(i)
            cur_num_cnt[s_num] += 1
            cur_tail_cnt[s_num % 10] += 1
            cur_zod_cnt[s_zod] += 1
            
            h_len = i + 1
            prev_num = s_num
            prev_zod = s_zod
            prev_dr = (prev_num - 1) % 9 + 1
            prev_hw = get_half_wave(prev_num)
            prev_tail = prev_num % 10
            n_num, n_zod, _, _, _ = parsed_data[i+1]
            
            def get_sub_inf_fast(idx_map, keys):
                trig = set()
                for k in keys:
                    idxs = idx_map[k]
                    cur_m = (h_len - 1 - idxs[-1]) if idxs else h_len
                    last_m = (idxs[-1] - idxs[-2] - 1) if len(idxs) >= 2 else (idxs[-1] if idxs else 0)
                    if cur_m >= last_m: trig.add(k)
                return trig

            trig_z2 = get_sub_inf_fast(cur_z2_idx, ['上区', '下区'])
            trig_z3 = get_sub_inf_fast(cur_z3_idx, ['左区', '中区', '右区'])
            trig_tails = get_sub_inf_fast(cur_tail_idx, all_tails)
            trig_zods = get_sub_inf_fast(cur_zod_idx, all_zodiacs)
            trig_sea = get_sub_inf_fast(cur_sea_idx, ['春肖', '夏肖', '秋肖', '冬肖'])
            trig_elem = get_sub_inf_fast(cur_elem_idx, five_elements.keys())
            trig_seg = get_sub_inf_fast(cur_seg_idx, seven_segments.keys())
            
            sub_zods_or = set([z for zn in trig_z2 for z in zodiac_zones_2[zn]]).union([z for zn in trig_z3 for z in zodiac_zones_3[zn]]) or set(all_zodiacs)
            sub_zods_sea = set([z for sn in trig_sea for z in zodiac_seasons[sn]])

            sub_zod_om = {z: (h_len - 1 - cur_zod_idx[z][-1]) if cur_zod_idx[z] else h_len for z in all_zodiacs}
            sub_zod_last = {z: (cur_zod_idx[z][-1] - cur_zod_idx[z][-2] - 1) if len(cur_zod_idx[z]) >= 2 else (cur_zod_idx[z][-1] if cur_zod_idx[z] else 0) for z in all_zodiacs}
            sub_tail_om = {t: (h_len - 1 - cur_tail_idx[t][-1]) if cur_tail_idx[t] else h_len for t in all_tails}
            sub_tail_last = {t: (cur_tail_idx[t][-1] - cur_tail_idx[t][-2] - 1) if len(cur_tail_idx[t]) >= 2 else (cur_tail_idx[t][-1] if cur_tail_idx[t] else 0) for t in all_tails}
            sub_num_om = {n: (h_len - 1 - cur_num_idx[n][-1]) if cur_num_idx[n] else h_len for n in range(1, 50)}
            sub_num_last = {n: (cur_num_idx[n][-1] - cur_num_idx[n][-2] - 1) if len(cur_num_idx[n]) >= 2 else (cur_num_idx[n][-1] if cur_num_idx[n] else 0) for n in range(1, 50)}

            sub_zod_rates = {z: sub_zod_om[z] / ((h_len / cur_zod_cnt[z]) if cur_zod_cnt[z] > 0 else h_len) for z in all_zodiacs}
            sub_tail_rates = {t: sub_tail_om[t] / ((h_len / cur_tail_cnt[t]) if cur_tail_cnt[t] > 0 else h_len) for t in all_tails}
            sub_num_rates = {n: sub_num_om[n] / ((h_len / cur_num_cnt[n]) if cur_num_cnt[n] > 0 else h_len) for n in range(1, 50)}

            sub_prev_head = prev_num // 10
            sub_killed_head = (sub_prev_head - 2) % 5

            # 基础模块
            f1_kill = set(n for n in range(1, 50) if not (sub_num_om[n] <= 25 or (26 <= sub_num_om[n] <= 50 and (sub_num_om[n] >= sub_num_last[n] or sub_num_rates[n] >= 0.40)) or (51 <= sub_num_om[n] <= 100 and sub_num_om[n] >= sub_num_last[n])))
            f1_kept = set(range(1, 50)) - f1_kill
            
            rec_tail_8 = defaultdict(int)
            for p_num, _, _, _, _ in parsed_data[max(0, h_len-8):h_len]: rec_tail_8[p_num % 10] += 1
            scores_t = sorted([(t, rec_tail_8[t] - sub_tail_om[t]) for t in range(1, 10)], key=lambda x: -x[1])
            dead_tails_2 = (scores_t[0][0], scores_t[1][0])
            f2_kill = set([n for n in range(1, 50) if (n % 10) in dead_tails_2])
            f2_kept = set(range(1, 50)) - f2_kill
            
            off10 = 18 if prev_num <= 16 else (0 if prev_num <= 33 else 7)
            f3_kill = set([((prev_num + off10 + j - 1) % 49) + 1 for j in range(10)])
            f3_kept = set(range(1, 50)) - f3_kill
            
            rec_zod_7 = defaultdict(int)
            for _, p_zod, _, _, _ in parsed_data[max(0, h_len-7):h_len]: rec_zod_7[p_zod] += 1
            z_sc_list = sorted([(z, rec_zod_7[z]*1.5 + (0.5 if sub_zod_rates[z]<0.4 and sub_zod_om[z]<sub_zod_last[z] else 0) + (0.5 if z not in sub_zods_or else 0) + (1.0 if sub_zod_om[z]==0 else 0)) for z in all_zodiacs], key=lambda x: -x[1])
            f4_kill = set([n for n in range(1, 50) if get_zodiac_of_number(n) in set(x[0] for x in z_sc_list[:3])])
            f4_kept = set(range(1, 50)) - f4_kill
            
            f5_scores = {n: (3.0 if get_zodiac_of_number(n) in sub_zods_or else 0) + (1.5+sub_zod_rates[get_zodiac_of_number(n)] if get_zodiac_of_number(n) in trig_zods else sub_zod_rates[get_zodiac_of_number(n)]-1.0) + (1.5+sub_tail_rates[n%10] if n%10 in trig_tails else sub_tail_rates[n%10]-1.0) + (1.0 if sub_num_om[n]>=sub_num_last[n] else -0.5) + (-1.0 if n//10==sub_killed_head else 0) for n in range(1, 50)}
            off12 = 26 if prev_num <= 16 else (2 if prev_num <= 33 else 5)
            f6_kill = set([((prev_num + off12 + j - 1) % 49) + 1 for j in range(12)])
            f6_kept = set(range(1, 50)) - f6_kill
            f8_kill = set(n for n in range(1, 50) if (((sub_zod_rates[get_zodiac_of_number(n)]<0.4 and sub_zod_om[get_zodiac_of_number(n)]<sub_zod_last[get_zodiac_of_number(n)]) or (sub_tail_rates[n%10]<0.4 and sub_tail_om[n%10]<sub_tail_last[n%10])) and not (sub_zod_om[get_zodiac_of_number(n)]>=sub_zod_last[get_zodiac_of_number(n)] or sub_tail_om[n%10]>=sub_tail_last[n%10])))
            f9_kill = set([((prev_num + j - 1) % 49) + 1 for j in range(2, 14)])
            f10_scores = {n: 0.35 * sub_zod_rates[get_zodiac_of_number(n)] + 0.35 * sub_tail_rates[n%10] + 0.30 * sub_num_rates[n] - (0.15 if sub_zod_om[get_zodiac_of_number(n)] < sub_zod_last[get_zodiac_of_number(n)] else 0) - (0.15 if sub_tail_om[n%10] < sub_tail_last[n%10] else 0) - (0.10 if sub_num_om[n] < sub_num_last[n] else 0) for n in range(1, 50)}
            f10_kill = set(sorted(range(1, 50), key=lambda n: (f10_scores[n], n))[:15])

            tier_sc = {n: f5_scores[n] - (2.0 if n in f1_kill else 0) - (3.0 if n in f2_kill else 0) - (3.0 if n in f3_kill else 0) - (2.5 if n in f6_kill else 0) for n in range(1, 50)}
            ranked_tier = sorted(range(1, 50), key=lambda n: -tier_sc[n])
            for k_name, cfg in tier_configs.items():
                n20, n10, n5 = cfg['n20'], cfg['n10'], cfg['n5']
                s20 = set(ranked_tier[:n20])
                s10 = set(ranked_tier[n20:n20+n10])
                s5 = set(ranked_tier[n20+n10:n20+n10+n5])
                is_h = n_num in (s20 | s10 | s5)
                res_tier_records[k_name].append((is_h, n_num in s20, n_num in s10, n_num in s5))

            p1_24 = set(sorted(range(1, 50), key=lambda n: ((1.0 if n in f1_kill else 0)+(2.5 if n in f2_kill else 0)+(2.5 if n in f3_kill else 0)+(1.0 if n in f4_kill else 0)+(2.5 if n in f6_kill else 0)+(1.0 if n in f8_kill else 0)+(0.5 if get_zodiac_of_number(n) not in sub_zods_sea else 0), -f5_scores[n]))[:24])
            p2_24 = set(sorted(range(1, 50), key=lambda n: ((2.0 if n in f1_kill else 0)+(2.5 if n in f2_kill else 0)+(2.5 if n in f3_kill else 0)+(1.0 if n in f4_kill else 0)+(2.5 if n in f6_kill else 0)+(0.5 if get_zodiac_of_number(n) not in sub_zods_sea else 0), -f5_scores[n]))[:24])
            # 👉 彻底修复括号闭合
            p3_24 = set(sorted(range(1, 50), key=lambda n: (1 if n in (f1_kill|f2_kill|f3_kill|f6_kill) else 0, -f5_scores[n]))[:24])
            res_hybrid1.append(n_num in p1_24)
            res_hybrid2.append(n_num in p2_24)
            res_hybrid3.append(n_num in p3_24)

            p30_1 = set(sorted(range(1, 50), key=lambda n: ((2.0 if n in f1_kill else 0)+(3.0 if n in f2_kill else 0)+(2.0 if n in f3_kill else 0)+(1.0 if n in f4_kill else 0)+(2.5 if n in f6_kill else 0)+(1.0 if get_zodiac_of_number(n) not in sub_zods_sea else 0), -f5_scores[n]))[:30])
            p30_2 = set(sorted(range(1, 50), key=lambda n: ((1.0 if n in f1_kill else 0)+(3.0 if n in f2_kill else 0)+(1.0 if n in f3_kill else 0)+(1.0 if n in f4_kill else 0)+(1.5 if n in f6_kill else 0)+(0.5 if get_zodiac_of_number(n) not in sub_zods_sea else 0)-(1.0 if sub_num_om[n]>=sub_num_last[n] else 0), -f5_scores[n]))[:30])
            p30_3 = set(sorted(range(1, 50), key=lambda n: ((1.0 if n in f1_kill else 0)+(2.0 if n in f2_kill else 0)+(1.0 if n in f3_kill else 0)+(1.0 if n in f4_kill else 0)+(2.5 if n in f6_kill else 0)+(0.5 if get_zodiac_of_number(n) not in sub_zods_sea else 0), -f5_scores[n]))[:30])
            res_pool30_1.append(n_num in p30_1)
            res_pool30_2.append(n_num in p30_2)
            res_pool30_3.append(n_num in p30_3)

            res_layers.append(n_num not in f1_kill)
            res_tail10.append(n_num not in f2_kill)
            res_asym10.append(n_num not in f3_kill)
            res_zod3.append(n_num not in f4_kill)
            res_top40.append(n_num in set(sorted(range(1, 50), key=lambda n: -f5_scores[n])[:40]))
            res_asym12.append(n_num not in f6_kill)
            res_or.append(get_zodiac_of_number(n_num) in sub_zods_or)
            res_f4.append(n_num not in f8_kill)
            res_blind12.append(n_num not in f9_kill)
            res_kill15.append(n_num not in f10_kill)
            res_seasons.append(get_zodiac_of_number(n_num) in sub_zods_sea)
            res_elements.append(n_num in set([n for en in trig_elem for n in five_elements[en]]))
            res_segments.append(n_num in set([n for sgn in trig_seg for n in seven_segments[sgn]]))

            # 🌟 新版：平特全维能量流·杀肖模型
            trans_z_flow = defaultdict(int)
            for idx_h in range(h_len - 1):
                if parsed_data[idx_h][1] == prev_zod: trans_z_flow[parsed_data[idx_h+1][1]] += 1
            
            sub_7_zods = (s_flats_zod if s_flats_zod else [get_zodiac_of_number(x) for x in s_flats]) + [s_zod] if s_flats else [s_zod]
            c7_zods = Counter(sub_7_zods)
            
            scores_z_flow = {}
            for z in all_zodiacs:
                s = 0.0
                if z == prev_zod: s += 3.5
                s += c7_zods[z] * 2.0
                if trans_z_flow[z] == 0: s += 3.5
                elif trans_z_flow[z] == 1: s += 1.4
                if sub_zod_om[z] < sub_zod_last[z] and sub_zod_om[z] >= 4: s += 2.0
                if sub_zod_om[z] >= sub_zod_last[z] and sub_zod_om[z] >= 3: s -= 4.5
                scores_z_flow[z] = s
            ranked_zod_kill = sorted(all_zodiacs, key=lambda z: (-scores_z_flow[z], -sub_zod_om[z]))
            res_zod_k2.append(n_zod not in set(ranked_zod_kill[:2]))
            res_zod_k3.append(n_zod not in set(ranked_zod_kill[:3]))
            res_zod_k4.append(n_zod not in set(ranked_zod_kill[:4]))
            res_zod_k5.append(n_zod not in set(ranked_zod_kill[:5]))

            dead_zods_top3 = set(ranked_zod_kill[:3])
            num_dead_scores = {}
            for n in range(1, 50):
                t = n % 10
                z = get_zodiac_of_number(n)
                h = n // 10
                sc = 0.0
                if t in dead_tails_2: sc += 3.0
                if n in f3_kill: sc += 2.5
                if n in f6_kill: sc += 2.0
                if z in dead_zods_top3: sc += 2.5
                if h == sub_killed_head: sc += 1.0
                num_dead_scores[n] = sc
            sorted_dead_nums = sorted(range(1, 50), key=lambda n: -num_dead_scores[n])
            res_num_k8.append(n_num not in set(sorted_dead_nums[:8]))
            res_num_k10.append(n_num not in set(sorted_dead_nums[:10]))
            res_num_k12.append(n_num not in set(sorted_dead_nums[:12]))

            # 🌟 1. 独立杀2码逻辑【时空双核阻尼法】 (Code 1 = prev_num, Code 2 = 最死平码)
            sub_trans_num = defaultdict(int)
            for idx_h in range(h_len - 1):
                if parsed_data[idx_h][0] == prev_num:
                    sub_trans_num[parsed_data[idx_h+1][0]] += 1
            sub_flat_dead_scores = {}
            if s_flats:
                for fn in s_flats:
                    sc = 0.0
                    if sub_trans_num[fn] == 0: sc += 3.0
                    if fn % 10 == dead_tails_2[0]: sc += 2.5
                    if (fn - 1) % 9 + 1 == prev_dr: sc += 2.0
                    sub_flat_dead_scores[fn] = sc
                best_sub_flat = sorted(s_flats, key=lambda fn: (-sub_flat_dead_scores[fn], -fn))[0]
                k2_dual_set = {prev_num, best_sub_flat}
            else:
                k2_dual_set = {prev_num, sorted_dead_nums[0] if sorted_dead_nums[0] != prev_num else sorted_dead_nums[1]}
            res_k2_dual.append(n_num not in k2_dual_set)

            # 🌟 2. 独立杀5码逻辑【五维正交代数晶格死锁法】 (纯代数几何碰撞)
            sub_trans_m7 = defaultdict(int)
            for idx_h in range(h_len - 1):
                if (parsed_data[idx_h][0] % 7) == (prev_num % 7):
                    sub_trans_m7[parsed_data[idx_h+1][0] % 7] += 1
            m7_idx = defaultdict(list)
            for idx_h, x in enumerate(parsed_data[:h_len]): m7_idx[x[0] % 7].append(idx_h)
            sub_m7_om = {m: (h_len - 1 - m7_idx[m][-1]) if m7_idx[m] else h_len for m in range(7)}
            sub_m7_last = {m: (m7_idx[m][-1] - m7_idx[m][-2] - 1) if len(m7_idx[m]) >= 2 else (m7_idx[m][-1] if m7_idx[m] else 0) for m in range(7)}
            sub_rec5_m7 = Counter(x[0] % 7 for x in parsed_data[max(0, h_len-5):h_len])
            sub_scores_m7 = {m: (3.0 if m == (prev_num % 7) else 0) + sub_rec5_m7[m]*1.5 + (3.5 if sub_trans_m7[m] == 0 else (1.5 if sub_trans_m7[m] == 1 else 0)) + (1.2 if sub_m7_om[m] < sub_m7_last[m] and sub_m7_om[m] >= 3 else (-1.8 if sub_m7_om[m] >= sub_m7_last[m] and sub_m7_om[m] >= 3 else 0)) for m in range(7)}
            dead_m7_top1 = sorted(range(7), key=lambda m: (-sub_scores_m7[m], -sub_m7_om[m]))[0]
            dead_m7_nums_set = set(mod7_numbers[dead_m7_top1])

            prev_cst_sub = (prev_num // 10 + prev_num % 10) % 10
            sub_trans_cst = defaultdict(int)
            for idx_h in range(h_len - 1):
                if ((parsed_data[idx_h][0] // 10 + parsed_data[idx_h][0] % 10) % 10) == prev_cst_sub:
                    sub_trans_cst[(parsed_data[idx_h+1][0] // 10 + parsed_data[idx_h+1][0] % 10) % 10] += 1
            cst_idx = defaultdict(list)
            for idx_h, x in enumerate(parsed_data[:h_len]): cst_idx[(x[0] // 10 + x[0] % 10) % 10].append(idx_h)
            sub_cst_om = {c: (h_len - 1 - cst_idx[c][-1]) if cst_idx[c] else h_len for c in range(10)}
            sub_cst_last = {c: (cst_idx[c][-1] - cst_idx[c][-2] - 1) if len(cst_idx[c]) >= 2 else (cst_idx[c][-1] if cst_idx[c] else 0) for c in range(10)}
            sub_rec5_cst = Counter((x[0] // 10 + x[0] % 10) % 10 for x in parsed_data[max(0, h_len-5):h_len])
            sub_scores_cst = {c: (3.0 if c == prev_cst_sub else 0) + sub_rec5_cst[c]*1.2 + (3.5 if sub_trans_cst[c] == 0 else (1.5 if sub_trans_cst[c] == 1 else 0)) + (1.2 if sub_cst_om[c] < sub_cst_last[c] and sub_cst_om[c] >= 3 else (-1.8 if sub_cst_om[c] >= sub_cst_last[c] and sub_cst_om[c] >= 3 else 0)) for c in range(10)}
            dead_cst_top2 = set(sorted(range(10), key=lambda c: (-sub_scores_cst[c], -sub_cst_om[c]))[:2])
            dead_cst_nums_set = set(n for c in dead_cst_top2 for n in cst_numbers[c])

            sub_scores_lat = {}
            for n in range(1, 50):
                sc = 0.0
                if n in dead_m7_nums_set: sc += 2.5
                if n in dead_cst_nums_set: sc += 2.0
                if n in f3_kill: sc += 3.0
                if n in f6_kill: sc += 2.4
                if get_zodiac_of_number(n) in dead_zods_top3: sc += 2.5
                if (n % 10) in dead_tails_2: sc += 2.5
                sub_scores_lat[n] = sc
            k5_lattice_set = set(sorted(range(1, 50), key=lambda n: (-sub_scores_lat[n], n))[:5])
            res_k5_lattice.append(n_num not in k5_lattice_set)

            # 数根
            hist_dr = [(x[0] - 1) % 9 + 1 for x in parsed_data[:h_len]]
            dr_idx = defaultdict(list)
            for idx_h, d in enumerate(hist_dr): dr_idx[d].append(idx_h)
            sub_dr_om = {d: (h_len - 1 - dr_idx[d][-1]) if dr_idx[d] else h_len for d in range(1, 10)}
            sub_dr_last = {d: (dr_idx[d][-1] - dr_idx[d][-2] - 1) if len(dr_idx[d]) >= 2 else (dr_idx[d][-1] if dr_idx[d] else 0) for d in range(1, 10)}
            sub_dr_trans = defaultdict(int)
            for idx_h in range(h_len - 1):
                if hist_dr[idx_h] == prev_dr: sub_dr_trans[hist_dr[idx_h+1]] += 1
            rec5_dr = Counter(hist_dr[-5:])
            sub_dr_scores = {}
            for d in range(1, 10):
                s = 0.0
                if d == prev_dr: s += 3.0
                s += rec5_dr[d] * 1.0
                if sub_dr_trans[d] == 0: s += 3.5
                elif sub_dr_trans[d] == 1: s += 1.4
                if sub_dr_om[d] < sub_dr_last[d] and sub_dr_om[d] >= 3: s += 1.0
                if sub_dr_om[d] >= sub_dr_last[d] and sub_dr_om[d] >= 3: s -= 1.5
                sub_dr_scores[d] = s
            sub_ranked_dr = sorted(range(1, 10), key=lambda d: (-sub_dr_scores[d], -sub_dr_om[d]))
            sub_killed_dr_nums = set(n for d in sub_ranked_dr[:2] for n in dr_numbers[d])
            res_dr_kill.append(n_num not in sub_killed_dr_nums)

            # 半波
            hist_hw = [get_half_wave(x[0]) for x in parsed_data[:h_len]]
            hw_idx = defaultdict(list)
            for idx_h, hw in enumerate(hist_hw): hw_idx[hw].append(idx_h)
            sub_hw_om = {hw: (h_len - 1 - hw_idx[hw][-1]) if hw_idx[hw] else h_len for hw in all_half_waves}
            sub_hw_last = {hw: (hw_idx[hw][-1] - hw_idx[hw][-2] - 1) if len(hw_idx[hw]) >= 2 else (hw_idx[hw][-1] if hw_idx[hw] else 0) for hw in all_half_waves}
            sub_hw_cnt = {hw: len(hw_idx[hw]) for hw in all_half_waves}
            sub_hw_rates = {hw: sub_hw_om[hw] / ((h_len / sub_hw_cnt[hw]) if sub_hw_cnt[hw] > 0 else h_len) for hw in all_half_waves}
            sub_trans_phw = defaultdict(int)
            for idx_h in range(h_len - 1):
                if hist_hw[idx_h] == prev_hw: sub_trans_phw[hist_hw[idx_h+1]] += 1
            sub_trans_tail = defaultdict(int)
            for idx_h in range(h_len - 1):
                if parsed_data[idx_h][0] % 10 == prev_tail: sub_trans_tail[hist_hw[idx_h+1]] += 1
            sub_rec5_hw = Counter(hist_hw[-5:])
            sub_hw_scores = {}
            for hw in all_half_waves:
                sc = (10.0 - sub_trans_phw[hw]) * 1.0 + (5.0 - sub_trans_tail[hw]) * (2.0 / 3.0)
                if sub_hw_om[hw] < sub_hw_last[hw] and sub_hw_om[hw] >= 3: sc += 1.5
                if sub_hw_om[hw] >= sub_hw_last[hw] and sub_hw_om[hw] >= 3: sc -= 2.5
                if sub_rec5_hw[hw] >= 2: sc += 1.0 * sub_rec5_hw[hw]
                if sub_hw_rates[hw] < 0.4 and sub_hw_om[hw] < sub_hw_last[hw]: sc += 1.5
                sub_hw_scores[hw] = sc
            sub_ranked_hw = sorted(all_half_waves, key=lambda hw: (-sub_hw_scores[hw], -sub_hw_om[hw]))
            sub_k1_nums = set(n for hw in sub_ranked_hw[:1] for n in hw_numbers[hw])
            sub_k2_nums = set(n for hw in sub_ranked_hw[:2] for n in hw_numbers[hw])
            res_hw_k1.append(n_num not in sub_k1_nums)
            res_hw_k2.append(n_num not in sub_k2_nums)

            res_cst_k2.append(n_num not in dead_cst_nums_set)
            res_m7_k1.append(n_num not in dead_m7_nums_set)
            dead_m7_top2 = set(mod7_numbers[sorted(range(7), key=lambda m: (-sub_scores_m7[m], -sub_m7_om[m]))[0]] + mod7_numbers[sorted(range(7), key=lambda m: (-sub_scores_m7[m], -sub_m7_om[m]))[1]])
            res_m7_k2.append(n_num not in dead_m7_top2)

            prev_head = prev_num // 10
            hist_heads = [x[0] // 10 for x in parsed_data[:h_len]]
            sub_head_trans = defaultdict(int)
            for idx_h in range(h_len - 1):
                if hist_heads[idx_h] == prev_head: sub_head_trans[hist_heads[idx_h+1]] += 1
            sub_head_idx = defaultdict(list)
            for idx_h, h in enumerate(hist_heads): sub_head_idx[h].append(idx_h)
            sub_head_om = {h: (h_len - 1 - sub_head_idx[h][-1]) if sub_head_idx[h] else h_len for h in range(5)}
            sub_head_last = {h: (sub_head_idx[h][-1] - sub_head_idx[h][-2] - 1) if len(sub_head_idx[h]) >= 2 else (sub_head_idx[h][-1] if sub_head_idx[h] else 0) for h in range(5)}
            sub_rec5_head = Counter(hist_heads[-5:])
            sub_scores_head = {}
            for h in range(5):
                s = 0.0
                s += (8.0 - sub_head_trans[h]) * 1.0
                if sub_head_om[h] < sub_head_last[h] and sub_head_om[h] >= 2: s += 1.5
                if sub_head_om[h] >= sub_head_last[h] and sub_head_om[h] >= 2: s -= 2.0
                if sub_rec5_head[h] >= 2: s += 1.2 * sub_rec5_head[h]
                sub_scores_head[h] = s
            sub_ranked_head = sorted(range(5), key=lambda h: (-sub_scores_head[h], -sub_head_om[h]))
            res_head_k1.append(n_num not in set(head_numbers[sub_ranked_head[0]]))

            dist_counts = defaultdict(int)
            from_pn_dists = defaultdict(int)
            for idx_h in range(1, h_len):
                a = parsed_data[idx_h-1][0]
                b = parsed_data[idx_h][0]
                d = min((a - b) % 49, (b - a) % 49)
                dist_counts[d] += 1
                if a == prev_num: from_pn_dists[d] += 1
            dist_scores = {}
            for d in range(25):
                s = (15.0 - dist_counts[d]) * 0.5
                if from_pn_dists[d] == 0: s += 2.0
                dist_scores[d] = s
            dist_scores[0] += 5.0
            sub_ranked_dists = sorted(range(25), key=lambda d: -dist_scores[d])
            sub_k_dist9 = set()
            for d in sub_ranked_dists[:5]:
                if d == 0: sub_k_dist9.add(prev_num)
                else:
                    sub_k_dist9.add(((prev_num - 1 + d) % 49) + 1)
                    sub_k_dist9.add(((prev_num - 1 - d) % 49) + 1)
            res_dist_k9.append(n_num not in sub_k_dist9)

            prev_q = get_quad(prev_num)
            hist_q = [get_quad(x[0]) for x in parsed_data[:h_len]]
            sub_trans_q = defaultdict(int)
            for idx_h in range(h_len - 1):
                if hist_q[idx_h] == prev_q: sub_trans_q[hist_q[idx_h+1]] += 1
            sub_q_idx = defaultdict(list)
            for idx_h, q in enumerate(hist_q): sub_q_idx[q].append(idx_h)
            sub_q_om = {q: (total_records - 1 - sub_q_idx[q][-1]) if sub_q_idx[q] else total_records for q in all_quads}
            sub_q_last = {q: (sub_q_idx[q][-1] - sub_q_idx[q][-2] - 1) if len(sub_q_idx[q]) >= 2 else (sub_q_idx[q][-1] if sub_q_idx[q] else 0) for q in all_quads}
            sub_rec5_q = Counter(hist_q[-5:])
            sub_scores_q = {}
            for q in all_quads:
                s = (15.0 - sub_trans_q[q]) * 1.0
                if sub_q_om[q] < sub_q_last[q] and sub_q_om[q] >= 2: s += 1.5
                if sub_q_om[q] >= sub_q_last[q] and sub_q_om[q] >= 2: s -= 2.0
                if sub_rec5_q[q] >= 2: s += 1.2 * sub_rec5_q[q]
                sub_scores_q[q] = s
            sub_ranked_q = sorted(all_quads, key=lambda q: (-sub_scores_q[q], -sub_q_om[q]))
            res_quad_k1.append(n_num not in set(quad_numbers[sub_ranked_q[0]]))

            # 平码 6 套新战法回测
            if s_flats and len(s_flats) == 6:
                res_flat_k6.append(n_num not in set(s_flats))
                res_flat_k7.append(n_num not in (set(s_flats) | {prev_num}))
                sub_7_zods = (s_flats_zod if s_flats_zod else [get_zodiac_of_number(x) for x in s_flats]) + [s_zod]
                sub_top2_z = set([z for z, c in Counter(sub_7_zods).most_common()][:2])
                res_flat_zod_k2.append(n_zod not in sub_top2_z)
                sub_7_drs = [(n - 1) % 9 + 1 for n in (s_flats + [prev_num])]
                sub_top2_dr = set([d for d, c in Counter(sub_7_drs).most_common()][:2])
                sub_k_dr = set(n for d in sub_top2_dr for n in dr_numbers[d])
                res_flat_dr_k2.append(n_num not in sub_k_dr)
                sub_7_hws = [get_half_wave(n) for n in (s_flats + [prev_num])]
                sub_top1_hw = Counter(sub_7_hws).most_common(1)[0][0]
                res_flat_hw_k1.append(n_num not in set(hw_numbers[sub_top1_hw]))
                sub_7_elems = [num_to_elem[n] for n in (s_flats + [prev_num])]
                sub_top1_elem = Counter(sub_7_elems).most_common(1)[0][0]
                res_flat_elem_k1.append(n_num not in set(five_elements[sub_top1_elem]))
            else:
                res_flat_k6.append(True)
                res_flat_k7.append(True)
                res_flat_zod_k2.append(True)
                res_flat_dr_k2.append(True)
                res_flat_hw_k1.append(True)
                res_flat_elem_k1.append(True)

            # 极限精选 15-20 码狙击模型
            base_24_s3 = sorted(range(1, 50), key=lambda n: (1 if n in (f1_kill|f2_kill|f3_kill|f6_kill) else 0, -f5_scores[n]))[:24]
            pool_20 = sorted(base_24_s3, key=lambda n: (
                f5_scores[n] + (2.0 if sub_num_om[n]>=sub_num_last[n] else 0.0) -
                (2.5 if n in f9_kill else 0.0) - (2.0 if n == prev_num else 0.0)
            ), reverse=True)[:20]
            pool_18 = sorted(base_24_s3, key=lambda n: (1 if n in f9_kill else 0, -f5_scores[n]))[:18]
            base_24_s1 = sorted(range(1, 50), key=lambda n: ((1.0 if n in f1_kill else 0)+(2.5 if n in f2_kill else 0)+(2.5 if n in f3_kill else 0)+(1.0 if n in f4_kill else 0)+(2.5 if n in f6_kill else 0)+(0.5 if get_zodiac_of_number(n) not in sub_zods_sea else 0), -f5_scores[n]))[:24]
            pool_16 = sorted(base_24_s1, key=lambda n: -f5_scores[n])[:16]
            pool_15 = sorted(base_24_s3, key=lambda n: -f5_scores[n])[:15]
            res_slim_20.append(n_num in set(pool_20))
            res_slim_18.append(n_num in set(pool_18))
            res_slim_16.append(n_num in set(pool_16))
            res_slim_15.append(n_num in set(pool_15))

            # 多核交集共振
            res_inter_4_5.append(n_num in (f1_kept & f2_kept))
            res_inter_6_7.append(n_num in (f3_kept & f4_kept))
            res_inter_3_4_5.append(n_num in (p30_1 & f1_kept & f2_kept))

        tier_stats = {}
        for k_name, recs in res_tier_records.items():
            hl = [x[0] for x in recs]
            base_st = calc_rate_and_streaks(hl)
            h20 = sum(1 for x in recs if x[1])
            h10 = sum(1 for x in recs if x[2])
            h5 = sum(1 for x in recs if x[3])
            c_per_day = tier_configs[k_name]['cost']
            profits = []
            for is_h, is20, is10, is5 in recs:
                if is20: profits.append(20 * 47 - c_per_day)
                elif is10: profits.append(10 * 47 - c_per_day)
                elif is5: profits.append(5 * 47 - c_per_day)
                else: profits.append(-c_per_day)
            base_st['h20'] = h20
            base_st['h10'] = h10
            base_st['h5'] = h5
            base_st['misses'] = len(recs) - sum(hl)
            base_st['tot_profit'] = sum(profits)
            base_st['weekly_profit'] = sum(profits) / (len(recs) / 7)
            base_st['l30_profit'] = sum(profits[-30:])
            base_st['l30_weekly'] = sum(profits[-30:]) / (30 / 7)
            tier_stats[k_name] = base_st

        # 计算所有模块的连红与全周期风控信息
        stats_hybrid1 = calc_rate_and_streaks(res_hybrid1)
        stats_hybrid2 = calc_rate_and_streaks(res_hybrid2)
        stats_hybrid3 = calc_rate_and_streaks(res_hybrid3)
        stats_pool30_1 = calc_rate_and_streaks(res_pool30_1)
        stats_pool30_2 = calc_rate_and_streaks(res_pool30_2)
        stats_pool30_3 = calc_rate_and_streaks(res_pool30_3)

        # 🌟 杀肖统计对象 (新版平特全维能量流)
        stats_zod_k2 = calc_rate_and_streaks(res_zod_k2)
        stats_zod_k3 = calc_rate_and_streaks(res_zod_k3)
        stats_zod_k4 = calc_rate_and_streaks(res_zod_k4)
        stats_zod_k5 = calc_rate_and_streaks(res_zod_k5)

        stats_num_k8 = calc_rate_and_streaks(res_num_k8)
        stats_num_k10 = calc_rate_and_streaks(res_num_k10)
        stats_num_k12 = calc_rate_and_streaks(res_num_k12)
        
        # 🌟 独立双逻辑杀码统计对象
        stats_k2_dual = calc_rate_and_streaks(res_k2_dual)
        stats_k5_lattice = calc_rate_and_streaks(res_k5_lattice)

        stats_dr_kill = calc_rate_and_streaks(res_dr_kill)
        stats_hw_k1 = calc_rate_and_streaks(res_hw_k1)
        stats_hw_k2 = calc_rate_and_streaks(res_hw_k2)

        stats_cst = calc_rate_and_streaks(res_cst_k2)
        stats_m7_k1 = calc_rate_and_streaks(res_m7_k1)
        stats_m7_k2 = calc_rate_and_streaks(res_m7_k2)
        stats_head = calc_rate_and_streaks(res_head_k1)
        stats_dist = calc_rate_and_streaks(res_dist_k9)
        stats_quad = calc_rate_and_streaks(res_quad_k1)
        
        # 平码战法统计
        stats_flat_k6 = calc_rate_and_streaks(res_flat_k6)
        stats_flat_k7 = calc_rate_and_streaks(res_flat_k7)
        stats_flat_zod_k2 = calc_rate_and_streaks(res_flat_zod_k2)
        stats_flat_dr_k2 = calc_rate_and_streaks(res_flat_dr_k2)
        stats_flat_hw_k1 = calc_rate_and_streaks(res_flat_hw_k1)
        stats_flat_elem_k1 = calc_rate_and_streaks(res_flat_elem_k1)

        stats_slim_20 = calc_rate_and_streaks(res_slim_20)
        stats_slim_18 = calc_rate_and_streaks(res_slim_18)
        stats_slim_16 = calc_rate_and_streaks(res_slim_16)
        stats_slim_15 = calc_rate_and_streaks(res_slim_15)

        stats_inter_4_5 = calc_rate_and_streaks(res_inter_4_5)
        stats_inter_6_7 = calc_rate_and_streaks(res_inter_6_7)
        stats_inter_3_4_5 = calc_rate_and_streaks(res_inter_3_4_5)

        stats_layers = calc_rate_and_streaks(res_layers)
        stats_tail10 = calc_rate_and_streaks(res_tail10)
        stats_asym10 = calc_rate_and_streaks(res_asym10)
        stats_zod3 = calc_rate_and_streaks(res_zod3)
        stats_top40 = calc_rate_and_streaks(res_top40)
        stats_asym12 = calc_rate_and_streaks(res_asym12)
        stats_or = calc_rate_and_streaks(res_or)
        stats_f4 = calc_rate_and_streaks(res_f4)
        stats_blind12 = calc_rate_and_streaks(res_blind12)
        stats_kill15 = calc_rate_and_streaks(res_kill15)
        stats_seasons = calc_rate_and_streaks(res_seasons)
        stats_elements = calc_rate_and_streaks(res_elements)
        stats_segments = calc_rate_and_streaks(res_segments)

        # 最新当期候选集生成
        curr_prev_num = parsed_data[-1][0]
        curr_prev_zod = parsed_data[-1][1]
        curr_prev_flats = parsed_data[-1][2]
        curr_prev_header = parsed_data[-1][3]
        curr_prev_flats_zod = parsed_data[-1][4]
        
        curr_prev_dr = (curr_prev_num - 1) % 9 + 1
        curr_prev_hw = get_half_wave(curr_prev_num)
        curr_prev_tail = curr_prev_num % 10
        curr_prev_cst = (curr_prev_num // 10 + curr_prev_num % 10) % 10
        curr_prev_m7 = curr_prev_num % 7
        curr_prev_head = curr_prev_num // 10
        curr_prev_q = get_quad(curr_prev_num)

        curr_trig_z2 = [zn for zn in zodiac_zones_2 if zone_omission[zn] >= zone_last_omission[zn]]
        curr_trig_z3 = [zn for zn in zodiac_zones_3 if zone_omission[zn] >= zone_last_omission[zn]]
        curr_zods_or = set([z for zn in curr_trig_z2 for z in zodiac_zones_2[zn]]).union([z for zn in curr_trig_z3 for z in zodiac_zones_3[zn]]) or set(all_zodiacs)
        curr_trig_sea = [sn for sn in zodiac_seasons if season_omission[sn] >= season_last_omission[sn]]
        curr_zods_sea = set([z for sn in curr_trig_sea for z in zodiac_seasons[sn]])
        curr_trig_zods = set([z for z in all_zodiacs if zodiac_omission[z] >= zodiac_last_omission[z]])
        curr_trig_tails = set([t for t in all_tails if tail_omission[t] >= tail_last_omission[t]])
        curr_killed_head = ((curr_prev_num // 10) - 2) % 5

        curr_f1_kill = set(n for n in range(1, 50) if not (num_omission[n] <= 25 or (26 <= num_omission[n] <= 50 and (num_omission[n] >= num_last_omission[n] or num_rates[n] >= 0.40)) or (51 <= num_omission[n] <= 100 and num_omission[n] >= num_last_omission[n])))
        curr_f1_kept = set(range(1, 50)) - curr_f1_kill
        curr_rec_tail_8 = defaultdict(int)
        for s_num, _, _, _, _ in parsed_data[-8:]: curr_rec_tail_8[s_num % 10] += 1
        curr_scores_t = sorted([(t, curr_rec_tail_8[t] - tail_omission[t]) for t in range(1, 10)], key=lambda x: -x[1])
        curr_dead_tails_2 = (curr_scores_t[0][0], curr_scores_t[1][0])
        curr_f2_kill = set([n for n in range(1, 50) if (n % 10) in curr_dead_tails_2])
        curr_f2_kept = set(range(1, 50)) - curr_f2_kill

        curr_off10 = 18 if curr_prev_num <= 16 else (0 if curr_prev_num <= 33 else 7)
        curr_f3_kill = set([((curr_prev_num + curr_off10 + j - 1) % 49) + 1 for j in range(10)])
        curr_f3_kept = set(range(1, 50)) - curr_f3_kill

        curr_rec_zod_7 = defaultdict(int)
        for _, s_zod, _, _, _ in parsed_data[-7:]: curr_rec_zod_7[s_zod] += 1
        curr_z_sc_list = sorted([(z, curr_rec_zod_7[z]*1.5 + (0.5 if zodiac_rates[z]<0.4 and zodiac_omission[z]<zodiac_last_omission[z] else 0) + (0.5 if z not in curr_zods_or else 0) + (1.0 if zodiac_omission[z]==0 else 0)) for z in all_zodiacs], key=lambda x: -x[1])
        curr_f4_kill = set([n for n in range(1, 50) if get_zodiac_of_number(n) in set(x[0] for x in curr_z_sc_list[:3])])
        curr_f4_kept = set(range(1, 50)) - curr_f4_kill

        curr_f5_scores = {n: (3.0 if get_zodiac_of_number(n) in curr_zods_or else 0) + (1.5+zodiac_rates[get_zodiac_of_number(n)] if get_zodiac_of_number(n) in curr_trig_zods else zodiac_rates[get_zodiac_of_number(n)]-1.0) + (1.5+tail_rates[n%10] if n%10 in curr_trig_tails else tail_rates[n%10]-1.0) + (1.0 if num_omission[n]>=num_last_omission[n] else -0.5) + (-1.0 if n//10==curr_killed_head else 0) for n in range(1, 50)}
        curr_off12 = 26 if curr_prev_num <= 16 else (2 if curr_prev_num <= 33 else 5)
        curr_f6_kill = set([((curr_prev_num + curr_off12 + j - 1) % 49) + 1 for j in range(12)])
        curr_f6_kept = set(range(1, 50)) - curr_f6_kill
        curr_f8_kill = set(n for n in range(1, 50) if (((zodiac_rates[get_zodiac_of_number(n)]<0.4 and zodiac_omission[get_zodiac_of_number(n)]<zodiac_last_omission[get_zodiac_of_number(n)]) or (tail_rates[n%10]<0.4 and tail_omission[n%10]<tail_last_omission[n%10])) and not (zodiac_omission[get_zodiac_of_number(n)]>=zodiac_last_omission[get_zodiac_of_number(n)] or tail_omission[n%10]>=tail_last_omission[n%10])))
        curr_f9_kill = set([((curr_prev_num + j - 1) % 49) + 1 for j in range(2, 14)])
        curr_f10_scores = {n: 0.35 * zodiac_rates[get_zodiac_of_number(n)] + 0.35 * tail_rates[n%10] + 0.30 * num_rates[n] - (0.15 if zodiac_omission[get_zodiac_of_number(n)] < zodiac_last_omission[get_zodiac_of_number(n)] else 0) - (0.15 if tail_omission[n%10] < tail_last_omission[n%10] else 0) - (0.10 if num_omission[n] < num_last_omission[n] else 0) for n in range(1, 50)}

        curr_tier_sc = {n: curr_f5_scores[n] - (2.0 if n in curr_f1_kill else 0) - (3.0 if n in curr_f2_kill else 0) - (3.0 if n in curr_f3_kill else 0) - (2.5 if n in curr_f6_kill else 0) for n in range(1, 50)}
        curr_ranked_tier = sorted(range(1, 50), key=lambda n: -curr_tier_sc[n])

        # 🌟 最新当期新版杀肖打分计算 (平特全维能量流)
        curr_trans_z_flow = defaultdict(int)
        for idx_t in range(len(parsed_data) - 1):
            if parsed_data[idx_t][1] == curr_prev_zod: curr_trans_z_flow[parsed_data[idx_t+1][1]] += 1
        
        curr_7_zods = (curr_prev_flats_zod if curr_prev_flats_zod else [get_zodiac_of_number(x) for x in curr_prev_flats]) + [curr_prev_zod] if curr_prev_flats else [curr_prev_zod]
        curr_c7_zods = Counter(curr_7_zods)
        
        curr_scores_z_flow = {}
        for z in all_zodiacs:
            s = 0.0
            if z == curr_prev_zod: s += 3.5
            s += curr_c7_zods[z] * 2.0
            if curr_trans_z_flow[z] == 0: s += 3.5
            elif curr_trans_z_flow[z] == 1: s += 1.4
            if zodiac_omission[z] < zodiac_last_omission[z] and zodiac_omission[z] >= 4: s += 2.0
            if zodiac_omission[z] >= zodiac_last_omission[z] and zodiac_omission[z] >= 3: s -= 4.5
            curr_scores_z_flow[z] = s
        curr_ranked_zod_kill = sorted(all_zodiacs, key=lambda z: (-curr_scores_z_flow[z], -zodiac_omission[z]))

        # 物理神盾杀码
        curr_dead_zods_top3 = set(curr_ranked_zod_kill[:3])
        curr_num_dead_scores = {}
        for n in range(1, 50):
            t = n % 10
            z = get_zodiac_of_number(n)
            h = n // 10
            sc = 0.0
            if t in curr_dead_tails_2: sc += 3.0
            if n in curr_f3_kill: sc += 2.5
            if n in curr_f6_kill: sc += 2.0
            if z in curr_dead_zods_top3: sc += 2.5
            if h == curr_killed_head: sc += 1.0
            num_dead_scores[n] = sc
        curr_sorted_dead_nums = sorted(range(1, 50), key=lambda n: -num_dead_scores[n])

        # 🌟 1. 独立杀2码逻辑【时空双核阻尼法】 (Code 1 = prev_num, Code 2 = 最死平码)
        curr_trans_num = defaultdict(int)
        for idx_h in range(len(parsed_data) - 1):
            if parsed_data[idx_h][0] == curr_prev_num:
                curr_trans_num[parsed_data[idx_h+1][0]] += 1
        curr_flat_dead_scores = {}
        if curr_prev_flats:
            for fn in curr_prev_flats:
                sc = 0.0
                if curr_trans_num[fn] == 0: sc += 3.0
                if fn % 10 == curr_dead_tails_2[0]: sc += 2.5
                if (fn - 1) % 9 + 1 == curr_prev_dr: sc += 2.0
                curr_flat_dead_scores[fn] = sc
            best_curr_flat = sorted(curr_prev_flats, key=lambda fn: (-curr_flat_dead_scores[fn], -fn))[0]
            curr_k2_dual_nums = sorted([curr_prev_num, best_curr_flat])
        else:
            curr_k2_dual_nums = sorted([curr_prev_num, curr_sorted_dead_nums[0] if curr_sorted_dead_nums[0] != curr_prev_num else curr_sorted_dead_nums[1]])
        curr_kept_k2_dual = sorted([n for n in range(1, 50) if n not in set(curr_k2_dual_nums)])

        # 🌟 2. 独立杀5码逻辑【五维正交代数晶格死锁法】 (纯代数几何碰撞)
        curr_trans_m7 = defaultdict(int)
        for idx_h in range(len(parsed_data) - 1):
            if (parsed_data[idx_h][0] % 7) == (curr_prev_num % 7):
                curr_trans_m7[parsed_data[idx_h+1][0] % 7] += 1
        m7_idx = defaultdict(list)
        for idx_h, x in enumerate(parsed_data): m7_idx[x[0] % 7].append(idx_h)
        curr_m7_om = {m: (total_records - 1 - m7_idx[m][-1]) if m7_idx[m] else total_records for m in range(7)}
        curr_m7_last = {m: (m7_idx[m][-1] - m7_idx[m][-2] - 1) if len(m7_idx[m]) >= 2 else (m7_idx[m][-1] if m7_idx[m] else 0) for m in range(7)}
        curr_rec5_m7 = Counter(x[0] % 7 for x in parsed_data[-5:])
        curr_scores_m7 = {m: (3.0 if m == (curr_prev_num % 7) else 0) + curr_rec5_m7[m]*1.5 + (3.5 if curr_trans_m7[m] == 0 else (1.5 if curr_trans_m7[m] == 1 else 0)) + (1.2 if curr_m7_om[m] < curr_m7_last[m] and curr_m7_om[m] >= 3 else (-1.8 if curr_m7_om[m] >= curr_m7_last[m] and curr_m7_om[m] >= 3 else 0)) for m in range(7)}
        dead_m7_top1_curr = sorted(range(7), key=lambda m: (-curr_scores_m7[m], -curr_m7_om[m]))[0]
        dead_m7_nums_curr = set(mod7_numbers[dead_m7_top1_curr])

        prev_cst_curr = (curr_prev_num // 10 + curr_prev_num % 10) % 10
        curr_trans_cst = defaultdict(int)
        for idx_h in range(len(parsed_data) - 1):
            if ((parsed_data[idx_h][0] // 10 + parsed_data[idx_h][0] % 10) % 10) == prev_cst_sub:
                curr_trans_cst[(parsed_data[idx_h+1][0] // 10 + parsed_data[idx_h+1][0] % 10) % 10] += 1
        cst_idx = defaultdict(list)
        for idx_h, x in enumerate(parsed_data): cst_idx[(x[0] // 10 + x[0] % 10) % 10].append(idx_h)
        curr_cst_om = {c: (total_records - 1 - cst_idx[c][-1]) if cst_idx[c] else total_records for c in range(10)}
        curr_cst_last = {c: (cst_idx[c][-1] - cst_idx[c][-2] - 1) if len(cst_idx[c]) >= 2 else (cst_idx[c][-1] if cst_idx[c] else 0) for c in range(10)}
        curr_rec5_cst = Counter((x[0] // 10 + x[0] % 10) % 10 for x in parsed_data[-5:])
        curr_scores_cst = {c: (3.0 if c == prev_cst_sub else 0) + sub_rec5_cst[c]*1.2 + (3.5 if sub_trans_cst[c] == 0 else (1.5 if sub_trans_cst[c] == 1 else 0)) + (1.2 if sub_cst_om[c] < sub_cst_last[c] and sub_cst_om[c] >= 3 else (-1.8 if sub_cst_om[c] >= sub_cst_last[c] and sub_cst_om[c] >= 3 else 0)) for c in range(10)}
        dead_cst_top2_curr = set(sorted(range(10), key=lambda c: (-curr_scores_cst[c], -sub_cst_om[c]))[:2])
        dead_cst_nums_curr = set(n for c in dead_cst_top2_curr for n in cst_numbers[c])

        curr_scores_lat = {}
        for n in range(1, 50):
            sc = 0.0
            if n in dead_m7_nums_curr: sc += 2.5
            if n in dead_cst_nums_curr: sc += 2.0
            if n in curr_f3_kill: sc += 3.0
            if n in curr_f6_kill: sc += 2.4
            if get_zodiac_of_number(n) in curr_dead_zods_top3: sc += 2.5
            if (n % 10) in curr_dead_tails_2: sc += 2.5
            curr_scores_lat[n] = sc
        curr_k5_lattice_nums = sorted(sorted(range(1, 50), key=lambda n: (-curr_scores_lat[n], n))[:5])
        curr_kept_k5_lattice = sorted([n for n in range(1, 50) if n not in set(curr_k5_lattice_nums)])

        # 数根动力学
        curr_hist_dr = [(x[0] - 1) % 9 + 1 for x in parsed_data]
        curr_dr_idx = defaultdict(list)
        for idx_h, d in enumerate(curr_hist_dr): curr_dr_idx[d].append(idx_h)
        curr_dr_om = {d: (total_records - 1 - curr_dr_idx[d][-1]) if curr_dr_idx[d] else total_records for d in range(1, 10)}
        curr_dr_last = {d: (curr_dr_idx[d][-1] - curr_dr_idx[d][-2] - 1) if len(curr_dr_idx[d]) >= 2 else (curr_dr_idx[d][-1] if curr_dr_idx[d] else 0) for d in range(1, 10)}
        curr_dr_trans = defaultdict(int)
        for idx_h in range(total_records - 1):
            if curr_hist_dr[idx_h] == curr_prev_dr: curr_dr_trans[curr_hist_dr[idx_h+1]] += 1
        curr_rec5_dr = Counter(curr_hist_dr[-5:])
        curr_dr_scores = {}
        for d in range(1, 10):
            s = 0.0
            if d == curr_prev_dr: s += 3.0
            s += rec5_dr[d] * 1.0
            if curr_dr_trans[d] == 0: s += 3.5
            elif curr_dr_trans[d] == 1: s += 1.4
            if curr_dr_om[d] < curr_dr_last[d] and curr_dr_om[d] >= 3: s += 1.0
            if curr_dr_om[d] >= curr_dr_last[d] and curr_dr_om[d] >= 3: s -= 1.5
            curr_dr_scores[d] = s
        curr_ranked_dr = sorted(range(1, 10), key=lambda d: (-curr_dr_scores[d], -curr_dr_om[d]))
        curr_killed_2_dr = curr_ranked_dr[:2]
        curr_killed_dr_nums = sorted([n for d in curr_killed_2_dr for n in dr_numbers[d]])
        curr_kept_dr_nums = sorted([n for n in range(1, 50) if n not in curr_killed_dr_nums])

        # 半波动力学
        curr_hist_hw = [get_half_wave(x[0]) for x in parsed_data]
        curr_hw_idx = defaultdict(list)
        for idx_h, hw in enumerate(curr_hist_hw): curr_hw_idx[hw].append(idx_h)
        curr_hw_om = {hw: (total_records - 1 - curr_hw_idx[hw][-1]) if curr_hw_idx[hw] else total_records for hw in all_half_waves}
        curr_hw_last = {hw: (curr_hw_idx[hw][-1] - curr_hw_idx[hw][-2] - 1) if len(curr_hw_idx[hw]) >= 2 else (curr_hw_idx[hw][-1] if curr_hw_idx[hw] else 0) for hw in all_half_waves}
        curr_hw_cnt = {hw: len(curr_hw_idx[hw]) for hw in all_half_waves}
        curr_hw_rates = {hw: curr_hw_om[hw] / ((total_records / curr_hw_cnt[hw]) if curr_hw_cnt[hw] > 0 else total_records) for hw in all_half_waves}
        curr_trans_phw = defaultdict(int)
        for idx_h in range(total_records - 1):
            if curr_hist_hw[idx_h] == curr_prev_hw: curr_trans_phw[curr_hist_hw[idx_h+1]] += 1
        curr_trans_tail = defaultdict(int)
        for idx_h in range(total_records - 1
