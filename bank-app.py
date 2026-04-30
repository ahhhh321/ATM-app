import streamlit as st
import time
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import copy
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# -------------------- INITIAL DATA --------------------
INITIAL_ACCOUNTS = {
    1234: {"balance": 5000, "history": []},
    5678: {"balance": 3000, "history": []},
    9999: {"balance": 10000, "history": []}
}

st.set_page_config(page_title="Smart ATM Dashboard", page_icon="🏦", layout="wide")

# -------------------- SESSION STATE --------------------
if "accounts" not in st.session_state:
    st.session_state.accounts = copy.deepcopy(INITIAL_ACCOUNTS)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.pin = None

accounts = st.session_state.accounts

# -------------------- UI STYLE --------------------
st.markdown("""
<style>
    .main {background-color: #0E1117; color: white;}
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        padding: 8px 16px;
    }
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏦 Smart ATM Dashboard Pro")

# -------------------- LOGIN --------------------
if not st.session_state.logged_in:
    st.subheader("🔐 Login")

    pin_input = st.text_input("Enter PIN", type="password")

    if st.button("Login"):
        try:
            pin = int(pin_input)

            if pin in accounts:
                st.session_state.logged_in = True
                st.session_state.pin = pin
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid PIN")

        except ValueError:
            st.error("PIN must be numeric")

# -------------------- DASHBOARD --------------------
else:
    user = accounts[st.session_state.pin]

    st.sidebar.title("📌 Menu")
    option = st.sidebar.radio("Select", [
        "Dashboard",
        "Withdraw",
        "Deposit",
        "Transactions",
        "Charts",
        "Download Report",
        "Logout"
    ])

    # ---------------- DASHBOARD ----------------
    if option == "Dashboard":
        st.subheader("Account Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric("Balance", f"Rs {user['balance']}")
        col2.metric("Transactions", len(user['history']))

        deposits = sum([t[1] for t in user['history'] if t[0] == "Deposit"])
        withdraws = sum([t[1] for t in user['history'] if t[0] == "Withdraw"])

        col3.metric("Net Flow", f"Rs {deposits - withdraws}")

    # ---------------- WITHDRAW ----------------
    elif option == "Withdraw":
        st.subheader("💸 Withdraw Money")
        amount = st.text_input("Enter amount")

        if st.button("Withdraw"):
            try:
                amount = float(amount)

                if amount <= 0:
                    st.warning("Invalid amount")
                elif amount > user['balance']:
                    st.error("Insufficient balance")
                else:
                    user['balance'] -= amount
                    user['history'].append(("Withdraw", amount, str(datetime.now())))
                    st.success("Withdrawal successful")
                    st.rerun()

            except ValueError:
                st.error("Enter numeric value")

    # ---------------- DEPOSIT ----------------
    elif option == "Deposit":
        st.subheader("💰 Deposit Money")
        amount = st.text_input("Enter amount")

        if st.button("Deposit"):
            try:
                amount = float(amount)

                if amount <= 0:
                    st.warning("Invalid amount")
                else:
                    user['balance'] += amount
                    user['history'].append(("Deposit", amount, str(datetime.now())))
                    st.success("Deposit successful")
                    st.rerun()

            except ValueError:
                st.error("Enter numeric value")

    # ---------------- TRANSACTIONS ----------------
    elif option == "Transactions":
        st.subheader("📄 Transaction History")

        if user['history']:
            df = pd.DataFrame(user['history'], columns=["Type", "Amount", "Time"])
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "Download CSV",
                df.to_csv(index=False).encode(),
                file_name="transactions.csv"
            )
        else:
            st.info("No transactions yet")

    # ---------------- CHARTS (FIXED & IMPROVED) ----------------
    elif option == "Charts":
        st.subheader("📊 Transaction Analytics")

        deposits = [t[1] for t in user['history'] if t[0] == "Deposit"]
        withdraws = [t[1] for t in user['history'] if t[0] == "Withdraw"]

        if user['history']:

            amounts = [t[1] for t in user['history']]
            labels = list(range(1, len(amounts) + 1))

            # Line Chart
            fig, ax = plt.subplots()
            ax.plot(labels, amounts, marker='o')
            ax.set_title("Transaction Trend Over Time")
            ax.set_xlabel("Transaction Number")
            ax.set_ylabel("Amount (Rs)")
            ax.grid(True)
            st.pyplot(fig)

        if deposits or withdraws:
            # Pie Chart
            fig2, ax2 = plt.subplots()
            ax2.pie(
                [sum(deposits), sum(withdraws)],
                labels=["Deposit", "Withdraw"],
                autopct='%1.1f%%'
            )
            ax2.set_title("Deposit vs Withdraw Distribution")
            st.pyplot(fig2)

    # ---------------- PDF REPORT ----------------
    elif option == "Download Report":
        st.subheader("📥 Generate Report")

        def generate_pdf():
            doc = SimpleDocTemplate("report.pdf")
            styles = getSampleStyleSheet()
            content = []

            content.append(Paragraph("ATM Transaction Report", styles['Title']))
            content.append(Spacer(1, 12))

            content.append(Paragraph(f"Balance: Rs {user['balance']}", styles['Normal']))
            content.append(Spacer(1, 12))

            for t in user['history']:
                content.append(Paragraph(f"{t[0]} - Rs {t[1]} ({t[2]})", styles['Normal']))

            doc.build(content)

            with open("report.pdf", "rb") as f:
                return f.read()

        if st.button("Generate PDF"):
            pdf = generate_pdf()
            st.download_button("Download PDF", pdf, file_name="ATM_Report.pdf")

    # ---------------- LOGOUT ----------------
    elif option == "Logout":
        st.session_state.logged_in = False
        st.session_state.pin = None
        st.success("Logged out")
        time.sleep(1)
        st.rerun()