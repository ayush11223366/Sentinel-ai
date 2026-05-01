import streamlit as st
# Import the compiled LangGraph engine we just built
from sentinel import sentinel_engine 

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Sentinel AI Auditor", page_icon="🛡️", layout="centered")

st.title("🛡️ Sentinel AI")
st.subheader("Fintech Compliance & Risk Assessment Engine")
st.markdown("Powered by **LangGraph Multi-Agent Architecture** and **ChromaDB RAG**.")
st.divider()

# --- INPUT SECTION ---
url_input = st.text_input("Enter Merchant URL to Audit:", placeholder="https://getintopc.com")

# --- EXECUTION TRIGGER ---
if st.button("Run Full Compliance Audit", type="primary", use_container_width=True):
    if not url_input:
        st.warning("⚠️ Please enter a URL to begin the audit.")
    else:
        # The progress spinner so the user knows the AI is thinking
        with st.spinner("🤖 Sentinel Agents deployed. Scraping, analyzing, and retrieving policy..."):
            
            # 1. Setup the exact initial memory state your graph expects
            initial_state = {
                "url": url_input,
                "scraped_text": "",
                "retrieved_policy": "", 
                "compliance_flags": [],
                "risk_score": 0.0,
                "summary": "",
                "final_decision": ""
            }
            
            try:
                # 2. RUN THE ENGINE!
                final_state = sentinel_engine.invoke(initial_state)
                
                # 3. RENDER THE UI RESULTS
                st.divider()
                st.markdown("## 📊 Final Audit Report")
                
                # Layout metrics side-by-side
                col1, col2 = st.columns(2)
                
                with col1:
                    if "Reject" in final_state['final_decision']:
                        st.error(f"**Decision:** {final_state['final_decision']}")
                    else:
                        st.success(f"**Decision:** {final_state['final_decision']}")
                        
                with col2:
                    st.warning(f"**Risk Flags Detected:** {len(final_state['compliance_flags'])}")
                
                # Summary Section
                st.markdown("### 📝 Executive Summary")
                st.info(final_state['summary'])
                
                # Flags Section
                if final_state['compliance_flags']:
                    st.markdown("### 🚩 Identified Risk Keywords")
                    for flag in final_state['compliance_flags']:
                        st.markdown(f"- `{flag}`")
                
                # "Under the Hood" Section to show off your engineering
                with st.expander("🔍 View AI RAG Context (What the AI read from the database)"):
                    st.write(final_state.get('retrieved_policy', 'No policy retrieved.'))
                    
            except Exception as e:
                st.error(f"🚨 Pipeline Execution Failed: {e}")
                st.markdown("Check your terminal for the full traceback.")