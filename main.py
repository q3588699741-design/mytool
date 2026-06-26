import streamlit as st
import pandas as pd
from collections import defaultdict

# 页面基础配置
st.set_page_config(page_title="数据全维度智能统计看板", layout="wide")
st.title("📊 开奖记录全维度综合统计看板")

# 1. 配置文件上传组件
uploaded_file = st.file_uploader("👉 上传最新开奖记录表格 (.csv/.xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # 自动读取
    df = pd.read_csv(uploaded_file, header=None) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file, header=None)
    df = df.dropna()
    
    parsed_data = []
    for idx, row in df.iterrows():
        try:
            num = int(row[0])
            zodiac = str(row[1]).strip()
            parsed_data.append((num, zodiac))
        except: continue
            
    total_records = len(parsed_data)
    if total_records < 2:
        st.error("数据不足")
    else:
        all_tails = list(range(10))
        all_zodiacs = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']

        tab1, tab2, tab3 = st.tabs(["🔥 大盘总量冷热", "⏳ 当前未出遗漏 (号码/生肖/尾数)", "🔄 前后行状态转移"])

        # TAB 2: 遗漏统计
        with tab2:
            st.subheader("⏳ 当前最新一期各指标遗漏统计")
            
            # --- 计算遗漏算法 ---
            def get_omission(items, data_type):
                omission = {}
                for item in items:
                    found = False
                    for i in range(total_records - 1, -1, -1):
                        val = (parsed_data[i][0] % 10) if data_type == 'tail' else (parsed_data[i][0] if data_type == 'num' else parsed_data[i][1])
                        if val == item:
                            omission[item] = (total_records - 1) - i
                            found = True
                            break
                    if not found: omission[item] = total_records
                return omission

            # 1. 号码遗漏 2. 生肖遗漏 3. 尾数遗漏
            num_omission = get_omission(range(1, 50), 'num')
            zodiac_omission = get_omission(all_zodiacs, 'zodiac')
            tail_omission = get_omission(all_tails, 'tail')

            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.markdown("### 🔢 号码遗漏")
                sorted_num = sorted(num_omission.items(), key=lambda x: (-x[1], x[0]))
                md = "| 号码 | 遗漏期 | 状态 |\n| :---: | :---: | :---: |\n"
                for n, m in sorted_num:
                    md += f"| **{n:02d}** | {m} | {'🎯' if m==0 else ('⚠️' if m>=10 else '正常')} |\n"
                st.markdown(md)
            
            with c2:
                st.markdown("### 🔮 生肖遗漏")
                sorted_zod = sorted(zodiac_omission.items(), key=lambda x: (-x[1], all_zodiacs.index(x[0])))
                md = "| 生肖 | 遗漏期 | 状态 |\n| :---: | :---: | :---: |\n"
                for z, m in sorted_zod:
                    md += f"| **{z}** | {m} | {'🎯' if m==0 else ('⚠️' if m>=5 else '正常')} |\n"
                st.markdown(md)

            with c3:
                st.markdown("### 🎯 尾数遗漏")
                sorted_tail = sorted(tail_omission.items(), key=lambda x: (-x[1], x[0]))
                md = "| 尾数 | 遗漏期 | 状态 |\n| :---: | :---: | :---: |\n"
                for t, m in sorted_tail:
                    md += f"| **{t}尾** | {m} | {'🎯' if m==0 else ('⚠️' if m>=8 else '正常')} |\n"
                st.markdown(md)
