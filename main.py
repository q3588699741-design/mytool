import streamlit as st
import pandas as pd
from collections import defaultdict

# 页面基础配置
st.set_page_config(page_title="开奖特征自动统计工具", layout="wide")
st.title("📊 开奖记录序列特征自动统计与推荐工具 (升级版)")
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
        max_tail_pred = {}     # 存放最高频尾数
        appear_tail_pred = {}  # 存放所有出现过的尾数
        tail_table_data = []
        
        for tail in range(10):
            nexts = tail_transitions[tail]
            total = len(nexts)
            counts = defaultdict(int)
            for n in nexts:
                counts[n] += 1
            
            # 计算最高频和所有出现过
            max_count = max(counts.values()) if counts else 0
            max_tail_pred[tail] = [t for t, c in counts.items() if c == max_count] if counts else []
            appear_tail_pred[tail] = [t for t, c in counts.items() if c > 0]
            
            prob_parts = []
            for t in all_tails:
                cnt = counts[t]
                prob = (cnt / total * 100) if total > 0 else 0.0
                prob_parts.append((t, cnt, prob))
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
        max_zodiac_pred = {}     # 存放最高频生肖
        appear_zodiac_pred = {}  # 存放所有出现过的生肖
        zodiac_table_data = []
        
        for zodiac in all_zodiacs:
            nexts = zodiac_transitions[zodiac]
            total = len(nexts)
            counts = defaultdict(int)
            for n in nexts:
                counts[n] += 1
                
            max_count = max(counts.values()) if counts else 0
            max_zodiac_pred[zodiac] = [z for z, c in counts.items() if c == max_count] if counts else []
            appear_zodiac_pred[zodiac] = [z for z, c in counts.items() if c > 0]
            
            prob_parts = []
            for z in all_zodiacs:
                cnt = counts[z]
                prob = (cnt / total * 100) if total > 0 else 0.0
                prob_parts.append((z, cnt, prob))
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
        
        # 🌟 核心升级：增加模式选择器
        predict_mode = st.radio(
            "🛠️ **请选择预测合并模式：**",
            ["🔥 容错模式（大网拦截：只要历史出现过、概率 > 0% 的条件全部组合）", 
             "⚡ 精选模式（精准打击：仅组合历史开出频次最高、并列第一的条件）"],
            index=0
        )
        
        # 获取最新开奖数据
        last_num, last_zodiac = parsed_data[-1]
        last_tail = last_num % 10
        
        st.markdown(f"📋 **最新一期（表格最后一行）**：号码 `**{last_num}**` ，生肖 `**{last_zodiac}**`（尾数 `{last_tail}`）")
        
        # 根据用户选择的模式切换过滤池
        if "容错模式" in predict_mode:
            target_tails = appear_tail_pred.get(last_tail, [])
            target_zodiacs = appear_zodiac_pred.get(last_zodiac, [])
            mode_text = "历史所有出现过"
        else:
            target_tails = max_tail_pred.get(last_tail, [])
            target_zodiacs = max_zodiac_pred.get(last_zodiac, [])
            mode_text = "历史最高频"
        
        # 渲染预测依据提示
        tail_tips = "、".join([f"{t}尾" for t in sorted(target_tails)])
        zodiac_tips = "、".join(target_zodiacs)
        
        p_col1, p_col2 = st.columns(2)
        p_col1.info(f"💡 依据【{mode_text}】：**{last_tail}尾** 下期可开出尾数 → **{tail_tips}**")
        p_col2.info(f"💡 依据【{mode_text}】：**{last_zodiac}** 下期可开出生肖 → **{zodiac_tips}**")
        
        # 扫描 1-49 号码库
        matched_numbers = []
        for n in range(1, 49 + 1):
            n_tail = n % 10
            n_zodiac = get_zodiac_of_number(n)
            
            # 双条件交叉验证
            if (n_tail in target_tails) and (n_zodiac in target_zodiacs):
                matched_numbers.append(f"{n:02d}")
        
        # 格式化输出
        if matched_numbers:
            st.success(f"🏁 **最终筛选：同时满足两项条件的号码共 {len(matched_numbers)} 个（已从小到大严格排序）**")
            st.markdown("👇 **请点击下方代码框右上角的图标，即可一键复制全部号码：**")
            
            copy_string = ", ".join(matched_numbers)
            st.code(copy_string, language="text")
        else:
            st.warning("⚠️ 提示：在此过滤条件下没有重合号码。")
