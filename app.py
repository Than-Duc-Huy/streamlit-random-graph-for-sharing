import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- Page Config ---
st.set_page_config(page_title="Cylinder Volume Explorer", layout="wide")

st.title("Cylinder Radius vs. Height Relationship")
st.markdown(
    """
This tool visualizes how the **Radius** and **Height** of a cylinder must change to maintain a constant volume.
The lines represent volume increments from **-50% to +50%** of your target cylinder.
"""
)

# --- Sidebar Inputs ---
st.sidebar.header("Input Parameters")
input_h = st.sidebar.number_input("Target Height (mm)", value=23.0, step=1.0)
input_d = st.sidebar.number_input("Target Diameter (mm)", value=36.0, step=1.0)

# Derived calculations
input_r = input_d / 2
initial_volume = np.pi * (input_r**2) * input_h

# Display calculated volume in sidebar
st.sidebar.metric("Calculated Volume", f"{initial_volume:,.2f} mm³")


# --- Logic & Data ---
def calculate_height(radius, volume):
    return volume / (np.pi * radius**2)


# Plotting range for Radius
r_min, r_max = 5.0, 25.0
r_values = np.linspace(r_min, r_max, 500)
# 50% to 150% in 10% increments
percentages = np.arange(0.5, 1.6, 0.1)

# --- Plotting ---
fig = go.Figure()

for p in percentages:
    vol_at_p = initial_volume * p
    h_values = calculate_height(r_values, vol_at_p)

    # Styling: Highlight the 100% (target) line
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

# Target point marker
fig.add_trace(
    go.Scatter(
        x=[input_r],
        y=[input_h],
        mode="markers",
        name=f"Target ({input_r}r, {input_h}h)",
        marker=dict(size=10, color="red"),
        hovertemplate=f"<b>Target Point</b><br>Radius: {input_r:.2f} mm<br>Height: {input_h:.2f} mm<extra></extra>",
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

# Add horizontal dashed lines at every y-axis tick (every 20 mm)
y_ticks = np.arange(0, 151, 20)
for y_tick in y_ticks:
    fig.add_hline(
        y=y_tick,
        line_dash="dash",
        line_color="rgba(150, 150, 150, 0.2)",
        line_width=1,
    )

# Add target crosshairs (more visible)
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
    title=f"Constant Volume Curves (Base: {initial_volume:.0f} mm³)",
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
        range=[0, 150],
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(200, 200, 200, 0.2)",
    ),
    template="plotly_white",
)

# --- Display in Streamlit ---
st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": True,
        "modeBarButtonsToAdd": ["resetScale2d"],
        "toImageButtonOptions": {"format": "png"},
    },
)
