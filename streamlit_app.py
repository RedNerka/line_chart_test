import streamlit as st
import pandas as pd
import math
from pathlib import Path
import altair as alt
import time

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Future YTM Realtime Monitor',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'plot_data/plot_data.csv'
    raw_df = pd.read_csv(DATA_FILENAME)

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
'''
# :earth_americas: GDP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
'''

# Add some spacing
# ''
# ''

# min_value = raw_df['Year'].min()
# max_value = raw_df['Year'].max()

# from_year, to_year = st.slider(
#     'What time range are you interested in?',
#     min_value=min_value,
#     max_value=max_value,
#     value=[min_value, max_value])

# selected_countries = st.multiselect(
#     'Which product would you like to view?',
#     ['ZB', 'ZN'],
#     ['ZB', 'ZN'])

# ''
# ''
# ''

# Filter the data
# filtered_gdp_df = gdp_df[
#     (gdp_df['Country Code'].isin(selected_countries))
#     & (gdp_df['Year'] <= to_year)
#     & (from_year <= gdp_df['Year'])
# ]

st.header('Realtime YTM', divider='gray')

''

# st.line_chart(
#     raw_df,
#     x='idx',
#     y='ytm_diff',
#     x_label='time',
#     color='Country Code',
# )
raw_df = get_gdp_data()

line_chart = alt.Chart(raw_df).mark_line().encode(
    x=alt.X('idx:Q', title='时间'),
    y=alt.Y('ytm_diff:Q', title='YTM息差')
)

points = alt.Chart(raw_df).mark_circle(opacity=0).encode(
    x='idx:Q',
    y='ytm_diff:Q',
    tooltip=[
        alt.Tooltip('time:N', title='时间'),
        alt.Tooltip('ytm_diff:Q', title='YTM 差值'),
        alt.Tooltip('idx:Q', title='数据点索引')
    ]
).interactive()

nearest = alt.selection(type='single', nearest=True, on='mouseover', fields=['date'], empty='none')

selectors = alt.Chart(raw_df).mark_point().encode(
    x='idx:Q',
    opacity=alt.value(0)
).add_selection(
    nearest
)

rules = alt.Chart(raw_df).mark_rule(color='gray').encode(
    x='idx:Q',
).transform_filter(nearest)

points = alt.Chart(raw_df).mark_circle().encode(
    x='idx:Q',
    y='ytm_diff:Q'
).transform_filter(nearest)

text = alt.Chart(raw_df).mark_text(align='left', dx=5, dy=-5).encode(
    x='idx:Q',
    y='ytm_diff:Q',
    text='ytm_diff:Q'
).transform_filter(nearest)

chart = alt.layer(line_chart, selectors, points, rules, text).interactive()

st.altair_chart(chart, use_container_width=True)


# ''
# ''


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
