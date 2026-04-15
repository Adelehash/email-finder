import streamlit as st
import pandas as pd
import dns.resolver
import smtplib

st.set_page_config(page_title="Email Finder", layout="wide")

# -------- CUSTOM CSS --------
st.markdown("""
<style>
.navbar {
    display: flex;
    gap: 20px;
    font-weight: 600;
    padding: 10px 0;
    border-bottom: 1px solid #ddd;
}
.title {
    font-size: 28px;
    font-weight: bold;
    margin-top: 20px;
}
.subtitle {
    color: gray;
    margin-bottom: 20px;
}
.result-valid {
    color: green;
    font-weight: bold;
}
.result-invalid {
    color: red;
}
</style>
""", unsafe_allow_html=True)

# -------- NAVBAR --------
st.markdown("""
<div class="navbar">
    <div>Website & Ecommerce</div>
    <div>Design</div>
    <div>IT-Security</div>
    <div>Business</div>
    <div>About Us</div>
</div>
""", unsafe_allow_html=True)

# -------- HEADER --------
st.markdown('<div class="title">Email Finder</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Find email addresses using name and domain</div>', unsafe_allow_html=True)

# -------- INPUT --------
col1, col2 = st.columns(2)

first_name = col1.text_input("First Name", "Jens")
last_name = col2.text_input("Last Name", "Johansson")

domain = st.text_input("Company Domain", "nordicwebteam.com")

# -------- EMAIL PATTERNS --------
def generate_emails(first, last, domain):
    first = first.lower()
    last = last.lower()
    f = first[0]

    return list(set([
        f"{first}@{domain}",
        f"{first}{last}@{domain}",
        f"{first}.{last}@{domain}",
        f"{first}_{last}@{domain}",
        f"{first}-{last}@{domain}",
        f"{f}{last}@{domain}",
        f"{f}.{last}@{domain}",
        f"{last}@{domain}",
    ]))

# -------- MX --------
def get_mx(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return str(records[0].exchange)
    except:
        return None

# -------- VERIFY --------
def verify(email, mx):
    try:
        server = smtplib.SMTP(timeout=10)
        server.connect(mx)
        server.helo("test.com")
        server.mail("test@test.com")
        code, _ = server.rcpt(email)
        server.quit()

        if code == 250:
            return "Valid"
        elif code == 550:
            return "Invalid"
        else:
            return "Unknown"
    except:
        return "Unknown"

# -------- BUTTON --------
if st.button("Find Email"):

    mx = get_mx(domain)

    if not mx:
        st.error("No MX records found")
    else:
        emails = generate_emails(first_name, last_name, domain)

        results = []

        for email in emails:
            status = verify(email, mx)

            results.append({
                "Email": email,
                "Result": status
            })

        df = pd.DataFrame(results)

        # -------- DISPLAY TABLE --------
        st.markdown("### Results")

        def highlight(val):
            if val == "Valid":
                return "color: green; font-weight: bold"
            elif val == "Invalid":
                return "color: red"
            else:
                return "color: orange"

        styled_df = df.style.applymap(highlight, subset=["Result"])

        st.dataframe(styled_df, use_container_width=True)
