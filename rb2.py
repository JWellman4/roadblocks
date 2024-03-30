import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Roadblock Trend Report",
    page_icon=	":volcano:",
    layout="wide",
)

@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# Load the data & create week columns
df = load_data('Roadblocks.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['Week'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)
my_tickvals = df['Week'].tolist()
my_ticktext = [wd.strftime("%b %d, %Y") for wd in my_tickvals]

# Adding Select All and Controling Filters
def add_select_all_option(options_data):
    options_with_select_all = ['Select All'] + options_data
    return options_with_select_all

def options_select():
    if "selected_options" in st.session_state:
        if "Select All" in st.session_state["selected_options"]:
            st.session_state["selected_options"] = [available_options[0]]
            st.session_state["max_selections"] = 1
        else:
            st.session_state["max_selections"] = len(available_options)

# Load options from a CSV file
options_data = df['Incident Waste Group'].unique().tolist()
options_with_select_all = add_select_all_option(options_data)
available_options = options_with_select_all

if "max_selections" not in st.session_state:
    st.session_state["max_selections"] = len(available_options)

# Creating the Sidebar
with st.sidebar:
    st.sidebar.title('Select Fitlers')
    min_date = min(df['Date'])
    max_date = max(df['Date'])
    select_week = st.date_input(
        label='Select Date(s)',
        value=(min_date, max_date),
    )
    select_options =st.multiselect(
        label='Select Roadblock(s)',
        options=options_with_select_all,
        key="selected_options",
        max_selections=st.session_state["max_selections"],
        on_change=options_select,
        format_func=lambda x: "Select All" if x == "Select All" else f"{x}",
    )
    st.markdown("**:violet[Roadblocks]** are **:violet[obstacles]** that keep your team from **performing**\
                at it's **peak**. Look at which ones are blocking your performance,\
                and **:violet[remove them]**!")

# Convert select_week to datetime64[ns]
start_date = pd.to_datetime(select_week[0])

# Check if select_week contains at least two elements before accessing the second element
if len(select_week) > 1:
    end_date = pd.to_datetime(select_week[1])
else:
    end_date = start_date

# Filter DataFrame based on selected options from both multiselects
if 'Select All' in select_options:
    df_filtered = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
else:
    df_filtered = df[df['Incident Waste Group'].isin(select_options) & (df['Date'] >= start_date) & (df['Date'] <= end_date)]

# Grouping and Calculations
filtered_df_grouped = df_filtered.groupby(by=['Incident Waste Group'], as_index=False)['Waste Hours'].sum()
top5_WasteHrs = filtered_df_grouped.head(5)
filtered_df_grouped_sum = df_filtered.groupby(by=['Week'], as_index=False)['Waste Hours'].sum()
filtered_df_grouped_cost = df_filtered.groupby(by=['Incident Waste Group'], as_index=False)['Cost'].sum()
top5_Cost = filtered_df_grouped_cost.head(5)

#Cards
cost_card = df_filtered['Cost'].sum()
formatted_cost = "${:,.2f}".format(cost_card)
hours_card = df_filtered['Waste Hours'].sum()
formatted_hours = "{:,.1f}".format(hours_card)

# Creating Charts to be Displayed
def top5hrs_bar_chart():
    fig = px.bar(
        top5_WasteHrs,
        x='Waste Hours',
        y='Incident Waste Group',
        width=500,
        height=300,
        color='Waste Hours', color_continuous_scale=px.colors.sequential.Sunsetdark,
        labels={'Incident Waste Group': '', 'Waste Hours': 'Hours'},
        orientation='h',
        title='Top 5 Roadblocks based on Hrs'
    )
    fig.update_xaxes(title='')
    fig.update_traces(hovertemplate= '%{x:,.1f} Hrs')
    fig.update_layout( yaxis={'categoryorder':'total ascending'}, hovermode="y")
    st.plotly_chart(fig, use_container_width=True)

fig2 = px.bar(
        filtered_df_grouped_sum,
        x='Week',
        y='Waste Hours',
        color='Waste Hours', color_continuous_scale=px.colors.sequential.Sunsetdark,
        labels={'Waste Hours': 'Hours'},
        title='Roadblock Hrs by Week'
    )
fig2.update_traces(hovertemplate= 'Week %{x} <br> %{y} Hrs')
fig2.update_xaxes(title='',
        tickangle=-45, 
        tickvals=my_tickvals,
        ticktext=my_ticktext)
fig2.update_traces(hovertemplate= '%{y:,.1f} Hrs')

def top5cost_bar_chart():
    fig = px.bar(
        top5_Cost,
        x='Cost',
        y='Incident Waste Group',
        width=500,
        height=300,
        color='Cost', color_continuous_scale=px.colors.sequential.Sunsetdark,
        labels={'Incident Waste Group': '', 'Cost': 'Cost'},
        orientation='h',
        title='Top 5 Roadblocks based on Cost'
    )
    fig.update_xaxes(title='',tickprefix='$',tickformat=',.0f')
    fig.update_traces(hovertemplate= '%{x}')
    fig.update_layout( yaxis={'categoryorder':'total ascending'}, hovermode="y")
    st.plotly_chart(fig, use_container_width=True)

# Create layout using st.columns
st.header("Find the Roadblocks Preventing Productivity")

col1, col2 = st.columns(2)
row1 = st.columns(1)
for col in row1:
    with col1:
        st.metric(label='Total Hours of Roadblocks', value=formatted_hours)
    with col2:
        st.metric(label='Total Cost of Roadblocks', value=formatted_cost)

row2 = st.columns(1)    
for col in row2:
    with col1:
        with st.popover("Top 5 Hrs"):
            top5hrs_bar_chart()
    with col2:
        with st.popover('Top 5 Cost'):
            top5cost_bar_chart()

st.plotly_chart(fig2, use_container_width=True)
