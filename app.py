import streamlit as st
import random
import math

# --- 1. ページ基本設定 ---
st.set_page_config(page_title="Textile Calc Pro +", page_icon="🧶", layout="wide")

# カスタムCSS（視認性とプロ感を向上）
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eee; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    div[data-testid="stExpander"] { background-color: #ffffff; border-radius: 10px; border: 1px solid #ddd; }
    .stButton>button { border-radius: 5px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. サイドバー（実務定数の設定） ---
with st.sidebar:
    st.title("⚙️ 定数設定")
    case_weight = st.number_input("1ケースの重量 (kg)", value=22.68, help="標準は22.68kgです")
    loss_rate_percent = st.slider("ロス率 (%)", 0, 10, 2)
    loss_rate = 1 + (loss_rate_percent / 100)
    st.divider()
    st.caption("繊維実務 原価計算エンジン v2.1")
    st.caption("Developed by Gemini App Collaboration")

# --- 3. セッション管理 ---
if 'problem' not in st.session_state:
    st.session_state.problem = None

def generate_problem():
    # 生機は1反10kg前後
    num_rolls = random.randint(10, 30)
    weight_per_roll = random.randint(8, 12)
    total_raw_weight = num_rolls * weight_per_roll
    
    # 糸の構成（1種類 or 3種類）をランダムに決定
    is_single = random.choice([True, False])
    if is_single:
        yarns = [{"name": "素材A", "p": 100, "price": random.randint(800, 1500)}]
    else:
        # 表・中・裏を33%前後のランダムな整数で調整
        p1 = random.randint(30, 35)
        p2 = random.randint(30, 35)
        yarns = [
            {"name": "表糸", "p": p1, "price": random.randint(1100, 1600)},
            {"name": "中糸", "p": p2, "price": random.randint(800, 1100)},
            {"name": "裏糸", "p": 100 - p1 - p2, "price": random.randint(900, 1200)}
        ]
    
    knitting_fee = random.randint(150, 300)
    
    # --- 計算プロセス ---
    total_yarn_cost = 0
    steps = []
    steps.append(f"① **生機の総重量を計算**: {num_rolls}反 × {weight_per_roll}kg = {total_raw_weight}kg")
    
    for y in yarns:
        # 混率とロスを加味した純必要量
        net_required = total_raw_weight * (y['p'] / 100) * loss_rate
        # ケース単位での切り上げ
        required_cases = math.ceil(net_required / case_weight)
        # 購入重量とコスト（余りは廃棄）
        purchase_weight = required_cases * case_weight
        cost = purchase_weight * y['price']
        total_yarn_cost += cost
        
        steps.append(f"② **{y['name']} ({y['p']}%)**: {net_required:.2f}kg必要 → {required_cases}ケース購入 ({purchase_weight:.2f}kg) → {cost:,.0f}円")
        
    total_knitting_cost = total_raw_weight * knitting_fee
    grand_total = total_yarn_cost + total_knitting_cost
    final_unit_price = grand_total / total_raw_weight
    
    steps.append(f"③ **編賃の算出**: {total_raw_weight}kg × {knitting_fee}円 = {total_k_cost:,.0f}円")
    steps.append(f"④ **生機1kgあたりの単価**: ({total_yarn_cost:,.0f} + {total_knitting_cost:,.0f}) ÷ {total_raw_weight} = **{final_unit_price:,.2f} 円/kg**")
    
    return {
        "num_rolls": num_rolls, "weight_per_roll": weight_per_roll, "total_raw": total_raw_weight,
        "yarns": yarns, "knitting_fee": knitting_fee, "answer": final_unit_price, "steps": steps
    }

# --- 4. メイン画面の表示 ---
st.title("Textile Cost Simulator Pro")
st.subheader("生機原価計算・実践特訓")

if st.button("✨ 新規オーダーを発行", use_container_width=True, type="primary"):
    st.session_state.problem = generate_problem()
    st.session_state.answered = False

if st.session_state.problem:
    p = st.session_state.problem
    
    # オーダー概要（メトリクス）
    st.markdown("### 📋 オーダー条件")
    c1, c2, c3 = st.columns(3)
    c1.metric("発注数", f"{p['num_rolls']} 反")
    c2.metric("1反重量", f"{p['weight_per_roll']} kg")
    c3.metric("編賃(1kgあたり)", f"{p['knitting_fee']} 円")
    
    # 糸の詳細
    st.markdown("#### 🧶 糸の構成")
    y_cols = st.columns(len(p['yarns']))
    for i, y in enumerate(p['yarns']):
        with y_cols[i]:
            st.info(f"**{y['name']}**\n\n混率: {y['p']}%\n\n単価: {y['price']}円/kg")

    st.divider()

    # --- 電卓（計算メモ）セクション ---
    st.markdown("#### 🧮 計算用メモ（電卓）")
    with st.expander("電卓を開く・閉じる"):
        st.caption("Excelのように数式を入力して計算できます（例: (200 * 0.7 * 1.02) / 22.68）")
        calc_input = st.text_input("数式を入力してください:", placeholder="例: (200 * 0.35 * 1.02) / 22.68")
        if calc_input:
            try:
                # 記号の置換（全角や×÷にも対応）
                safe_input = calc_input.replace('×', '*').replace('÷', '/').replace('x', '*')
                result = eval(safe_input)
                st.success(f"計算結果: **{result:,.4f}**")
            except Exception:
                st.error("数式が正しくありません。半角の + - * / ( ) を使用してください。")

    # 解答入力
    st.markdown("#### 🖋️ 回答入力")
    ans_col, btn_col = st.columns([2, 1])
    with ans_col:
        user_ans = st.number_input("算出された生機単価 (円/kg)", min_value=0.0, format="%.2f", step=0.01)
    with btn_col:
        st.write(" ") # スペース調整
        check_btn = st.button("採点する", use_container_width=True)

    if check_btn:
        # 誤差0.5%以内判定
        error = abs(user_ans - p['answer']) / p['answer']
        if error <= 0.005:
            st.success(f"🎊 正解です！ 正解: {p['answer']:,.2f} 円/kg")
            st.balloons()
        else:
            st.error(f"❌ 不正解です。正解は {p['answer']:,.2f} 円/kg です。")
            with st.expander("詳しい計算プロセス（証跡）を見る"):
                for s in p['steps']:
                    st.write(s)
else:
    st.info("上のボタンを押して、新しい計算問題を開始してください。")
