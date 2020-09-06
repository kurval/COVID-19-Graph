#!/usr/bin/python3
import datadotworld as dw
import pandas as pd
import streamlit as st
import altair as alt
import click
from PIL import Image
from Functions.graph_functions import show_most_cases, compare_countries, show_world_scatter, continent_cases
from Functions.option_functions import choose_chart,choose_chart_type, choose_time_period

DATASET_ID = 'vale123/covid-19-complete-dataset'

QUERY = """
        SELECT continent,
        location,
        date,
        total_cases,
        total_deaths,
        new_cases,
        new_deaths,
        new_cases_per_million,
        new_deaths_per_million
        FROM owid_covid_data
        WHERE location != 'International'
        """

# Cache for 6 hours
@st.cache(ttl=3600*6, show_spinner=False)
def import_data():
    '''
    Imports data from dataworld.
    Query a dataset using the var = datadotworld.query('dataset_ID', 'query')
    '''
    result = dw.query(
        DATASET_ID,
        QUERY
    )
    df = result.dataframe
    df['date'] = pd.to_datetime(df['date'])
    floats = df.select_dtypes(include=['float64']).columns.tolist()
    df[floats] = df[floats].astype('float32')
    return df

def main():
    st.beta_set_page_config(
        page_title="COVID-19 STATISTICS", 
        page_icon=":globe_with_meridians:"
    )

    with st.spinner('Please wait...'):
        df = import_data()
        
    labels = {
        '1':'total_cases',
        '2':'total_deaths',
        '3':'new_cases',
        '4':'new_deaths',
        '5':'new_cases_per_million',
        '6':'new_deaths_per_million'
    }

    st.sidebar.markdown("# Choose statistics")
    graph = st.sidebar.radio("Chart:",
        ("Country compare",
        "Worst-hit countries",
        "Cases by continent",
        "Cases worldwide")
    )

    # Header image with timestamp
    youngest = max(df['date'])
    oldest = min(df['date'])
    image = Image.open('./Images/header.png')
    st.image(
        image, 
        use_column_width=True, 
        caption=f"Updated: {youngest.strftime('%Y-%m-%d')}"
    )
    
    # Compare countries chart
    if (graph == "Country compare"):
        chart = choose_chart()
        chart_type = choose_chart_type()
        countries = df['location'].unique()
        log = False
        stack = False
        slot_for_checkbox = st.empty()
        # Reordering figure to show here
        slot_for_graph = st.empty()

        startdate, period = choose_time_period(youngest, oldest, 1)
        st.sidebar.markdown("# Select countries")
        options = st.sidebar.multiselect(
                'Countries:', 
                list(countries), 
                default=['Finland']
        )
        if chart_type == '1':
            log = slot_for_checkbox.checkbox(
                "Logarithmic scale", 
                value=False
            )
        else:
            stack = slot_for_checkbox.checkbox(
                "Stack values", 
                value=True
            ) if len(options) > 1 else False
        fig = compare_countries(df, labels[chart], chart_type, startdate, options, period, log, stack)
        slot_for_graph.altair_chart(fig, use_container_width=True)

    # Worst-hit countries charts
    if (graph == "Worst-hit countries"):
        st.markdown("""
        ## COVID-19: total confirmed cases and deaths in the worst-hit countries
        """)
        rate_m = st.checkbox('Per one million of population', value=False)
        label1 = labels['5'] if rate_m else labels['3']
        label2 = labels['6'] if rate_m else labels['4']
        slot_for_date = st.empty()
        startdate, period = choose_time_period(youngest, oldest, 2)
        date = startdate.strftime('%Y-%m-%d')
        slot_for_date.markdown(f'***Date {date}***')

        fig = show_most_cases(df, startdate, label1)
        st.altair_chart(fig, use_container_width=True)
        fig = show_most_cases(df, startdate, label2)
        st.altair_chart(fig, use_container_width=True)

    # Cases by continent
    if (graph == "Cases by continent"):
        st.markdown("""
        ## COVID-19: new confirmed cases by continent\n
        Hover over each area to see the values
        """)
        fig = continent_cases(df, labels['3'])
        st.altair_chart(fig, use_container_width=True)

    # World scatter plot
    if (graph == "Cases worldwide"):
        st.markdown("""
        ## COVID-19: new confirmed cases worldwide 🌐\n
        Hover over each circle to see the values
        """)
        fig = show_world_scatter(df, labels['3'])
        st.altair_chart(fig, use_container_width=True)

    ##Tips info text
    st.sidebar.markdown("# Tips")
    if (graph == "Country compare"):
        info_text = """
        **Use the sidebar** to select or deselect countries.\n
        **Compare countries** by selecting multiple options.\n
        **Choose the type of the statistics** from the select box.\n
        **Adjust time period** by dragging the slider or just clicking it.\n
        **Hover over** each line/block to see the values.
        """
    elif (graph == "Worst-hit countries"):
        info_text = """
        **Adjust time period** by dragging the slider or just clicking it.\n
        **By clicking the checkbox** you can see the values per one million of population.\n
        **Hover over** each line/block to see the values.
        """
    elif (graph == "Cases by continent"):
        info_text = """
        **Hover over** each line/block to see the values.
        """
    elif (graph == "Cases worldwide"):
        info_text = """
        **Hover over** each area to see the values.
        """
    st.sidebar.info(info_text)

    #About info text
    st.sidebar.markdown("# About")
    st.sidebar.info("""
    **This project's mission** is to transform COVID-19 data into understandable and shareable visuals.
    Data also needs to be reliable and up-to-date throughout the duration of the COVID-19 pandemic.\n
    This app is maintained by [*Valtteri Kurkela*](https://github.com/kurval) and 
    data is sourced from [**Our World in Data**](https://ourworldindata.org/coronavirus).
    """)

    st.info("""
    ℹ️ You can select different statistics from the sidebar on the left corner.
    """)

    # Footer info
    st.markdown("""
    by: *V.Kurkela* | source: [Github](https://github.com/kurval/COVID-19-Statistics) |
    data source: [Dataworld](https://data.world/vale123/covid-19-complete-dataset)
    (orginally: [Ourworldindata](https://ourworldindata.org/coronavirus-source-data))
    """)

if __name__ == "__main__":
    main()
