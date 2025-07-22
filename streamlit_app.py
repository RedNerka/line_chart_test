import streamlit as st
import pandas as pd
import math
from pathlib import Path
import altair as alt
import time
from streamlit_autorefresh import st_autorefresh
import os

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Future YTM Realtime Monitor',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'plot_data/plot_data.csv'
    raw_df = pd.read_csv('https://raw.githubusercontent.com/RedNerka/line_chart_test/refs/heads/main/plot_data/plot_data.csv')
    # MIN_YEAR = 1960
    # MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    # gdp_df = raw_df.melt(
    #     ['Country Code'],
    #     [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
    #     'Year',
    #     'GDP',
    # )

    # # Convert years from string to integers
    # gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

    return raw_df

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
# '''
# # :earth_americas: GDP dashboard

# Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
# notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
# But it's otherwise a great (and did I mention _free_?) source of data.
# '''

# Add some spacing
# ''
# ''
st_autorefresh(interval=15 * 1000, key="data-refresh")

if int(time.time()) % 60 < 2:  # 每分钟拉一次
    os.system("git pull origin main")

raw_df = get_gdp_data()

min_value = 3000
max_value = len(raw_df)

# selected_countries = st.multiselect(
#     'Which product would you like to view?',
#     ['ZB', 'ZN'],
#     ['ZB', 'ZN'])

# ''
# ''
# ''

st.header('Realtime YTM', divider='gray')

''

count = st.slider(
    'How many data points to show? 4800~5400 points per day',
    min_value=min_value,
    max_value=max_value,
    value=5400)

filtered_df = raw_df.iloc[-count:]

placeholder_1 = st.empty()
placeholder_2 = st.empty()

line_chart = alt.Chart(filtered_df).mark_line().encode(
    x=alt.X('idx:Q', title='时间'),
    y=alt.Y('ytm_diff:Q', title='息差', scale=alt.Scale(nice=True, zero=False)),
    tooltip=[
        alt.Tooltip('time:N', title='时间'),
        alt.Tooltip('ytm_diff:Q', title='息差')
    ]
).interactive()
with placeholder_1:
    st.altair_chart(line_chart, use_container_width=True)

''

line_chart_2 = alt.Chart(filtered_df).mark_line().encode(
    x=alt.X('idx:Q', title='时间'),
    y=alt.Y('ytm_diff_norm:Q', title='标准化息差', scale=alt.Scale(nice=True, zero=False)),
    tooltip=[
        alt.Tooltip('time:N', title='时间'),
        alt.Tooltip('ytm_diff_norm:Q', title='标准化息差')
    ]
).interactive()
with placeholder_2:
    st.altair_chart(line_chart_2, use_container_width=True)


# first_year = gdp_df[gdp_df['Year'] == from_year]
# last_year = gdp_df[gdp_df['Year'] == to_year]

# st.header(f'GDP in {to_year}', divider='gray')

# ''

# cols = st.columns(4)

# for i, country in enumerate(selected_countries):
#     col = cols[i % len(cols)]

#     with col:
#         first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
#         last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

#         if math.isnan(first_gdp):
#             growth = 'n/a'
#             delta_color = 'off'
#         else:
#             growth = f'{last_gdp / first_gdp:,.2f}x'
#             delta_color = 'normal'

#         st.metric(
#             label=f'{country} GDP',
#             value=f'{last_gdp:,.0f}B',
#             delta=growth,
#             delta_color=delta_color
#         )
