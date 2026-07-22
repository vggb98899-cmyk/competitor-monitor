"""竞品数据看板"""
import streamlit as st
import pandas as pd
import mysql.connector
from datetime import date, timedelta

DB = {"host": "127.0.0.1", "port": 3306, "user": "root",
      "password": "123456", "database": "competitor_db"}

st.set_page_config(page_title="竞品数据看板", layout="wide")
st.title("📊 竞品数据看板")

@st.cache_data(ttl=60)
def load_data():
    conn = mysql.connector.connect(**DB)
    products = pd.read_sql("SELECT id, store, title, category, first_seen, last_seen, is_active FROM products", conn)
    snapshots = pd.read_sql("""SELECT s.product_id, p.store, p.title, p.category, s.price, s.status, s.captured_at 
                               FROM snapshots s JOIN products p ON s.product_id = p.id 
                               ORDER BY s.captured_at DESC""", conn)
    conn.close()
    products["first_seen"] = pd.to_datetime(products["first_seen"])
    snapshots["captured_at"] = pd.to_datetime(snapshots["captured_at"])
    return products, snapshots

products, snapshots = load_data()
stores = sorted(products["store"].unique())
cats = sorted(products["category"].unique())

tab1, tab2, tab3 = st.tabs(["🔍 品牌分析", "📊 品类对比", "📈 品类趋势"])

# ═══════════════════════════════════════
# TAB 1: 品牌分析
# ═══════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1, 3])
    with col_left:
        store = st.selectbox("品牌", stores, key="s1")
        days = st.slider("天数", 1, 90, 7, key="d1")
    cutoff = date.today() - timedelta(days=days)
    sp = products[products["store"] == store].copy()

    with col_right:
        c1, c2, c3, c4 = st.columns(4)
        active = len(sp[sp["is_active"] == 1])
        new = len(sp[sp["first_seen"] >= pd.Timestamp(cutoff)])
        removed = len(sp[sp["is_active"] == 0])
        total = len(sp)
        c1.metric("📦 在售", active)
        c2.metric("🆕 新品", new)
        c3.metric("🗑️ 下架", removed)
        c4.metric("合计", total)

    st.subheader("品类分布")
    active_sp = sp[sp["is_active"] == 1]
    cat_dist = active_sp.groupby("category").size().reset_index(name="数量")
    cat_dist["占比"] = (cat_dist["数量"] / cat_dist["数量"].sum() * 100).round(1).astype(str) + "%"
    st.dataframe(cat_dist, use_container_width=True, hide_index=True)

    st.subheader("价格变动记录")
    ss = snapshots[snapshots["store"] == store].copy()
    changes = ss.groupby("title").agg(
        最早=("price", "first"), 最新=("price", "last"), 天数=("captured_at", "nunique")
    ).reset_index()
    changes = changes[changes["最早"] != changes["最新"]]
    if not changes.empty:
        changes["变动"] = changes.apply(lambda r: f"${float(r['最早']):.2f} → ${float(r['最新']):.2f}", axis=1)
        st.dataframe(changes[["title", "变动", "天数"]], use_container_width=True, hide_index=True)
    else:
        st.info(f"✅ 该品牌近{days}天无价格变动")

    st.subheader(f"近{days}天新品")
    new_items = sp[sp["first_seen"] >= pd.Timestamp(cutoff)]
    if not new_items.empty:
        st.dataframe(new_items[["title", "category", "first_seen"]], use_container_width=True, hide_index=True)
    else:
        st.info(f"该品牌近{days}天无新品上架")

# ═══════════════════════════════════════
# TAB 2: 品类对比
# ═══════════════════════════════════════
with tab2:
    col_left, col_right = st.columns([1, 3])
    with col_left:
        cat2 = st.selectbox("品类", cats, key="c2")
        sel_stores = st.multiselect("店铺（可多选）", stores, default=stores[:4], key="ss2")
    with col_right:
        if sel_stores:
            snap_latest = snapshots.drop_duplicates(subset=["product_id"], keep="first")
            filtered = products[(products["store"].isin(sel_stores)) & 
                                (products["category"] == cat2) & (products["is_active"] == 1)]
            sku_count = filtered.groupby("store").size().reset_index(name="SKU数")
            price_stats = snap_latest[snap_latest["store"].isin(sel_stores)].groupby("store").agg(
                均价=("price", "mean"), 最低=("price", "min"), 最高=("price", "max")
            ).reset_index()
            for c in ["均价", "最低", "最高"]:
                price_stats[c] = price_stats[c].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
            summary = sku_count.merge(price_stats, on="store", how="left")
            st.dataframe(summary, use_container_width=True, hide_index=True)
            
            latest = snap_latest[snap_latest["store"].isin(sel_stores)]
            merged = filtered.merge(latest[["product_id", "price"]], left_on="id", right_on="product_id", how="left")
            st.dataframe(merged[["store", "title", "price"]], use_container_width=True, hide_index=True)
        else:
            st.info("请选择至少一个店铺")

# ═══════════════════════════════════════
# TAB 3: 品类趋势（按时间）
# ═══════════════════════════════════════
with tab3:
    col_left, col_right = st.columns([1, 3])
    with col_left:
        store3 = st.selectbox("品牌", stores, key="s3")
        cat3 = st.selectbox("品类", cats, key="c3")
        days3 = st.slider("过去天数", 7, 90, 30, key="d3")
    with col_right:
        cutoff3 = date.today() - timedelta(days=days3)
        trend_data = snapshots[(snapshots["store"] == store3) & 
                               (snapshots["category"] == cat3) &
                               (snapshots["captured_at"] >= pd.Timestamp(cutoff3))].copy()
        if not trend_data.empty:
            trend_data["date"] = trend_data["captured_at"].dt.date
            daily = trend_data.groupby("date").agg(
                商品数=("product_id", "nunique"),
                均价=("price", "mean"),
            ).reset_index()
            daily["均价"] = daily["均价"].round(2)
            st.line_chart(daily.set_index("date")["均价"])
            st.dataframe(daily, use_container_width=True, hide_index=True)
            st.caption(f"{store3}「{cat3}」品类过去{days3}天的均价变化")
        else:
            st.info(f"{store3}「{cat3}」品类在过去{days3}天内无数据")

st.sidebar.markdown("---")
st.sidebar.caption(f"数据更新至 {date.today()}")
