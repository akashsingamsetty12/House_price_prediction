import streamlit as st
import pandas as pd
import numpy as np
import pickle

# ----------- LOAD FILES -----------
model = pickle.load(open("house_model.pkl", "rb"))
columns = pickle.load(open("columns.pkl", "rb"))
medians = pickle.load(open("medians.pkl", "rb"))

# ----------- PAGE CONFIG -----------
st.set_page_config(page_title="House Price Predictor", layout="wide")

# ----------- HEADER -----------
st.title("🏡 House Price Prediction App")
st.markdown("### Enter property details to estimate price")

st.markdown("---")

# ----------- BASIC INPUTS -----------
st.subheader("🔹 Basic Details")

col1, col2, col3 = st.columns(3)

with col1:
    overall_qual = st.slider("Overall Quality", 1, 10, 5)
    full_bath = st.slider("Bathrooms", 0, 4, 2)

with col2:
    gr_liv_area = st.number_input("Living Area (sq ft)", 500, 5000, 1500)
    total_bsmt = st.number_input("Basement Area (sq ft)", 0, 3000, 800)

with col3:
    garage_cars = st.slider("Garage Capacity", 0, 5, 1)
    year_built = st.number_input("Year Built", 1900, 2025, 2000)

st.markdown("---")

# ----------- ADVANCED INPUTS -----------
st.subheader("⚙️ Advanced Inputs (Optional)")

advanced_inputs = {}

with st.expander("Click to customize more features"):
    for col in columns:
        if col not in [
            'Overall Qual', 'Gr Liv Area', 'Garage Cars',
            'Total Bsmt SF', 'Full Bath', 'Year Built', 'SalePrice'
        ]:
            advanced_inputs[col] = st.number_input(
                f"{col}", value=float(medians[col])
            )

st.markdown("---")

# ----------- PREDICTION -----------
if st.button("🔮 Predict Price", use_container_width=True):

    # Start with medians
    input_data = medians.to_dict()

    # Override with user inputs
    input_data.update({
        'Overall Qual': overall_qual,
        'Gr Liv Area': gr_liv_area,
        'Garage Cars': garage_cars,
        'Total Bsmt SF': total_bsmt,
        'Full Bath': full_bath,
        'Year Built': year_built
    })

    # Advanced override
    input_data.update(advanced_inputs)

    # Convert to DataFrame
    input_df = pd.DataFrame([input_data])

    # ----------- MODEL PREDICTION -----------
    pred_log = model.predict(input_df)[0]
    pred_price_usd = np.expm1(pred_log)

    # Convert USD → INR
    pred_price_inr = pred_price_usd * 83

    # ----------- OUTPUT -----------
    st.markdown("## 💰 Estimated Price")

    st.markdown(
        f"<h2 style='color:green;'>₹ {round(pred_price_inr, 2):,}</h2>",
        unsafe_allow_html=True
    )

    # ----------- PRICE CATEGORY -----------
    st.subheader("📊 Price Category")

    if pred_price_inr < 5000000:  # < 50 Lakhs
        st.error("🏠 Low Budget House")
    elif pred_price_inr < 15000000:  # 50L - 1.5Cr
        st.warning("🏡 Mid Range House")
    else:
        st.success("🏢 Premium House")

    # ----------- VISUAL BAR -----------
    st.subheader("📈 Price Indicator")

    progress = min(int(pred_price_inr / 20000000 * 100), 100)
    st.progress(progress)
