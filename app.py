
import os
import sys
import django
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt  # For any traditional plots if needed
import plotly.express as px      # --- NEW: For interactive charts
import matplotlib.dates as mdates  # For date formatting if required
from datetime import datetime

# -------------------- Django Setup --------------------
# Add your Django project path (update if needed)
sys.path.append(r"C:\Users\ADMIN\Desktop\PRIYA\Python\project\FoodDonationApp")
# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "food_project.settings")
django.setup()

# Import your Django model
from donations.models import Donation

st.set_page_config(page_title="Food Donation Tracker", layout="centered")
st.title("🥗 NourishNet: Smart Food Donation & Distribution")

# Show total active donations from the Django DB
active_donations = Donation.objects.filter(status="Available").count()
st.info(f"📦 Total Active Donations: **{active_donations}**")

# --- Tabs: Donate / View / Admin / Dashboard ---
tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Donate Food", 
    "📋 View Donations", 
    "🛠️ Admin Panel", 
    "📊 Dashboard"
])

# --- Tab 1: Donate Form ---
with tab1:
    st.subheader("Log a New Food Donation")

    donor = st.text_input("Donor Name / Restaurant")
    contact = st.text_input("Contact (Phone/Email)")
    category = st.selectbox("Category", ["Cooked", "Packaged", "Raw"])
    food_item = st.text_input("Food Item")
    quantity = st.number_input("Quantity (Servings)", min_value=1)
    expiry = st.date_input("Expiry Date", min_value=datetime.today())
    location = st.text_input("Pickup Location")

    # --- NEW: Dropdown-based Location Picker for Geolocation ---
    location_coords = {
        "Delhi": (28.6139, 77.2090),
        "Mumbai": (19.0760, 72.8777),
        "Bangalore": (12.9716, 77.5946),
        "Chennai": (13.0827, 80.2707),
        "Kolkata": (22.5726, 88.3639)
    }
    selected_city = st.selectbox("Select City (for Auto Coordinates)", list(location_coords.keys()))
    latitude, longitude = location_coords[selected_city]
    st.write(f"📍 Coordinates: **Lat:** {latitude}, **Lon:** {longitude}")

    if st.button("Submit Donation"):
        Donation.objects.create(
            donor=donor,
            contact=contact,
            category=category,
            food_item=food_item,
            quantity=quantity,
            expiry_date=expiry,
            location=location,
            latitude=latitude,
            longitude=longitude,
            status="Available"
        )
        st.success("✅ Donation submitted!")

# --- Tab 2: View & Filter Donations ---
with tab2:
    st.subheader("Available Donations")
    all_donations = Donation.objects.all().values()
    df = pd.DataFrame(all_donations)

    if not df.empty:
        cat_filter = st.selectbox("Filter by Category", ["All"] + df["category"].unique().tolist())
        status_filter = st.selectbox("Filter by Status", ["All", "Available", "Collected"])

        if cat_filter != "All":
            df = df[df["category"] == cat_filter]
        if status_filter != "All":
            df = df[df["status"] == status_filter]

        df["expiry_date"] = pd.to_datetime(df["expiry_date"])
        today = pd.to_datetime(datetime.today().date())
        df["Expired"] = df["expiry_date"] < today

        st.dataframe(df.drop(columns=["Expired"]))

        expired_count = df["Expired"].sum()
        if expired_count > 0:
            st.warning(f"⚠️ {expired_count} donation(s) have expired. Please review.")

        st.subheader("Update Donation Status")
        to_mark = st.text_input("Enter Donor Name to Mark as Collected")
        if st.button("Mark Collected"):
            Donation.objects.filter(donor=to_mark).update(status="Collected")
            st.success(f"✅ Donations by {to_mark} marked as collected.")
    else:
        st.info("No donations available.")

# --- Tab 3: Admin Panel ---
with tab3:
    st.subheader("🧹 Admin: Remove Donations")
    donor_delete = st.text_input("Enter Donor Name to DELETE all their donations")
    if st.button("Delete Donations"):
        Donation.objects.filter(donor=donor_delete).delete()
        st.warning(f"❌ All donations by {donor_delete} have been deleted.")

# --- Tab 4: Dashboard with Interactive Charts ---
with tab4:
    st.subheader("📊 Donation Dashboard")

    all_donations = Donation.objects.all().values()
    dashboard_df = pd.DataFrame(all_donations)

    if dashboard_df.empty:
        st.warning("No donation data available for dashboard.")
    else:
        total_donations = len(dashboard_df)
        st.metric("Total Donations", total_donations)

        st.subheader("Donation Categories (Pie Chart)")
        pie_fig = px.pie(dashboard_df, names="category", title="Donations by Category")
        st.plotly_chart(pie_fig)

        st.subheader("Donations Per Day")
        dashboard_df["expiry_date"] = pd.to_datetime(dashboard_df["expiry_date"])
        daily_counts = dashboard_df.groupby(dashboard_df["expiry_date"].dt.date).size().reset_index(name='Count')
        daily_counts["expiry_date"] = pd.to_datetime(daily_counts["expiry_date"])
        line_fig = px.line(daily_counts, x="expiry_date", y="Count", markers=True,
                           title="Donations per Day",
                           labels={"expiry_date": "Date", "Count": "Number of Donations"})
        st.plotly_chart(line_fig)

        st.subheader("Map of Donations")
        if "latitude" in dashboard_df.columns and "longitude" in dashboard_df.columns:
            map_df = dashboard_df.dropna(subset=["latitude", "longitude"])
            map_df["latitude"] = pd.to_numeric(map_df["latitude"], errors="coerce")
            map_df["longitude"] = pd.to_numeric(map_df["longitude"], errors="coerce")
            map_df = map_df.dropna(subset=["latitude", "longitude"])
            if not map_df.empty:
                st.map(map_df[["latitude", "longitude"]])
            else:
                st.info("No geolocation data available for mapping.")
        else:
            st.info("Donation model does not include geolocation data for mapping.")

