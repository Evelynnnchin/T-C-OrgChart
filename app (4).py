import os
import io
import json
import math
import textwrap
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="Editable Org Chart", layout="wide")
st.title("🏢 Editable Organizational Chart")


# =========================================================
# FILE STORAGE
# =========================================================
DATA_FILE = "org_chart_saved_data.csv"
SETTINGS_FILE = "org_chart_settings.json"


DEFAULT_DATA = pd.DataFrame({
    "Name": [
        "Alice Tan",
        "Bob Lim",
        "Charlie Ng",
        "David Lee",
        "Eve Wong",
        "Frank Goh",
    ],
    "Role": [
        "CEO",
        "VP Engineering",
        "VP Sales",
        "Lead Developer",
        "Backend Developer",
        "Sales Executive",
    ],
    "Department": [
        "Management",
        "Engineering",
        "Sales",
        "Engineering",
        "Engineering",
        "Sales",
    ],
    "Supervisor": [
        "",
        "Alice Tan",
        "Alice Tan",
        "Bob Lim",
        "David Lee",
        "Charlie Ng",
    ],
    "Box Colour": [
        "#DDEBFF",
        "#E8F5E9",
        "#FFF3E0",
        "#E8F5E9",
        "#E8F5E9",
        "#FFF3E0",
    ],
})


DEFAULT_SETTINGS = {
    "box_width": 190,
    "box_height": 92,
    "font_size": 12,
    "horizontal_gap": 40,
    "vertical_gap": 95,
    "pdf_margin": 40,
}


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Make sure required columns exist."""
    required = ["Name", "Role", "Department", "Supervisor", "Box Colour"]
    for col in required:
        if col not in df.columns:
            if col == "Box Colour":
                df[col] = "#DDEBFF"
            else:
                df[col] = ""
    df = df[required].copy()
    df = df.fillna("")
    return df


def load_data() -> pd.DataFrame:
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, dtype=str).fillna("")
            return ensure_columns(df)
        except Exception:
            return DEFAULT_DATA.copy()
    return DEFAULT_DATA.copy()


def save_data(df: pd.DataFrame) -> None:
    df = ensure_columns(df)
    df.to_csv(DATA_FILE, index=False)


def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            settings = DEFAULT_SETTINGS.copy()
            settings.update(saved)
            return settings
        except Exception:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


if "org_data" not in st.session_state:
    st.session_state.org_data = load_data()

if "settings" not in st.session_state:
    st.session_state.settings = load_settings()


# =========================================================
# SIDEBAR SETTINGS
# =========================================================
with st.sidebar:
    st.header("Chart Settings")

    st.session_state.settings["box_width"] = st.slider(
        "Box width",
        min_value=120,
        max_value=360,
        value=int(st.session_state.settings["box_width"]),
        step=10,
    )

    st.session_state.settings["box_height"] = st.slider(
        "Box height",
        min_value=60,
        max_value=180,
        value=int(st.session_state.settings["box_height"]),
        step=5,
    )

    st.session_state.settings["font_size"] = st.slider(
        "Font size",
        min_value=8,
        max_value=24,
        value=int(st.session_state.settings["font_size"]),
        step=1,
    )

    st.session_state.settings["horizontal_gap"] = st.slider(
        "Horizontal gap",
        min_value=10,
        max_value=160,
        value=int(st.session_state.settings["horizontal_gap"]),
        step=5,
    )

    st.session_state.settings["vertical_gap"] = st.slider(
        "Vertical gap",
        min_value=50,
        max_value=220,
        value=int(st.session_state.settings["vertical_gap"]),
        step=5,
    )

    save_settings(st.session_state.settings)

    st.divider()

    st.caption("Tip: Use hex colours like #DDEBFF, #E8F5E9, #FFF3E0.")


# =========================================================
# DATA EDITOR
# =========================================================
st.markdown("### ✏️ Edit Data")
st.write(
    "Edit the table directly. Add rows at the bottom, or select rows and delete them. "
    "The data auto-saves after every edit."
)

edited_df = st.data_editor(
    ensure_columns(st.session_state.org_data),
    num_rows="dynamic",
    use_container_width=True,
    height=330,
    column_config={
        "Box Colour": st.column_config.TextColumn(
            "Box Colour",
            help="Use hex colour format, for example #DDEBFF",
        )
    },
    key="org_editor",
)

edited_df = ensure_columns(edited_df)
st.session_state.org_data = edited_df
save_data(edited_df)

sg_time = datetime.now(ZoneInfo("Asia/Singapore")).strftime("%d %b %Y, %I:%M %p")
st.caption(f"Auto-saved at {sg_time} Singapore time.")


# =========================================================
# ORG CHART HELPERS
# =========================================================
def clean_hex(value: str, fallback: str = "#DDEBFF") -> str:
    value = str(value).strip()
    if not value.startswith("#"):
        return fallback
    if len(value) not in [4, 7]:
        return fallback
    try:
        colors.HexColor(value)
        return value
    except Exception:
        return fallback


def get_roots(df: pd.DataFrame) -> list:
    names = set(df["Name"].astype(str).str.strip())
    roots = []

    for _, row in df.iterrows():
        name = str(row["Name"]).strip()
        sup = str(row["Supervisor"]).strip()
        if not name:
            continue
        if sup == "" or sup.lower() in ["none", "nan", "n/a", "-"] or sup not in names:
            roots.append(name)

    return roots


def build_children_map(df: pd.DataFrame) -> dict:
    names = set(df["Name"].astype(str).str.strip())
    children = {name: [] for name in names if name}

    for _, row in df.iterrows():
        name = str(row["Name"]).strip()
        sup = str(row["Supervisor"]).strip()
        if not name:
            continue
        if sup in names and sup != name:
            children.setdefault(sup, []).append(name)

    return children


def build_record_map(df: pd.DataFrame) -> dict:
    record_map = {}
    for _, row in df.iterrows():
        name = str(row["Name"]).strip()
        if not name:
            continue
        record_map[name] = {
            "name": name,
            "role": str(row.get("Role", "")).strip(),
            "department": str(row.get("Department", "")).strip(),
            "supervisor": str(row.get("Supervisor", "")).strip(),
            "colour": clean_hex(row.get("Box Colour", "#DDEBFF")),
        }
    return record_map


def detect_cycles(df: pd.DataFrame) -> list:
    """Simple cycle detection to prevent infinite org loops."""
    record_map = build_record_map(df)
    names = set(record_map.keys())
    supervisor = {
        name: record_map[name]["supervisor"]
        for name in names
        if record_map[name]["supervisor"] in names
    }

    cycles = []
    for name in names:
        seen = set()
        current = name
        while current in supervisor:
            if current in seen:
                cycles.append(name)
                break
            seen.add(current)
            current = supervisor[current]
    return sorted(set(cycles))


def to_echarts_tree(name: str, record_map: dict, children_map: dict) -> dict:
    rec = record_map.get(name, {})
    role = rec.get("role", "")
    dept = rec.get("department", "")
    colour = rec.get("colour", "#DDEBFF")

    label_text = name
    if role:
        label_text += f"\n{role}"
    if dept:
        label_text += f"\n{dept}"

    return {
        "name": label_text,
        "itemStyle": {
            "color": colour,
            "borderColor": "#555555",
            "borderWidth": 1,
        },
        "children": [
            to_echarts_tree(child, record_map, children_map)
            for child in children_map.get(name, [])
        ],
    }


def make_echarts_option(df: pd.DataFrame, settings: dict) -> dict:
    record_map = build_record_map(df)
    children_map = build_children_map(df)
    roots = get_roots(df)

    if len(roots) == 0:
        return {}

    if len(roots) == 1:
        data = [to_echarts_tree(roots[0], record_map, children_map)]
    else:
        data = [{
            "name": "Organization",
            "itemStyle": {
                "color": "#F5F5F5",
                "borderColor": "#555555",
                "borderWidth": 1,
            },
            "children": [
                to_echarts_tree(root, record_map, children_map)
                for root in roots
            ],
        }]

    font_size = int(settings["font_size"])

    return {
        "tooltip": {
            "trigger": "item",
            "triggerOn": "mousemove",
        },
        "series": [{
            "type": "tree",
            "data": data,
            "top": "4%",
            "left": "3%",
            "bottom": "4%",
            "right": "18%",
            "symbolSize": 14,
            "orient": "TB",
            "roam": True,
            "expandAndCollapse": True,
            "initialTreeDepth": -1,
            "label": {
                "position": "top",
                "verticalAlign": "middle",
                "align": "center",
                "fontSize": font_size,
                "lineHeight": font_size + 5,
                "width": int(settings["box_width"]),
                "overflow": "break",
            },
            "leaves": {
                "label": {
                    "position": "bottom",
                    "verticalAlign": "middle",
                    "align": "center",
                }
            },
            "emphasis": {
                "focus": "descendant"
            },
            "animationDuration": 350,
            "animationDurationUpdate": 500,
        }]
    }


# =========================================================
# PDF LAYOUT HELPERS
# =========================================================
def calculate_tree_positions(df: pd.DataFrame, settings: dict):
    """
    Calculates a full org chart layout for PDF export.
    It uses a simple tidy tree algorithm:
    - Leaves get consecutive x positions.
    - Parents are centred above their children.
    """
    record_map = build_record_map(df)
    children_map = build_children_map(df)
    roots = get_roots(df)

    if not roots:
        return {}, {}, [], 0, 0

    # If there are multiple roots, make a virtual root so all appear in one PDF.
    virtual_root = "__ORG_ROOT__"
    if len(roots) > 1:
        record_map[virtual_root] = {
            "name": "Organization",
            "role": "",
            "department": "",
            "supervisor": "",
            "colour": "#F5F5F5",
        }
        children_map[virtual_root] = roots
        root_nodes = [virtual_root]
    else:
        root_nodes = roots

    box_w = int(settings["box_width"])
    box_h = int(settings["box_height"])
    h_gap = int(settings["horizontal_gap"])
    v_gap = int(settings["vertical_gap"])

    positions = {}
    depths = {}
    next_leaf_x = [0]

    def assign(node, depth):
        depths[node] = depth
        kids = children_map.get(node, [])

        if not kids:
            x = next_leaf_x[0]
            next_leaf_x[0] += 1
        else:
            child_xs = []
            for child in kids:
                assign(child, depth + 1)
                child_xs.append(positions[child][0])
            x = (min(child_xs) + max(child_xs)) / 2

        y = depth
        positions[node] = (x, y)

    for root in root_nodes:
        assign(root, 0)

    max_depth = max(depths.values()) if depths else 0
    leaf_count = max(next_leaf_x[0], 1)

    # Convert layout units into PDF points.
    x_spacing = box_w + h_gap
    y_spacing = box_h + v_gap

    point_positions = {}
    for node, (x_unit, y_unit) in positions.items():
        point_positions[node] = (
            x_unit * x_spacing,
            y_unit * y_spacing,
        )

    chart_w = max((leaf_count - 1) * x_spacing + box_w, box_w)
    chart_h = (max_depth + 1) * box_h + max_depth * v_gap

    return point_positions, record_map, children_map, chart_w, chart_h


def draw_wrapped_centered_text(c, text, x, y, width, font_name, font_size, max_lines):
    """
    Draws wrapped text centred inside a box.
    x, y = top-left start area for text block.
    """
    if not text:
        return

    # Approximate wrap width by points.
    avg_char_width = max(font_size * 0.48, 1)
    wrap_chars = max(int(width / avg_char_width), 8)
    lines = []

    for part in str(text).split("\n"):
        wrapped = textwrap.wrap(part, width=wrap_chars) or [""]
        lines.extend(wrapped)

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        if len(lines[-1]) > 3:
            lines[-1] = lines[-1][:-3] + "..."

    line_height = font_size + 3
    total_h = len(lines) * line_height

    current_y = y - (0 if len(lines) == 1 else 0)
    start_y = current_y - (line_height / 2)

    for i, line in enumerate(lines):
        line_w = stringWidth(line, font_name, font_size)
        c.drawString(x + (width - line_w) / 2, start_y - i * line_height, line)


def create_pdf_bytes(df: pd.DataFrame, settings: dict) -> bytes:
    df = ensure_columns(df)
    cycles = detect_cycles(df)
    if cycles:
        raise ValueError(
            "Supervisor loop detected. Please fix these names before exporting: "
            + ", ".join(cycles)
        )

    positions, record_map, children_map, chart_w, chart_h = calculate_tree_positions(df, settings)

    if not positions:
        raise ValueError("No valid names found to export.")

    box_w = int(settings["box_width"])
    box_h = int(settings["box_height"])
    margin = int(settings["pdf_margin"])

    # Add space for title and timestamp.
    title_space = 55

    page_w = chart_w + margin * 2
    page_h = chart_h + margin * 2 + title_space

    # Limit extremely huge PDFs to a still usable size.
    # PDF points: 72 points = 1 inch.
    max_page_size = 14400  # 200 inches
    page_w = min(max(page_w, 800), max_page_size)
    page_h = min(max(page_h, 600), max_page_size)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(page_w, page_h))

    # Title
    c.setFont("Helvetica-Bold", 18)
    title = "Organization Chart"
    c.drawString(margin, page_h - margin, title)

    c.setFont("Helvetica", 9)
    sg_time = datetime.now(ZoneInfo("Asia/Singapore")).strftime("%d %b %Y, %I:%M %p SGT")
    c.drawString(margin, page_h - margin - 16, f"Exported: {sg_time}")

    # Start drawing from top.
    top_y = page_h - margin - title_space

    # Draw connectors first.
    c.setStrokeColor(colors.HexColor("#777777"))
    c.setLineWidth(1)

    for parent, kids in children_map.items():
        if parent not in positions:
            continue
        px, py = positions[parent]
        parent_center_x = margin + px + box_w / 2
        parent_bottom_y = top_y - py - box_h

        for child in kids:
            if child not in positions:
                continue
            cx, cy = positions[child]
            child_center_x = margin + cx + box_w / 2
            child_top_y = top_y - cy

            mid_y = (parent_bottom_y + child_top_y) / 2
            c.line(parent_center_x, parent_bottom_y, parent_center_x, mid_y)
            c.line(parent_center_x, mid_y, child_center_x, mid_y)
            c.line(child_center_x, mid_y, child_center_x, child_top_y)

    # Draw boxes.
    for node, (x, y) in positions.items():
        rec = record_map[node]
        left = margin + x
        top = top_y - y
        bottom = top - box_h

        fill_colour = colors.HexColor(clean_hex(rec.get("colour", "#DDEBFF")))
        c.setFillColor(fill_colour)
        c.setStrokeColor(colors.HexColor("#444444"))
        c.roundRect(left, bottom, box_w, box_h, radius=8, fill=1, stroke=1)

        # Name
        name_font = max(int(settings["font_size"]) + 1, 8)
        role_font = max(int(settings["font_size"]) - 1, 7)
        dept_font = max(int(settings["font_size"]) - 2, 7)

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", name_font)
        draw_wrapped_centered_text(
            c,
            rec.get("name", ""),
            left + 8,
            top - 18,
            box_w - 16,
            "Helvetica-Bold",
            name_font,
            max_lines=2,
        )

        # Role
        c.setFont("Helvetica", role_font)
        draw_wrapped_centered_text(
            c,
            rec.get("role", ""),
            left + 8,
            top - 45,
            box_w - 16,
            "Helvetica",
            role_font,
            max_lines=2,
        )

        # Department
        c.setFont("Helvetica-Oblique", dept_font)
        draw_wrapped_centered_text(
            c,
            rec.get("department", ""),
            left + 8,
            bottom + 20,
            box_w - 16,
            "Helvetica-Oblique",
            dept_font,
            max_lines=1,
        )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


# =========================================================
# VALIDATION
# =========================================================
df_for_chart = ensure_columns(st.session_state.org_data)
df_for_chart = df_for_chart[df_for_chart["Name"].astype(str).str.strip() != ""].copy()

cycles = detect_cycles(df_for_chart)
if cycles:
    st.error(
        "Supervisor loop detected. Please fix this before viewing/exporting: "
        + ", ".join(cycles)
    )

duplicate_names = df_for_chart["Name"][df_for_chart["Name"].duplicated()].tolist()
if duplicate_names:
    st.warning(
        "Duplicate names found. The org chart works best when every Name is unique: "
        + ", ".join(sorted(set(duplicate_names)))
    )


# =========================================================
# CHART VIEW
# =========================================================
st.markdown("### 📊 Org Chart Preview")
st.write("Drag to move around. Scroll to zoom. The PDF export below will include the full chart.")

option = make_echarts_option(df_for_chart, st.session_state.settings)

if option and not cycles:
    chart_height = max(650, min(1300, 220 + df_for_chart.shape[0] * 40))
    st_echarts(
        options=option,
        height=f"{chart_height}px",
        width="100%",
        key="org_chart",
    )
else:
    st.info("Add at least one person with a Name to generate the org chart.")


# =========================================================
# PDF DOWNLOAD
# =========================================================
st.markdown("### 📥 Download Full Scale PDF")

try:
    pdf_bytes = create_pdf_bytes(df_for_chart, st.session_state.settings)
    filename_time = datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y%m%d_%H%M")
    st.download_button(
        label="Download Full Org Chart as PDF",
        data=pdf_bytes,
        file_name=f"full_org_chart_{filename_time}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    st.success("PDF is ready. It exports the full org chart, not just the visible screen area.")
except Exception as e:
    st.error(f"PDF export is not ready yet: {e}")


# =========================================================
# OPTIONAL DATA DOWNLOAD
# =========================================================
st.markdown("### 💾 Backup Data")

csv_bytes = df_for_chart.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Data as CSV",
    data=csv_bytes,
    file_name="org_chart_data_backup.csv",
    mime="text/csv",
    use_container_width=True,
)
