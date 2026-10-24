import streamlit as st
from agent import run_agent

st.set_page_config(page_title="Research Agent", page_icon="🔎")

st.title("🔎 Research Agent")
st.write("Ask a question. The agent searches the web, reads pages, and answers with sources.")

question = st.text_input("Your question")

if st.button("Ask") and question:
    steps_box = st.expander("Agent steps", expanded=True)

    def show_step(message):
        steps_box.write(message)

    with st.spinner("Researching..."):
        answer = run_agent(question, on_step=show_step)
    st.markdown(answer)