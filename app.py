import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Triguna Study Behaviour Model", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem;}
div[data-testid="metric-container"] {
    background-color: #f7f9fc;
    padding: 12px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

st.title("Triguna and Study Behaviour Model")
st.caption("An Indian Knowledge System-based data science app to explore student study patterns.")

with st.sidebar:
    st.header("Student Inputs")
    name = st.text_input("Name", value="")
    age = st.number_input("Age", min_value=10, max_value=40, value=18)
    gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
    st.divider()
    st.subheader("Triguna Scores")
    sattva = st.slider("Sattva", 0, 10, 6)
    rajas = st.slider("Rajas", 0, 10, 5)
    tamas = st.slider("Tamas", 0, 10, 4)
    st.divider()
    st.subheader("Study Behaviour")
    study_hours = st.slider("Study hours/day", 0.0, 12.0, 4.0, 0.5)
    sleep_hours = st.slider("Sleep hours/night", 0.0, 12.0, 7.0, 0.5)
    screen_time = st.slider("Screen time/day", 0.0, 15.0, 5.0, 0.5)
    stress = st.slider("Stress level", 0, 10, 5)
    procrastination = st.slider("Procrastination level", 0, 10, 5)

submitted = st.button("Generate Result", type="primary")


def get_label(score):
    if score >= 4:
        return "High study behaviour"
    elif score >= 1.5:
        return "Moderate study behaviour"
    return "Low study behaviour"


def radar_chart(sattva, rajas, tamas):
    categories = ["Sattva", "Rajas", "Tamas"]
    values = [sattva, rajas, tamas]
    values += values[:1]
    categories += categories[:1]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line_color='#4F46E5',
        name='Triguna Profile'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        height=420
    )
    return fig


def factor_chart(study_hours, sleep_hours, screen_time, stress, procrastination):
    labels = ["Study Hours", "Sleep Hours", "Screen Time", "Stress", "Procrastination"]
    values = [study_hours, sleep_hours, screen_time, stress, procrastination]
    fig = go.Figure([go.Bar(x=labels, y=values, marker_color=['#2563EB','#10B981','#F59E0B','#EF4444','#8B5CF6'])])
    fig.update_layout(
        yaxis_title="Value",
        xaxis_title="Factors",
        height=420,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    return fig

if submitted:
    study_score = (
        0.35 * sattva +
        0.15 * rajas +
        0.20 * study_hours +
        0.15 * sleep_hours -
        0.20 * tamas -
        0.15 * screen_time -
        0.20 * stress -
        0.20 * procrastination
    )
    label = get_label(study_score)

    col1, col2, col3 = st.columns(3)
    col1.metric("Study Behaviour Score", f"{study_score:.2f}")
    col2.metric("Prediction", label)
    col3.metric("Balance Index", f"{(sattva + sleep_hours) - (tamas + stress):.2f}")

    st.success(f"Predicted result: {label}")

    tab1, tab2, tab3 = st.tabs(["Overview", "Charts", "Saved Data"])

    with tab1:
        c1, c2 = st.columns(2)
        c1.subheader("Interpretation")
        if sattva >= rajas and sattva >= tamas:
            c1.write("The profile is dominated by Sattva, which suggests calmness, clarity, and discipline.")
        elif tamas >= sattva and tamas >= rajas:
            c1.write("The profile is dominated by Tamas, which may indicate low energy, delay, and reduced consistency.")
        else:
            c1.write("The profile is dominated by Rajas, which suggests activity and drive, but also possible restlessness.")
        c2.subheader("Inputs")
        df_one = pd.DataFrame([{
            "Name": name, "Age": age, "Gender": gender,
            "Sattva": sattva, "Rajas": rajas, "Tamas": tamas,
            "Study Hours": study_hours, "Sleep Hours": sleep_hours,
            "Screen Time": screen_time, "Stress": stress,
            "Procrastination": procrastination, "Score": round(study_score, 2),
            "Label": label
        }])
        c2.dataframe(df_one, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        c1.plotly_chart(radar_chart(sattva, rajas, tamas), use_container_width=True)
        c2.plotly_chart(factor_chart(study_hours, sleep_hours, screen_time, stress, procrastination), use_container_width=True)

    with tab3:
        data = {
            "Name": [name],
            "Age": [age],
            "Gender": [gender],
            "Sattva": [sattva],
            "Rajas": [rajas],
            "Tamas": [tamas],
            "Study Hours": [study_hours],
            "Sleep Hours": [sleep_hours],
            "Screen Time": [screen_time],
            "Stress": [stress],
            "Procrastination": [procrastination],
            "Study Behaviour Score": [round(study_score, 2)],
            "Label": [label]
        }
        new_df = pd.DataFrame(data)
        file_path = Path("triguna_study_behaviour_data.csv")
        if file_path.exists():
            old_df = pd.read_csv(file_path)
            final_df = pd.concat([old_df, new_df], ignore_index=True)
        else:
            final_df = new_df
        final_df.to_csv(file_path, index=False)
        st.write("Response saved successfully.")
        st.dataframe(final_df, use_container_width=True)

st.info("Use the sidebar to enter values, then click Generate Result.")
