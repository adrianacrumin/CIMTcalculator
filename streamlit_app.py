import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Streamlit Config ---
st.set_page_config(page_title="CIMT Risk Calculator", layout="centered")
st.title("CIMT Risk Report Calculator")

# --- Input Section ---
right_cimt = st.number_input("Right CIMT (mm)", value=0.0, format="%.3f")
left_cimt = st.number_input("Left CIMT (mm)", value=0.0, format="%.3f")
age = st.number_input("Patient Age", min_value=15, max_value=100, value=15)
sex = st.selectbox("Sex", ["Male", "Female"])

# Race selection logic
if age <= 42 or age >= 67:
    st.write("General population reference is used for ages ≤42 or ≥67.")
    race = "General (15-40 & 70+)"
else:
    race = st.selectbox("Select Race (Required for ages 43-66)", ["White", "Black"])

plaque_input = st.text_input("Plaque sizes (comma-separated)", "0.0, 0.0")
plaques = [float(p.strip()) for p in plaque_input.split(",") if p.strip()]

# --- Chart Definitions (Chart A Right/Left and General Chart remain unchanged) ---
# (Insert your complete chart_A_right, chart_A_left, and general_chart here — omitted for brevity)

# --- Functions ---

def get_cimt_percentile(cimt_value, age, sex, race, side="right"):
    if race == "General (15-40 & 70+)" or age <= 40 or age >= 70:
        closest_age = min(general_chart[sex].keys(), key=lambda x: abs(x - age))
        thresholds = general_chart[sex][closest_age]
    else:
        group = f"{race} {sex}"
        chart = chart_A_right if side == "right" else chart_A_left
        if group not in chart:
            return "No reference data available for this group"
        closest_age = min(chart[group].keys(), key=lambda x: abs(x - age))
        thresholds = chart[group][closest_age]

    sorted_thresholds = sorted(thresholds.items(), key=lambda x: float(x[0].replace("th", "")))

    if cimt_value <= sorted_thresholds[0][1]:
        return f"Below {sorted_thresholds[0][0]} percentile"

    for i in range(len(sorted_thresholds) - 1):
        lower_label, lower_value = sorted_thresholds[i]
        upper_label, upper_value = sorted_thresholds[i + 1]
        if lower_value < cimt_value <= upper_value:
            return f"Between {lower_label} and {upper_label} percentile"

    return f"Above {sorted_thresholds[-1][0]} percentile"

def estimate_vascular_age_from_curve(cimt_avg, sex):
    ages = np.arange(15, 86)
    if sex == "Male":
        curve = 0.35 + 0.008 * (ages - 15)
    else:
        curve = 0.33 + 0.0075 * (ages - 15)

    closest_age = ages[np.abs(curve - cimt_avg).argmin()]
    return closest_age

def generate_impression(rp, lp, has_plaque):
    low_risk_levels = ["2.5th percentile","Between 2.5th and 10th percentile", "10th percentile",  "Between 10th and 25th percentile", "25th percentile", "Between 25th and 50th percentile"]
    moderate_risk_levels = ["50th percentile", "Between 50th and 75th percentile"]
    high_risk_levels = ["75th percentile","Between 75th and 90th percentile", "90th percentile", "Above 90th percentile"]

    if not has_plaque:
        if rp in low_risk_levels and lp in low_risk_levels:
            return "Low cardiovascular risk based on CIMT and absence of plaque."
        elif rp in high_risk_levels or lp in high_risk_levels:
            return "High cardiovascular risk based on elevated CIMT without plaque."
        else:
            return "Moderate cardiovascular risk based on CIMT findings without plaque."
    else:
        if rp in high_risk_levels or lp in high_risk_levels:
            return "High cardiovascular risk due to elevated CIMT and presence of plaque."
        else:
            return "Moderate cardiovascular risk due to presence of plaque despite lower CIMT."

def plot_cimt_chart_with_point_pairs(avg_cimt, vascular_age, sex):
    # Male reference points (age, CIMT)
    male_curve_points = [
        (6, 0.38), (10, 0.395), (15, 0.43), (20, 0.475), (22, 0.50), (25, 0.50),
        (28, 0.50), (30, 0.51), (35, 0.545), (37, 0.55), (40, 0.58), (41, 0.595),
        (45, 0.61), (47, 0.605), (50, 0.65), (55, 0.70), (60, 0.75), (65, 0.80),
        (70, 0.85), (75, 0.90), (80, 0.95), (90, 1.00)
    ]

    # Female reference points (age, CIMT)
    female_curve_points = [
        (6, 0.38), (10, 0.405), (15, 0.40), (21, 0.449), (25.5, 0.449), (30, 0.48),
        (35, 0.50), (36, 0.515), (41.5, 0.53), (45, 0.55), (50, 0.59), (55, 0.635),
        (60, 0.68), (65, 0.715), (70, 0.765), (75, 0.81), (80, 0.86), (85, 0.91)
    ]

    # Extract points
    male_ages, male_cimt_values = zip(*male_curve_points)
    female_ages, female_cimt_values = zip(*female_curve_points)

    # Create Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(male_ages, male_cimt_values, label="Average Male", color="black", linewidth=2)
    ax.plot(female_ages, female_cimt_values, label="Average Female", color="gray", linewidth=2)
    ax.axhline(y=avg_cimt, color="red", linestyle="--", label="Patient CIMT")
    ax.scatter(vascular_age, avg_cimt, color="red", s=100, zorder=5, label=f"Vascular Age: {vascular_age}")

    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Mean Distal 1 cm CCA IMT (mm)")
    ax.set_title("Mean Distal 1 cm CCA IMT of General Population\nwith No Coronary Heart History")
    ax.set_xlim(0, 80)
    ax.set_ylim(0.00, 1.15)
    ax.set_yticks(np.arange(0.00, 1.20, 0.05))
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)


# --- Calculation & Output Block ---
if right_cimt > 0 and left_cimt > 0:
    avg_cimt = (right_cimt + left_cimt) / 2

    # Estimate vascular age from curve (not race-dependent)
    vascular_age = estimate_vascular_age_from_curve(avg_cimt, sex)

    # Get percentiles (race-dependent)
    right_percentile = get_cimt_percentile(right_cimt, age, sex, race, "right")
    left_percentile = get_cimt_percentile(left_cimt, age, sex, race, "left")

    # Plaque burden and impression
    plaque_burden = sum(p for p in plaques if p >= 1.2)
    has_plaque = plaque_burden > 0
    impression = generate_impression(right_percentile, left_percentile, has_plaque)

    # Display CIMT Risk Summary
    st.subheader("CIMT Risk Summary")
    st.write(f"**Right CIMT**: {right_cimt} mm → _{right_percentile}_")
    st.write(f"**Left CIMT**: {left_cimt} mm → _{left_percentile}_")
    st.write(f"**Average CIMT**: {avg_cimt:.3f} mm")
    st.write(f"**Vascular Age Estimate**: {vascular_age} years")
    st.write(f"**Plaque Burden**: {plaque_burden:.3f} mm")
    st.markdown(f"**Impression**: _{impression}_")
    st.markdown("**Note:** There is a 95% correlation between carotid and coronary arteries for presence of plaque. "
                "Consider further testing such as coronary calcium scoring for high-risk patients.")

    # --- Show the Plot ---
    plot_cimt_chart_with_point_pairs(avg_cimt, vascular_age, sex)

else:
    st.info("Please enter valid Right and Left CIMT values greater than 0.0 to generate the report.")

