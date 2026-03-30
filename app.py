import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Cylinder Volume Explorer", layout="wide")


# --- Physics Constants ---
R_CONSTANT = 8.314  # J/(mol·K) = Pa·m³/(mol·K)
TEMP_K = 25 + 273.15  # 25°C in Kelvin
P_ATMOS_PA = 101325  # Standard atmospheric pressure in Pa
P_ATMOS_CMHG = 76.0  # Standard atmospheric pressure in cmHg
# Conversion factor
PA_TO_CMHG = 76 / 101325  # ~0.000750062 (1 Pa ≈ 0.00075 cmHg)

# --- Sidebar Inputs ---
st.sidebar.header("Cylinder Size")

# Toggle for pressure units (first element)
pressure_unit = st.sidebar.radio(
    "Pressure Unit", ["cmHg", "Pa"], key="pressure_unit_radio"
)

input_h = st.sidebar.number_input("Current Height (mm)", value=23.0, step=1.0)
input_d = st.sidebar.number_input("Current Diameter (mm)", value=36.0, step=1.0)

# Derived calculations
input_r = input_d / 2
initial_volume = np.pi * (input_r**2) * input_h

# Display calculated volume in sidebar
st.sidebar.metric("Cylinder Volume", f"{initial_volume:,.2f} mm³")

# --- Starting Volume Input ---
st.sidebar.header("Starting Volume")
v_start_input_mm3 = st.sidebar.number_input(
    "Starting Volume (mm³)",
    value=3500.0,
    step=100.0,
    help="Input starting volume in cubic millimeters",
)
# Auto-convert to liters
v_start_input_liters = v_start_input_mm3 / 1e6
st.sidebar.metric("Starting Volume (mm³)", f"{v_start_input_mm3:,.0f} mm³")

# Convert to m³ for calculations
v_start_m3 = v_start_input_mm3 / 1e9

# Calculate number of moles from starting volume using PV = nRT → n = PV/(RT)
n_moles = (P_ATMOS_PA * v_start_m3) / (R_CONSTANT * TEMP_K)


# --- Logic & Data ---
def calculate_height(radius, volume):
    return volume / (np.pi * radius**2)


def calculate_pressure_change(v_start_m3, v_total_m3, n_moles, T_K):
    """
    Calculate pressure change when volume changes at constant temperature and moles.
    Using PV = nRT
    P_initial = P0 (1 atm)
    P_final = nRT / V_final
    ΔP = P_final - P_initial
    """
    P_final = (n_moles * R_CONSTANT * T_K) / v_total_m3
    delta_P_pa = P_final - P_ATMOS_PA
    delta_P_cmhg = delta_P_pa * PA_TO_CMHG
    p_atm = P_final / P_ATMOS_PA
    return delta_P_pa, delta_P_cmhg, P_final, p_atm


# Plotting range for Radius
r_min, r_max = 10.0, 20.0
r_values = np.linspace(r_min, r_max, 500)
# 50% to 150% in 10% increments
percentages = np.arange(0.5, 1.6, 0.1)

# --- Calculate Pressure Changes for Each Volume ---
pressure_data = []
for p in percentages:
    vol_at_p = initial_volume * p
    v_total_m3 = v_start_m3 + (vol_at_p / 1e9)  # Convert mm³ to m³ and add
    delta_P_pa, delta_P_cmhg, P_final, p_atm = calculate_pressure_change(
        v_start_m3, v_total_m3, n_moles, TEMP_K
    )

    pressure_data.append(
        {
            "Volume Change (%)": p * 100,
            "Volume Change (mm³)": vol_at_p,
            "Total Volume (L)": v_start_input_liters + (vol_at_p / 1e6),
            "Total Volume (mm³)": v_start_input_mm3 + vol_at_p,
            "Pressure (Pa)": P_final,
            "Pressure (atm)": p_atm,
            "ΔP (Pa)": delta_P_pa,
            "Pressure (cmHg)": P_final * PA_TO_CMHG,
            "ΔP (cmHg)": delta_P_cmhg,
        }
    )

pressure_df = pd.DataFrame(pressure_data)

# --- Plotting ---
fig = go.Figure()

for p in percentages:
    vol_at_p = initial_volume * p
    h_values = calculate_height(r_values, vol_at_p)

    # Styling: Highlight the 100% (Current) line
    is_center = np.isclose(p, 1.0)
    opacity = 1.0 if is_center else 0.5
    linewidth = 4 if is_center else 2
    label = f"{int(p*100)}% Vol"

    fig.add_trace(
        go.Scatter(
            x=r_values,
            y=h_values,
            mode="lines",
            name=label,
            line=dict(width=linewidth),
            opacity=opacity,
            hovertemplate=f"<b>{label}</b><br>Radius: %{{x:.2f}} mm<br>Height: %{{y:.2f}} mm<extra></extra>",
        )
    )

# Current point marker
fig.add_trace(
    go.Scatter(
        x=[input_r],
        y=[input_h],
        mode="markers",
        name=f"Current",
        marker=dict(size=10, color="red"),
        hovertemplate=f"<b>Current Point</b><br>Radius: {input_r:.2f} mm<br>Height: {input_h:.2f} mm<extra></extra>",
    )
)

# Add vertical dashed lines at every x-axis tick (every 5 mm)
x_ticks = np.arange(r_min, r_max + 1, 5)
for x_tick in x_ticks:
    fig.add_vline(
        x=x_tick,
        line_dash="dash",
        line_color="rgba(150, 150, 150, 0.2)",
        line_width=1,
    )

# Add horizontal dashed lines at every y-axis tick (every 10 mm)
y_ticks = np.arange(10, 61, 10)
for y_tick in y_ticks:
    fig.add_hline(
        y=y_tick,
        line_dash="dash",
        line_color="rgba(150, 150, 150, 0.2)",
        line_width=1,
    )

# Add Current crosshairs (more visible)
fig.add_vline(
    x=input_r,
    line_dash="dash",
    line_color="rgba(200, 100, 100, 0.5)",
    line_width=2,
    annotation_text=f"R: {input_r:.1f}mm",
    annotation_position="top",
)

fig.add_hline(
    y=input_h,
    line_dash="dash",
    line_color="rgba(100, 100, 200, 0.5)",
    line_width=2,
    annotation_text=f"H: {input_h:.1f}mm",
    annotation_position="right",
)

# Update layout
fig.update_layout(
    xaxis_title="Radius (mm)",
    yaxis_title="Height (mm)",
    hovermode="closest",
    height=600,
    xaxis=dict(
        range=[r_min, r_max],
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(200, 200, 200, 0.2)",
    ),
    yaxis=dict(
        range=[10, 60],
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(200, 200, 200, 0.2)",
    ),
    template="plotly_white",
)

# --- Second Graph: Constant Volume Curves Labeled by Pressure ---
# Use same percentages as first graph, but label by pressure
fig2 = go.Figure()

for p in percentages:
    vol_at_p = initial_volume * p
    h_values = calculate_height(r_values, vol_at_p)

    # Calculate pressure for this volume
    v_total_m3 = v_start_m3 + (vol_at_p / 1e9)
    P_final = (n_moles * R_CONSTANT * TEMP_K) / v_total_m3
    delta_P_pa = P_final - P_ATMOS_PA

    # Styling: Highlight the 100% (Current) line
    is_center = np.isclose(p, 1.0)
    opacity = 1.0 if is_center else 0.5
    linewidth = 4 if is_center else 2

    # Format comprehensive label with volume %, delta volume, and delta pressure
    delta_P_cmhg = delta_P_pa * PA_TO_CMHG
    vol_pct = int(p * 100)
    label = f"{vol_pct}%V; ΔV = {vol_at_p:,.0f} mm³; ΔP = {delta_P_cmhg:.3f} cmHg"

    fig2.add_trace(
        go.Scatter(
            x=r_values,
            y=h_values,
            mode="lines",
            name=label,
            line=dict(width=linewidth),
            opacity=opacity,
            hovertemplate=f"<b>{label}</b><br>Radius: %{{x:.2f}} mm<br>Height: %{{y:.2f}} mm<extra></extra>",
        )
    )

# Current point marker (same as before)
fig2.add_trace(
    go.Scatter(
        x=[input_r],
        y=[input_h],
        mode="markers",
        name=f"Current",
        marker=dict(size=10, color="red"),
        hovertemplate=f"<b>Current Point</b><br>Radius: {input_r:.2f} mm<br>Height: {input_h:.2f} mm<extra></extra>",
    )
)

# Add vertical dashed lines
x_ticks = np.arange(r_min, r_max + 1, 5)
for x_tick in x_ticks:
    fig2.add_vline(
        x=x_tick,
        line_dash="dash",
        line_color="rgba(150, 150, 150, 0.2)",
        line_width=1,
    )

# Add horizontal dashed lines
y_ticks = np.arange(10, 61, 10)
for y_tick in y_ticks:
    fig2.add_hline(
        y=y_tick,
        line_dash="dash",
        line_color="rgba(150, 150, 150, 0.2)",
        line_width=1,
    )

# Add current crosshairs
fig2.add_vline(
    x=input_r,
    line_dash="dash",
    line_color="rgba(200, 100, 100, 0.5)",
    line_width=2,
    annotation_text=f"R: {input_r:.1f}mm",
    annotation_position="top",
)

fig2.add_hline(
    y=input_h,
    line_dash="dash",
    line_color="rgba(100, 100, 200, 0.5)",
    line_width=2,
    annotation_text=f"H: {input_h:.1f}mm",
    annotation_position="right",
)

# Update layout
fig2.update_layout(
    xaxis_title="Radius (mm)",
    yaxis_title="Height (mm)",
    hovermode="closest",
    height=600,
    xaxis=dict(
        range=[r_min, r_max],
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(200, 200, 200, 0.2)",
    ),
    yaxis=dict(
        range=[10, 60],
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(200, 200, 200, 0.2)",
    ),
    template="plotly_white",
)

# --- Display in Streamlit ---
st.header("Constant Volume Curves")
st.plotly_chart(
    fig2,
    use_container_width=True,
    config={
        "displayModeBar": True,
        "modeBarButtonsToAdd": ["resetScale2d"],
        "toImageButtonOptions": {"format": "png"},
    },
)

# --- Display Pressure Changes Table ---
st.header("Pressure Changes")
st.markdown(
    f"""
**Physics Setup:**
- Ideal Gas Law: PV = nRT
- Starting Volume: {v_start_input_mm3:,.0f} mm³ at standard conditions (25°C, 1 atm = {P_ATMOS_PA:,.0f} Pa = {P_ATMOS_CMHG:.1f} cmHg))
- Amount of Air: {n_moles} mole(s)
- Temperature: {TEMP_K - 273.15:.1f}°C (constant)
- Cylinder adds volume while keeping molecular count constant

**Calculation:** At constant T and n: P₁V₁ = P₂V₂, so ΔP = P₂ - P₁
"""
)

if pressure_unit == "Pa":
    display_df = pressure_df[
        [
            "Volume Change (%)",
            "Volume Change (mm³)",
            "Total Volume (mm³)",
            "Pressure (Pa)",
            "ΔP (Pa)",
        ]
    ].copy()
    display_df.columns = [
        "Volume Change (%)",
        "Volume Change (mm³)",
        "Total Volume (mm³)",
        "Pressure (Pa)",
        "Pressure Change ΔP (Pa)",
    ]
    display_df["Pressure (Pa)"] = display_df["Pressure (Pa)"].round(1)
    display_df["Pressure Change ΔP (Pa)"] = display_df["Pressure Change ΔP (Pa)"].round(
        1
    )
else:  # cmHg
    display_df = pressure_df[
        [
            "Volume Change (%)",
            "Volume Change (mm³)",
            "Total Volume (mm³)",
            "Pressure (cmHg)",
            "ΔP (cmHg)",
        ]
    ].copy()
    display_df.columns = [
        "Volume Change (%)",
        "Volume Change (mm³)",
        "Total Volume (mm³)",
        "Pressure (cmHg)",
        "Pressure Change ΔP (cmHg)",
    ]
    display_df["Pressure (cmHg)"] = display_df["Pressure (cmHg)"].round(4)
    display_df["Pressure Change ΔP (cmHg)"] = display_df[
        "Pressure Change ΔP (cmHg)"
    ].round(6)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)
