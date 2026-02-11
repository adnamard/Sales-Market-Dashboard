import streamlit as st
import pandas as pd
import plotly.express as px


# Page Configuration
# -----------------------------------------------------
st.set_page_config(
    page_title="Restaurant Sales Dashboard",
    page_icon="🍽️",
    layout="wide"
)

PRIMARY_COLOR = px.colors.sequential.Teal

st.title("🍽️ Restaurant Sales Insight Dashboard")
st.markdown(
    """
    Interactive dashboard to explore restaurant sales behavior, 
    revenue drivers, and customer ordering patterns.
    """
)


@st.cache_data
def load_data():
    df = pd.read_csv("restaurant_data.csv")
    df["order_date"] = pd.to_datetime(df["order_date"])

    df["day"] = df["order_date"].dt.date
    df["weekday"] = df["order_date"].dt.day_name()
    df["week"] = df["order_date"].dt.isocalendar().week
    df["month"] = df["order_date"].dt.month
    df["year"] = df["order_date"].dt.year

    return df

df = load_data()

# -----------------------------------------------------
# Sidebar Filters
st.sidebar.header("🔎 Filters")

selected_category = st.sidebar.multiselect(
    "Select Category",
    options=df["category"].unique(),
    default=df["category"].unique()
)

selected_weekday = st.sidebar.multiselect(
    "Select Weekday",
    options=df["weekday"].unique(),
    default=df["weekday"].unique()
)

filtered_df = df[
    (df["category"].isin(selected_category)) &
    (df["weekday"].isin(selected_weekday))
]
st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 Creator")
st.sidebar.markdown(
    """
    **Ramanda**  
    🔗 [GitHub](https://github.com/adnamard)  
    🌐 [Portfolio](https://s.id/ramanda-gardens)
    """
)

# KPI Metrics
# -----------------------------------------------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "💰 Total Revenue",
    f"$ {filtered_df['order_total'].sum():,.2f}"
)

col2.metric(
    "📦 Total Items Sold",
    f"{int(filtered_df['quantity'].sum())} pcs"
    )

col3.metric(
    "🧾 Avg Order Value",
    f"$ {filtered_df['order_total'].mean():,.2f}"
)

st.divider()

# Customer Analysis
# -----------------------------------------------------
st.header("Customer Analysis")

st.markdown(
    """
    To better understand customer behavior, we segment customers into two distinct types 
    based on **spending value** and **purchase frequency**.
    """
)
st.subheader("💎 Biggest Spenders (Top 10)")
st.markdown("""Customers who contribute **high total revenue**, even if they purchase 
        **infrequently**.""")
customer_revenue = (
    filtered_df
    .groupby("cust_id", as_index=False)
    .agg(total_spent=("order_total", "sum"))
    .sort_values("total_spent", ascending=False)
    .head(10)
)

top_spender = customer_revenue.iloc[0]

col1, col2 = st.columns([1, 2])

col1.metric(
    label="Top Spender",
    value=f"Customer {top_spender['cust_id']}",
    delta=f"${top_spender['total_spent']:,.2f}"
)

fig_spender = px.bar(
    customer_revenue,
    x="cust_id",
    y="total_spent",
    text_auto=".4s",
    height=300,
    color="total_spent",
    color_continuous_scale=PRIMARY_COLOR
)

fig_spender.update_layout(
    showlegend=False,
    xaxis_title="Customer ID",
    yaxis_title="Total Spending"
)

col2.plotly_chart(fig_spender, use_container_width=True)

st.caption(
    "Insight: A small number of customers contribute a disproportionate share of revenue."
)
st.subheader("🤝 Most Loyal Customers (Top 10)")
st.markdown("""Customers who purchase **frequently**, creating stable and predictable revenue.
""")
customer_loyalty = (
    filtered_df
    .groupby("cust_id", as_index=False)
    .agg(total_orders=("order_id", "nunique"))
    .sort_values("total_orders", ascending=False)
    .head(10)
)

most_loyal = customer_loyalty.iloc[0]

col1, col2 = st.columns([1, 2])

col1.metric(
    label="Most Loyal Customer",
    value=f"Customer {most_loyal['cust_id']}",
    delta=f"{most_loyal['total_orders']} Orders"
)

fig_loyal = px.bar(
    customer_loyalty,
    x="cust_id",
    y="total_orders",
    text_auto=".s",
    height=300,
    color="total_orders",
    color_continuous_scale=PRIMARY_COLOR
)

fig_loyal.update_layout(
    showlegend=False,
    xaxis_title="Customer ID",
    yaxis_title="Number of Orders"
)

col2.plotly_chart(fig_loyal, use_container_width=True)

st.caption(
    "Insight: Loyal customers ensure consistent demand even when order values are smaller."
)

# Visualization 1: Revenue by Category
# -----------------------------------------------------
st.header(" Category Performance")

st.markdown(
    """
    Category performance analysis helps identify which product categories 
    **drive revenue** and which ones **drive demand volume**.
    Revenue and quantity do not always move together — a category may sell 
    frequently but contribute less revenue, or vice versa.
    """
)


st.subheader("📊 Revenue Contribution by Category")
st.markdown(
        """
        Categories that contribute **high total revenue**, usually driven by 
        higher-priced items.
        """
    )
rev_cat = (
    filtered_df
    .groupby("category", as_index=False)
    .agg(total_revenue=("order_total", "sum"))
)

fig1 = px.bar(
    rev_cat,
    x="category",
    y="total_revenue",
    text_auto=".5s",
    height=320,
    color="category",
    color_discrete_sequence=px.colors.qualitative.Set1
)

fig1.update_layout(
    showlegend=False,
    xaxis_title="Category",
    yaxis_title="Total Revenue"
)

st.plotly_chart(fig1, use_container_width=True)

st.caption(
    "Insight: Revenue-driven categories may rely on fewer but higher-value transactions."
)

st.subheader("📦 Sales Volume by Category")
st.markdown(
        """
        Categories that sell **frequently**, even if individual items are lower priced.

        """
    )
vol_cat = (
    filtered_df
    .groupby("category", as_index=False)
    .agg(total_quantity=("quantity", "sum"))
)

fig2 = px.bar(
    vol_cat,
    x="category",
    y="total_quantity",
    text_auto=".5s",
    height=320,
    color="category",
    color_discrete_sequence=px.colors.qualitative.Set1
)

fig2.update_layout(
    showlegend=False,
    xaxis_title="Category",
    yaxis_title="Total Quantity Sold"
)

st.plotly_chart(fig2, use_container_width=True)

st.caption(
    "Insight: High-volume categories indicate strong demand, even if revenue per item is lower."
)

# Visualization 1: Item Performance Analysis
# -----------------------------------------------------
st.header(" Item Performance Analysis")

st.markdown(
    """
    Item performance analysis highlights which menu items 
    **drive sales volume** and which ones **contribute the most revenue** 
    within each category.
    
    This helps identify hero items, upsell opportunities, and menu optimization strategies.
    """
)

item_perf = (
    filtered_df
    .groupby(["category", "item"], as_index=False)
    .agg(
        total_quantity=("quantity", "sum"),
        total_revenue=("order_total", "sum")
    )
)

fig_item = px.bar(
    item_perf,
    x="item",
    y="total_quantity",
    color="category",
    barmode="group",
    text_auto=".2s",
    height=380,
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_item.update_layout(
    xaxis_title="Menu Item",
    yaxis_title="Total Quantity Sold"
)

st.plotly_chart(fig_item, use_container_width=True)

st.caption(
    "Insight: This reveals which items actually drive volume inside each category, not just revenue."
)



# -----------------------------------------------------
# Visualization 3: Orders by Weekday
# -----------------------------------------------------
st.subheader("📆 Ordering Pattern by Weekday")

weekday_order = (
    filtered_df
    .groupby("weekday", as_index=False)
    .agg(total_orders=("order_id", "nunique"))
)

fig3 = px.bar(
    weekday_order,
    x="weekday",
    y="total_orders",
    height=320,
    text_auto=".4s",
    color="total_orders",
    color_continuous_scale=PRIMARY_COLOR
)

fig3.update_layout(
    showlegend=False,
    xaxis_title="Weekday",
    yaxis_title="Total Orders"
)

st.plotly_chart(fig3, use_container_width=True)

st.caption(
    "Insight: Identify peak ordering days for staffing and promotions."
)

#DAILY REVENUE

MONTH_MAP = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}
st.subheader("📈 Daily Revenue Trend by Year")
col_2022, col_2023 = st.columns(2)
with col_2022:
    st.markdown("### 🟦 2022")

    df_2022 = filtered_df[filtered_df["year"] == 2022]

    months_2022 = sorted(df_2022["month"].dropna().unique().tolist())
    month_options_2022 = ["All Months"] + [MONTH_MAP[m] for m in months_2022]

    selected_month_2022 = st.selectbox(
        "Select Month (2022)",
        options=month_options_2022,
        key="month_2022"
    )

    if selected_month_2022 == "All Months":
        plot_df = df_2022
    else:
        month_num = [k for k, v in MONTH_MAP.items() if v == selected_month_2022][0]
        plot_df = df_2022[df_2022["month"] == month_num]

    daily_rev_2022 = (
        plot_df
        .groupby("day", as_index=False)
        .agg(daily_revenue=("order_total", "sum"))
    )

    if daily_rev_2022.empty:
        st.info("No data available for this month.")
    else:
        fig_2022 = px.line(
            daily_rev_2022,
            x="day",
            y="daily_revenue",
            markers=True,
            height=300,
            color_discrete_sequence=["#4C72B0"]
        )

        fig_2022.update_layout(
            xaxis_title="Date",
            yaxis_title="Daily Revenue"
        )

        st.plotly_chart(fig_2022, use_container_width=True)
with col_2023:
    st.markdown("### 🟩 2023")

    df_2023 = filtered_df[filtered_df["year"] == 2023]

    months_2023 = sorted(df_2023["month"].dropna().unique().tolist())
    month_options_2023 = ["All Months"] + [MONTH_MAP[m] for m in months_2023]

    selected_month_2023 = st.selectbox(
        "Select Month (2023)",
        options=month_options_2023,
        key="month_2023"
    )

    if selected_month_2023 == "All Months":
        plot_df = df_2023
    else:
        month_num = [k for k, v in MONTH_MAP.items() if v == selected_month_2023][0]
        plot_df = df_2023[df_2023["month"] == month_num]

    daily_rev_2023 = (
        plot_df
        .groupby("day", as_index=False)
        .agg(daily_revenue=("order_total", "sum"))
    )

    if daily_rev_2023.empty:
        st.info("No data available for this month.")
    else:
        fig_2023 = px.line(
            daily_rev_2023,
            x="day",
            y="daily_revenue",
            markers=True,
            height=300,
            color_discrete_sequence=["#55A868"]
        )

        fig_2023.update_layout(
            xaxis_title="Date",
            yaxis_title="Daily Revenue"
        )

        st.plotly_chart(fig_2023, use_container_width=True)
st.caption(
    "Insight: Side-by-side daily revenue trends reveal year-over-year demand shifts and seasonal patterns."
)


# -----------------------------------------------------
# Footer
# -----------------------------------------------------
st.markdown("---")
st.markdown(
    "Built with ❤️ using **Streamlit** | Designed by Adnamar."
)
