"""竞品数据看板：本地运行，浏览器打开查看"""
import streamlit as st
import pandas as pd
import mysql.connector
from datetime import date, timedelta
import json
from pathlib import Path

DB = {"host": "127.0.0.1", "port": 3306, "user": "root",
      "password": "123456", "database": "competitor_db"}

st.set_page_config(page_title="竞品数据看板", layout="wide")
st.title("📊 竞品数据看板")

@st.cache_data(ttl=60)
def load_data():
    conn = mysql.connector.connect(**DB)
    products = pd.read_sql("SELECT id, store, title, category, first_seen, last_seen, is_active FROM products", conn)
    snapshots = pd.read_sql("SELECT s.product_id, p.store, p.title, p.category, s.price, s.status, s.captured_at FROM snapshots s JOIN products p ON s.product_id = p.id ORDER BY s.captured_at DESC", conn)
    conn.close()
    return products, snapshots

products, snapshots = load_data()
stores = sorted(products["store"].unique())

# ─── 侧边栏 ───
st.sidebar.header("筛选条件")

# Tab1: 品牌分析
tab1, tab2 = st.tabs(["🔍 品牌分析", "📊 品类对比"])

with tab1:
    store = st.sidebar.selectbox("选择品牌", stores, key="s1")
    days = st.sidebar.slider("过去N天", 1, 90, 7, key="d1")
    cutoff = date.today() - timedelta(days=days)

    st.subheader(f"🏷️ {store} — 过去{days}天动态")

    col1, col2, col3 = st.columns(3)
    store_products = products[products["store"] == store]
    
    with col1:
        new_count = len(store_products[store_products["first_seen"] >= str(cutoff)])
        st.metric("🆕 新品上架", new_count)
    with col2:
        removed = store_products[store_products["is_active"] == 0]
        st.metric("🗑️ 下架", len(removed))
    with col3:
        total = len(store_products[store_products["is_active"] == 1])
        st.metric("📦 在售总数", total)

    # 品类分布
    st.subheader("品类分布")
    cat_counts = store_products[store_products["is_active"] == 1].groupby("category").size().reset_index(name="数量")
    cat_counts["占比"] = (cat_counts["数量"] / cat_counts["数量"].sum() * 100).round(1).astype(str) + "%"
    st.dataframe(cat_counts, use_container_width=True, hide_index=True)

    # 近期价格变动
    st.subheader("价格变动记录")
    store_snap = snapshots[snapshots["store"] == store]
    store_snap["captured_at"] = pd.to_datetime(store_snap["captured_at"])
    
    # 找价格有变化的商品
    price_changes = store_snap.groupby("title").agg(
        最早价格=("price", "first"),
        最新价格=("price", "last"),
        采集次数=("price", "count"),
    ).reset_index()
    price_changes["变动"] = price_changes.apply(
        lambda r: f"${float(r['最早价格']):.2f} → ${float(r['最新价格']):.2f}" 
        if r["最早价格"] != r["最新价格"] else "无变动", axis=1
    )
    changed = price_changes[price_changes["最早价格"] != price_changes["最新价格"]]
    if not changed.empty:
        st.dataframe(changed[["title", "变动", "采集次数"]], use_container_width=True, hide_index=True)
    else:
        st.info("该品牌近期无价格变动")

    # 新品列表
    st.subheader("新品列表")
    new_items = store_products[store_products["first_seen"] >= str(cutoff)]
    if not new_items.empty:
        st.dataframe(new_items[["title", "category", "first_seen"]], use_container_width=True, hide_index=True)
    else:
        st.info("该品牌近期无新品")

with tab2:
    st.subheader("📊 品类横向对比")
    
    # 选品类
    all_cats = sorted(products["category"].unique())
    category = st.sidebar.selectbox("选择品类", all_cats, key="c1")
    
    # 选店铺（默认全部）
    selected_stores = st.sidebar.multiselect("选择店铺（可多选）", stores, default=stores[:5], key="ss1")
    
    if selected_stores:
        filtered = products[(products["store"].isin(selected_stores)) & 
                           (products["category"] == category) & 
                           (products["is_active"] == 1)]
        
        # 按店铺汇总
        summary = filtered.groupby("store").agg(
            SKU数量=("id", "count"),
            最低价=("price", "min"),
            最高价=("price", "max"),
        ).reset_index()
        
        # 补充均价
        snap_filtered = snapshots[snapshots["store"].isin(selected_stores)]
        avg_prices = snap_filtered.groupby("store")["price"].mean().reset_index()
        avg_prices.columns = ["store", "均价"]
        summary = summary.merge(avg_prices, on="store", how="left")
        summary["均价"] = summary["均价"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
        
        st.dataframe(summary, use_container_width=True, hide_index=True)
        
        # 商品列表
        st.subheader(f"「{category}」商品列表")
        st.dataframe(filtered[["store", "title", "price"]], use_container_width=True, hide_index=True)
    else:
        st.info("请选择至少一个店铺")

st.sidebar.markdown("---")
st.sidebar.caption(f"数据更新至 {date.today()}")
