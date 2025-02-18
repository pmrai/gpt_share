import streamlit as st
import pandas as pd
import altair as alt

# Set page configuration
st.set_page_config(
    page_title="Bar Chart with Metric (Grid Layout)",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for grey tile, center alignment, and block container adjustments
st.markdown(
    """
    <style>
    /* Grey tile styling */
    .grey-tile {
        background-color: #393939;  /* Grey background */
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        display: flex;
        flex-direction: column;
        align-items: center;  /* Center align content horizontally */
        justify-content: center;  /* Center align content vertically */
        text-align: center;  /* Center align text */
        height: 400px;  /* Fixed height for the tile */
    }

    /* Adjust block container padding and margins */
    [data-testid="block-container"] {
        padding-left: 2rem;
        padding-right: 2rem;
        padding-top: 1rem;
        padding-bottom: 0rem;
        margin-bottom: -7rem;
    }

    /* Adjust vertical block padding */
    [data-testid="stVerticalBlock"] {
        padding-left: 0rem;
        padding-right: 0rem;
    }

    /* Top bar styling */
    .top-bar {
        background-color: #393939;
        color: black;
        padding: 10px;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        width: 100%;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 1000;
    }

    /* Add text next to the hamburger menu */
    .menu-text {
        position: fixed;
        top: 15px;
        left: 60px;
        font-size: 18px;
        color: black;
        z-index: 1000;
    }

    /* Change background color of top bar */
    header[data-testid="stHeader"] {
        background-color: #393939; /* Change to your preferred color */
    }

    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    # Title of the app
    with st.container():
        st.markdown(
            "<div style='background-color: #393930; padding: 10px; border-radius: 0px; text-align: center;'><b>Control Knobs</b></div><br><br>",
            unsafe_allow_html=True
        )

    # First range slider
    values1 = st.slider(
        "Rotation Speed",
        min_value=0,
        max_value=100,
        value=(20, 80),
        step=1,
        help='test',
        key="slider1",
    )
    current_value1, simulated_value1 = values1
    #st.write(f"Current: {current_value1}, Simulated: {simulated_value1}")

    # Second range slider
    values2 = st.slider(
        "Discharge Pressure",
        min_value=0,
        max_value=200,
        value=(50, 150),
        step=5,
        key="slider2",
    )
    current_value2, simulated_value2 = values2

    # Third range slider
    values3 = st.slider(
        "Suction Flow",
        min_value=0.0,
        max_value=1.0,
        value=(0.3, 0.7),
        step=0.1,
        key="slider3",
    )
    current_value3, simulated_value3 = values3

    # Fourth range slider
    values4 = st.slider(
        "DP Circulator Discharge",
        min_value=-100,
        max_value=100,
        value=(-50, 50),
        step=10,
        key="slider4",
    )
    current_value4, simulated_value4 = values4

# Sample data for horizontal bar chart
prod_data = {
    "Category": ['Current', "Simulated"],
    "Value": [current_value1, simulated_value1],  # Use slider values here
}
prod_df = pd.DataFrame(prod_data)

# Metrics for each bar chart
metrics = [
    {"label": "Sales", "value": "$1,234", "delta": "+5%"},
    {"label": "Revenue", "value": "$5,678", "delta": "+10%"},
    {"label": "Profit", "value": "$9,012", "delta": "+15%"},
]

col = st.columns((5, 3), gap='medium')

with col[0]:
    chart = alt.Chart(prod_df).mark_bar().encode(
        x="Value:Q",
        y=alt.Y("Category:N", sort="-x"),
        color=alt.value("#f63366"),
    ).properties(
        width=600,
        height=300,
    )

    with st.container():
        st.markdown(
            "<div style='background-color: #393930; padding: 10px; border-radius: 0px; text-align: left;'><b>Productivity Metric</b></div><br><br>",
            unsafe_allow_html=True
        )
        st.altair_chart(chart, use_container_width=True)

with col[1]:
    st.metric(label=metrics[0]["label"], value=metrics[0]["value"], delta=metrics[0]["delta"])

col = st.columns((5, 3), gap='medium')

with col[0]:
    chart = alt.Chart(prod_df).mark_bar().encode(
        x="Value:Q",
        y=alt.Y("Category:N", sort="-x"),
        color=alt.value("#f63366"),
    ).properties(
        width=600,
        height=300,
    )

    with st.container():
        st.markdown(
            "<div style='background-color: #393930; padding: 10px; border-radius: 0px; text-align: left;'><b>Health Metric</b></div><br><br>",
            unsafe_allow_html=True
        )
        st.altair_chart(chart, use_container_width=True)

with col[1]:
    st.metric(label=metrics[1]["label"], value=metrics[1]["value"], delta=metrics[1]["delta"])

col = st.columns((5, 3), gap='medium')

with col[0]:
    chart = alt.Chart(prod_df).mark_bar(size=50).encode(
        x="Value:Q",
        y=alt.Y("Category:N", sort="-x",axis=alt.Axis(title=None), scale=alt.Scale(bandPaddingInner=0.1)),
        color=alt.value("#f63366"),
    ).properties(
        width=600,
        height=300,
    ).configure_axis(
        grid=False  # Remove grid lines
    )

    with st.container():
        st.markdown(
            "<div style='background-color: #393930; padding: 10px; border-radius: 0px; text-align: left;'><b>Energy Metric</b></div><br><br>",
            unsafe_allow_html=True
        )
        st.altair_chart(chart, use_container_width=True)

with col[1]:
    st.metric(label=metrics[2]["label"], value=metrics[2]["value"], delta=metrics[2]["delta"])