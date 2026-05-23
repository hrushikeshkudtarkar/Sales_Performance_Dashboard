import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title='Sales Dashboard',
    layout='wide',
    page_icon='📊'
)

# LOAD DATA

@st.cache_data
def load_data():

    df = pd.read_csv('Sales-Export_2019-2020.csv')

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert revenue column
    df['order_value_EUR'] = (
        df['order_value_EUR']
        .astype(str)
        .str.replace(',', '')
        .astype(float)
    )

    # Convert cost column
    df['cost'] = (
        df['cost']
        .astype(str)
        .str.replace(',', '')
        .astype(float)
    )

    # Convert date
    df['date'] = pd.to_datetime(df['date'])

    # Create profit column
    df['profit'] = df['order_value_EUR'] - df['cost']

    # Create month column
    df['month'] = df['date'].dt.strftime('%Y-%m')

    return df


df = load_data()

# SIDEBAR FILTERS

st.sidebar.header('Filters')

selected_country = st.sidebar.multiselect(
    'Select Country',
    df['country'].unique(),
    default=df['country'].unique()
)

selected_category = st.sidebar.multiselect(
    'Select Category',
    df['category'].unique(),
    default=df['category'].unique()
)

selected_device = st.sidebar.multiselect(
    'Select Device Type',
    df['device_type'].unique(),
    default=df['device_type'].unique()
)

# -----------------------------------
# FILTER DATA
# -----------------------------------

filtered_df = df[
    (df['country'].isin(selected_country)) &
    (df['category'].isin(selected_category)) &
    (df['device_type'].isin(selected_device))
]

# -----------------------------------
# HEADER
# -----------------------------------

st.title('📈 Sales Performance Dashboard')
st.markdown('Business Sales Analytics Dashboard')

# -----------------------------------
# KPI METRICS
# -----------------------------------

revenue = filtered_df['order_value_EUR'].sum()
cost = filtered_df['cost'].sum()
profit = filtered_df['profit'].sum()
orders = filtered_df['order_id'].nunique()

profit_margin = (profit / revenue) * 100

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric('Total Revenue', f'€{revenue:,.0f}')
col2.metric('Total Cost', f'€{cost:,.0f}')
col3.metric('Total Profit', f'€{profit:,.0f}')
col4.metric('Orders', orders)
col5.metric('Profit Margin', f'{profit_margin:.2f}%')

st.markdown('---')

# -----------------------------------
# MONTHLY SALES TREND
# -----------------------------------

monthly_sales = (
    filtered_df
    .groupby('month')['order_value_EUR']
    .sum()
    .reset_index()
)

fig_monthly = px.line(
    monthly_sales,
    x='month',
    y='order_value_EUR',
    title='Monthly Revenue Trend',
    markers=True
)

st.plotly_chart(fig_monthly, use_container_width=True)

# -----------------------------------
# COUNTRY PERFORMANCE
# -----------------------------------

col6, col7 = st.columns(2)

country_sales = (
    filtered_df
    .groupby('country')['order_value_EUR']
    .sum()
    .reset_index()
)

fig_country = px.bar(
    country_sales,
    x='country',
    y='order_value_EUR',
    title='Revenue by Country',
    text_auto=True
)

col6.plotly_chart(fig_country, use_container_width=True)

# -----------------------------------
# CATEGORY ANALYSIS
# -----------------------------------

category_sales = (
    filtered_df
    .groupby('category')['order_value_EUR']
    .sum()
    .reset_index()
)

fig_category = px.pie(
    category_sales,
    names='category',
    values='order_value_EUR',
    title='Category Distribution'
)

col7.plotly_chart(fig_category, use_container_width=True)

# -----------------------------------
# SALES REPRESENTATIVE PERFORMANCE
# -----------------------------------

sales_rep_perf = (
    filtered_df
    .groupby('sales_rep')['profit']
    .sum()
    .reset_index()
    .sort_values(by='profit', ascending=False)
)

fig_rep = px.bar(
    sales_rep_perf,
    x='sales_rep',
    y='profit',
    title='Sales Representative Profit Performance',
    text_auto=True
)

st.plotly_chart(fig_rep, use_container_width=True)

# -----------------------------------
# DEVICE TYPE ANALYSIS
# -----------------------------------

fig_device = px.histogram(
    filtered_df,
    x='device_type',
    y='order_value_EUR',
    color='device_type',
    title='Device Type Sales Analysis'
)

st.plotly_chart(fig_device, use_container_width=True)

# -----------------------------------
# TOP CUSTOMERS TABLE
# -----------------------------------

st.subheader('Top Customers')

customer_table = (
    filtered_df
    .groupby('customer_name')[['order_value_EUR', 'profit']]
    .sum()
    .sort_values(by='order_value_EUR', ascending=False)
    .head(10)
)

st.dataframe(customer_table, use_container_width=True)

# -----------------------------------
# RAW DATA
# -----------------------------------

with st.expander('View Raw Data'):
    st.dataframe(filtered_df)