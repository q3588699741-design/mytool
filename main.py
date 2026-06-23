import streamlit as st
import pandas as pd
from collections import defaultdict

# 页面基础配置
st.set_page_config(page_title="开奖特征自动统计工具", layout="wide")
st.title("📊 开奖记录序列特征自动统计与推荐工具")
st.caption("支持一键上传最新的中奖记录表格，全自动双重概率池对齐交叉预测")

# 1. 配置文件上传组件
uploaded_file = st.file_uploader("👉 请上传最新的开奖记录表格 (支持 .csv 或 .xlsx 格式)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # 2. 自动兼容读取 CSV 或 Excel
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, header=None)
    else:
        df = pd.read_excel(uploaded_file, header=None)
    
    # 清洗并解析数据 (默认第一列为号码，第二列为生肖)
    df = df.dropna()
    parsed_data = []
    for idx, row in df.iterrows():
        try:
            num = int(row[0])
            zodiac = str(row[1]).strip()
            parsed_data.append((num, zodiac))
        except:
            continue
            
    if len(parsed_data) < 2:
        st.error("❌ 表格内有效数据行数不足，无法进行前后行规律统计！")
    else:
        # 定义全局标准集合
        all_tails = list(range(10))
        all_zodiacs = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
        
        # 2026年岁次丙午马年 1-49 号码生肖对照基准 (1=马, 2=蛇, 3=龙...)
        base_zodiacs = ['马', '蛇', '龙', '兔', '虎', '牛', '鼠', '猪', '狗', '鸡', '猴', '羊']
        def get_zodiac_of_number(n):
            return base_zodiacs[(n - 1) % 12]

        # 3. 核心统计逻辑：前后行状态转移
        tail_transitions = defaultdict(list)
        zodiac_transitions = defaultdict(list)
        
        for i in range(len(parsed_data) - 1):
            curr_tail = parsed_data[i][0] % 10
            next_tail = parsed_data[i+1][0] % 10
            tail_transitions[curr_tail].append(next_tail)
            
            curr_zodiac = parsed_data[i][1]
            next_zodiac = parsed_data[i+1][1]
            zodiac_transitions[curr_zodiac].append(next_zodiac)
            
        # 创建两列布局展示完整分布表
        col1, col2 = st.columns(2)
        
        # --- 模块一：尾数概率计算 ---
        best_tail_pred = {}
        tail_table_data = []
        for tail in range(10):
            nexts = tail_transitions[tail]
            total = len(nexts)
            counts = defaultdict(int)
            for n in nexts:
                counts[n] += 1
            
            # 记录最大频次的尾数作为预测候选池
            max_count = max(counts.values()) if counts else 0
            best_tail_pred[tail] = [t for t, c in counts.items() if c == max_count] if counts else []
            
            prob_parts = []
            for t in all_tails:
                cnt = counts[t]
                prob = (cnt / total * 100) if total > 0 else 0.0
                prob_parts.append((t, cnt, prob))
            # 降序排列
            prob_parts.sort(key=lambda x: (-x[1], x[0]))
            prob_str = ", ".join([f"{t}尾: {p:.1f}%({c}次)" for t, c, p in prob_parts])
            
            tail_table_data.append({
                "当前尾数": f"{tail}尾",
                "历史出现总计": f"{total}次",
                "下一行尾数完整分布 (降序排列)": prob_str
            })
            
        with col1:
            st.subheader("🔢 1. 尾数 0-9 后各尾数完整概率分布")
            st.dataframe(pd.DataFrame(tail_table_data), use_container_width=True, hide_index=True)

        # --- 模块二：生肖概率计算 ---
        best_zodiac_pred = {}
        zodiac_table_data = []
        for zodiac in all_zodiacs:
            nexts = zodiac_transitions[zodiac]
            total = len(nexts)
            counts = defaultdict(int)
            for n in nexts:
                counts[n] += 1
                
            # 记录最大频次的生肖作为预测候选池
            max_count = max(counts.values()) if counts else 0
            best_zodiac_pred[zodiac] = [z for z, c in counts.items() if c == max_count] if counts else []
            
            prob_parts = []
            for z in all_zodiacs:
                cnt = counts[z]
                prob = (cnt / total * 100) if total > 0 else 0.0
                prob_parts.append((z, cnt, prob))
            # 降序排列
            prob_parts.sort(key=lambda x: (-x[1], all_zodiacs.index(x[0])))
            prob_str = ", ".join([f"{z}: {p:.1f}%({c}次)" for z, c, p in prob_parts])
            
            zodiac_table_data.append({
                "当前生肖": zodiac,
                "历史出现总计": f"{total}次",
                "下一行生肖完整分布 (降序排列)": prob_str
            })
            
        with col2:
            st.subheader("🔮 2. 各生肖后各生肖完整概率分布")
            st.dataframe(pd.DataFrame(zodiac_table_data), use_container_width=True, hide_index=True)

        # --- 模块三：自动交叉对齐号码推荐 ---
        st.write("---")
        st.subheader("🎯 3. 下期精准双条件重合号码预测")
        
        # 获取表格里最后一期的最新开奖数据
        last_num, last_zodiac = parsed_data[-1]
        last_tail = last_num % 10
        
        st.markdown(f"📋 **检测到表格最新一期结果**：号码为 `**{last_num}**` ，生肖为 `**{last_zodiac}**`（尾数为 `{last_tail}`）")
        
        # 提取高频池
        target_tails = best_tail_pred.get(last_tail, [])
        target_zodiacs = best_zodiac_pred.get(last_zodiac, [])
        
        # 渲染预测依据提示
        tail_tips = "、".join([f"{t}尾" for t in target_tails])
        zodiac_tips = "、".join(target_zodiacs)
        
        p_col1, p_col2 = st.columns(2)
        p_col1.info(f"💡 依据历史转换：**{last_tail}尾** 下期高频推荐开出 → **{tail_tips}**")
        p_col2.info(f"💡 依据历史转换：**{last_zodiac}** 下期高频推荐开出 → **{zodiac_tips}**")
        
        # 扫描 1-49 号码库，找出同时具备高频尾数和高频生肖的号码
        matched_numbers = []
        for n in range(1, 50):
            n_tail = n % 10
            n_zodiac = get_zodiac_of_number(n)
            
            if (n_tail in target_tails) and (n_zodiac in target_zodiacs):
                matched_numbers.append(f"{n:02d}({n_zodiac})")
        
        # 打印最终筛选出的推荐号码结果
        if matched_numbers:
            st.success(f"🏁 **最终筛选结果：同时满足上述两个最高概率分布的号码共 {len(matched_numbers)} 个**")
            # 用醒目的区块把号码排列展示
            st.markdown(
                f"<div style='background-color:#f0f2f6; padding:15px; border-radius:10px; font-size:24px; font-weight:bold; color:#ff4b4b; text-align:center; letter-spacing: 5px;'>"
                f"{' ｜ '.join(matched_numbers)}"
                f"</div>", 
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ 提示：当前两项最高概率条件没有重合的单个号码，你可以适当通过上方图表参考第二高频的特征做手动扩充。")
