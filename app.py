"""
Name: Rene Hernandez
CS230: Section 3
Data: I Used the AirBnB Boston Data, Specifically the listings.csv, calendar.csv and reviews.csv.gz
URL:
Description: This program uses AirBnB Boston data to display listings in the Boston Metro area, interactive map with prices.
There is also price distribution charts, as well as the top 10 most expensive and least expensive neighbourhoods.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import os

# Dynamically construct paths for the CSV files
listings_csv_path = os.path.join(os.getcwd(), "listings.csv")
calendar_csv_path = os.path.join(os.getcwd(), "calendar.csv")
reviews_csv_path = os.path.join(os.getcwd(), "reviews_1.csv")

# [PY3] Error checking with try/except
@st.cache_data
def load_listings_data():
    try:
        data = pd.read_csv(listings_csv_path)
        data["last_review"] = pd.to_datetime(data["last_review"], errors='coerce')  # [DA1] Clean the data
        return data
    except FileNotFoundError:
        st.error(f"Error: {listings_csv_path} not found!")
        return pd.DataFrame()  # Return an empty DataFrame on error

@st.cache_data
def load_calendar_data():
    try:
        data = pd.read_csv(calendar_csv_path)
        data["date"] = pd.to_datetime(data["date"], errors='coerce')  # [DA1] Clean the data
        data["price"] = data["price"].replace('[\$,]', '', regex=True).astype(float)  # [DA1] Clean the data
        return data
    except FileNotFoundError:
        st.error(f"Error: {calendar_csv_path} not found!")
        return pd.DataFrame()  # Return an empty DataFrame on error

@st.cache_data
def load_reviews_data():
    try:
        data = pd.read_csv(reviews_csv_path)
        data["date"] = pd.to_datetime(data["date"], errors='coerce')  # [DA1] Clean the data
        return data
    except FileNotFoundError:
        st.error(f"Error: {reviews_csv_path} not found!")
        return pd.DataFrame()  # Return an empty DataFrame on error

listings_df = load_listings_data()
calendar_df = load_calendar_data()
reviews_df = load_reviews_data()

# [PY1] A function with two or more parameters, one of which has a default value, called at least twice (once with the default value, and once without)
def filter_listings(df, room_types, neighbourhoods, price_range=(50, 500)):
    return df[
        (df["room_type"].isin(room_types)) &  # [DA5] Filter data by two conditions with AND
        (df["neighbourhood"].isin(neighbourhoods)) &  # [DA5] Filter data by two conditions with AND
        (df["price"] >= price_range[0]) &  # [DA5] Filter data by two conditions with AND
        (df["price"] <= price_range[1])  # [DA5] Filter data by two conditions with AND
    ]

# Test function calls for [PY1] with default parameters
filtered_listings_default = filter_listings(listings_df, ["Entire home/apt"], ["Back Bay"])  # Called with default price range
filtered_listings_custom = filter_listings(listings_df, ["Entire home/apt"], ["Back Bay"], price_range=(100, 400))  # Called with custom price range

# [PY2] A function that returns more than one value
def get_summary_stats(df):
    avg_price = df["price"].mean()  # [DA9] Add a new column or perform calculations on DataFrame columns
    total_reviews = df["number_of_reviews"].sum()  # [DA9] Add a new column or perform calculations on DataFrame columns
    avg_availability = df["availability_365"].mean()  # [DA9] Add a new column or perform calculations on DataFrame columns
    return avg_price, total_reviews, avg_availability  # Return multiple values

# [ST4] Sidebar for user input
st.sidebar.title("Filter Options")
room_types = st.sidebar.multiselect(
    "Select Room Types",
    listings_df["room_type"].unique(),
    default = listings_df["room_type"].unique()
)  # [ST1] Multi-select widget for room types
# [ST4] Custom Fonts
'''
Code for Custom fonts based on code from ChatGPT. See section 1 of accompanying document.
'''


st.markdown(
    """
    <style>
        body {
            font-family: 'Roboto', sans-serif;  # Change to any font family you prefer
        }
        h1, h2, h3 {
            font-family: 'Roboto', sans-serif;  # Specific font for headers
        }
    </style>
    """, unsafe_allow_html=True
)



# [ST1] (Bonus Multi-Select)  for Neighbourhoods
neighbourhood_options = ["ALL"] + list(listings_df["neighbourhood"].unique())

# Sidebar multi-select widget
selected_neighbourhoods = st.sidebar.multiselect(
    "Select Neighbourhoods",
    options=neighbourhood_options,
    default="ALL"  # Default to "ALL"
)

# Handle the "ALL" selection logic
if "ALL" in selected_neighbourhoods:
    filtered_neighbourhoods = listings_df["neighbourhood"].unique()  # Select all neighbourhoods
else:
    filtered_neighbourhoods = selected_neighbourhoods

# Price range slider
price_range = st.sidebar.slider(
    "Select Price Range",
    int(listings_df["price"].min()),
    int(listings_df["price"].max()),
    (50, 500)
)  # [ST2] Slider widget for price range

#[DA4]  Filter data using the function after user input
filtered_listings = filter_listings(listings_df, room_types, filtered_neighbourhoods, price_range)  # [PY1] Function called with custom parameters


# Summary Statistics using the function that returns multiple values
avg_price, total_reviews, avg_availability = get_summary_stats(filtered_listings)
# [MAP] Advanced Map with PyDeck
st.subheader("AirBnB Listings in Boston Metro Area")
layer = pdk.Layer(
    "ScatterplotLayer",
    filtered_listings,
    pickable=True,
    opacity=0.5,
    get_position=["longitude", "latitude"],
    get_radius=100,
    get_color=[200, 30, 0, 160],
)

view_state = pdk.ViewState(
    latitude=listings_df["latitude"].mean(),
    longitude=listings_df["longitude"].mean(),
    zoom=11,
    pitch=50,
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{neighbourhood}\nPrice: ${price}\nReviews: {number_of_reviews}"}

)
st.pydeck_chart(deck)
# Display summary stats
col1, col2, col3 = st.columns(3)
col1.metric("Average Price", f"${avg_price:.2f}")
col2.metric("Total Reviews", total_reviews)
col3.metric("Average Availability", f"{avg_availability:.1f} days")

# [VIZ1] Price Distribution Plot
st.header("Price Distribution")
fig, ax = plt.subplots()
filtered_listings["price"].hist(bins=30, ax=ax, color='skyblue')
ax.set_title("Price Distribution")
ax.set_xlabel("Price")
ax.set_ylabel("Frequency")
st.pyplot(fig)
#[VIZ2] Top 10 Most Expensive neighbourhoods
st.header("Top 10 Most Expensive neighbourhoods")
top_expensive_neighbourhoods = listings_df.groupby("neighbourhood")["price"].mean().sort_values(ascending=False).head(10)
# [DA2] Sort data in ascending or descending order
# [DA3] Top largest (most expensive) values (in price) of Neighbourhoods (column)
fig, ax = plt.subplots()
top_expensive_neighbourhoods.plot(kind="bar", ax=ax, color="red")
ax.set_title("Top 10 Most Expensive neighbourhoods")
ax.set_xlabel("neighbourhood")
ax.set_ylabel("Average Price")
st.pyplot(fig)

#[VIZ3] Top 10 least expensive neighbourhoods
st.header("Top 10 Least Expensive neighbourhoods")
least_expensive_neighbourhoods = listings_df.groupby("neighbourhood")["price"].mean().sort_values(ascending=True).head(10) # [DA2] Sort data in ascending or descending order
fig, ax = plt.subplots()
least_expensive_neighbourhoods.plot(kind="bar", ax=ax, color="green")
ax.set_title("Top 10 Least Expensive neighbourhoods")
ax.set_xlabel("neighbourhood")
ax.set_ylabel("Average Price")
st.pyplot(fig)

# [PY4] A list comprehension: Get list of unique room types
unique_room_types = [room for room in listings_df["room_type"].unique() if "apt" in room.lower()]

# [PY5] neighbourhood statistics using a dictionary (Bonus) I never ended up calling this dictionary because I didn't like how it looked
neighbourhood_counts = {neighbourhood: filtered_listings[filtered_listings["neighbourhood"] == neighbourhood].shape[0] for neighbourhood in filtered_listings["neighbourhood"].unique()}





# Calendar Insights for Listing ID
# Create a custom label that combines listing ID and neighbourhood
filtered_listings["id_neighbourhood"] = filtered_listings["id"].astype(str) + " - " + filtered_listings["neighbourhood"]


# Review Insights
st.header("Review Insights")
# Use the custom label in the dropdown
listing_id_label = st.selectbox(
    "Select a Listing & Neighbourhood",
    filtered_listings["id_neighbourhood"]  # [ST3] Dropdown options with ID and neighbourhood
)


#[DA8] Iterate through rows of a DataFrame with iterrows(). I created the code but I do not see the use to display it.
for index, row in filtered_listings.iterrows():
    listing_id = row["id"]
    room_type = row["room_type"]
    price = row["price"]
    neighbourhood = row["neighbourhood"]


# Extract the actual listing ID from the selected option
selected_listing_id = int(listing_id_label.split(" - ")[0])  # Extract and convert the listing ID to integer



# [VIZ4] (Bonus Table) Display latest reviews for the selected listing
listing_reviews = reviews_df[reviews_df["listing_id"] == int(selected_listing_id)]
st.subheader(f"Latest Reviews for Listing {selected_listing_id}")
latest_reviews = listing_reviews.sort_values("date", ascending=False).head(5)  # [DA2] Sort data in ascending or descending order

# Use st.dataframe for wrapping text in the "comments" column
st.dataframe(
    latest_reviews[["date", "reviewer_name", "comments"]].style.set_properties(
        subset=["comments"],
        **{"white-space": "normal"}  # Ensures text wrapping
    )
)





