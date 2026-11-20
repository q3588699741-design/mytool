import streamlit as st
import pandas as pd
from collections import Counter
import itertools
import os
import re

# ==========================================
# 1. 页面基础配置与全局常量
# ==========================================
st.set_page_config(page_title="开奖记录多维统计与预测看板", page_icon="🔮", layout="wide", initial_sidebar_state="expanded")

st.title("🔮 开奖记录全维度统计与量化参考预测看板")
st.caption("📥 文本批量粘贴 / 表格自动存档 ｜ 跨年动态生肖对齐 ｜ 🔮 自定义权重量化预测与自动寻优 ｜ 🔍 交互式组合筛选器")

LOCAL_DB_FILE = "saved_history.csv"

ZODIAC_ORDER = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
DEFAULT_YEAR_ZODIAC = '马'  # 2026 丙午马年默认基准

RED_BALLS = {1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46}
BLUE_BALLS = {3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48}
GREEN_BALLS = {5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49}

_ZODIAC_MAP_CACHE = {}

def get_zodiac_map(year_zodiac: str) -> dict:
    yz = year_zodiac if year_zodiac in ZODIAC_ORDER else DEFAULT_YEAR_ZODIAC
    if yz not in _ZODIAC_MAP_CACHE:
        start_idx = ZODIAC_ORDER.index(yz)
        _ZODIAC_MAP_CACHE[yz] = {
            num: ZODIAC_ORDER[(start_idx - (num - 1)) % 12]
            for num in range(1, 50)
        }
    return _ZODIAC_MAP_CACHE[yz]

def get_wave_color(n: int) -> str:
    if n in RED_BALLS: return '红波'
    elif n in BLUE_BALLS: return '蓝波'
    elif n in GREEN_BALLS: return '绿波'
    return '未知'

def get_big_small(n: int) -> str:
    if n == 49: return '和(49)'
    return '大(25-48)' if n >= 25 else '小(01-24)'

def get_odd_even(n: int) -> str:
    if n == 49: return '和(49)'
    return '单' if n % 2 == 1 else '双'

# ==========================================
# 2. 本地数据库持久化与多格式解析引擎
# ==========================================
def save_to_local_db(records: list, filepath: str = LOCAL_DB_FILE):
    rows = []
    for r in records:
        flats = r.get("flats") if (r.get("flats") and len(r["flats"]) == 6) else [None] * 6
        rows.append({
            "issue": r["issue"],
            "year_zodiac": r.get("year_zodiac", DEFAULT_YEAR_ZODIAC),
            "n1": flats[0], "n2": flats[1], "n3": flats[2],
            "n4": flats[3], "n5": flats[4], "n6": flats[5],
            "special": r["special"],
            "special_zodiac": r.get("special_zodiac", ""),
        })
    pd.DataFrame(rows).to_csv(filepath, index=False, encoding="utf-8-sig")

def load_from_local_db(filepath: str = LOCAL_DB_FILE) -> list:
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        return []
    df = pd.read_csv(filepath)
    records = []
    for _, row in df.iterrows():
        has_f = pd.notna(row.get("n1")) and pd.notna(row.get("n6"))
        flats = [int(row[f"n{k}"]) for k in range(1, 7)] if has_f else None
        yz = str(row.get("year_zodiac", DEFAULT_YEAR_ZODIAC)).strip()
        if yz not in ZODIAC_ORDER:
            yz = DEFAULT_YEAR_ZODIAC
        sp = int(row["special"])
        sp_z = str(row.get("special_zodiac", "")).strip()
        if not sp_z or sp_z == "nan":
            sp_z = get_zodiac_map(yz)[sp]
        records.append({
            "issue": str(row["issue"]).strip(),
            "year_zodiac": yz,
            "flats": flats,
            "special": sp,
            "special_zodiac": sp_z,
        })
    return records

def append_text_to_db(raw_text: str, default_yz: str, filepath: str = LOCAL_DB_FILE) -> tuple:
    existing = load_from_local_db(filepath)
    existing_issues = {r["issue"] for r in existing}
    added, dup, failed = 0, 0, 0

    for line in raw_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        yz = default_yz
        z_match = re.search(r"[\[\(【（]([鼠牛虎兔龙蛇马羊猴鸡狗猪])年?[\]\)】）]", line)
        if z_match:
            yz = z_match.group(1)

        tokens = re.findall(r"\d+", line)
        if len(tokens) < 8:
            failed += 1
            continue

        issue = tokens[0]
        balls = [int(x) for x in tokens[1:8]]
        if any(b < 1 or b > 49 for b in balls) or len(set(balls)) != 7:
            failed += 1
            continue

        if issue in existing_issues:
            dup += 1
            continue

        sp = balls[6]
        existing.append({
            "issue": issue,
            "year_zodiac": yz,
            "flats": balls[:6],
            "special": sp,
            "special_zodiac": get_zodiac_map(yz)[sp],
        })
        existing_issues.add(issue)
        added += 1

    if added > 0:
        save_to_local_db(existing, filepath)
    return added, dup, failed

def parse_uploaded_table(uploaded_file, default_yz: str) -> list:
    if uploaded_file.name.endswith('.csv'):
        df_raw = pd.read_csv(uploaded_file, header=None)
    else:
        df_raw = pd.read_excel(uploaded_file, header=None)

    has_period_header = any('期' in str(df_raw.iloc[r, 0]) for r in range(min(15, len(df_raw))))
    records = []

    if has_period_header and df_raw.shape[1] >= 7:
        i = 0
        temp = []
        while i < len(df_raw):
            val = str(df_raw.iloc[i, 0])
            if '期' in val:
                try:
                    issue_str = val.split('期')[0].strip()
                    nums = df_raw.iloc[i+1, :].tolist()
                    zods = df_raw.iloc[i+2, :].tolist()
                    p_flats = [int(nums[k]) for k in range(6)]
                    te = int(nums[7])
                    zte = str(zods[7]).strip()
                    temp.append({
                        "issue": issue_str if issue_str else val.strip(),
                        "year_zodiac": default_yz,
                        "flats": p_flats,
                        "special": te,
                        "special_zodiac": zte if zte in ZODIAC_ORDER else get_zodiac_map(default_yz)[te],
                    })
                    i += 3
                except Exception:
                    i += 1
            else:
                i += 1

        if len(temp) >= 2:
            d0 = int(''.join(filter(str.isdigit, temp[0]['issue']))) if any(c.isdigit() for c in temp[0]['issue']) else 0
            d1 = int(''.join(filter(str.isdigit, temp[-1]['issue']))) if any(c.isdigit() for c in temp[-1]['issue']) else 0
            if d0 > d1:
                temp = temp[::-1]

        seen = set()
        for item in temp:
            if item["issue"] not in seen:
                seen.add(item["issue"])
                records.append(item)
    else:
        df_clean = df_raw.dropna(how="all")
        for idx, row in df_clean.iterrows():
            vals = [str(x).strip() for x in row.tolist() if pd.notna(x)]
            if not vals or not vals[0].isdigit():
                continue
            if len(vals) >= 8 and all(v.isdigit() for v in vals[:8]):
                sp = int(vals[7])
                records.append({
                    "issue": vals[0],
                    "year_zodiac": default_yz,
                    "flats": [int(x) for x in vals[1:7]],
                    "special": sp,
                    "special_zodiac": get_zodiac_map(default_yz)[sp],
                })
            elif len(vals) >= 2 and vals[0].isdigit():
                sp = int(vals[0])
                z_str = vals[1] if vals[1] in ZODIAC_ORDER else get_zodiac_map(default_yz)[sp]
                records.append({
                    "issue": str(idx + 1),
                    "year_zodiac": default_yz,
                    "flats": None,
                    "special": sp,
                    "special_zodiac": z_str,
                })

    return records

# ==========================================
# 3. 支持动态权重与自动寻优的量化评分预测算法
# ==========================================
def extract_step_features(sub_records: list, default_yz: str) -> list:
    """提取单期特征基础分（剥离权重系数，便于高速网格搜索与即时打分）"""
    n_draws = len(sub_records)
    last_draw = sub_records[-1]
    latest_yz = last_draw.get("year_zodiac", default_yz)
    z_map = get_zodiac_map(latest_yz)

    window = sub_records[-min(30, n_draws):]
    w_len = len(window)

    curr_miss = {num: 0 for num in range(1, 50)}
    for d in sub_records:
        sp = d["special"]
        for num in range(1, 50):
            curr_miss[num] = 0 if num == sp else curr_miss[num] + 1

    w_wave = Counter(get_wave_color(d["special"]) for d in window)
    w_bs = Counter(get_big_small(d["special"]) for d in window)
    w_oe = Counter(get_odd_even(d["special"]) for d in window)
    w_zod = Counter(get_zodiac_map(d.get("year_zodiac", default_yz))[d["special"]] for d in window)
    w_tail = Counter(d["special"] % 10 for d in window)

    theory_wave = {"红波": 17 / 49, "蓝波": 16 / 49, "绿波": 16 / 49}
    theory_bs = {"小(01-24)": 24 / 49, "大(25-48)": 24 / 49, "和(49)": 1 / 49}
    theory_oe = {"单": 24 / 49, "双": 24 / 49, "和(49)": 1 / 49}

    prev_special = last_draw["special"]
    prev_flats = set(last_draw["flats"]) if last_draw.get("flats") else set()

    features = []
    for num in range(1, 50):
        w = get_wave_color(num)
        bs = get_big_small(num)
        oe = get_odd_even(num)
        z = z_map[num]
        t = num % 10

        desire_ratio = min(curr_miss[num] / 49.0, 2.2)
        base_omission = desire_ratio * 35.0

        wave_deficit = max(0.0, theory_wave[w] - (w_wave[w] / w_len))
        bs_deficit = max(0.0, theory_bs[bs] - (w_bs[bs] / w_len))
        oe_deficit = max(0.0, theory_oe[oe] - (w_oe[oe] / w_len))

        z_pool = 5 if z == latest_yz else 4
        zod_deficit = max(0.0, (z_pool / 49.0) - (w_zod[z] / w_len))

        t_pool = 4 if t == 0 else 5
        tail_deficit = max(0.0, (t_pool / 49.0) - (w_tail[t] / w_len))

        base_balance = (
            wave_deficit * 60.0 +
            bs_deficit * 50.0 +
            oe_deficit * 50.0 +
            zod_deficit * 80.0 +
            tail_deficit * 70.0
        )

        raw_penalty = 25.0 if num == prev_special else (10.0 if num in prev_flats else 0.0)

        features.append({
            "num": num,
            "base_omission": base_omission,
            "base_balance": base_balance,
            "raw_penalty": raw_penalty,
            "wave": w,
            "zodiac": z,
            "big_small": bs,
            "odd_even": oe,
            "tail": t,
            "curr_miss": curr_miss[num],
            "wave_deficit": wave_deficit,
            "zod_deficit": zod_deficit,
            "is_prev_sp": num == prev_special,
            "is_prev_fl": num in prev_flats,
        })
    return features


def score_numbers_for_next_draw(
    sub_records: list,
    default_yz: str,
    w_omission: float = 1.0,
    w_balance: float = 1.0,
    w_penalty: float = 1.0,
) -> list:
    feats = extract_step_features(sub_records, default_yz)
    scored = []
    for f in feats:
        total_score = round(
            50.0 + f["base_omission"] * w_omission + f["base_balance"] * w_balance - f["raw_penalty"] * w_penalty,
            2
        )
        reasons = []
        if f["curr_miss"] >= 49:
            reasons.append(f"遗漏{f['curr_miss']}期(超均值)")
        elif f["curr_miss"] >= 30:
            reasons.append(f"遗漏{f['curr_miss']}期")
        if f["wave_deficit"] > 0.05:
            reasons.append(f"{f['wave']}偏冷回补")
        if f["zod_deficit"] > 0.03:
            reasons.append(f"{f['zodiac']}肖偏冷")
        if f["is_prev_sp"]:
            reasons.append("上期特码降权")
        elif f["is_prev_fl"]:
            reasons.append("上期平码降权")

        scored.append({
            "num": f["num"],
            "score": total_score,
            "wave": f["wave"],
            "zodiac": f["zodiac"],
            "big_small": f["big_small"],
            "odd_even": f["odd_even"],
            "tail": f["tail"],
            "curr_miss": f["curr_miss"],
            "reasons": " / ".join(reasons) if reasons else "均衡常规态",
        })

    scored.sort(key=lambda x: (-x["score"], -x["curr_miss"], x["num"]))
    return scored


def backtest_prediction_model(
    records: list,
    default_yz: str,
    w_omission: float = 1.0,
    w_balance: float = 1.0,
    w_penalty: float = 1.0,
) -> dict:
    if len(records) < 15:
        return {}
    start_idx = max(10, len(records) - 60)
    hits_12, hits_24, safe_excl_10 = 0, 0, 0
    eval_count = 0

    for i in range(start_idx, len(records) - 1):
        ranked = score_numbers_for_next_draw(
            records[:i+1], default_yz,
            w_omission=w_omission, w_balance=w_balance, w_penalty=w_penalty
        )
        top12 = {x["num"] for x in ranked[:12]}
        top24 = {x["num"] for x in ranked[:24]}
        bot10 = {x["num"] for x in ranked[-10:]}

        actual_next = records[i + 1]["special"]
        if actual_next in top12:
            hits_12 += 1
        if actual_next in top24:
            hits_24 += 1
        if actual_next not in bot10:
            safe_excl_10 += 1
        eval_count += 1

    return {
        "eval_count": eval_count,
        "rate_12": round(hits_12 / eval_count * 100, 1),
        "theory_12": round(12 / 49 * 100, 1),
        "rate_24": round(hits_24 / eval_count * 100, 1),
        "theory_24": round(24 / 49 * 100, 1),
        "safe_10": round(safe_excl_10 / eval_count * 100, 1),
        "theory_safe_10": round(39 / 49 * 100, 1),
    }


def optimize_weights_grid_search(records: list, default_yz: str) -> dict:
    """
    预提取每期特征向量，高速遍历 100 组权重组合，寻找历史回测综合得分最优参数
    """
    if len(records) < 15:
        return {}
    start_idx = max(10, len(records) - 60)
    cached_steps = []
    for i in range(start_idx, len(records) - 1):
        feats = extract_step_features(records[:i+1], default_yz)
        actual_next = records[i + 1]["special"]
        cached_steps.append((feats, actual_next))

    eval_count = len(cached_steps)
    om_grid = [0.0, 0.5, 1.0, 1.5, 2.2]
    bal_grid = [0.0, 0.5, 1.0, 1.5, 2.2]
    pen_grid = [0.0, 0.5, 1.0, 2.0]

    best_result = None
    best_objective = -1.0

    for w_om, w_bal, w_pen in itertools.product(om_grid, bal_grid, pen_grid):
        h12, h24, s10 = 0, 0, 0
        for feats, actual_next in cached_steps:
            # 快速排序
            ranked_nums = sorted(
                feats,
                key=lambda f: (
                    -(f["base_omission"] * w_om + f["base_balance"] * w_bal - f["raw_penalty"] * w_pen),
                    -f["curr_miss"],
                    f["num"]
                )
            )
            top12 = {x["num"] for x in ranked_nums[:12]}
            top24 = {x["num"] for x in ranked_nums[:24]}
            bot10 = {x["num"] for x in ranked_nums[-10:]}

            if actual_next in top12:
                h12 += 1
            if actual_next in top24:
                h24 += 1
            if actual_next not in bot10:
                s10 += 1

        r12 = h12 / eval_count * 100
        r24 = h24 / eval_count * 100
        rs10 = s10 / eval_count * 100

        # 综合目标函数：兼顾 Top12 精选命中率、Top24 大底命中率与排除安全率
        objective = r12 * 1.5 + r24 * 1.0 + rs10 * 0.5
        if objective > best_objective:
            best_objective = objective
            best_result = {
                "w_omission": w_om,
                "w_balance": w_bal,
                "w_penalty": w_pen,
                "rate_12": round(r12, 1),
                "rate_24": round(r24, 1),
                "safe_10": round(rs10, 1),
                "eval_count": eval_count,
            }

    return best_result


# ==========================================
# 4. 侧边栏：数据录入、口径切换与清空管理
# ==========================================
with st.sidebar:
    st.header("📥 1. 录入开奖数据")
    default_yz = st.selectbox(
        "当前年份生肖（跨年可在行内标注 [蛇]）：",
        options=ZODIAC_ORDER,
        index=ZODIAC_ORDER.index(DEFAULT_YEAR_ZODIAC)
    )

    raw_paste_text = st.text_area(
        "粘贴最新开奖记录（每行一期，自动去重）：",
        height=150,
        placeholder="示例：\n2026311期: 04, 11, 22, 29, 35, 41 特 17\n2025360期 [蛇]: 02, 11, 19, 25, 37, 43 特 17"
    )
    if st.button("🚀 解析并追加到本地库", use_container_width=True):
        if raw_paste_text.strip():
            added_c, dup_c, fail_c = append_text_to_db(raw_paste_text, default_yz)
            st.success(f"入库完成！新增 {added_c} 期，跳过重复 {dup_c} 期，格式错误 {fail_c} 行。")
            if added_c > 0:
                st.rerun()
        else:
            st.warning("请先粘贴开奖文本。")

    st.divider()
    st.header("⚙️ 2. 统计口径与库管理")
    stat_mode = st.radio(
        "选择统计范围：",
        options=["special_only", "all_balls"],
        format_func=lambda x: "仅统计特码 (1球/期)" if x == "special_only" else "全码统计 (6平码 + 1特码)"
    )

    if os.path.isfile(LOCAL_DB_FILE):
        if st.button("🗑️ 清空本地历史数据库", use_container_width=True):
            os.remove(LOCAL_DB_FILE)
            st.warning("本地历史库已清空，请重新导入数据。")
            st.rerun()

# ==========================================
# 5. 加载历史数据
# ==========================================
uploaded_file = st.file_uploader("👉 上传开奖记录表格 (.csv / .xlsx，导入一次后自动永久本地存档)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        parsed_records = parse_uploaded_table(uploaded_file, default_yz)
        if len(parsed_records) >= 1:
            save_to_local_db(parsed_records)
            st.success(f"✅ 成功解析并更新本地数据库，共载入 {len(parsed_records)} 期记录！")
    except Exception as e:
        st.error(f"❌ 解析上传表格失败: {e}")
        st.stop()
else:
    parsed_records = load_from_local_db()

if not parsed_records:
    st.info("👋 当前暂无历史数据。请在左侧边栏粘贴开奖文本并点击「解析并追加到本地库」，或直接在上方上传 `.csv` / `.xlsx` 表格。")
    st.stop()

# ==========================================
# 6. 多维核心指标计算引擎
# ==========================================
total_draws = len(parsed_records)
latest_yz = parsed_records[-1].get("year_zodiac", default_yz)
has_flats_available = any(r.get("flats") is not None for r in parsed_records)

if stat_mode == "all_balls" and not has_flats_available:
    st.warning("⚠️ 当前数据仅包含特码，已自动切换为「仅统计特码」模式。")
    stat_mode = "special_only"

freq_counter = Counter()
wave_counter = Counter()
zodiac_counter = Counter()
tail_counter = Counter()
bs_counter = Counter()
oe_counter = Counter()
zodiac_pool_sum = Counter()

curr_missing = {num: 0 for num in range(1, 50)}
max_missing = {num: 0 for num in range(1, 50)}

tail_curr_missing = {t: 0 for t in range(10)}
zodiac_curr_missing = {z: 0 for z in ZODIAC_ORDER}

bs_categories = ["小(01-24)", "大(25-48)", "和(49)"]
bs_curr_missing = {k: 0 for k in bs_categories}
bs_max_missing = {k: 0 for k in bs_categories}

oe_categories = ["单", "双", "和(49)"]
oe_curr_missing = {k: 0 for k in oe_categories}
oe_max_missing = {k: 0 for k in oe_categories}

for draw in parsed_records:
    draw_yz = draw.get("year_zodiac", default_yz)
    z_map = get_zodiac_map(draw_yz)

    for z in ZODIAC_ORDER:
        zodiac_pool_sum[z] += 5 if z == draw_yz else 4

    if stat_mode == "all_balls" and draw.get("flats"):
        target_balls = draw["flats"] + [draw["special"]]
    else:
        target_balls = [draw["special"]]

    drawn_set = set(target_balls)
    drawn_tails = set()
    drawn_zodiacs = set()
    drawn_bs = set()
    drawn_oe = set()

    for ball in target_balls:
        freq_counter[ball] += 1
        wave_counter[get_wave_color(ball)] += 1
        z = z_map[ball]
        t = ball % 10
        bs = get_big_small(ball)
        oe = get_odd_even(ball)

        zodiac_counter[z] += 1
        tail_counter[t] += 1
        bs_counter[bs] += 1
        oe_counter[oe] += 1

        drawn_zodiacs.add(z)
        drawn_tails.add(t)
        drawn_bs.add(bs)
        drawn_oe.add(oe)

    for num in range(1, 50):
        if num in drawn_set:
            curr_missing[num] = 0
        else:
            curr_missing[num] += 1
            max_missing[num] = max(max_missing[num], curr_missing[num])

    for t in range(10):
        tail_curr_missing[t] = 0 if t in drawn_tails else tail_curr_missing[t] + 1
    for z in ZODIAC_ORDER:
        zodiac_curr_missing[z] = 0 if z in drawn_zodiacs else zodiac_curr_missing[z] + 1

    for k in bs_categories:
        if k in drawn_bs:
            bs_curr_missing[k] = 0
        else:
            bs_curr_missing[k] += 1
            bs_max_missing[k] = max(bs_max_missing[k], bs_curr_missing[k])

    for k in oe_categories:
        if k in drawn_oe:
            oe_curr_missing[k] = 0
        else:
            oe_curr_missing[k] += 1
            oe_max_missing[k] = max(oe_max_missing[k], oe_curr_missing[k])

total_balls_counted = sum(freq_counter.values())
latest_z_map = get_zodiac_map(latest_yz)

rows_49 = []
for num in range(1, 50):
    cnt = freq_counter[num]
    rows_49.append({
        "号码": f"{num:02d}",
        "波色": get_wave_color(num),
        "当前生肖": latest_z_map[num],
        "尾数": num % 10,
        "大小": get_big_small(num),
        "单双": get_odd_even(num),
        "历史出现次数": cnt,
        "单期出现率(%)": round((cnt / total_draws) * 100, 2),
        "当前遗漏期数": curr_missing[num],
        "历史最大遗漏": max_missing[num],
    })
df_49 = pd.DataFrame(rows_49)

# ==========================================
# 7. 顶部核心 KPI 概览
# ==========================================
k1, k2, k3, k4 = st.columns(4)
k1.metric("历史样本总期数", f"{total_draws} 期", f"范围: {parsed_records[0]['issue']} -> {parsed_records[-1]['issue']}")
k2.metric("统计号码总球数", f"{total_balls_counted} 个", "仅特码" if stat_mode == "special_only" else "6平码+1特码")
k3.metric("最新一期特码", f"{parsed_records[-1]['special']:02d} ({parsed_records[-1]['special_zodiac']})", f"{get_wave_color(parsed_records[-1]['special'])} | {get_big_small(parsed_records[-1]['special'])}")
k4.metric("当前生肖基准", f"{latest_yz}年", "本命5码: 01,13,25,37,49")

st.divider()

# ==========================================
# 8. 🔮 自定义权重量化评分与自动寻优预测模块
# ==========================================
st.subheader("🔮 下一期多维量化评分与参考选号池（支持实时权重调节与自动寻优）")
st.caption("⚠️ 客观提示：摇奖本质为独立随机事件，历史回测最优权重不代表未来必然延续，以下号码池仅供统计分析参考。")

# 初始化 session_state 权重默认值
if "w_omission_val" not in st.session_state:
    st.session_state["w_omission_val"] = 1.0
if "w_balance_val" not in st.session_state:
    st.session_state["w_balance_val"] = 1.0
if "w_penalty_val" not in st.session_state:
    st.session_state["w_penalty_val"] = 1.0
if "opt_banner_msg" not in st.session_state:
    st.session_state["opt_banner_msg"] = ""

# 寻优与重置操作栏
opt_col1, opt_col2, opt_col3 = st.columns([1.2, 1.2, 3.6])
with opt_col1:
    if st.button("⚡ 一键自动寻优权重", use_container_width=True, type="primary"):
        if len(parsed_records) < 15:
            st.warning("⚠️ 历史样本不足 15 期，暂无法执行自动回测寻优，请先录入更多历史数据。")
        else:
            with st.spinner("正在遍历 100 组权重组合进行历史回测寻优..."):
                best_opt = optimize_weights_grid_search(parsed_records, default_yz)
                if best_opt:
                    st.session_state["w_omission_val"] = best_opt["w_omission"]
                    st.session_state["w_balance_val"] = best_opt["w_balance"]
                    st.session_state["w_penalty_val"] = best_opt["w_penalty"]
                    st.session_state["opt_banner_msg"] = (
                        f"✅ 自动寻优完成！基于近 {best_opt['eval_count']} 期回测，已自动填入最优权重："
                        f"**遗漏回补 = `{best_opt['w_omission']}`** ｜ "
                        f"**属性冷偏 = `{best_opt['w_balance']}`** ｜ "
                        f"**防连庄阻尼 = `{best_opt['w_penalty']}`** "
                        f"（历史回测 Top12 命中率 **{best_opt['rate_12']}%**，Top24 命中率 **{best_opt['rate_24']}%**）"
                    )
                    st.rerun()

with opt_col2:
    if st.button("🔄 重置默认权重 (1.0)", use_container_width=True):
        st.session_state["w_omission_val"] = 1.0
        st.session_state["w_balance_val"] = 1.0
        st.session_state["w_penalty_val"] = 1.0
        st.session_state["opt_banner_msg"] = ""
        st.rerun()

with opt_col3:
    if st.session_state["opt_banner_msg"]:
        st.success(st.session_state["opt_banner_msg"])

# 三个实时权重调节滑动条（绑定 session_state）
w_col1, w_col2, w_col3 = st.columns(3)
with w_col1:
    w_omission = st.slider(
        "⏳ 遗漏回补权重（欲出率倍率）",
        min_value=0.0, max_value=3.0, step=0.1,
        key="w_omission_val",
        help="调高会更偏向长期未开出的大遗漏冷号；设为 0 则不考虑单码遗漏期数。"
    )
with w_col2:
    w_balance = st.slider(
        "⚖️ 属性冷偏补偿权重（波色/大小/生肖平衡倍率）",
        min_value=0.0, max_value=3.0, step=0.1,
        key="w_balance_val",
        help="调高会优先加权近期开出偏少的波色、大小、单双及生肖属性。"
    )
with w_col3:
    w_penalty = st.slider(
        "🛡️ 防连庄阻尼力度（上期特码/平码减分倍率）",
        min_value=0.0, max_value=3.0, step=0.1,
        key="w_penalty_val",
        help="控制对上期刚开出的特码与平码的降权强度，设为 0 则不惩罚重复号码。"
    )

ranked_next = score_numbers_for_next_draw(
    parsed_records, default_yz,
    w_omission=w_omission, w_balance=w_balance, w_penalty=w_penalty
)
bt_res = backtest_prediction_model(
    parsed_records, default_yz,
    w_omission=w_omission, w_balance=w_balance, w_penalty=w_penalty
)

if bt_res:
    b1, b2, b3 = st.columns(3)
    b1.metric(
        f"当前权重下近 {bt_res['eval_count']} 期 Top 12 命中率",
        f"{bt_res['rate_12']}%",
        f"随机理论均值: {bt_res['theory_12']}%"
    )
    b2.metric(
        f"当前权重下近 {bt_res['eval_count']} 期 Top 24 命中率",
        f"{bt_res['rate_24']}%",
        f"随机理论均值: {bt_res['theory_24']}%"
    )
    b3.metric(
        f"当前权重下近 {bt_res['eval_count']} 期末位 10 码排除安全率",
        f"{bt_res['safe_10']}%",
        f"随机理论均值: {bt_res['theory_safe_10']}%"
    )

p_col1, p_col2, p_col3 = st.columns(3)
top12_nums = sorted([f"{x['num']:02d}" for x in ranked_next[:12]])
top24_nums = sorted([f"{x['num']:02d}" for x in ranked_next[:24]])
bot10_nums = sorted([f"{x['num']:02d}" for x in ranked_next[-10:]])

with p_col1:
    st.success("🎯 **核心精选参考池（综合评分 Top 12 码）**")
    st.code(", ".join(top12_nums), language="text")
with p_col2:
    st.info("🛡️ **稳健大底参考池（综合评分 Top 24 码）**")
    st.code(", ".join(top24_nums), language="text")
with p_col3:
    st.error("🚫 **过热/防重排除参考池（综合评分末位 10 码）**")
    st.code(", ".join(bot10_nums), language="text")

with st.expander("📋 查看 1-49 号码下一期综合评分明细排行榜"):
    df_rank = pd.DataFrame([
        {
            "综合排名": f"第 {idx} 名",
            "号码": f"{x['num']:02d}",
            "综合得分": x["score"],
            "波色": x["wave"],
            "生肖": x["zodiac"],
            "大小": x["big_small"],
            "单双": x["odd_even"],
            "当前遗漏": f"{x['curr_miss']} 期",
            "评分依据": x["reasons"],
        }
        for idx, x in enumerate(ranked_next, 1)
    ])
    st.dataframe(df_rank, use_container_width=True, hide_index=True)

st.divider()

# ==========================================
# 9. 交互式组合条件筛选器
# ==========================================
st.subheader("🔍 交互式组合条件筛选器（实时滤码 & 一键复制）")

fc1, fc2, fc3, fc4, fc5, fc6 = st.columns(6)
with fc1:
    sel_waves = st.multiselect("波色（不选则不限）", ["红波", "蓝波", "绿波"])
with fc2:
    sel_bs = st.multiselect("大小（不选则不限）", ["小(01-24)", "大(25-48)", "和(49)"])
with fc3:
    sel_oe = st.multiselect("单双（不选则不限）", ["单", "双", "和(49)"])
with fc4:
    sel_zodiacs = st.multiselect("当前生肖（不选则不限）", ZODIAC_ORDER)
with fc5:
    sel_tails = st.multiselect("尾数（不选则不限）", list(range(10)))
with fc6:
    min_miss = st.number_input("当前遗漏期数 >=", min_value=0, max_value=1000, value=0, step=1)

filtered_df = df_49.copy()
if sel_waves:
    filtered_df = filtered_df[filtered_df["波色"].isin(sel_waves)]
if sel_bs:
    filtered_df = filtered_df[filtered_df["大小"].isin(sel_bs)]
if sel_oe:
    filtered_df = filtered_df[filtered_df["单双"].isin(sel_oe)]
if sel_zodiacs:
    filtered_df = filtered_df[filtered_df["当前生肖"].isin(sel_zodiacs)]
if sel_tails:
    filtered_df = filtered_df[filtered_df["尾数"].isin(sel_tails)]
if min_miss > 0:
    filtered_df = filtered_df[filtered_df["当前遗漏期数"] >= min_miss]

filtered_df = filtered_df.sort_values(by=["当前遗漏期数", "历史最大遗漏"], ascending=[False, False])

matched_nums = filtered_df["号码"].tolist()
st.success(f"🎯 **共筛选出 `{len(matched_nums)}` 个符合条件的号码（点击右侧图标一键复制）：**")
st.code(", ".join(matched_nums) if matched_nums else "无符合条件的号码，请放宽上方筛选条件", language="text")

st.dataframe(filtered_df, use_container_width=True, hide_index=True)

csv_export = filtered_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 导出当前筛选明细为 Excel / CSV",
    data=csv_export,
    file_name="filtered_numbers_report.csv",
    mime="text/csv",
)

st.divider()

# ==========================================
# 10. 全维度历史分布与遗漏对比看板
# ==========================================
st.subheader("📈 各维度历史分布与遗漏深度对比")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "大小 & 单双 & 波色",
    "12生肖跨年精准分布",
    "0-9 尾数分布",
    "49码完整冷热遗漏总表",
    "最近 20 期开奖记录"
])

with tab1:
    c_bs, c_oe, c_wv = st.columns(3)
    with c_bs:
        st.markdown("##### 大小分布（1-24小 / 25-48大 / 49和）")
        theory_bs = {"小(01-24)": 24 / 49, "大(25-48)": 24 / 49, "和(49)": 1 / 49}
        df_bs = pd.DataFrame([
            {
                "类型": k,
                "次数": bs_counter[k],
                "实际占比(%)": round(bs_counter[k] / total_balls_counted * 100, 2),
                "理论占比(%)": round(theory_bs[k] * 100, 2),
                "当前遗漏": bs_curr_missing[k],
                "最大遗漏": bs_max_missing[k],
            }
            for k in bs_categories
        ])
        st.bar_chart(df_bs.set_index("类型")[["实际占比(%)", "理论占比(%)"]])
        st.dataframe(df_bs, use_container_width=True, hide_index=True)

    with c_oe:
        st.markdown("##### 单双分布（49独立计和）")
        theory_oe = {"单": 24 / 49, "双": 24 / 49, "和(49)": 1 / 49}
        df_oe = pd.DataFrame([
            {
                "类型": k,
                "次数": oe_counter[k],
                "实际占比(%)": round(oe_counter[k] / total_balls_counted * 100, 2),
                "理论占比(%)": round(theory_oe[k] * 100, 2),
                "当前遗漏": oe_curr_missing[k],
                "最大遗漏": oe_max_missing[k],
            }
            for k in oe_categories
        ])
        st.bar_chart(df_oe.set_index("类型")[["实际占比(%)", "理论占比(%)"]])
        st.dataframe(df_oe, use_container_width=True, hide_index=True)

    with c_wv:
        st.markdown("##### 波色分布（红17 / 蓝16 / 绿16）")
        theory_wv = {"红波": 17 / 49, "蓝波": 16 / 49, "绿波": 16 / 49}
        df_wv = pd.DataFrame([
            {
                "波色": w,
                "次数": wave_counter[w],
                "实际占比(%)": round(wave_counter[w] / total_balls_counted * 100, 2),
                "理论占比(%)": round(theory_wv[w] * 100, 2),
                "偏差(%)": round((wave_counter[w] / total_balls_counted - theory_wv[w]) * 100, 2),
            }
            for w in ["红波", "蓝波", "绿波"]
        ])
        st.bar_chart(df_wv.set_index("波色")[["实际占比(%)", "理论占比(%)"]])
        st.dataframe(df_wv, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("##### 12 生肖跨农历年精准分布（按每期开奖当年实际生肖动态累计）")
    df_z = pd.DataFrame([
        {
            "生肖": z,
            "当前码数": 5 if z == latest_yz else 4,
            "出现次数": zodiac_counter[z],
            "实际占比(%)": round(zodiac_counter[z] / total_balls_counted * 100, 2),
            "加权理论占比(%)": round(zodiac_pool_sum[z] / (total_draws * 49) * 100, 2),
            "当前遗漏期数": zodiac_curr_missing[z],
        }
        for z in ZODIAC_ORDER
    ])
    st.bar_chart(df_z.set_index("生肖")[["实际占比(%)", "加权理论占比(%)"]])
    st.dataframe(df_z, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("##### 0-9 尾数分布与当前遗漏")
    df_t = pd.DataFrame([
        {
            "尾数": f"{t}尾",
            "包含码数": 4 if t == 0 else 5,
            "出现次数": tail_counter[t],
            "实际占比(%)": round(tail_counter[t] / total_balls_counted * 100, 2),
            "理论占比(%)": round((4 if t == 0 else 5) / 49 * 100, 2),
            "当前遗漏期数": tail_curr_missing[t],
        }
        for t in range(10)
    ])
    st.bar_chart(df_t.set_index("尾数")[["实际占比(%)", "理论占比(%)"]])
    st.dataframe(df_t, use_container_width=True, hide_index=True)

with tab4:
    st.markdown("##### 1-49 号码全维度统计总表（点击列标题可自由升降序排列）")
    st.dataframe(df_49, use_container_width=True, hide_index=True)

with tab5:
    st.markdown("##### 最近 20 期历史开奖明细")
    recent_rows = []
    for d in reversed(parsed_records[-20:]):
        sp = d["special"]
        recent_rows.append({
            "期号": d["issue"],
            "年份生肖": d.get("year_zodiac", latest_yz),
            "平码": " - ".join([f"{x:02d}" for x in d["flats"]]) if d.get("flats") else "无平码",
            "特码": f"{sp:02d}",
            "特码生肖": d.get("special_zodiac", get_zodiac_map(d.get("year_zodiac", latest_yz))[sp]),
            "波色": get_wave_color(sp),
            "大小": get_big_small(sp),
            "单双": get_odd_even(sp),
        })
    st.dataframe(pd.DataFrame(recent_rows), use_container_width=True, hide_index=True)
