import duckdb
import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px

DB_PATH = "data/warehouse.duckdb"

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "E-Com Data Platform"


# ── DB Helper ─────────────────────────────────────
def query(sql: str) -> pd.DataFrame:
    con = duckdb.connect(DB_PATH)
    df = con.execute(sql).df()
    con.close()
    return df


# ── Layout ─────────────────────────────────────────
app.layout = html.Div([
    html.Div([
        html.H1("E-Commerce Data Platform"),
        html.P("Powered by Kafka · DuckDB · dbt"),
    ]),

    dcc.Tabs(id="tabs", value="overview", children=[
        dcc.Tab(label="Overview", value="overview"),
        dcc.Tab(label="Customer 360", value="customer360"),
        dcc.Tab(label="Products", value="products"),
        dcc.Tab(label="Transactions", value="transactions"),
    ]),

    html.Div(id="page-content")
])


# ── Router ─────────────────────────────────────────
@app.callback(Output("page-content", "children"), Input("tabs", "value"))
def render(tab):
    if tab == "overview":
        return overview_page()
    if tab == "customer360":
        return customer360_page()
    if tab == "products":
        return products_page()
    if tab == "transactions":
        return transactions_page()


# ── Overview ───────────────────────────────────────
def overview_page():
    try:
        rev = query("""
            SELECT round(sum(amount_inr - discount_inr)/1e7,2) as r
            FROM silver_transactions
        """)

        orders = query("""
            SELECT count(distinct order_id) as o
            FROM silver_transactions
        """)

        custs = query("""
            SELECT count(distinct customer_id) as c
            FROM silver_transactions
        """)
    except Exception as e:
        return html.P(f"Error: {e}", style={"color": "red"})

    return html.Div([
        html.H3("Overview"),
        html.P(f"Revenue: ₹{rev['r'].iloc[0]} Cr"),
        html.P(f"Orders: {int(orders['o'].iloc[0])}"),
        html.P(f"Customers: {int(custs['c'].iloc[0])}")
    ])


# ── Customer 360 ───────────────────────────────────
def customer360_page():
    try:
        df = query("SELECT * FROM gold_customer_360 LIMIT 50")
    except Exception as e:
        return html.P(f"Error: {e}", style={"color": "red"})

    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        page_size=10
    )


# ── Products ───────────────────────────────────────
def products_page():
    try:
        df = query("""
            SELECT
                category,
                avg(rating) as avg_rating,
                count(*) as total_reviews
            FROM silver_reviews
            GROUP BY category
        """)
    except Exception as e:
        return html.P(f"Error: {e}", style={"color": "red"})

    fig = px.bar(df, x="category", y="avg_rating", title="Average Rating by Category")
    return dcc.Graph(figure=fig)


# ── Transactions ───────────────────────────────────
def transactions_page():
    try:
        df = query("""
            SELECT
                payment_type,
                sum(amount_inr - discount_inr) as revenue
            FROM silver_transactions
            GROUP BY payment_type
        """)
    except Exception as e:
        return html.P(f"Error: {e}", style={"color": "red"})

    fig = px.pie(df, names="payment_type", values="revenue", title="Revenue by Payment Type")
    return dcc.Graph(figure=fig)


# ── Run ────────────────────────────────────────────
if __name__ == "__main__":
    print("Dashboard running at http://localhost:8050")
    app.run(debug=True, port=8050)