# Import necessary libraries
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os

# Function to convert matplotlib figure to base64 string
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# Set display options for pandas
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# Create Airbnb ticker object
abnb = yf.Ticker('ABNB')

# Get various financial data
income_stmt = abnb.income_stmt
balance_sheet = abnb.balance_sheet
cash_flow = abnb.cash_flow
earnings_history = abnb.earnings_history

# Print available data for debugging
print("\nAvailable data keys:")
print("Income Statement:", income_stmt.index)
print("\nBalance Sheet:", balance_sheet.index)
print("\nCash Flow:", cash_flow.index)

# Create expense breakdown
try:
    expense_data = pd.DataFrame({
        'Cost of Revenue': income_stmt.loc['Cost Of Revenue'],
        'Research Development': income_stmt.loc['Research And Development'],
        'SG&A Expense': income_stmt.loc['Selling General And Administration'],
        'Marketing Expense': income_stmt.loc['Marketing Expense'] if 'Marketing Expense' in income_stmt.index else None,
        'Operating Expenses': income_stmt.loc['Operating Expense']
    }).dropna(axis=1)  # Remove columns with no data
except Exception as e:
    print(f"Some expense categories not found: {e}")
    expense_data = pd.DataFrame()

# Try to get geographical revenue if available
try:
    geo_revenue = pd.DataFrame({
        'North America': income_stmt.loc['North America Revenue'] if 'North America Revenue' in income_stmt.index else None,
        'Europe': income_stmt.loc['Europe Revenue'] if 'Europe Revenue' in income_stmt.index else None,
        'Asia Pacific': income_stmt.loc['Asia Pacific Revenue'] if 'Asia Pacific Revenue' in income_stmt.index else None,
        'Rest of World': income_stmt.loc['Rest Of World Revenue'] if 'Rest Of World Revenue' in income_stmt.index else None
    }).dropna(axis=1)  # Remove columns with no data
except Exception as e:
    print(f"Geographical revenue data not found: {e}")
    geo_revenue = pd.DataFrame()

# Create DataFrames for different financial aspects
financial_data = pd.DataFrame({
    'Net Income': income_stmt.loc['Net Income'],
    'Revenue': income_stmt.loc['Total Revenue'],
    'Operating Income': income_stmt.loc['Operating Income'],
    'Operating Expenses': income_stmt.loc['Operating Expense']
})

balance_sheet_data = pd.DataFrame({
    'Total Assets': balance_sheet.loc['Total Assets'],
    'Total Liabilities': balance_sheet.loc['Total Liabilities Net Minority Interest'],
    'Total Equity': balance_sheet.loc['Total Equity Gross Minority Interest'],
    'Cash': balance_sheet.loc['Cash And Cash Equivalents']
})

cash_flow_data = pd.DataFrame({
    'Operating Cash Flow': cash_flow.loc['Operating Cash Flow'],
    'Investing Cash Flow': cash_flow.loc['Investing Cash Flow'],
    'Financing Cash Flow': cash_flow.loc['Financing Cash Flow'],
    'Free Cash Flow': cash_flow.loc['Free Cash Flow']
})

# Create visualizations
def create_financial_plot(data, title, ylabel):
    fig = plt.figure(figsize=(12, 6))
    for column in data.columns:
        plt.plot(data.index, data[column], marker='o', label=column)
    plt.title(title)
    plt.xlabel('Quarter')
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    img = fig_to_base64(fig)
    plt.close()
    return img

# Generate plots
income_img = create_financial_plot(financial_data, 'Airbnb Income Statement Trends', 'Amount (USD)')
balance_img = create_financial_plot(balance_sheet_data, 'Airbnb Balance Sheet Overview', 'Amount (USD)')
cash_flow_img = create_financial_plot(cash_flow_data, 'Airbnb Cash Flow Analysis', 'Amount (USD)')

# Analyze earnings surprises - using the correct column names
try:
    surprises = earnings_history[['epsEstimate', 'epsActual', 'surprisePercent']].sort_index(ascending=False)
    surprises.columns = ['EPS Estimate', 'Reported EPS', 'Surprise (%)']
except KeyError as e:
    print(f"Error accessing columns: {e}")
    surprises = pd.DataFrame()  # Empty DataFrame as fallback

# Create second visualization
if not surprises.empty:
    fig2 = plt.figure(figsize=(12, 6))
    plt.bar(range(len(surprises)), surprises['Surprise (%)'])
    plt.title('Airbnb Earnings Surprises (%)')
    plt.xlabel('Quarters (Most Recent First)')
    plt.ylabel('Surprise %')
    plt.grid(True, axis='y')
    plt.tight_layout()
    img2 = fig_to_base64(fig2)
    plt.close()
else:
    img2 = None

# Create additional visualizations for new data
if not expense_data.empty:
    expense_img = create_financial_plot(expense_data, 'Airbnb Expense Breakdown', 'Amount (USD)')

if not geo_revenue.empty:
    geo_img = create_financial_plot(geo_revenue, 'Airbnb Revenue by Region', 'Amount (USD)')

# Enhanced HTML content
html_content = f"""
<html>
<head>
    <title>Airbnb Financial Analysis</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        .figure {{
            margin: 20px 0;
            text-align: center;
        }}
        table {{
            border-collapse: collapse;
            margin: 20px 0;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f5f5f5;
        }}
        .section {{
            margin: 40px 0;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <h1>Airbnb Comprehensive Financial Analysis</h1>
    
    <div class="section">
        <h2>Income Statement Analysis</h2>
        <div class="figure">
            <img src="data:image/png;base64,{income_img}" alt="Income Statement Trends">
        </div>
        <h3>Detailed Income Statement Data</h3>
        {financial_data.to_html()}
    </div>

    <div class="section">
        <h2>Balance Sheet Overview</h2>
        <div class="figure">
            <img src="data:image/png;base64,{balance_img}" alt="Balance Sheet Overview">
        </div>
        <h3>Detailed Balance Sheet Data</h3>
        {balance_sheet_data.to_html()}
    </div>

    <div class="section">
        <h2>Cash Flow Analysis</h2>
        <div class="figure">
            <img src="data:image/png;base64,{cash_flow_img}" alt="Cash Flow Analysis">
        </div>
        <h3>Detailed Cash Flow Data</h3>
        {cash_flow_data.to_html()}
    </div>

    <div class="section">
        <h2>Earnings History</h2>
        {earnings_history.to_html()}
    </div>
"""

if not expense_data.empty:
    html_content += f"""
    <div class="section">
        <h2>Expense Breakdown</h2>
        <div class="figure">
            <img src="data:image/png;base64,{expense_img}" alt="Expense Breakdown">
        </div>
        <h3>Detailed Expense Data</h3>
        {expense_data.to_html()}
    </div>
"""

if not geo_revenue.empty:
    html_content += f"""
    <div class="section">
        <h2>Revenue by Region</h2>
        <div class="figure">
            <img src="data:image/png;base64,{geo_img}" alt="Revenue by Region">
        </div>
        <h3>Detailed Regional Revenue Data</h3>
        {geo_revenue.to_html()}
    </div>
"""

if not surprises.empty:
    html_content += f"""
    <div class="section">
        <h2>Earnings Surprises</h2>
        {surprises.to_html()}
        <div class="figure">
            <img src="data:image/png;base64,{img2}" alt="Earnings Surprises">
        </div>
    </div>
"""

html_content += """
</body>
</html>
"""

# Set output directory
output_dir = r'C:\xxy\product\github\company_performance_analysis\output'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Create output path
output_path = os.path.join(output_dir, 'airbnb_financial_analysis.html')

# Save the file
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Analysis has been saved to: {output_path}") 