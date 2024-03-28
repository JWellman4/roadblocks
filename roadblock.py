import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Roadblock Report",
    page_icon=	":volcano:",
    layout="wide",
)

@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# Load the data
df = load_data('Roadblocks.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['Week'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)
my_tickvals = df['Week'].tolist()
my_ticktext = [wd.strftime("%b %d, %Y") for wd in my_tickvals]

# Creating Defs
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

with st.sidebar:
    st.title('Select Filters')
    select_options =st.multiselect(
            label="Select a Roadblock",
            options=options_with_select_all,
            key="selected_options",
            max_selections=st.session_state["max_selections"],
            on_change=options_select,
            format_func=lambda x: "Select All" if x == "Select All" else f"{x}",
    )

# Filter DataFrame based on selected options from both multiselects
if 'Select All' in select_options:
    df_filtered = df
else:
    df_filtered = df[df['Incident Waste Group'].isin(select_options)]

# Grouping and Calculations
filtered_df_grouped = df_filtered.groupby(by=['Incident Waste Group'], as_index=False)['Waste Hours'].sum()
filtered_df_grouped_sum = df_filtered.groupby(by=['Week'], as_index=False)['Waste Hours'].sum()

# Display selected options
def bar_chart():
    fig = px.bar(
        filtered_df_grouped,
        x='Waste Hours',
        y='Incident Waste Group',
        color='Waste Hours', color_continuous_scale=px.colors.sequential.Sunsetdark,
        labels={'Incident Waste Group': '', 'Waste Hours': 'Hours'},
        orientation='h'
    )
    fig.update_traces(hovertemplate= '%{x} Hrs')
    fig.update_layout( yaxis={'categoryorder':'total ascending'}, hovermode="y")
    st.plotly_chart(fig, use_container_width=True)

fig2 = px.bar(
        filtered_df_grouped_sum,
        x='Week',
        y='Waste Hours',
        width=400,
        height=300,
        color='Waste Hours', color_continuous_scale=px.colors.sequential.Sunsetdark,
        labels={'Waste Hours': 'Hours'},
        title='Roadblock Hrs by Week'
    )
fig2.update_traces(hovertemplate= 'Week %{x} <br> %{y} Hrs')
fig2.update_xaxes(title='',
        tickangle=-45, 
        tickvals=my_tickvals,
        ticktext=my_ticktext)

# Create layout using st.columns
col1, col2 = st.columns([2,3], gap='medium')
with col1:
    st.header("Find the Roadblocks that are hindering your productivity")
    st.markdown("**:violet[Roadblocks]** are **:violet[obstacles]** that keep your team from **performing**\
                at it's **peak**. Look at which ones are blocking your performance,\
                and **:violet[remove them]**!")
    with st.popover("Discover Weekly Trend"):
        st.plotly_chart(fig2, use_container_width=True)

with col2:
    bar_chart()
