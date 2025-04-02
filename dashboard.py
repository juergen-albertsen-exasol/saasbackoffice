#!/usr/bin/env python3

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pyexasol
import os
from configparser import ConfigParser
from datetime import datetime, timedelta


# Set the page layout to wide
st.set_page_config(layout="wide")

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), ".exasolrc"))

DB_DSN = config.get("connection", "dsn")
DB_USER = config.get("connection", "user")
DB_PASSWORD = config.get("connection", "password")
DB_SCHEMA = config.get("connection", "schema")


def with_connection(callback):
    connection = None
    try:
        connection = pyexasol.connect(
            dsn=DB_DSN, user=DB_USER, password=DB_PASSWORD, schema=DB_SCHEMA
        )
        return callback(connection)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if connection:
            connection.close()


def query(query):
    def execute_query(connection):
        result = connection.execute(query)
        return [row for row in result]

    return with_connection(execute_query)


def convert_row_to_dict(row):
    dict = {"account_uuid": row[0], "company": row[1], "amount": float(row[2])}
    comnpany = dict["company"]
    if comnpany:
        dict["account"] = comnpany
    else:
        dict["account"] = dict["account_uuid"]
    return dict


# Helper function to get the last 12 months
def get_last_12_months():
    today = datetime.today()
    first_of_this_month = today.replace(day=1)
    months = [
        (first_of_this_month - timedelta(days=30 * i)).strftime("%Y-%m")
        for i in range(12)
    ]
    return months[::-1]  # Reverse to show oldest first


# Get the last 12 months and set the default to the last full month
last_12_months = get_last_12_months()
default_month = last_12_months[-2]  # Second-to-last month (last full month)

# Add a select box for the month
selected_month = st.selectbox("Select Month", last_12_months, index=len(last_12_months) - 2)

# Calculate start_date and end_date based on the selected month
start_date = f"{selected_month}-01"
end_date = (
    datetime.strptime(start_date, "%Y-%m-%d").replace(day=28) + timedelta(days=4)
).strftime("%Y-%m-01")

# Query the database
result = query(
    f"""
    SELECT DISTINCT c.account_uuid, a.company, c.amount 
    FROM costs_per_account c
    LEFT JOIN accounts a
    ON c.account_uuid = a.account_uuid
    WHERE start_date = '{start_date}' AND end_date <= '{end_date}'
    ORDER BY c.amount DESC
    """
)
data = [convert_row_to_dict(row) for row in result]
if not data:
    st.write("No Data for This Period.")
    st.stop() 


# Convert data to a DataFrame
df = pd.DataFrame(data)

# Streamlit app
st.title(f"AWS Costs Dashboard: {selected_month}")

# Sorting options
sort_by = st.radio("Sort by:", ["Amount", "Account"])

# Sort the DataFrame
if sort_by == "Account":
    df = df.sort_values("account")
else:
    df = df.sort_values("amount", ascending=False)

# Display the sorted data
st.write("### Sorted Data")
st.dataframe(df, use_container_width=True)  # Use full width for the table

# Create a horizontal bar graph
fig, ax = plt.subplots(figsize=(15, 30))
ax.barh(df["account"], df["amount"], color="skyblue")
ax.set_xlabel("Amount")
ax.set_ylabel("Account")
ax.set_title(f"AWS Costs by Account for {selected_month}")
ax.invert_yaxis()
st.pyplot(fig)
