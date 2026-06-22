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
st.markdown("""
<style>
.stApp {
    background-color: #F4EFE6;
}

[data-testid="stSidebar"] {
    background-color: #E8E0D3;
}

h1, h2, h3 {
    color: #2D2D2D;
}

p, div, span, label {
    color: #444444;
}

[data-testid="stMetricValue"] {
    color: #1F4E5F;
}
</style>
""", unsafe_allow_html=True)

PRIMARY_COLOR = px.colors.sequential.Teal

st.title("🍽️ Restaurant Sales Insight Dashboard")

st.markdown("""
### Understanding customer behavior, revenue drivers, and operational opportunities

This dashboard explores restaurant transaction data to answer four key business questions:

- Who are the most valuable customers?
- Which categories generate the most revenue?
- Which products drive demand?
- When are customers most active?

The goal is to translate transaction data into actionable business insights.
""")


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

st.header("Executive Summary")

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
st.caption("""
These metrics provide a high-level snapshot of restaurant performance.
Next, we explore which customers and products are responsible for these results.
""")


st.header("Dataset Overview")

left, right = st.columns([1,2])

with left:
    st.markdown("""
    Before we dive into business insights, let's first understand the data.

    The dataset contains restaurant transactions including:

    - Customer information
    - Menu categories
    - Purchased items
    - Revenue
    - Order dates

    This will be the foundation for all analyses presented below.
    """)

with right:
    st.dataframe(
        filtered_df.head(10),
        use_container_width=True,
    )
    st.caption(
    f"Dataset contains {len(filtered_df):,} filtered transactions."
)


# Customer Analysys
# -----------------------------------------------------

st.divider()
st.header("👤 Customer Analysis")

customer_revenue = (
    filtered_df
    .groupby("cust_id", as_index=False)
    .agg(total_spent=("order_total", "sum"))
    .sort_values("total_spent", ascending=False)
    .head(10)
)

top_spender = customer_revenue.iloc[0]

left, right = st.columns([1,2])

with left:
    st.subheader("A. Biggest Spenders")

    st.markdown("""
    Biggest spender often defined as a customers who contribute **high total revenue**, even if they purchase 
        **infrequently**.
    
    Not all customers contribute equally.

    A small portion of customers often generates a significant
    share of total revenue.

    Identifying these customers helps businesses:

    - Improve retention
    - Build loyalty programs
    - Increase customer lifetime value
    """)


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

with right:
    st.plotly_chart(
        fig_spender,
        use_container_width=True
    )
    st.metric(
        label="Top Spender",
        value=f"Customer {top_spender['cust_id']}",
        delta=f"${top_spender['total_spent']:,.2f}"
    )

st.divider()
st.divider()

customer_loyalty = (
    filtered_df
    .groupby("cust_id", as_index=False)
    .agg(total_orders=("order_id", "nunique"))
    .sort_values("total_orders", ascending=False)
    .head(10)
)

most_loyal = customer_loyalty.iloc[0]

left, right = st.columns([1,2])

with left:
    st.subheader("B. Most Loyal Customers")

    st.markdown("""
    Revenue is important, but consistency matters too.

    Loyal customers create predictable demand
    and stabilize business performance.

    This analysis highlights customers who return most frequently.
    """)

    

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
with right:
    st.plotly_chart(
        fig_loyal,
        use_container_width=True
    )
    st.metric(
        label="Most Loyal Customer",
        value=f"Customer {most_loyal['cust_id']}",
        delta=f"{most_loyal['total_orders']} Orders"
    )
    

st.divider()

# Visualization 1: Revenue by Category
# -----------------------------------------------------
st.header("📦 Category Performance")

st.markdown(
    """
    Category performance analysis helps identify which product categories 
    **drive revenue** and which ones **drive demand volume**.
    Revenue and quantity do not always move together, because a category may sell 
    frequently but contribute less revenue, or vice versa.
    """
)

left, right = st.columns([1,2])

with left:
    st.subheader("A. Revenue Contribution by Category")

    st.markdown("""
    Which categories generate the most money?

    Revenue contribution helps identify where the
    restaurant creates the greatest business value.

    Categories with strong revenue performance may deserve:
    
    - Additional promotions
    - Inventory prioritization
    - Strategic focus
    
    """)
    
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
top_cat = rev_cat.sort_values(
    "total_revenue",
    ascending=False
).iloc[0]

lowest_cat = rev_cat.sort_values(
    "total_revenue"
).iloc[0]

with right:
    st.plotly_chart(fig1, use_container_width=True)
    st.caption(f"""
    The restaurant's largest revenue contributor is **{top_cat['category']}**
    with total revenue of approximately **{top_cat['total_revenue']:,.0f}**.

    Meanwhile, **{lowest_cat['category']}** generated the lowest revenue
    at only **{lowest_cat['total_revenue']:,.0f}**.

    This suggests that business value is heavily concentrated in
    the {top_cat['category']} category, making it a strong candidate
    for promotional campaigns and strategic investment.
    """)
    
st.divider()
st.divider()

# Visualization 2: Volume by Category
# -----------------------------------------------------
left, right = st.columns([1,2])

with left:
    st.subheader("B. Sales Volume by Category")

    st.markdown("""
    Revenue alone doesn't tell the whole story.

    Some categories may generate lower revenue
    while still driving large order volumes.

    Understanding demand helps support inventory planning.
    """)
    
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

top_vol = vol_cat.sort_values(
    "total_quantity",
    ascending=False
).iloc[0]

with right:
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(f"""
    The highest-demand category is **{top_vol['category']}**,
    with approximately **{top_vol['total_quantity']:,.0f} units sold**.

    Interestingly, demand distribution across categories appears
    relatively balanced, indicating that customers interact with
    a broad range of menu offerings rather than relying on a single category.
    """)
    
st.divider()
st.divider()



# Visualization 3: Item Performance Analysis
# -----------------------------------------------------
st.header("🍔 Item Performance Analysis")

left, right = st.columns([1,2])

with left:
    st.subheader("A. Item Performance")

    st.markdown("""
    Category-level insights are useful,
    but businesses ultimately sell products.

    This analysis identifies which menu items
    drive customer demand.

    High-performing items can become:

    - Hero products
    - Promotional anchors
    - Upselling opportunities
    """)

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

best_item = item_perf.sort_values(
    "total_quantity",
    ascending=False
).iloc[0]
with right:
    st.plotly_chart(
        fig_item,
        use_container_width=True
    )
    st.markdown(f"""
    Among all menu items, **{best_item['item']}**
    emerges as the strongest performer with total sales of
    approximately **{best_item['total_quantity']:,.0f} units**.

    This item acts as a potential hero product,
    demonstrating strong customer preference and repeat demand.
    """)

st.divider()
st.divider()

# -----------------------------------------------------
# Visualization 4: Orders by Weekday
# -----------------------------------------------------
left, right = st.columns([1,2])

with left:
    st.subheader("📆 Ordering Pattern")

    st.markdown("""
    Customer demand varies across the week.

    Understanding peak ordering days helps improve:

    - Staffing allocation
    - Inventory preparation
    - Promotional scheduling
    """)

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

best_day = weekday_order.sort_values(
    "total_orders",
    ascending=False
).iloc[0]
worst_day = weekday_order.sort_values(
    "total_orders"
).iloc[0]

with right:
    st.plotly_chart(
        fig3,
        use_container_width=True
    )
    st.markdown(f"""
    Customer activity peaks on **{best_day['weekday']}**
    with approximately **{best_day['total_orders']} orders**.

    In contrast, **{worst_day['weekday']}**
    records the lowest transaction volume.

    This pattern suggests that staffing levels,
    inventory preparation, and promotional campaigns
    should be adjusted according to daily demand fluctuations.
    """)
st.divider()
st.divider()

# -----------------------------------------------------
# Visualization 5: Revenue Analysis
# -----------------------------------------------------
st.header("📈 Revenue Trend Analysis")

left, right = st.columns([1,2])

with left:
    st.markdown("""
    Revenue trends reveal how customer demand changes over time.

    Comparing multiple years helps uncover:

    - Growth patterns
    - Seasonality
    - Revenue fluctuations

    These insights support forecasting and strategic planning.
    """)


#DAILY REVENUE
with right:
    st.info(
        "Use the month selectors below to compare revenue patterns between years."
    )
    MONTH_MAP = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}
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
    
    best_day = daily_rev_2022.loc[
    daily_rev_2022["daily_revenue"].idxmax()
]
    worst_day = daily_rev_2022.loc[
    daily_rev_2022["daily_revenue"].idxmin()
]

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
    
    best_day2023 = daily_rev_2023.loc[
    daily_rev_2023["daily_revenue"].idxmax()
]
    worst_day2023 = daily_rev_2023.loc[
    daily_rev_2023["daily_revenue"].idxmin()
]

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

with col_2022: 
    st.caption(f"""
The strongest performance occurred on
**{best_day['day']}** with revenue reaching approximately
**${best_day['daily_revenue']:,.0f}**.

Meanwhile, the weakest day was
**{worst_day['day']}**, generating only
**${worst_day['daily_revenue']:,.0f}**.
""")
    
with col_2023: 
    st.caption(f"""
The strongest performance occurred on
**{best_day2023['day']}** with revenue reaching approximately
**${best_day2023['daily_revenue']:,.0f}**.

Meanwhile, the weakest day was
**{worst_day2023['day']}**, generating only
**${worst_day2023['daily_revenue']:,.0f}**.
""")

# -----------------------------------------------------
# Footer
# -----------------------------------------------------
st.markdown("---")
st.markdown(
    "Built with ❤️ using **Streamlit** | Designed by Adnamar."
)
