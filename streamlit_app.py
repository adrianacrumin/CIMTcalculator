import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="CIMT Risk Calculator", layout="centered")

st.title("CIMT Risk Report Calculator")

# --- Input section ---
right_cimt = st.number_input("Right CIMT (mm)", value=0.632, format="%.3f")
left_cimt = st.number_input("Left CIMT (mm)", value=0.670, format="%.3f")
age = st.number_input("Patient Age", min_value=15, max_value=100, value=49)
sex = st.selectbox("Sex", [ "Male", "Female"])
race = st.selectbox("Race", ["General", "White", "Black"])
plaque_input = st.text_input("Plaque sizes (comma-separated)", "2.0, 1.5")
plaques = [float(p.strip()) for p in plaque_input.split(",") if p.strip()]
avg_cimt = (right_cimt + left_cimt) / 2

# --- Chart A values ---

chart_A_right = {
    "White Male": {
        45: {"25th": 0.534, "50th": 0.617, "75th": 0.714},
        55: {"25th": 0.610, "50th": 0.711, "75th": 0.834},
        65: {"25th": 0.648, "50th": 0.758, "75th": 0.894}
    },
    "White Female": {
        45: {"25th": 0.509, "50th": 0.576, "75th": 0.660},
        55: {"25th": 0.575, "50th": 0.676, "75th": 0.760},
        65: {"25th": 0.608, "50th": 0.608, "75th": 0.810}
    },
    "Black Male": {
        45: {"25th": 0.514, "50th": 0.604, "75th": 0.700},
        55: {"25th": 0.614, "50th": 0.724, "75th": 0.824},
        65: {"25th": 0.714, "50th": 0.844, "75th": 1.000}
    },
    "Black Female": {
        40: {"25th": 0.719, "50th": 0.790, "75th": 0.880},
        45: {"25th": 0.518, "50th": 0.588, "75th": 0.664},
        55: {"25th": 0.578, "50th": 0.668, "75th": 0.764},
        65: {"25th": 0.638, "50th": 0.748, "75th": 0.864}
    }
}

#Chart A left
chart_A_left = {
    "White Male": {
        45: {"25th": 0.556, "50th": 0.641, "75th": 0.748},
        55: {"25th": 0.620, "50th": 0.727, "75th": 0.864},
        65: {"25th": 0.652, "50th": 0.770, "75th": 0.922}
    },
    "White Female": {
        45: {"25th": 0.556, "50th": 0.641, "75th": 0.748},
        45: {"25th": 0.506, "50th": 0.580, "75th": 0.660},
        55: {"25th": 0.574, "50th": 0.664, "75th": 0.760},
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
        15: {"2.5th": 0.263, "10th": 0.311, "25th": 0.354, "50th": 0.401, "75th": 0.449, "90th":0.492},
        20: {"2.5th": 0.280, "10th": 0.331, "25th": 0.377, "50th": 0.427, "75th": 0.478, "90th":0.524},
        25: {"2.5th": 0.297, "10th": 0.351, "25th": 0.400, "50th": 0.453, "75th": 0.507, "90th":0.556},
        30: {"2.5th": 0.314, "10th": 0.372, "25th": 0.423, "50th": 0.479, "75th": 0.536, "90th":0.587},
        35: {"2.5th": 0.331, "10th": 0.392, "25th": 0.446, "50th": 0.505, "75th": 0.565, "90th":0.619},
        40: {"2.5th": 0.349, "10th": 0.412, "25th": 0.468, "50th": 0.531, "75th": 0.594, "90th":0.651},
        70: {"2.5th": 0.451, "10th": 0.533, "25th": 0.606, "50th": 0.688, "75th": 0.769, "90th":0.842},
        75: {"2.5th": 0.469, "10th": 0.554, "25th": 0.629, "50th": 0.714, "75th": 0.798, "90th":0.873},
        80: {"2.5th": 0.486, "10th": 0.574, "25th": 0.652, "50th": 0.740, "75th": 0.827, "90th":0.905},
        85: {"2.5th": 0.503, "10th": 0.594, "25th": 0.675, "50th": 0.766, "75th": 0.856, "90th":0.937}
    },
    
    "Female": {
        15: {"2.5th": 0.265, "10th": 0.311, "25th": 0.351, "50th": 0.396, "75th": 0.441, "90th":0.482},
        20: {"2.5th": 0.282, "10th": 0.330, "25th": 0.373, "50th": 0.421, "75th": 0.469, "90th":0.512},
        25: {"2.5th": 0.299, "10th": 0.350, "25th": 0.395, "50th": 0.446, "75th": 0.497, "90th":0.542},
        30: {"2.5th": 0.315, "10th": 0.369, "25th": 0.417, "50th": 0.471, "75th": 0.524, "90th":0.572},
        35: {"2.5th": 0.332, "10th": 0.389, "25th": 0.439, "50th": 0.496, "75th": 0.552, "90th":0.602},
        40: {"2.5th": 0.349, "10th": 0.408, "25th": 0.461, "50th": 0.521, "75th": 0.580, "90th":0.633},
        70: {"2.5th": 0.450, "10th": 0.526, "25th": 0.594, "50th": 0.670, "75th": 0.745, "90th":0.813},
        75: {"2.5th": 0.466, "10th": 0.545, "25th": 0.616, "50th": 0.694, "75th": 0.773, "90th":0.843},
        80: {"2.5th": 0.483, "10th": 0.565, "25th": 0.638, "50th": 0.719, "75th": 0.801, "90th":0.874},
        85: {"2.5th": 0.500, "10th": 0.585, "25th": 0.660, "50th": 0.744, "75th": 0.828, "90th":0.904}
        # ...
    }
}

def get_cimt_percentile(cimt_value, age, sex, race, side="right"):
    if age <= 40 or age >= 65:
        # General Chart Usage
        closest_age = min(general_chart[sex].keys(), key=lambda x: abs(x - age))
        thresholds = general_chart[sex][closest_age]
    else:
        # Race-Specific Chart Usage
        group = f"{race} {sex}"
        chart = chart_A_right if side == "right" else chart_A_left
        closest_age = min(chart[group].keys(), key=lambda x: abs(x - age))
        thresholds = chart[group][closest_age]

    # Sort thresholds by numerical percentile value
    sorted_thresholds = sorted(
        thresholds.items(),
        key=lambda x: float(x[0].replace("th", "").replace("≤", ""))
    )

    # Loop through sorted percentiles and find the closest match
    for i, (percentile, value) in enumerate(sorted_thresholds):
        if cimt_value <= value:
            return f"{percentile} percentile"

    # If above all thresholds
    return f"Above {sorted_thresholds[-1][0]} percentile"
    
right_percentile = get_cimt_percentile(right_cimt, age, sex, race, "right")
left_percentile = get_cimt_percentile(left_cimt, age, sex, race, "left")

# --- Vascular Age ---
def estimate_vascular_age(cimt_avg, sex):
    vascular_age_curve = {
        "Male": {0.50: 35, 0.55: 40, 0.60: 45, 0.65: 50, 0.70: 55, 0.75: 60, 0.80: 65, 0.85: 70, 0.90: 75},
        "Female": {0.50: 40, 0.55: 45, 0.60: 50, 0.65: 55, 0.70: 60, 0.75: 65, 0.80: 70, 0.85: 75, 0.90: 80}
    }
    values = vascular_age_curve[sex]
    closest = min(values.keys(), key=lambda x: abs(cimt_avg - x))
    return values[closest]

vascular_age = estimate_vascular_age(avg_cimt, sex)

# --- Plaque burden ---
plaque_burden = sum(p for p in plaques if p >= 1.2)
has_plaque = plaque_burden > 0

# --- Impression generator ---
def generate_impression(rp, lp, has_plaque):
    low_risk_levels = ["2.5th percentile", "10th percentile", "25th percentile"]
    high_risk_levels = ["75th percentile", "90th percentile", "Above 90th percentile"]

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

impression = generate_impression(right_percentile, left_percentile, has_plaque)

# --- Output section ---
st.subheader("CIMT Risk Summary")
st.write(f"**Right CIMT**: {right_cimt} mm → _{right_percentile}_")
st.write(f"**Left CIMT**: {left_cimt} mm → _{left_percentile}_")
st.write(f"**Average CIMT**: {avg_cimt:.3f} mm")
st.write(f"**Vascular Age Estimate**: {vascular_age} years")
st.write(f"**Plaque Burden**: {plaque_burden:.3f} mm")
st.markdown(f"**Impression**: _{impression}_")

st.markdown("**Note:** There is a 95% correlation between carotid and coronary arteries for presence of plaque. "
            "Consider further testing such as coronary calcium scoring for high-risk patients.")

# --- Chart 3 Visualization ---
ages = np.arange(15, 86)
male_curve = 0.5 + 0.006 * (ages - 15)
female_curve = 0.48 + 0.0055 * (ages - 15)

fig, ax = plt.subplots()
ax.plot(ages, male_curve, label="Male Avg", color="black")
ax.plot(ages, female_curve, label="Female Avg", color="gray")
ax.axhline(avg_cimt, color="red", linestyle="--", label="Patient CIMT")
ax.scatter(vascular_age, avg_cimt, color="red", zorder=5)
ax.set_xlabel("Age")
ax.set_ylabel("CIMT (mm)")
ax.set_title("Vascular Age Estimate (Chart 3)")
ax.grid(True)
ax.legend()
st.pyplot(fig)
