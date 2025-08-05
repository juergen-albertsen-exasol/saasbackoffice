import streamlit as st
import pandas as pd
import plotly.express as px
import pyexasol
from configparser import ConfigParser
import os


config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), ".exasolrc"))
DB_DSN = config.get("connection", "dsn")
DB_USER = config.get("connection", "user")
DB_PASSWORD = config.get("connection", "password")
DB_SCHEMA = config.get("connection", "schema")


def query_database(query, params=None):
    connection = pyexasol.connect(
        dsn=DB_DSN, user=DB_USER, password=DB_PASSWORD, schema=DB_SCHEMA
    )
    try:
        return connection.export_to_pandas(query, query_params=params)
    finally:
        connection.close()


# Streamlit app setup
st.set_page_config(page_title="AWS Cost Dashboard", layout="wide")
st.title("AWS Cost Dashboard")

# Date pickers
start_date = st.date_input("Select Start Date")
end_date = st.date_input("Select End Date")

if start_date and end_date:
    # Query company cost data
    query = """
        SELECT COMPANY, SUM(COST) AS TOTAL_COST
        FROM AWS_COST_REPORT
        WHERE START_DATE >= {start_date} AND START_DATE <= {end_date}
        GROUP BY COMPANY
        ORDER BY TOTAL_COST DESC
    """
    params = {"start_date": start_date, "end_date": end_date}
    company_cost_df = query_database(query, params)

    if not company_cost_df.empty:
        # Display company cost table
        selected_company = st.selectbox(
            "Select a Company", company_cost_df["COMPANY"]
        )

        # Query cost category data for the selected company
        if selected_company:
            query = """
                SELECT COST_CATEGORY, SUM(COST) AS TOTAL_COST
                FROM AWS_COST_REPORT
                WHERE COMPANY = {company}
                GROUP BY COST_CATEGORY
            """
            params = {"company": selected_company}
            cost_category_df = query_database(query, params)

            if not cost_category_df.empty:
                cost_category_df["PERCENTAGE"] = (
                    cost_category_df["TOTAL_COST"]
                    / cost_category_df["TOTAL_COST"].sum()
                ) * 100
                cost_category_df["LABEL"] = (
                    cost_category_df["COST_CATEGORY"]
                    + " ("
                    + cost_category_df["PERCENTAGE"].round(2).astype(str)
                    + "%)"
                )

                # Display treemap
                fig = px.treemap(
                    cost_category_df,
                    path=["LABEL"],
                    values="TOTAL_COST",
                    title=f"Cost Distribution for {selected_company}",
                )
                st.plotly_chart(fig, use_container_width=True)
        return []
    query = """
        SELECT COMPANY, SUM(COST) AS TOTAL_COST
        FROM AWS_COST_REPORT
        WHERE START_DATE >= {start_date} AND START_DATE <= {end_date}
        GROUP BY COMPANY
        ORDER BY TOTAL_COST DESC
    """
    params = {"start_date": start_date, "end_date": end_date}
    df = query_database(query, params)
    return df.to_dict("records")


@app.callback(
    Output("cost-treemap", "figure"),
    [Input("company-cost-table", "selected_rows"), Input("company-cost-table", "data")],
)
def update_cost_treemap(selected_rows, table_data):
    if not selected_rows or not table_data:
        return None  # Do not show any graph
    selected_company = table_data[selected_rows[0]]["COMPANY"]
    query = """
        SELECT COST_CATEGORY, SUM(COST) AS TOTAL_COST
        FROM AWS_COST_REPORT
        WHERE COMPANY = {company}
        GROUP BY COST_CATEGORY
    """
    params = {"company": selected_company}
    df = query_database(query, params)
    if df.empty:
        return None  # Do not show any graph
    df["PERCENTAGE"] = (df["TOTAL_COST"] / df["TOTAL_COST"].sum()) * 100
    df["LABEL"] = df["COST_CATEGORY"] + " (" + df["PERCENTAGE"].round(2).astype(str) + "%)"
    return px.treemap(
        df,
        path=["LABEL"],
        values="TOTAL_COST",
        title=f"Cost Distribution for {selected_company}",
    ).update_traces(
        hovertemplate="<b>%{label}</b><br>Total Cost: %{value}<extra></extra>"
    )


if __name__ == "__main__":
    app.run(debug=True)
