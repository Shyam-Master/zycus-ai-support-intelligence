import streamlit as st
from app.schemas.triage import TriageRequest
from app.services.triage_service import TriageService
from app.services.tam_service import TamService
from app.utils.data_loader import DataLoader

# --- Page Config ---
st.set_page_config(
    page_title="Zycus AI Support",
    page_icon="🤖",
    layout="wide"
)

# --- Header ---
st.title("Zycus AI Support")
st.subheader("AI-Powered Support Triage & TAM Account Intelligence")
st.divider()

# --- Tabs ---
tab1, tab2 = st.tabs(["🎫 Support Triage", "📊 TAM Account Analysis"])

# ==========================================
# TAB 1: SUPPORT TRIAGE
# ==========================================
with tab1:
    st.header("Support Issue Triage")
    
    # Inputs
    subject = st.text_input("Issue Subject", placeholder="e.g. Cannot log in")
    body = st.text_area("Issue Description", placeholder="e.g. All users are seeing a 500 error on the login page after the SSO update.")
    
    if st.button("Analyze Issue", type="primary"):
        if not subject.strip() and not body.strip():
            st.error("Please provide either a subject or a description.")
        else:
            with st.spinner("Analyzing issue..."):
                try:
                    # Instantiate Service
                    triage_svc = TriageService()
                    request = TriageRequest(subject=subject, body=body)
                    
                    # Call Agent
                    response = triage_svc.triage_ticket(request)
                    
                    # Top Metrics
                    st.subheader("Triage Results")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Urgency", response.urgency)
                    with col2:
                        st.metric("Product Area", response.product_area)
                    with col3:
                        st.metric("Issue Category", response.issue_category)
                    with col4:
                        st.metric("Recommended Team", response.recommended_team)
                        
                    st.divider()
                    
                    # Detailed Sections
                    st.markdown("### Reasoning")
                    st.write(response.reasoning)
                    
                    st.markdown("### Draft Response")
                    st.info(response.draft_response)
                    
                    with st.expander("Relevant Knowledge Base Documents", expanded=True):
                        if response.relevant_kb_docs:
                            for doc in response.relevant_kb_docs:
                                st.markdown(f"- {doc}")
                        else:
                            st.write("No relevant documents found.")
                            
                    with st.expander("Known Issue Patterns", expanded=True):
                        if response.known_issue_patterns:
                            for pattern in response.known_issue_patterns:
                                st.markdown(f"- {pattern}")
                        else:
                            st.write("No known issue patterns detected.")
                            
                except Exception as e:
                    st.error(f"An error occurred during triage: {str(e)}")

# ==========================================
# TAB 2: TAM ACCOUNT ANALYSIS
# ==========================================
with tab2:
    st.header("TAM Account Health Analysis")
    
    # Load Valid Accounts
    try:
        accounts = DataLoader.load_accounts()
        account_options = [acc['account_id'] for acc in accounts]
    except Exception as e:
        st.error("Failed to load accounts from dataset.")
        account_options = []
        
    if account_options:
        selected_account = st.selectbox("Select Account ID", options=account_options)
        
        if st.button("Analyze Account", type="primary"):
            with st.spinner("Generating account health brief..."):
                try:
                    # Instantiate Service
                    tam_svc = TamService()
                    
                    # Call Agent
                    response = tam_svc.generate_brief(selected_account)
                    
                    # Top Metrics
                    st.subheader(f"Account: {response.account_name} ({response.account_id})")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if response.overall_health == "Healthy":
                            st.metric("Overall Health", response.overall_health, delta="Stable", delta_color="normal")
                        else:
                            st.metric("Overall Health", response.overall_health, delta="Attention Required", delta_color="inverse")
                    with col2:
                        st.metric("Recent Ticket Count (90 Days)", response.recent_ticket_count)
                        
                    st.divider()
                    
                    # Executive Summary
                    st.markdown("### Executive Summary")
                    st.markdown(response.executive_summary)
                    
                    # Recommended Talking Points
                    st.markdown("### Recommended Talking Points")
                    for point in response.recommended_talking_points:
                        st.markdown(f"- {point}")
                        
                    st.divider()
                    
                    # Open Risks
                    st.markdown("### Open Risks")
                    if response.open_risks:
                        for risk in response.open_risks:
                            # Render risk dictionaries dynamically safely
                            with st.expander(f"Risk: {risk.get('risk', 'Unknown')}", expanded=True):
                                st.write(f"**Severity:** {risk.get('severity', 'Unknown')}")
                                st.write(f"**Ticket ID:** {risk.get('ticket_id', 'N/A')}")
                                st.write(f"**Reason:** {risk.get('reason', 'N/A')}")
                                st.write(f"**Evidence Quote:** _{risk.get('evidence_quote', 'N/A')}_")
                    else:
                        st.success("No open risks identified.")
                        
                    # Escalation Signals
                    st.markdown("### Escalation Signals")
                    if response.escalation_signals:
                        for sig in response.escalation_signals:
                            st.warning(f"**{sig.get('signal', 'Unknown')}** in Ticket {sig.get('ticket_id', 'N/A')}: _{sig.get('evidence_quote', '')}_")
                    else:
                        st.write("No escalation signals detected.")
                        
                    # Churn Risk Signals
                    st.markdown("### Churn Risk Signals")
                    if response.churn_risk_signals:
                        for sig in response.churn_risk_signals:
                            st.error(f"**{sig.get('signal', 'Unknown')}** in Ticket {sig.get('ticket_id', 'N/A')}: _{sig.get('evidence_quote', '')}_")
                    else:
                        st.write("No explicit churn risk signals detected.")
                        
                except ValueError as ve:
                    st.warning(str(ve))
                except Exception as e:
                    st.error(f"An error occurred during account analysis: {str(e)}")
