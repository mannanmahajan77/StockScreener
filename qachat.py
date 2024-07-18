import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# Load company data
def load_company_data():
    return pd.read_csv('Contests/data.csv')

# Search for companies based on user input
def search_companies(query, df):
    return df[df['company'].str.contains(query, case=False, na=False) | df['symbol'].str.contains(query, case=False, na=False)]

def main():
    # Add CSS
    st.markdown(
        """
        <style>
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-color: #f0f3f5;
            padding: 20px;
            border-right: 1px solid #d1d8de;
        }
        .sidebar .sidebar-content input[type="text"], .sidebar .sidebar-content input[type="date"] {
            background-color: #ffffff;
            border: 1px solid #d1d8de;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 10px;
            width: 100%;
        }
        .sidebar .sidebar-content input[type="text"]:focus, .sidebar .sidebar-content input[type="date"]:focus {
            border-color: #00aaff;
            box-shadow: 0 0 5px rgba(0, 170, 255, 0.5);
        }
        .stButton button {
            background-color: #007bff;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 10px;
            margin-top: 10px;
            width: 100%;
        }
        .stButton button:hover {
            background-color: #0056b3;
        }
        /* Main content styling */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            color: #ffffff;
            font-family: 'Helvetica Neue', sans-serif;
        }
        .stMarkdown p {
            color: #ffffff;
            font-family: 'Helvetica Neue', sans-serif;
        }
        .stDataFrame, .stPlotlyChart {
            margin-top: 20px;
        }
        /* Tab styling */
        .stTabs div[role="tab"] {
            background-color: #f0f3f5;
            border: 1px solid #d1d8de;
            border-bottom: none;
            padding: 10px;
            margin-right: 5px;
            cursor: pointer;
        }
        .stTabs div[role="tab"]:hover {
            background-color: #d1d8de;
        }
        .stTabs div[aria-selected="true"] {
            background-color: #ffffff;
            border-bottom: 2px solid #007bff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.title("Stock Data Viewer")

    # Load company data
    df = load_company_data()

    # Search bar for company name or symbol
    query = st.sidebar.text_input("Enter the company name or stock symbol:", "")
    start_date = st.sidebar.date_input('Start Date')
    end_date = st.sidebar.date_input('End Date')

    if query:
        # Fetch company suggestions
        results = search_companies(query, df)
        
        if not results.empty:
            selected_company = st.sidebar.selectbox("Select a company", results['company'])
            selected_symbol = results[results['company'] == selected_company]['symbol'].values[0]
            
            try:
                # Fetch stock data using selected symbol
                stock = yf.Ticker(selected_symbol)
                stock_info = stock.info

                st.header(f"Stock Data for {selected_symbol.upper()}")
                
                # For the graph
                data = yf.download(selected_symbol, start=start_date, end=end_date)
                fig = px.line(data, x=data.index, y='Adj Close', title=selected_symbol)
                st.plotly_chart(fig)

                main, pricing_data = st.tabs(["Main Info", "Pricing Data"])

                with main:
                    # Display important stock data
                    st.write("**Company Name:**", stock_info.get('longName', 'N/A'))
                    st.write("**Sector:**", stock_info.get('sector', 'N/A'))
                    st.write("**Industry:**", stock_info.get('industry', 'N/A'))
                    st.write("**Market Cap:**", stock_info.get('marketCap', 'N/A'))
                    st.write("**Previous Close:**", stock_info.get('previousClose', 'N/A'))
                    st.write("**Open:**", stock_info.get('open', 'N/A'))
                    st.write("**Day's High:**", stock_info.get('dayHigh', 'N/A'))
                    st.write("**Day's Low:**", stock_info.get('dayLow', 'N/A'))
                    st.write("**52 Week High:**", stock_info.get('fiftyTwoWeekHigh', 'N/A'))
                    st.write("**52 Week Low:**", stock_info.get('fiftyTwoWeekLow', 'N/A'))
                    st.write("**Volume:**", stock_info.get('volume', 'N/A'))
                    st.write("**Average Volume:**", stock_info.get('averageVolume', 'N/A'))
                    st.write("**Dividend Yield:**", stock_info.get('dividendYield', 'N/A'))
                    st.write("**Forward PE:**", stock_info.get('forwardPE', 'N/A'))
                    st.write("**Price to Book:**", stock_info.get('priceToBook', 'N/A'))

                with pricing_data:
                    st.header('Price Movements')
                    data2 = data.copy()
                    data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
                    data2.dropna(inplace=True)
                    st.write(data2)
                    annual_return = data2['% Change'].mean() * 252 * 100
                    st.write('Annual return is', annual_return, '%')
                    stdev = np.std(data2['% Change']) * np.sqrt(252)
                    st.write('Standard Deviation is', stdev * 100, '%')
                    st.write('Risk Adjusted Returns is ', annual_return/(stdev*100))

            except Exception as e:
                st.sidebar.error(f"Error fetching data for {selected_symbol.upper()}: {e}")
        else:
            st.sidebar.error("No companies found. Please check your input.")
    else:
        st.sidebar.write("Please enter a company name or stock symbol to search.")

if __name__ == "__main__":
    main()
