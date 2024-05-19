import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Sample SuperStore EDA")

# fl = st.file_uploader(":file_folder: Upload a file",type=(["csv"]))
dataset_path = "D:/Data_science/Interactive_Dashboard_Project/Sample - Superstore.csv"
df = pd.read_csv(dataset_path, encoding = "ISO-8859-1")
st.header(f"Dataset: {dataset_path}")
# Assuming df is your DataFrame and "Order Date" is the relevant column
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()
startDate_date = startDate.date()
endDate_date = endDate.date()
st.sidebar.header("Choose your filter: ")

#Data input with constrains
date1 = st.sidebar.date_input("Select Start Order Date", startDate_date, min_value=startDate_date, max_value=endDate_date)

date2 = st.sidebar.date_input("Select End Order Date", endDate_date, min_value=startDate_date, max_value=endDate_date)

# Filter data
step = True
if date1:
    date1_timestamp = pd.to_datetime(date1)  # Chuyển đổi chuỗi ngày tháng thành đối tượng thời gian
    step = step & (pd.to_datetime(df["Order Date"]) >= date1_timestamp)
if date2:
    date2_timestamp = pd.to_datetime(date2)  # Chuyển đổi chuỗi ngày tháng thành đối tượng thời gian
    step = step & (pd.to_datetime(df["Order Date"]) <= date2_timestamp)
df_region = df[step]
selected_regions = st.sidebar.multiselect("Pick your Region", df_region["Region"].unique())

step = True
if date1:
    date1_timestamp = pd.to_datetime(date1)  # Chuyển đổi chuỗi ngày tháng thành đối tượng thời gian
    step = step & (pd.to_datetime(df["Order Date"]) >= date1_timestamp)
if date2:
    date2_timestamp = pd.to_datetime(date2)  # Chuyển đổi chuỗi ngày tháng thành đối tượng thời gian
    step = step & (pd.to_datetime(df["Order Date"]) <= date2_timestamp)
if selected_regions:
    step = step & df["Region"].isin(selected_regions)
df_state = df[step]
selected_states = st.sidebar.multiselect("Pick your State", df_state["State"].unique())
filter_button = st.sidebar.button("Apply Filters", type='primary')
status = None

#CHAINING FILTER
step = True
if filter_button:
    if date1 > date2:
        st.error("Start Date cannot be greater than End Date")
    else:
        step = (pd.to_datetime(df["Order Date"]) >= pd.to_datetime(date1)) & (pd.to_datetime(df["Order Date"]) <= pd.to_datetime(date2))
        status = "Filtered_date"

        if selected_states:
            step = step & df["State"].isin(selected_states)
        if selected_regions:
            step = step & df["Region"].isin(selected_regions)

        if status == "Filtered_date":
            final_filtered_df = df[step]
            col1, col2,col3 = st.columns([1,1,1])
            with col1:
                with st.expander("View Data"):
                    st.write(final_filtered_df)
            with col2:
                st.subheader('Region wise Sales')
                region = final_filtered_df.groupby(by = ["Region"], as_index = False)["Sales"].sum()
                st.write(region.style.background_gradient(cmap="Oranges"))
            with col3:
                st.subheader('State wise Sales')
                state = final_filtered_df.groupby(by = ["Region","State"], as_index = False)["Sales"].sum()
                st.write(state.style.background_gradient(cmap="Oranges"))

            chart1, chart2 = st.columns((2))
            with chart1:
                st.subheader('Segment wise Sales')
                fig = px.pie(final_filtered_df, values = "Sales", names = "Segment", template = "plotly_dark")
                fig.update_traces(text = final_filtered_df["Segment"], textposition = "inside")
                st.plotly_chart(fig,use_container_width=True)

            with chart2:
                st.subheader('Category wise Sales')
                fig = px.pie(final_filtered_df, values = "Sales", names = "Category", template = "gridon")
                fig.update_traces(text = final_filtered_df["Category"], textposition = "inside")
                st.plotly_chart(fig,use_container_width=True)
            st.subheader('Time Series Analysis')

            final_filtered_df["month_year"] = pd.to_datetime(final_filtered_df['Order Date']).dt.strftime("%Y : %b")
            linechart = final_filtered_df.groupby(["month_year"])["Sales"].sum().reset_index()

            # Sort by month_year in datetime format for proper order
            linechart['month_year'] = pd.to_datetime(linechart['month_year'], format='%Y : %b')
            linechart = linechart.sort_values('month_year')
            linechart['month_year'] = linechart['month_year'].dt.strftime('%Y : %b')

            # Create and display the line chart
            fig2 = px.line(linechart, x='month_year', y='Sales', labels={'Sales': 'Amount'}, height=500, width=1000, template='gridon')
            st.plotly_chart(fig2, use_container_width=True)

            st.subheader("Hierarchical view of Sales using TreeMap")
            fig3 = px.treemap(final_filtered_df, path = ["Region","State","Category","Sub-Category"], values = "Sales",hover_data = ["Sales"],
                            color = "Sub-Category")
            fig3.update_layout(width = 800, height = 650)
            st.plotly_chart(fig3, use_container_width=True)
        

        else:
            st.error("Error occurred. Can not filter data")
