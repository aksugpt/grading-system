import streamlit as st

import config
from grader import grade_essay

st.set_page_config(page_title="Essay Grader", page_icon="📝", layout="centered")
st.title("📝 Essay Grader")
st.caption(f"Model: {config.MODEL} · scores are an AI estimate, not an official grade")

essay_prompt = st.text_area(
    "Essay prompt / question (optional)", height=80,
    placeholder="e.g. Discuss the impact of social media on teenagers.",
)
essay = st.text_area("Paste your essay", height=320)
st.write(f"Words: {len(essay.split())}")

if st.button("Grade essay", type="primary"):
    try:
        with st.spinner("Grading..."):
            result = grade_essay(essay, essay_prompt)
    except Exception as e:
        st.error(str(e))
    else:
        col1, col2 = st.columns(2)
        col1.metric("Overall score", f"{result['total']} / 100")
        col2.metric("Grade", result["letter"])

        st.subheader("Criteria")
        for name, weight in config.WEIGHTS.items():
            score = result["scores"][name]
            st.markdown(f"**{name.title()}** ({int(weight * 100)}%): {score:g} / 10")
            st.progress(min(max(score / 10, 0.0), 1.0))
            st.caption(result["reasons"][name])

        st.subheader("Feedback")
        st.write(result["feedback"])
        left, right = st.columns(2)
        with left:
            st.markdown("**Strengths**")
            for s in result["strengths"]:
                st.markdown(f"- {s}")
        with right:
            st.markdown("**To improve**")
            for s in result["improvements"]:
                st.markdown(f"- {s}")
