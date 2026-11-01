import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="Customer Intelligence System",
    page_icon="📊",
    layout="wide"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
.card {
    padding: 20px;
    border-radius: 15px;
    background-color: #1c1f26;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
    margin-bottom: 15px;
}
.metric-title {
    font-size: 14px;
    color: #9aa0a6;
}
.metric-value {
    font-size: 28px;
    font-weight: bold;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ------------------ LOAD DATA ------------------
rfm = pd.read_csv('rfm_segments.csv', index_col='CustomerID')
similarity_df = pd.read_csv('customer_similarity_small.csv', index_col=0)
item_similarity_df = pd.read_csv('item_similarity_small.csv', index_col=0)
basket = pd.read_csv('basket_compact.csv')

# Convert string to list
import ast
basket['Products'] = basket['Products'].apply(ast.literal_eval)

basket = basket.set_index('CustomerID')
product_dict = joblib.load('product_mapping.pkl')

# ------------------ DATA CLEANING ------------------
rfm['Monetary'] = pd.to_numeric(rfm['Monetary'], errors='coerce')
rfm['Recency'] = pd.to_numeric(rfm['Recency'], errors='coerce')
rfm['Frequency'] = pd.to_numeric(rfm['Frequency'], errors='coerce')
rfm = rfm.dropna(subset=['Monetary', 'Recency', 'Frequency'])

rfm.index = rfm.index.astype(int)
similarity_df.index = similarity_df.index.astype(int)
similarity_df.columns = similarity_df.columns.astype(int)
basket.index = basket.index.astype(int)

rfm = rfm[~rfm.index.duplicated(keep='first')]
product_dict = {str(k): v for k, v in product_dict.items()}

# ------------------ TITLE ------------------
st.title("📊 Customer Intelligence System")
st.markdown("Premium dashboard for customer segmentation & recommendations")

# ------------------ SIDEBAR ------------------
st.sidebar.header("🔍 Select Customer")
customer_id = st.sidebar.number_input("Enter Customer ID", step=1)

# ------------------ MAIN ------------------
if st.sidebar.button("Get Insights"):

    if customer_id in rfm.index:

        segment = str(rfm.loc[customer_id, 'Segment'])

        value = rfm.loc[customer_id, 'Monetary']
        if isinstance(value, pd.Series):
            value = value.iloc[0]

        try:
            value = float(value)
        except:
            value = 0.0

        # ------------------ METRIC CARDS ------------------
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
        <div class="card">
            <div class="metric-title">Customer ID</div>
            <div class="metric-value">{customer_id}</div>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="card">
            <div class="metric-title">Segment</div>
            <div class="metric-value">{segment}</div>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class="card">
            <div class="metric-title">Total Spend</div>
            <div class="metric-value">₹ {round(value,2)}</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ------------------ CUSTOMER CHART ------------------
        st.subheader("📊 Customer Behavior")

        fig, ax = plt.subplots()
        values = [
            rfm.loc[customer_id, 'Recency'],
            rfm.loc[customer_id, 'Frequency'],
            rfm.loc[customer_id, 'Monetary']
        ]
        labels = ['Recency', 'Frequency', 'Monetary']
        ax.bar(labels, values)
        st.pyplot(fig)

        st.divider()

        # ------------------ SIMILAR CUSTOMERS ------------------
        st.subheader("👥 Similar Customers")

        try:
            similar = similarity_df[customer_id].sort_values(ascending=False)[1:6]
            st.dataframe(similar)
        except:
            st.warning("Similarity data not available")

        st.divider()

        # ------------------ RECOMMENDATIONS ------------------
        st.subheader("🛒 Recommended Products")

        try:
            if customer_id in basket.index:

                purchased_products = basket.loc[customer_id, 'Products']

                recommended_products = []

                for product in purchased_products[:5]:
                    if product in item_similarity_df.columns:
                        similar_items = item_similarity_df[product].sort_values(ascending=False)[1:4]
                        recommended_products.extend(similar_items.index.tolist())

                recommended_products = list(set(recommended_products))

                product_names = []

                for code in recommended_products:
                    name = product_dict.get(str(code))
                    if name:
                        product_names.append(name)

                if product_names:
                    for name in product_names[:5]:
                        st.markdown(f"""
                        <div class="card">
                            🛒 {name}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No recommendations found")

            else:
                st.warning("Customer purchase data not available")

        except:
            st.warning("Recommendation error")

        st.divider()

        # ------------------ SEGMENT CHART ------------------
        st.subheader("📈 Segment Distribution")

        fig2, ax2 = plt.subplots()
        rfm['Segment'].value_counts().plot(kind='bar', ax=ax2)
        st.pyplot(fig2)

        st.divider()

        # ------------------ BUSINESS INSIGHT ------------------
        st.subheader("💡 Business Recommendation")

        if segment == 'High Value Customers':
            st.success("Offer premium products and loyalty rewards.")
        elif segment == 'At Risk Customers':
            st.warning("Send discounts and re-engagement offers.")
        elif segment == 'Regular Customers':
            st.info("Promote cross-selling and bundles.")
        else:
            st.error("Increase engagement campaigns.")

    else:
        st.error("Customer not found")

# ------------------ FOOTER ------------------
st.markdown("---")
st.caption("Built for Data Science Portfolio | Customer Intelligence System")
