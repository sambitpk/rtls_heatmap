import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread

# Load CAD layout image
floorplan_path = "CN4_1F RFID_page-0001.jpg"
bg_img = imread(floorplan_path)
img_height, img_width = bg_img.shape[:2]

st.set_page_config(layout="wide")
st.title("📡 RFID Reader Radiation Pattern Designer")

# Default reader locations
default_readers = {
    "01": [510, 1910],
    "02": [510, 1202],
    "03": [525, 485],
    "04": [1650, 2125],
    "05": [1660, 1400],
    "06": [1340, 1110],
    "07": [1570, 390],
    "08": [2050, 1800],
    "09": [2340, 1152],
    "10": [2100, 450],
    "11": [2900, 1910],
    "12": [3000, 1202],
    "13": [3040, 600],
}

pixels_per_meter = 11871  # Assumed scale

# --- Sidebar: RFID Control Panel ---
st.sidebar.markdown("### 📍 RFID Reader Parameters")

reader_positions = {}
for rid, default_xy in default_readers.items():
    with st.sidebar.expander(f"Reader {rid}", expanded=False):
        x = st.slider(f"X-{rid}", 0, img_width, default_xy[0], step=1)
        y = st.slider(f"Y-{rid}", 0, img_height, default_xy[1], step=1)
        radius_m = st.slider(f"Radius-{rid} (m)", 30, 100, 75, step=5)
        reader_positions[rid] = {"pos": (x, y), "radius": radius_m}

# --- Heatmap Computation ---
X, Y = np.meshgrid(np.linspace(0, img_width, img_width),
                   np.linspace(0, img_height, img_height))
Z = np.zeros_like(X)

for reader in reader_positions.values():
    x0, y0 = reader["pos"]
    r_px = reader["radius"] * pixels_per_meter
    sigma = r_px / 2.5
    Z += np.exp(-((X - x0)**2 + (Y - y0)**2) / (2 * sigma**2))

Z = Z / np.max(Z)  # Normalize

# --- Main Plot ---
fig, ax = plt.subplots(figsize=(12, 10))
ax.imshow(bg_img, extent=[0, img_width, img_height, 0])
ax.imshow(Z, cmap='jet', alpha=0.45, extent=[0, img_width, img_height, 0])

for rid, reader in reader_positions.items():
    x, y = reader["pos"]
    ax.plot(x, y, 'go')
    ax.text(x + 5, y - 5, rid, color='lime', fontsize=9, weight='bold')

ax.set_title("Combined RFID Reader Coverage Map", fontsize=14)
ax.axis("off")
st.pyplot(fig)

# --- Optional Download ---
if st.button("📥 Download as PNG"):
    fig.savefig("custom_rfid_coverage.png", dpi=300)
    st.success("Saved as custom_rfid_coverage.png")

# --- Sidebar: Color Legend ---
import io
from matplotlib import cm

with st.sidebar:
    st.markdown("### 🎨 Heatmap Legend")
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    fig_legend, ax_legend = plt.subplots(figsize=(4, 0.4))
    ax_legend.imshow(gradient, aspect='auto', cmap='jet')
    ax_legend.set_axis_off()
    st.pyplot(fig_legend)
    st.caption("⬅️ Blue = Weak, Green = Good, Red = Strong")
