#!/usr/bin/env python3

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pyexasol
import os
from configparser import ConfigParser


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


result = query(
    """
    select distinct a.account_uuid, a.company, amount from costs_per_account c, accounts a
    where c.account_uuid = a.account_uuid OR c.account_uuid = "UNATTRIBUTED
    and start_date = '2025-03-01' and end_date <= '2025-04-01'
    """
)
data = [{"account_uuid": row[0], "company": row[1], "amount": float(row[2])} for row in result]
print(type(data[0]["amount"]))

# Convert data to a DataFrame
df = pd.DataFrame(data)

# Streamlit app
st.title("AWS Costs Dashboard")

# Sorting options
sort_by = st.radio("Sort by:", ["Company Name", "Amount"])

# Sort the DataFrame
if sort_by == "Company Name":
    df = df.sort_values("company")
else:
    df = df.sort_values("amount", ascending=True)

# Display the sorted data
st.write("### Sorted Data")
st.dataframe(df)

# Create a horizontal bar graph
fig, ax = plt.subplots(figsize=(15, 30))
ax.barh(df["company"], df["amount"], color="skyblue")
ax.set_xlabel("Amount")
ax.set_ylabel("Account")
ax.set_title("AWS Costs by Account")
st.pyplot(fig)
