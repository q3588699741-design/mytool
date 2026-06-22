import streamlit as st
import pandas as pd

# 页面基础配置 (手机自适应屏幕)
st.set_page_config(page_title="2026大盘量化操盘系统", layout="wide")
st.title("🦅 2026 大盘量化操盘系统 (AND/OR 二合一双阵型版)")
st.caption("核心战略：只吃当年局部热浪 | 兼顾【突击高盈亏比】与【四天一收网稳健复利】")

# 锁死 2026 马年核心生肖字典
ZODIAC_NUMBERS_2026 = {
    '马': [1, 13, 25, 37, 49], '蛇': [2, 14, 26, 38], '龙': [3, 15, 27, 39],
    '兔': [4, 16, 28, 40], '虎': [5, 17, 29, 41], '牛': [6, 18, 30, 42],
    '鼠': [7, 19, 31, 43], '猪': [8, 20, 32, 44], '狗': [9, 21, 33, 45],
    '鸡': [10, 22, 34, 46], '猴': [11, 23, 35, 47], '羊': [12, 24, 36, 48]
}

def get_zodiac_by_num(num):
    for zod, nums in ZODIAC_NUMBERS_2026.items():
        if num in nums:
            return zod
    return None

def get_top_n_with_ties(series, n=6):
    counts = series.value_counts()
    if len(counts) <= n:
        return list(counts.index), counts.to_dict()
    threshold = counts.iloc[n-1]
    allowed = list(counts[counts >= threshold].index)
    return allowed, counts.to_dict()

st.markdown("### 🕹️ 核心战术指挥部")
mode = st.radio("请选择今晚操盘布阵模式：", ["⚔️ AND 铁血尖刀流 (每天投·高盈亏比)", "📊 OR 权重得分流 (四天一收网·稳健版)"])

target_count = 40
if mode == "📊 OR 权重得分流 (四天一收网·稳健版)":
    target_count = st.slider("🎯 OR盘目标控码数 (默认40码)", min_value=30, max_value=45, value=40, step=1)

st.markdown("---")

uploaded_file = st.file_uploader("📥 请在手机端上传最新的《2026开奖更新.xlsx》", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=None)
        else:
            df = pd.read_excel(uploaded_file, header=None)
            
        df.columns = ['number', 'zodiac']
        df['tail'] = df['number'] % 10
        
        df['next_tail'] = df['tail'].shift(-1)
        df['next_zodiac'] = df['zodiac'].shift(-1)
        df_clean = df.dropna().copy()
        df_clean['next_tail'] = df_clean['next_tail'].astype(int)
        
        tails_map = {}
        tails_freq_raw = {}
        for t in range(10):
            allowed, freq_dict = get_top_n_with_ties(df_clean[df_clean['tail'] == t]['next_tail'], 6)
            tails_map[t] = allowed
            tails_freq_raw[t] = freq_dict
            
        zodiacs_map = {}
        zodiacs_freq_raw = {}
        for z in ZODIAC_NUMBERS_2026.keys():
            allowed, freq_dict = get_top_n_with_ties(df_clean[df_clean['zodiac'] == z]['next_zodiac'], 6)
            zodiacs_map[z] = allowed
            zodiacs_freq_raw[z] = freq_dict
            
        last_row = df.iloc[-1]
        last_num = int(last_row['number'])
        last_zodiac = last_row['zodiac']
        last_tail = int(last_row['tail'])
        
        st.markdown(f"📍 当前最新大盘坐标：上期开出 **{last_num:02d} ({last_zodiac})**")
        
        allowed_t = tails_map[last_tail]
        allowed_z = zodiacs_map[last_zodiac]
        
        if mode == "⚔️ AND 铁血尖刀流 (每天投·高盈亏比)":
            final_numbers = []
            for num in range(1, 50):
                t = num % 10
                z = get_zodiac_by_num(num)
                if (t in allowed_t) and (z in allowed_z):
                    final_numbers.append(f"{num:02d}")
            
            st.success(f"🔥 今晚 AND 阵型火力全开！共筛出 **{len(final_numbers)}** 个精尖特码：")
            st.code(", ".join(sorted(final_numbers)), language="text")
            st.info("💡 战术提示：此模式号码极度压缩（如今天仅 15 码），错一次亏得极少，中一次利润翻倍，适合日投碎单。")
            
        else:
            freq_t_dict = tails_freq_raw[last_tail]
            freq_z_dict = zodiacs_freq_raw[last_zodiac]
            
            qualified_pool = []
            for num in range(1, 50):
                t = num % 10
                z = get_zodiac_by_num(num)
                
                if (t in allowed_t) or (z in allowed_z):
                    score_tail = freq_t_dict.get(t, 0)
                    score_zodiac = freq_z_dict.get(z, 0)
                    total_score = score_tail + score_zodiac
                    identity = "双项全能 (AND)" if (t in allowed_t and z in allowed_z) else "单腿支撑 (OR)"
                    
                    qualified_pool.append({
                        "号码": f"{num:02d}",
                        "生肖": z,
                        "尾数": t,
                        "🔥 综合战功总得分": total_score,
                        "血统标签": identity
                    })
            
            pool_df = pd.DataFrame(qualified_pool)
            pool_df = pool_df.sort_values(by=["🔥 综合战功总得分", "号码"], ascending=[False, True]).reset_index(drop=True)
            
            final_elite_df = pool_df.head(target_count)
            final_numbers_list = sorted(final_elite_df["号码"].tolist())
            
            st.success(f"🎯 今晚 OR 权重阵型已就位！精准截取前 **{target_count}** 个黄金高分码：")
            st.code(", ".join(final_numbers_list), language="text")
            st.info(f"💡 战术提示：专为【四天一收网】深度定制。留下的这 {target_count} 码具备极高防御力，中奖即赚绝对净剩余！")
            
            with st.expander("📊 查看今晚全量号码战功得分大排队详情"):
                def color_row(row):
                    if row.name < target_count:
                        return ['background-color: rgba(40, 167, 69, 0.1)'] * len(row)
                    else:
                        return ['background-color: rgba(220, 53, 69, 0.1); color: gray; text-decoration: line-through'] * len(row)
                st.dataframe(pool_df.style.apply(color_row, axis=1), use_container_width=True)
                
    except Exception as e:
        st.error(f"💥 账本解析失败，错误原因: {str(e)}")
