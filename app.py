import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="LinkedIn → Email Finder", page_icon="📧")

st.title("📧 LinkedIn URL → Email Finder (ContactOut)")

API_KEY = st.secrets["CONTACTOUT_API_KEY"]

# -------- FUNCTION --------
def fetch_contact(linkedin_url):
    url = "https://api.contactout.com/v1/people/linkedin"

    params = {
        "profile": linkedin_url,
        "include_phone": "false"   # only emails
    }

    headers = {
        "token": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json()

        profile = data.get("profile", {})
        emails = profile.get("email", [])

        return emails

    except:
        return []

# ============================
# 🔹 SINGLE LOOKUP
# ============================

st.subheader("🔍 Single Lookup")

linkedin_url = st.text_input("Enter LinkedIn Profile URL")

if st.button("Find Email"):

    if not linkedin_url:
        st.warning("Please enter LinkedIn URL")
    else:
        with st.spinner("Fetching..."):
            emails = fetch_contact(linkedin_url)

            if emails:
                df = pd.DataFrame({"email": emails})
                st.success("Emails Found 🎉")
                st.dataframe(df)
            else:
                st.error("No emails found")

# ============================
# 🔹 BULK LOOKUP
# ============================

st.divider()
st.subheader("📂 Bulk Lookup")

uploaded_file = st.file_uploader("Upload CSV with 'linkedin_url'", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if "linkedin_url" not in df.columns:
        st.error("CSV must contain 'linkedin_url' column")
    else:
        st.write(f"Total rows: {len(df)}")

        if st.button("Start Bulk Processing"):
            results = []

            with st.spinner("Processing..."):
                for _, row in df.iterrows():
                    url = row["linkedin_url"]

                    emails = fetch_contact(url)

                    if emails:
                        for email in emails:
                            results.append({
                                "linkedin_url": url,
                                "email": email
                            })
                    else:
                        results.append({
                            "linkedin_url": url,
                            "email": "Not Found"
                        })

            result_df = pd.DataFrame(results)

            st.success("Done 🎉")
            st.dataframe(result_df)

            csv = result_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download Results",
                csv,
                "linkedin_emails.csv",
                "text/csv"
            )