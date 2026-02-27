import streamlit as st
import random
import math

# --- 1. ページ基本設定 ---
st.set_page_config(page_title="Textile Calc Pro", page_icon="🧵", layout="wide")

# カスタムCSSで見た目を整える
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div[data-testid="stExpander"] { background-color: #ffffff; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. サイドバー（設定・定数） ---
with st.sidebar:
    st.title("⚙️ 設定")
    case_weight = st.number_input("1ケースの重量 (kg)", value=22.68)
    loss_rate_percent = st.slider("ロス率 (%)", 0, 10, 2)
    loss_rate = 1 + (loss_rate_percent / 100)
    st.divider()
    st.caption("繊維実務 原価計算エンジン v2.0")

# --- 3. セッション管理 ---
if 'problem' not in st.session_state:
    st.session_state.problem = None

def generate_problem():
    num_rolls = random.randint(10, 30)
    weight_per_roll = random.randint(8, 12)
    total_raw_weight = num_rolls * weight_per_roll
    
    is_single = random.choice([True, False])
    if is_single:
        yarns = [{"name": "素材A", "p": 100, "price": random.randint(800, 1500)}]
    else:
        p1 = random.randint(30, 35)
        p2 = random.randint(30, 35)
        yarns = [
            {"name": "表糸", "p": p1, "price": random.randint(1000, 1500)},
            {"name": "中糸", "p": p2, "price": random.randint(800, 1200)},
            {"name": "裏糸", "p": 100 - p1 - p2, "price": random.randint(900, 1300)}
        ]
    
    knitting_fee = random.randint(150, 300)
    
    # 計算ロジック
    total_yarn_cost = 0
    steps = []
    steps.append(f"✅ **生機総重量**: {num_rolls}反 × {weight_per_roll}kg = {total_raw_weight}kg")
    
    for y in yarns:
        net = total_raw_weight * (y['p'] / 100) * loss_rate
        cases = math.ceil(net / case_weight)
        cost = cases * case_weight * y['price']
        total_yarn_cost += cost
        steps.append(f"🧵 **{y['name']}**: {net:.2f}kg必要 → {cases}ケース購入 ({cases * case_weight:.2f}kg) → {cost:,.0f}円")
        
    total_k_cost = total_raw_weight * knitting_fee
    grand_total = total_yarn_cost + total_k_cost
    final_unit_price = grand_total / total_raw_weight
    
    steps.append(f"⚙️ **編賃合計**: {total_raw_weight}kg × {knitting_fee}円 = {total_k_cost:,.0f}円")
    steps.append(f"📊 **最終コスト**: {grand_total:,.0f}円 ÷ {total_raw_weight}kg = **{final_unit_price:,.2f} 円/kg**")
    
    return {
        "num_rolls": num_rolls, "weight_per_roll": weight_per_roll, "total_raw": total_raw_weight,
        "yarns": yarns, "knitting_fee": knitting_fee, "answer": final_unit_price, "steps": steps
    }

# --- 4. メインコンテンツ ---
st.title("Textile Cost Simulator")
st.subheader("生機原価計算・特訓モード")

col_action, col_empty = st.columns([1, 2])
with col_action:
    if st.button("✨ 新規オーダーを生成", use_container_width=True):
        st.session_state.problem = generate_problem()
        st.session_state.answered = False

if st.session_state.problem:
    p = st.session_state.problem
    
    # オーダー概要をカードで表示
    st.markdown("### 📋 Order Specifications")
    c1, c2, c3 = st.columns(3)
    c1.metric("発注数", f"{p['num_rolls']} 反")
    c2.metric("1反重量", f"{p['weight_per_roll']} kg")
    c3.metric("編賃", f"{p['knitting_fee']} 円/kg")
    
    # 糸の情報を表示
    st.markdown("#### 🧵 糸構成（混率と単価）")
    y_cols = st.columns(len(p['yarns']))
    for i, y in enumerate(p['yarns']):
        with y_cols[i]:
            st.write(f"**{y['name']}**")
            st.info(f"{y['p']}%  /  {y['price']}円/kg")

    st.divider()
    
    # 解答エリア
    st.markdown("#### 🖋️ Answer")
    ans_col, btn_col = st.columns([2, 1])
    with ans_col:
        user_ans = st.number_input("算出単価 (円/kg)", min_value=0.0, format="%.2f")
    with btn_col:
        st.write(" ") # 余白調整
        check_btn = st.button("採点する", use_container_width=True, type="primary")

    if check_btn:
        error = abs(user_ans - p['answer']) / p['answer']
        if error <= 0.005:
            st.success(f"**Excellent.** 正解です: {p['answer']:,.2f} 円/kg")
            st.balloons()
        else:
            st.error(f"**Calculation Error.** 正解は {p['answer']:,.2f} 円/kg です")
            with st.expander("詳細な計算プロセス（エビデンス）を確認"):
                for s in p['steps']:
                    st.write(s)
else:
    st.write("「新規オーダーを生成」ボタンを押して特訓を開始してください。")