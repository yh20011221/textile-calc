import streamlit as st
import random
import math

# --- 1. ページ設定 ---
st.set_page_config(page_title="生機原価計算", page_icon="🧶", layout="wide")

# カスタムCSS（少しだけ余白とカードの見た目を整えています）
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #eee;
        padding: 15px !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. サイドバー（実務定数） ---
with st.sidebar:
    st.title("⚙️ 設定")
    case_weight = st.number_input("1ケースの重量 (kg)", value=22.68)
    loss_rate_percent = st.slider("ロス率 (%)", 0, 10, 2)
    loss_rate = 1 + (loss_rate_percent / 100)
    st.divider()
    st.caption("繊維実務 原価計算 v2.6")
    if st.button("計算履歴をクリア"):
        st.session_state.calc_history = []
        st.rerun()

# --- 3. セッション状態の初期化 ---
if 'problem' not in st.session_state:
    st.session_state.problem = None
if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

def generate_problem():
    num_rolls = random.randint(10, 30)
    weight_per_roll = random.randint(8, 12)
    total_raw_weight = num_rolls * weight_per_roll
    
    is_single = random.choice([True, False])
    if is_single:
        yarns = [{"name": "素材A", "p": 100, "price": random.randint(800, 1500)}]
    else:
        p1, p2 = random.randint(30, 35), random.randint(30, 35)
        yarns = [
            {"name": "表糸", "p": p1, "price": random.randint(1100, 1600)},
            {"name": "中糸", "p": p2, "price": random.randint(800, 1100)},
            {"name": "裏糸", "p": 100 - p1 - p2, "price": random.randint(900, 1200)}
        ]
    
    knitting_fee = random.randint(150, 300)
    
    # --- 正解の計算プロセス ---
    total_yarn_cost = 0
    steps = []
    steps.append(f"① **生機の総重量**: {num_rolls}反 × {weight_per_roll}kg = {total_raw_weight}kg")
    
    for y in yarns:
        net = total_raw_weight * (y['p'] / 100) * loss_rate
        cases = math.ceil(net / case_weight)
        purchase_weight = cases * case_weight
        cost = purchase_weight * y['price']
        total_yarn_cost += cost
        steps.append(f"② **{y['name']}({y['p']}%)**: {net:.2f}kg必要 → {cases}箱購入 ({purchase_weight:.2f}kg) → {cost:,.0f}円")
        
    total_knitting_cost = total_raw_weight * knitting_fee
    grand_total = total_yarn_cost + total_knitting_cost
    final_unit_price = grand_total / total_raw_weight
    
    steps.append(f"③ **編賃合計**: {total_raw_weight}kg × {knitting_fee}円 = {total_knitting_cost:,.0f}円")
    steps.append(f"④ **最終コスト**: ({total_yarn_cost:,.0f} + {total_knitting_cost:,.0f}) ÷ {total_raw_weight} = **{final_unit_price:,.2f} 円/kg**")
    
    return {
        "num_rolls": num_rolls, "weight_per_roll": weight_per_roll, "total_raw": total_raw_weight,
        "yarns": yarns, "knitting_fee": knitting_fee, "answer": final_unit_price, "steps": steps
    }

# --- 4. メイン画面 ---
st.title("🧶 繊維実務：生機原価計算特訓")

if st.button("新しい問題を生成", type="primary"):
    st.session_state.problem = generate_problem()
    st.session_state.answered = False

if st.session_state.problem:
    p = st.session_state.problem
    
    # ▼ ここを以前のカード形式に戻しました
    st.markdown("#### 📋 出題条件")
    c1, c2, c3 = st.columns(3)
    c1.metric("発注数", f"{p['num_rolls']} 反")
    c2.metric("生機単重", f"{p['weight_per_roll']} kg")
    c3.metric("編賃(1kgあたり)", f"¥{p['knitting_fee']}")
    
    # 糸の詳細表示
    st.markdown("#### 🧵 糸の構成")
    y_cols = st.columns(len(p['yarns']))
    for i, y in enumerate(p['yarns']):
        y_cols[i].info(f"**{y['name']}**\n\n混率: {y['p']}%\n\n単価: {y['price']}円/kg")

    st.divider()

    # --- 電卓セクション（履歴機能付き） ---
    st.markdown("#### 🧮 計算用メモ（履歴付き）")
    with st.expander("電卓と履歴を表示", expanded=True):
        calc_col, history_col = st.columns([1, 1])
        with calc_col:
            with st.form(key='calc_form', clear_on_submit=True):
                calc_input = st.text_input("数式入力 (例: 200*0.35*1.02/22.68):")
                submit_calc = st.form_submit_button("計算して履歴に追加")
                if submit_calc and calc_input:
                    try:
                        formula = calc_input.replace('×', '*').replace('÷', '/').replace('x', '*')
                        res = eval(formula)
                        st.session_state.calc_history.append(f"{calc_input} = {res:,.4f}")
                        st.success(f"結果: **{res:,.4f}**")
                    except:
                        st.error("数式が正しくありません。")
        with history_col:
            st.caption("計算履歴（直近5件）")
            if st.session_state.calc_history:
                for item in reversed(st.session_state.calc_history[-5:]):
                    st.text(item)
            else:
                st.write("履歴はありません")

    # --- 解答入力 ---
    st.markdown("#### 🖋️ 解答入力")
    ans_col, btn_col = st.columns([2, 1])
    with ans_col:
        user_ans = st.number_input("算出された生機単価 (円/kg):", min_value=0.0, format="%.2f", step=0.01)
    with btn_col:
        st.write(" ") 
        if st.button("採点する", use_container_width=True):
            error = abs(user_ans - p['answer']) / p['answer']
            if error <= 0.005:
                st.success(f"🎊 正解です！ 答え: {p['answer']:,.2f} 円/kg")
                st.balloons()
            else:
                st.error(f"❌ 不正解... 正解は {p['answer']:,.2f} 円/kg です")
                with st.expander("計算のステップを見る"):
                    for s in p['steps']:
                        st.write(s)
else:
    st.info("上のボタンを押して問題を開始してください。")
