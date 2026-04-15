import streamlit as st
import pandas as pd
import dns.resolver
import smtplib

st.set_page_config(page_title="Email Finder", layout="centered")

# -------- TITLE --------
st.markdown("<h1 style='text-align:center;'>Email Finder</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>Find email addresses using name and company domain</p>", unsafe_allow_html=True)

# -------- INPUT --------
full_name = st.text_input("Full Name (e.g. Jens Johansson)")
domain = st.text_input("Company Domain (e.g. nordicwebteam.com)")

# -------- SPLIT NAME --------
def split_name(full_name):
    parts = full_name.lower().strip().split()
    first = parts[0] if len(parts) > 0 else ""
    last = parts[1] if len(parts) > 1 else ""
    return first, last

# -------- EMAIL PATTERNS --------
def generate_emails(first, last, domain):
    f = first[0] if first else ""

    return list(set([
        f"{first}.{last}@{domain}",
        f"{f}.{last}@{domain}",
        f"{first}@{domain}",
        f"{f}{last}@{domain}",
        f"{first}{last}@{domain}",
        f"{last}@{domain}",
        f"{first}_{last}@{domain}",
        f"{first}-{last}@{domain}",
    ]))

# -------- MX --------
def get_mx(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return str(records[0].exchange)
    except:
        return None

# -------- SMTP --------
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

# -------- CATCH-ALL --------
def is_catch_all(domain, mx):
    fake = f"random123@{domain}"
    return verify(fake, mx) == "Valid"

# -------- BUTTON --------
if st.button("Find Email", type="primary"):

    if not full_name or not domain:
        st.warning("Please fill both fields")
    else:
        first, last = split_name(full_name)

        if not first or not last:
            st.error("Please enter full name (first and last)")
        else:
            with st.spinner("Checking..."):

                mx = get_mx(domain)

                if not mx:
                    st.error("No MX records found")
                else:
                    catch_all = is_catch_all(domain, mx)
                    emails = generate_emails(first, last, domain)

                    results = []

                    for email in emails:
                        status = verify(email, mx)

                        if catch_all:
                            status = "Catch-all"

                        if status in ["Valid", "Catch-all"]:
                            results.append((email, status))

                    if results:
                        st.success("Emails Found 🎉")

                        for i, (email, status) in enumerate(results):
                            color = "green" if status == "Valid" else "orange"

                            st.markdown(f"""
                            <div style="display:flex; justify-content:space-between; align-items:center;
                                        padding:8px; border-bottom:1px solid #eee;">
                                
                                <div>{email}</div>

                                <div style="display:flex; gap:10px; align-items:center;">
                                    <div style="color:{color}; font-weight:bold;">{status}</div>

                                    <button onclick="navigator.clipboard.writeText('{email}')"
                                            style="padding:4px 10px; cursor:pointer;">
                                        Copy
                                    </button>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    else:
                        st.error("Emails not found")
