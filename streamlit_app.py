import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Streamlit Config ---
st.set_page_config(page_title="CIMT Risk Calculator", layout="centered")
st.title("CIMT Risk Report Calculator")

# --- Input Section ---
right_cimt = st.number_input(
    "Right CIMT (mm)", 
    min_value=0.0, 
    step=0.001, 
    format="%.3f"
)
left_cimt = st.number_input(
    "Left CIMT (mm)", 
    min_value=0.0, 
    step=0.001, 
    format="%.3f"
)
age = st.number_input("Patient Age", min_value=15, max_value=100)
sex = st.selectbox("Sex", ["Male", "Female"])

if age <= 42 or age >= 67:
    st.write("General population reference is used for ages ≤42 or ≥67.")
    race = "General (15-40 & 70+)"
else:
    race = st.selectbox("Select Race (Required for ages 43-66)", ["White", "Black"])

plaque_input = st.text_input("Plaque sizes (comma-separated)")
plaques = [float(p.strip()) for p in plaque_input.split(",") if p.strip()]

# --- Chart Definitions ---
chart_A_right = {
    "White Male": {
        45: {"25th": 0.496, "50th": 0.570, "75th": 0.654},
        50: {"25th": 0.534, "50th": 0.617, "75th": 0.714},
        55: {"25th": 0.572, "50th": 0.664, "75th": 0.774},
        60: {"25th": 0.610, "50th": 0.711, "75th": 0.834},
        65: {"25th": 0.648, "50th": 0.758, "75th": 0.894}
    },
    "White Female": {
        45: {"25th": 0.476, "50th": 0.536, "75th": 0.610},
        50: {"25th": 0.509, "50th": 0.576, "75th": 0.660},
        55: {"25th": 0.542, "50th": 0.616, "75th": 0.710},
        60: {"25th": 0.575, "50th": 0.676, "75th": 0.760},
        65: {"25th": 0.608, "50th": 0.608, "75th": 0.810}
    },
    "Black Male": {
        45: {"25th": 0.514, "50th": 0.604, "75th": 0.700},
        55: {"25th": 0.614, "50th": 0.724, "75th": 0.824},
        65: {"25th": 0.714, "50th": 0.844, "75th": 1.000}
    },
    "Black Female": {
        45: {"25th": 0.518, "50th": 0.588, "75th": 0.664},
        55: {"25th": 0.578, "50th": 0.668, "75th": 0.764},
        65: {"25th": 0.638, "50th": 0.748, "75th": 0.864}
    }
}

chart_A_left = {
    "White Male": {
        45: {"25th": 0.524, "50th": 0.598, "75th": 0.690},
        50: {"25th": 0.556, "50th": 0.641, "75th": 0.748},
        55: {"25th": 0.588, "50th": 0.684, "75th": 0.806},
        60: {"25th": 0.620, "50th": 0.727, "75th": 0.864},
        65: {"25th": 0.652, "50th": 0.770, "75th": 0.922}
    },
    "White Female": {
        45: {"25th": 0.472, "50th": 0.538, "75th": 0.610},
        50: {"25th": 0.506, "50th": 0.580, "75th": 0.660},
        55: {"25th": 0.540, "50th": 0.622, "75th": 0.710},
        60: {"25th": 0.574, "50th": 0.664, "75th": 0.760},
        65: {"25th": 0.608, "50th": 0.706, "75th": 0.810}
    },
    "Black Male": {
        45: {"25th": 0.530, "50th": 0.614, "75th": 0.704},
        55: {"25th": 0.610, "50th": 0.714, "75th": 0.840},
        65: {"25th": 0.690, "50th": 0.814, "75th": 0.976}
    },
    "Black Female": {
        45: {"25th": 0.494, "50th": 0.566, "75th": 0.644},
        55: {"25th": 0.558, "50th": 0.646, "75th": 0.748},
        65: {"25th": 0.622, "50th": 0.726, "75th": 0.852}
    }
}

general_chart = {
    "Male": {
        15: {"2.5th": 0.263, "10th": 0.311, "25th": 0.354, "50th": 0.401, "75th": 0.449, "90th": 0.492},
        20: {"2.5th": 0.280, "10th": 0.331, "25th": 0.377, "50th": 0.427, "75th": 0.478, "90th": 0.524},
        25: {"2.5th": 0.297, "10th": 0.351, "25th": 0.400, "50th": 0.453, "75th": 0.507, "90th": 0.556},
        30: {"2.5th": 0.314, "10th": 0.372, "25th": 0.423, "50th": 0.479, "75th": 0.536, "90th": 0.587},
        35: {"2.5th": 0.331, "10th": 0.392, "25th": 0.446, "50th": 0.505, "75th": 0.565, "90th": 0.619},
        40: {"2.5th": 0.349, "10th": 0.412, "25th": 0.468, "50th": 0.531, "75th": 0.594, "90th": 0.651},
        70: {"2.5th": 0.451, "10th": 0.533, "25th": 0.606, "50th": 0.688, "75th": 0.769, "90th": 0.842},
        75: {"2.5th": 0.469, "10th": 0.554, "25th": 0.629, "50th": 0.714, "75th": 0.798, "90th": 0.873},
        80: {"2.5th": 0.486, "10th": 0.574, "25th": 0.652, "50th": 0.740, "75th": 0.827, "90th": 0.905},
        85: {"2.5th": 0.503, "10th": 0.594, "25th": 0.675, "50th": 0.766, "75th": 0.856, "90th": 0.937}
    },
    "Female": {
        15: {"2.5th": 0.265, "10th": 0.311, "25th": 0.351, "50th": 0.396, "75th": 0.441, "90th": 0.482},
        20: {"2.5th": 0.282, "10th": 0.330, "25th": 0.373, "50th": 0.421, "75th": 0.469, "90th": 0.512},
        25: {"2.5th": 0.299, "10th": 0.350, "25th": 0.395, "50th": 0.446, "75th": 0.497, "90th": 0.542},
        30: {"2.5th": 0.315, "10th": 0.369, "25th": 0.417, "50th": 0.471, "75th": 0.524, "90th": 0.572},
        35: {"2.5th": 0.332, "10th": 0.389, "25th": 0.439, "50th": 0.496, "75th": 0.552, "90th": 0.602},
        40: {"2.5th": 0.349, "10th": 0.408, "25th": 0.461, "50th": 0.521, "75th": 0.580, "90th": 0.633},
        70: {"2.5th": 0.450, "10th": 0.526, "25th": 0.594, "50th": 0.670, "75th": 0.745, "90th": 0.813},
        75: {"2.5th": 0.466, "10th": 0.545, "25th": 0.616, "50th": 0.694, "75th": 0.773, "90th": 0.843},
        80: {"2.5th": 0.483, "10th": 0.565, "25th": 0.638, "50th": 0.719, "75th": 0.801, "90th": 0.874},
        85: {"2.5th": 0.500, "10th": 0.585, "25th": 0.660, "50th": 0.744, "75th": 0.828, "90th": 0.904}
    }
}

# --- Helpers: band + label and impression ---
def cimt_band_and_label(cimt_value, age, sex, race, side="right"):
    """
    Returns:
      band  : 0=≤25th, 1=25–50th, 2=50–75th, 3=≥75th
      label : human-readable label to display
    """
    if race == "General (15-40 & 70+)" or age <= 40 or age >= 70:
        closest_age = min(general_chart[sex].keys(), key=lambda x: abs(x - age))
        thresholds = general_chart[sex][closest_age]
    else:
        group = f"{race} {sex}"
        chart = chart_A_right if side == "right" else chart_A_left
        if group not in chart:
            return 0, "No reference data available for this group"
        closest_age = min(chart[group].keys(), key=lambda x: abs(x - age))
        thresholds = chart[group][closest_age]

    v25, v50, v75 = thresholds["25th"], thresholds["50th"], thresholds["75th"]

    if cimt_value <= v25:
        return 0, "≤25th percentile"
    elif cimt_value <= v50:
        return 1, "25th–50th percentile"
    elif cimt_value <= v75:
        return 2, "Between 50th and 75th percentile"
    else:
        return 3, "Above 75th percentile"

def generate_impression(r_band, l_band, has_plaque):
    worst = max(r_band, l_band)
    if not has_plaque:
        if worst >= 3:
            return "High cardiovascular risk based on elevated CIMT (≥75th percentile) without plaque."
        elif worst == 2:
            return "Moderate cardiovascular risk based on CIMT in the 50th–75th percentile without plaque."
        else:
            return "Low cardiovascular risk based on CIMT (≤50th percentile) and absence of plaque."
    else:
        if worst >= 3:
            return "High cardiovascular risk due to plaque and CIMT ≥75th percentile."
        elif worst == 2:
            return "Moderate cardiovascular risk due to plaque with CIMT in the 50th–75th percentile."
        else:
            return "Moderate cardiovascular risk due to presence of plaque despite lower CIMT."

# --- Vascular age (your original) ---
def estimate_vascular_age_from_curve(cimt_avg, sex):
    male_curve_points = [
        (6, 0.38), (10, 0.395), (15, 0.43), (20, 0.475), (22, 0.50), (25, 0.50),
        (28, 0.50), (30, 0.51), (35, 0.545), (37, 0.55), (40, 0.58), (41, 0.595),
        (45, 0.61), (47, 0.605), (50, 0.65), (55, 0.70), (60, 0.75), (65, 0.80),
        (70, 0.85), (75, 0.90), (80, 0.95), (90, 1.00)
    ]
    female_curve_points = [
        (6, 0.38), (10, 0.405), (15, 0.40), (21, 0.449), (25.5, 0.449), (30, 0.48),
        (35, 0.50), (36, 0.515), (41.5, 0.53), (45, 0.55), (50, 0.59), (55, 0.635),
        (60, 0.68), (65, 0.715), (70, 0.765), (75, 0.81), (80, 0.86), (85, 0.91)
    ]
    curve_points = male_curve_points if sex == "Male" else female_curve_points
    curve_ages, curve_cimt_values = zip(*curve_points)
    idx = np.abs(np.array(curve_cimt_values) - cimt_avg).argmin()
    return curve_ages[idx]

def plot_cimt_chart_with_point_pairs(avg_cimt, vascular_age, sex):
    male_curve_points = [
        (6, 0.38), (10, 0.395), (15, 0.43), (20, 0.475), (22, 0.50), (25, 0.50),
        (28, 0.50), (30, 0.51), (35, 0.545), (37, 0.55), (40, 0.58), (41, 0.595),
        (45, 0.61), (47, 0.605), (50, 0.65), (55, 0.70), (60, 0.75), (65, 0.80),
        (70, 0.85), (75, 0.90), (80, 0.95), (90, 1.00)
    ]
    female_curve_points = [
        (6, 0.38), (10, 0.405), (15, 0.40), (21, 0.449), (25.5, 0.449), (30, 0.48),
        (35, 0.50), (36, 0.515), (41.5, 0.53), (45, 0.55), (50, 0.59), (55, 0.635),
        (60, 0.68), (65, 0.715), (70, 0.765), (75, 0.81), (80, 0.86), (85, 0.91)
    ]
    male_ages, male_cimt_values = zip(*male_curve_points)
    female_ages, female_cimt_values = zip(*female_curve_points)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(male_ages, male_cimt_values, label="Average Male", color="black", linewidth=2)
    ax.plot(female_ages, female_cimt_values, label="Average Female", color="gray", linewidth=2)
    ax.axhline(y=avg_cimt, color="red", linestyle="--", label="Patient CIMT")
    ax.scatter(vascular_age, avg_cimt, color="red", s=100, zorder=5, label=f"Vascular Age: {vascular_age}")

    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Mean Distal 1 cm CCA IMT (mm)")
    ax.set_title("Mean Distal 1 cm CCA IMT of General Population\nwith No Coronary Heart History")
    ax.set_xlim(0, 80)
    ax.set_xticks(np.arange(0, 90, 5))
    ax.set_ylim(0.00, 1.15)
    ax.set_yticks(np.arange(0.00, 1.20, 0.05))
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

# --- Calculation and Report Block ---
if right_cimt > 0 and left_cimt > 0:
    avg_cimt = (right_cimt + left_cimt) / 2
    vascular_age = estimate_vascular_age_from_curve(avg_cimt, sex)

    r_band, right_percentile = cimt_band_and_label(right_cimt, age, sex, race, "right")
    l_band, left_percentile  = cimt_band_and_label(left_cimt,  age, sex, race, "left")

    plaque_burden = sum(p for p in plaques if p >= 1.2)
    has_plaque = plaque_burden > 0
    impression = generate_impression(r_band, l_band, has_plaque)

    st.subheader("CIMT Risk Summary")
    st.write(f"**Right CIMT**: {right_cimt:.3f} mm → _{right_percentile}_")
    st.write(f"**Left CIMT**: {left_cimt:.3f} mm → _{left_percentile}_")
    st.write(f"**Average CIMT**: {avg_cimt:.3f} mm")
    st.write(f"**Vascular Age Estimate**: {vascular_age} years")
    st.write(f"**Plaque Burden**: {plaque_burden:.3f} mm")
    st.markdown(f"**Impression**: _{impression}_")
    st.markdown("**Note:** There is a 95% correlation between carotid and coronary arteries for presence of plaque. "
                "Consider further testing such as coronary calcium scoring for high-risk patients.")

    plot_cimt_chart_with_point_pairs(avg_cimt, vascular_age, sex)
else:
    st.info("Please enter valid Right and Left CIMT values greater than 0.0 to generate the report.")

