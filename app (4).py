import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import re
import io
from datetime import datetime
from zoneinfo import ZoneInfo
import textwrap

# ReportLab is used only for the full-scale PDF download.
# The app will still run even if reportlab is missing.
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.pdfbase.pdfmetrics import stringWidth
    REPORTLAB_AVAILABLE = True
except ModuleNotFoundError:
    REPORTLAB_AVAILABLE = False


# =========================================================
# 1. Page Configuration
# =========================================================
st.set_page_config(page_title="Editable T&C Org Chart", layout="wide")
st.title("🏢 Editable T&C Organizational Chart")


# =========================================================
# 2. Pre-load Data
# Built-in protection against KeyErrors from old sessions
# =========================================================
if 'org_data' not in st.session_state or 'Name / Team Name' not in st.session_state.org_data.columns:
    st.session_state.org_data = pd.DataFrame({
        'Name / Team Name': [
            'Eric Tan', 'Project Based', 'Shared T&C Pool', 'CRL / OSIT', 'JRL Mainline', 'RTS',
            'ATC', 'ATC / ATS', 'ATS', 'CBI', 'Comms / DCS / RCS / Network', 'CSF', 'Signalling',
            'Subcon', 'Train', 'Augustine', 'Eric', 'Helmi', 'TBC', 'Diyana', 'Teerapat', 'Erwin',
            'Keri', 'Unal', 'YC (from DTL)', 'Aceline', 'YC', 'Zhonghan', 'Adib', 'Apurva', 'Jack',
            'Raymond', 'Damuel', 'Marek', 'Farid', 'Manish', 'Irfan', 'Khai', 'Mohan', 'Nazmi',
            'Sam', 'Sufian', 'Syafiq', 'Vincent', 'Zaki', 'Zul', 'Akmal', 'Irwan', 'Richter'
        ],
        'Type': [
            'Person', 'Team Box', 'Team Box', 'Team Box', 'Team Box', 'Team Box',
            'Team Box', 'Team Box', 'Team Box', 'Team Box', 'Team Box', 'Team Box', 'Team Box',
            'Team Box', 'Team Box', 'Person', 'Person', 'Person', 'Person', 'Person', 'Person', 'Person',
            'Person', 'Person', 'Person', 'Person', 'Person', 'Person', 'Person', 'Person', 'Person',
            'Person', 'Person', 'Person', 'Person', 'Person', 'Person', 'Person', 'Person', 'Person',
            'Person', 'Person', 'Person', 'Person', 'Person', 'Person', 'Person', 'Person', 'Person'
        ],
        'Job Title': [
            'T&C Manager', '', '', '', '', '',
            '', '', '', '', '', '', '',
            '', '', 'OSIT Manager', 'T&C Engineer 2', 'ATS T&C Engineer 1', 'Mainline T&C Manager', 'T&C Coordinator', 'T&C Coordinator', 'ATC T&C Engineer 2',
            'ATC T&C Engineer 1', 'ATC T&C Engineer 1', 'ATC T&C Engineer 1', 'ATC/ATS T&C Engineer 3', 'ATC/ATS T&C Engineer 1', 'ATS T&C Engineer 3', 'ATS T&C Engineer', 'ATS T&C Engineer 2', 'Sig T&C Engineer 2',
            'ATS T&C Engineer 3', 'Comms T&C Engineer 3', 'RCS/Network Engineer', 'Sig T&C Engineer 1', 'Sig T&C Engineer 4', 'Subcon 4', 'Subcon 1', 'Subcon 1', 'Subcon 3',
            'Subcon 2', 'Subcon 2', 'Subcon 4', 'Subcon 2', 'Subcon 1', 'Subcon 3', 'Subcon', 'Train Engineer 1', 'Train Engineer 2'
        ],
        'Reports To': [
            'None', 'Eric Tan', 'Eric Tan', 'Project Based', 'Project Based', 'Project Based',
            'Shared T&C Pool', 'Shared T&C Pool', 'Shared T&C Pool', 'Shared T&C Pool', 'Shared T&C Pool', 'Shared T&C Pool', 'Shared T&C Pool',
            'Shared T&C Pool', 'Shared T&C Pool', 'CRL / OSIT', 'CRL / OSIT', 'CRL / OSIT', 'CRL / OSIT', 'JRL Mainline', 'RTS', 'ATC',
            'ATC', 'ATC', 'ATC', 'ATC / ATS', 'ATC / ATS', 'ATC / ATS', 'ATS', 'ATS', 'ATS',
            'ATS', 'Comms / DCS / RCS / Network', 'Comms / DCS / RCS / Network', 'Signalling', 'Signalling', 'Subcon', 'Subcon', 'Subcon', 'Subcon',
            'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Train', 'Train'
        ],
        'Color Group': [
            'Management', 'Group', 'Group', 'CRL / OSIT', 'JRL Mainline', 'RTS', 'ATC',
            'ATC / ATS', 'ATS', 'ATC', 'Comms / DCS / RCS / Network', 'Group', 'Signalling', 'Subcon',
            'Train', 'CRL / OSIT', 'CRL / OSIT', 'CRL / OSIT', 'CRL / OSIT', 'JRL Mainline', 'RTS', 'ATC',
            'ATC', 'ATC', 'ATC', 'ATC / ATS', 'ATC / ATS', 'ATC / ATS', 'ATS', 'ATS', 'ATS',
            'ATS', 'Comms / DCS / RCS / Network', 'Comms / DCS / RCS / Network', 'Signalling', 'Signalling', 'Subcon', 'Subcon', 'Subcon', 'Subcon',
            'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Train', 'Train'
        ],
        'Time Period': [
            'Feb 25 to Dec 29', '', '', '', '', '',
            '', '', '', '', '', '', '',
            '', '', 'Jul 25 to Dec 35', 'Jun 26 to Jul 26', 'Oct 26 to Jun 28', '', 'May 25 to Dec 29', 'Jan 26 to Dec 26', 'Jan 26 to Oct 26',
            'Apr 26 to Nov 26', 'Jan 26 to Oct 26', 'Oct 27 to Dec 27', 'Dec 25 to Sep 28', 'Jan 27 to Sep 28', 'Aug 25 to Sep 28', 'Jul 26 to Sep 26', 'Apr 26 to Nov 26', 'Dec 25 to Sep 27',
            'Jul 26 to Jul 27', 'Aug 25 to Feb 27', 'Jun 26 to Jul 26', 'Aug 25 to Jul 27', 'Apr 26 to Nov 26', 'Aug 26 to Nov 26', 'Dec 25 to Sep 26', 'Oct 26 to Sep 28', 'Aug 26 to Nov 26',
            'Oct 26 to Sep 28', 'Aug 25 to Jul 27', 'Oct 26 to Dec 27', 'Dec 25 to Sep 26', 'Aug 25 to Jul 27', 'Oct 26 to Dec 27', '', 'Jan 26 to Dec 28', 'Jan 26 to Dec 28'
        ]
    })


# =========================================================
# Helper functions
# =========================================================
def prepare_clean_df(df):
    clean = df.dropna(subset=['Name / Team Name']).copy()
    clean['Name / Team Name'] = clean['Name / Team Name'].astype(str).str.strip()
    clean = clean[clean['Name / Team Name'] != ''].copy()

    for col in ['Type', 'Job Title', 'Reports To', 'Color Group', 'Time Period']:
        if col not in clean.columns:
            clean[col] = ''

    clean['Reports To'] = clean['Reports To'].fillna('None').astype(str).str.strip()
    clean['Job Title'] = clean['Job Title'].fillna('').astype(str)
    clean['Color Group'] = clean['Color Group'].fillna('').astype(str)
    clean['Type'] = clean['Type'].fillna('Person').astype(str)
    clean['Time Period'] = clean['Time Period'].fillna('').astype(str)

    clean['Role Group'] = clean['Job Title'].apply(lambda x: re.sub(r'\s*\d+$', '', str(x)).strip())
    return clean


def hex_to_reportlab_colour(hex_code, fallback="#ced4da"):
    if not REPORTLAB_AVAILABLE:
        return None

    value = str(hex_code).strip()
    if not value.startswith("#"):
        value = fallback

    try:
        return colors.HexColor(value)
    except Exception:
        return colors.HexColor(fallback)


def detect_loops(df):
    """
    Prevents infinite loops if someone is accidentally set under themselves
    or there is a circular reporting line.
    """
    names = set(df['Name / Team Name'].astype(str).str.strip())
    reports_to = {}

    for _, row in df.iterrows():
        name = str(row['Name / Team Name']).strip()
        manager = str(row['Reports To']).strip()
        if name and manager in names and manager != 'None':
            reports_to[name] = manager

    problem_names = []
    for name in names:
        seen = set()
        current = name

        while current in reports_to:
            if current in seen:
                problem_names.append(name)
                break
            seen.add(current)
            current = reports_to[current]

    return sorted(set(problem_names))


# =========================================================
# 3. Sidebar - View Options
# =========================================================
clean_df = prepare_clean_df(st.session_state.org_data)

st.sidebar.header("🔍 View Options")
filter_type = st.sidebar.radio(
    "Select a view:",
    ["Show All (No Filters)", "Highlight by Name", "Highlight by Role Group", "Highlight by Color Group"]
)

selected_person = "All"
selected_role_group = "All"
selected_dept = "All"

if filter_type == "Highlight by Name":
    selected_person = st.sidebar.selectbox(
        "Select Name:",
        sorted(clean_df['Name / Team Name'].unique().tolist())
    )
elif filter_type == "Highlight by Role Group":
    valid_roles = sorted([r for r in clean_df['Role Group'].unique().tolist() if r != ''])
    selected_role_group = st.sidebar.selectbox("Select Role Group:", valid_roles)
    role_count = len(clean_df[clean_df['Role Group'] == selected_role_group])
    st.sidebar.success(f"👥 Total {selected_role_group} count: **{role_count}**")
elif filter_type == "Highlight by Color Group":
    selected_dept = st.sidebar.selectbox(
        "Select Color Group:",
        sorted(clean_df['Color Group'].unique().tolist())
    )

filter_active = filter_type != "Show All (No Filters)"


# =========================================================
# 3b. Sidebar - Custom Colors
# =========================================================
st.sidebar.header("🎨 Customise Team Colors")

default_palette = {
    'Management': '#0081a7',
    'Group': '#00afb9',
    'Project Based': '#00afb9',
    'Shared Pool': '#00afb9',
    'CRL / OSIT': '#00afb9',
    'JRL Mainline': '#00afb9',
    'RTS': '#00afb9',
    'ATC': '#00afb9',
    'ATC / ATS': '#00afb9',
    'ATS': '#00afb9',
    'Comms / DCS / RCS / Network': '#00afb9',
    'Signalling': '#00afb9',
    'Subcon': '#ffb703',
    'Train': '#00afb9'
}

color_map = {}
with st.sidebar.expander("Click to change colors"):
    for dept in sorted(clean_df['Color Group'].unique()):
        default_c = default_palette.get(dept, '#ced4da')
        color_map[dept] = st.color_picker(f"{dept}", default_c)


# =========================================================
# 3c. Sidebar - Spacing
# =========================================================
st.sidebar.header("📐 Adjust Chart Spacing")
with st.sidebar.expander("Layout Settings"):
    chart_width = st.slider("Horizontal Width", 1000, 8000, 1800, 100)
    chart_height = st.slider("Vertical Height", 500, 5000, 1000, 100)


# =========================================================
# 3d. Sidebar - Font Size and Box Size
# =========================================================
st.sidebar.header("🔠 Font / Box Settings")
with st.sidebar.expander("Font and Box Settings", expanded=True):
    name_font_size = st.slider("Name Font Size", 8, 30, 12, 1)
    role_font_size = st.slider("Role / Job Title Font Size", 6, 24, 10, 1)
    time_font_size = st.slider("Time Period Font Size", 6, 22, 9, 1)

    node_width = st.slider("Box Width", 120, 360, 150, 10)
    node_height = st.slider("Box Height", 50, 180, 60, 10)

    horizontal_gap = st.slider("PDF Horizontal Gap", 30, 200, 55, 5)
    vertical_gap = st.slider("PDF Vertical Gap", 40, 220, 80, 5)


# =========================================================
# 4. Data Editor
# =========================================================
st.markdown("### ✏️ Edit Data Directly")
st.write("Click any cell to edit. *Reports To* and *Color Group* have dropdowns so you don't have to type out names.")

all_possible_managers = clean_df['Name / Team Name'].tolist() + ['None']

edited_df = st.data_editor(
    st.session_state.org_data,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    height=350,
    column_config={
        "Name / Team Name": st.column_config.TextColumn(
            "Name / Team Name",
            required=True
        ),
        "Type": st.column_config.SelectboxColumn(
            "Type",
            help="Is this a real person or a structural team box?",
            options=["Person", "Team Box"],
            required=True
        ),
        "Job Title": st.column_config.TextColumn(
            "Job Title"
        ),
        "Reports To": st.column_config.SelectboxColumn(
            "Reports To",
            help="Select the Person or Team this row sits under.",
            options=all_possible_managers,
            required=True
        ),
        "Color Group": st.column_config.SelectboxColumn(
            "Color Group",
            help="Select which department color to apply to the box.",
            options=list(default_palette.keys())
        ),
        "Time Period": st.column_config.TextColumn(
            "Time Period"
        )
    }
)

# Save edits back to session state
st.session_state.org_data = edited_df

# Re-clean after editing so the chart updates immediately.
clean_df = prepare_clean_df(st.session_state.org_data)

st.markdown("***")


# =========================================================
# 5. Build Tree Data
# =========================================================
def get_node_display_data(current_name, df):
    person_data = df[df['Name / Team Name'] == current_name]
    if person_data.empty:
        return None

    person = person_data.iloc[0]
    role = person.get('Job Title', '')
    role_group = person.get('Role Group', '')
    time_period = person.get('Time Period', '')
    dept = person.get('Color Group', 'N/A')
    entry_type = person.get('Type', 'Person')

    is_match = True
    if filter_active:
        if filter_type == "Highlight by Name" and current_name != selected_person:
            is_match = False
        elif filter_type == "Highlight by Role Group" and role_group != selected_role_group:
            is_match = False
        elif filter_type == "Highlight by Color Group" and dept != selected_dept:
            is_match = False

    return {
        "name": current_name,
        "role": str(role),
        "role_group": str(role_group),
        "time_period": str(time_period),
        "dept": str(dept),
        "entry_type": str(entry_type),
        "is_match": is_match
    }


def build_tree(current_name, df, visited=None, real_supervisor=None):
    if visited is None:
        visited = set()

    if current_name in visited:
        return None

    visited.add(current_name)

    node_data = get_node_display_data(current_name, df)
    if node_data is None:
        return None

    role = node_data["role"]
    role_group = node_data["role_group"]
    time_period = node_data["time_period"]
    dept = node_data["dept"]
    entry_type = node_data["entry_type"]
    is_match = node_data["is_match"]

    person = df[df['Name / Team Name'] == current_name].iloc[0]
    actual_supervisor = person.get('Reports To', 'None')
    display_supervisor = real_supervisor if real_supervisor else actual_supervisor

    real_direct_reports = df[df['Reports To'] == current_name]['Name / Team Name'].tolist()
    reports_str = ", ".join(real_direct_reports) if real_direct_reports else "None"

    node_color = color_map.get(dept, '#ced4da')

    # Rich text styling for the ECharts preview
    if filter_active and not is_match:
        item_style = {"color": "#f8f9fa", "borderColor": "#ced4da", "borderWidth": 1}
        display_text = f"{{name_faded|{current_name}}}"
        if entry_type == 'Person' and str(role).strip() != '':
            display_text += f"\n{{role_faded|{role}}}"
        if time_period and str(time_period).strip() != '':
            display_text += f"\n{{time_faded|{time_period}}}"
    else:
        item_style = {"color": node_color, "borderColor": node_color, "borderWidth": 1}
        display_text = f"{{name_active|{current_name}}}"
        if entry_type == 'Person' and str(role).strip() != '':
            display_text += f"\n{{role_active|{role}}}"
        if time_period and str(time_period).strip() != '':
            display_text += f"\n{{time_active|{time_period}}}"

    tooltip_value = (
        f"<b>Name / Team:</b> {current_name}<br/>"
        f"<b>Role:</b> {role if str(role).strip() != '' else 'N/A'}<br/>"
        f"<b>Color Group:</b> {dept}<br/>"
        f"<b>Time Period:</b> {time_period if str(time_period).strip() != '' else 'N/A'}<br/>"
        f"<b>Reports To:</b> {display_supervisor}<br/>"
        f"<b>Direct Reports ({len(real_direct_reports)}):</b> {reports_str}"
    )

    node = {
        "name": display_text,
        "value": tooltip_value,
        "itemStyle": item_style,
        "raw": node_data,
        "children": []
    }

    # VERTICAL STACKING LOGIC
    is_bottom_level = True
    for report in real_direct_reports:
        if not df[df['Reports To'] == report].empty:
            is_bottom_level = False
            break

    if is_bottom_level and len(real_direct_reports) > 0:
        current_chain_link = node
        for report in real_direct_reports:
            child_node = build_tree(report, df, visited, real_supervisor=current_name)
            if child_node:
                current_chain_link["children"].append(child_node)
                current_chain_link = child_node
    else:
        for report in real_direct_reports:
            child_node = build_tree(report, df, visited)
            if child_node:
                node["children"].append(child_node)

    return node


def get_root_name(df):
    top_level_matches = df[df['Reports To'].str.lower() == 'none']
    if not top_level_matches.empty:
        return top_level_matches.iloc[0]['Name / Team Name']
    return df.iloc[0]['Name / Team Name']


# =========================================================
# 6. Full PDF Export
# =========================================================
def assign_tree_positions(root):
    """
    Assigns positions to every node in the tree.
    Leaves are placed left-to-right.
    Parents are centred above their children.
    """
    positions = {}
    nodes = {}
    edges = []
    next_leaf_x = [0]
    max_depth = [0]

    def walk(node, depth, path):
        node_id = path
        nodes[node_id] = node
        max_depth[0] = max(max_depth[0], depth)

        children = node.get("children", [])

        if children:
            child_x_values = []
            for idx, child in enumerate(children):
                child_id = f"{path}.{idx}"
                edges.append((node_id, child_id))
                walk(child, depth + 1, child_id)
                child_x_values.append(positions[child_id][0])

            x = (min(child_x_values) + max(child_x_values)) / 2
        else:
            x = next_leaf_x[0]
            next_leaf_x[0] += 1

        positions[node_id] = (x, depth)

    walk(root, 0, "0")
    leaf_count = max(next_leaf_x[0], 1)

    return positions, nodes, edges, leaf_count, max_depth[0]


def draw_centered_wrapped_text(c, text, x, top_y, width, font_name, font_size, max_lines):
    if not text or str(text).strip() == "":
        return

    safe_text = str(text).replace("&amp;", "&")
    approx_char_width = max(font_size * 0.52, 1)
    wrap_chars = max(int(width / approx_char_width), 8)

    lines = []
    for part in safe_text.split("\n"):
        wrapped = textwrap.wrap(part, width=wrap_chars) or [""]
        lines.extend(wrapped)

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        if len(lines[-1]) > 3:
            lines[-1] = lines[-1][:-3] + "..."

    line_height = font_size + 3

    for idx, line in enumerate(lines):
        line_width = stringWidth(line, font_name, font_size)
        c.drawString(x + (width - line_width) / 2, top_y - (idx * line_height), line)


def make_full_org_chart_pdf(tree_data, chart_title="T&C Organizational Chart"):
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("reportlab is not installed. Add reportlab to requirements.txt.")

    positions, nodes, edges, leaf_count, max_depth = assign_tree_positions(tree_data)

    # Use sidebar-controlled box size and gaps
    box_w = node_width
    box_h = node_height
    x_gap = horizontal_gap
    y_gap = vertical_gap

    margin_x = 45
    margin_y = 45
    title_space = 55

    chart_w = (leaf_count - 1) * (box_w + x_gap) + box_w
    chart_h = (max_depth + 1) * box_h + max_depth * y_gap

    page_w = max(chart_w + margin_x * 2, 900)
    page_h = max(chart_h + margin_y * 2 + title_space, 650)

    # ReportLab has practical limits on massive pages.
    max_page_size = 14400
    page_w = min(page_w, max_page_size)
    page_h = min(page_h, max_page_size)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(page_w, page_h))

    # Title
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin_x, page_h - margin_y, chart_title)

    c.setFont("Helvetica", 9)
    exported_time = datetime.now(ZoneInfo("Asia/Singapore")).strftime("%d %b %Y, %I:%M %p SGT")
    c.drawString(margin_x, page_h - margin_y - 16, f"Exported: {exported_time}")

    chart_top_y = page_h - margin_y - title_space

    def node_box_xy(node_id):
        x_unit, depth = positions[node_id]
        left = margin_x + x_unit * (box_w + x_gap)
        top = chart_top_y - depth * (box_h + y_gap)
        bottom = top - box_h
        return left, top, bottom

    # Connectors first
    c.setStrokeColor(colors.HexColor("#6c757d"))
    c.setLineWidth(1)

    for parent_id, child_id in edges:
        p_left, p_top, p_bottom = node_box_xy(parent_id)
        c_left, c_top, c_bottom = node_box_xy(child_id)

        parent_x = p_left + box_w / 2
        child_x = c_left + box_w / 2
        parent_y = p_bottom
        child_y = c_top

        mid_y = (parent_y + child_y) / 2
        c.line(parent_x, parent_y, parent_x, mid_y)
        c.line(parent_x, mid_y, child_x, mid_y)
        c.line(child_x, mid_y, child_x, child_y)

    # PDF font sizes based on sidebar controls
    pdf_name_size = max(name_font_size * 0.8, 6)
    pdf_role_size = max(role_font_size * 0.8, 5)
    pdf_time_size = max(time_font_size * 0.8, 5)

    # Dynamic vertical positions inside the box
    name_y_offset = max(12, pdf_name_size + 5)
    role_y_offset = name_y_offset + max(16, pdf_role_size + 8)
    time_y_offset_from_bottom = max(10, pdf_time_size + 4)

    # Boxes
    for node_id, node in nodes.items():
        raw = node.get("raw", {})
        name = raw.get("name", "")
        role = raw.get("role", "")
        time_period = raw.get("time_period", "")
        entry_type = raw.get("entry_type", "Person")
        dept = raw.get("dept", "")
        is_match = raw.get("is_match", True)

        node_color = color_map.get(dept, '#ced4da')

        left, top, bottom = node_box_xy(node_id)

        if filter_active and not is_match:
            fill = colors.HexColor("#f8f9fa")
            stroke = colors.HexColor("#ced4da")
            name_colour = colors.HexColor("#6c757d")
            role_colour = colors.HexColor("#adb5bd")
            time_colour = colors.HexColor("#adb5bd")
        else:
            fill = hex_to_reportlab_colour(node_color, '#ced4da')
            stroke = fill
            name_colour = colors.white
            role_colour = colors.HexColor("#f8f9fa")
            time_colour = colors.HexColor("#e9ecef")

        c.setFillColor(fill)
        c.setStrokeColor(stroke)
        c.roundRect(left, bottom, box_w, box_h, radius=6, fill=1, stroke=1)

        # Name
        c.setFont("Helvetica-Bold", pdf_name_size)
        c.setFillColor(name_colour)
        draw_centered_wrapped_text(
            c,
            name,
            left + 8,
            top - name_y_offset,
            box_w - 16,
            "Helvetica-Bold",
            pdf_name_size,
            max_lines=2
        )

        # Role
        if entry_type == "Person" and str(role).strip() != "":
            c.setFont("Helvetica", pdf_role_size)
            c.setFillColor(role_colour)
            draw_centered_wrapped_text(
                c,
                role,
                left + 8,
                top - role_y_offset,
                box_w - 16,
                "Helvetica",
                pdf_role_size,
                max_lines=1
            )

        # Time period
        if str(time_period).strip() != "":
            c.setFont("Helvetica", pdf_time_size)
            c.setFillColor(time_colour)
            draw_centered_wrapped_text(
                c,
                time_period,
                left + 8,
                bottom + time_y_offset_from_bottom,
                box_w - 16,
                "Helvetica",
                pdf_time_size,
                max_lines=1
            )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


# =========================================================
# 7. Build and Render the Chart
# =========================================================
if not clean_df.empty:
    duplicate_names = clean_df[clean_df['Name / Team Name'].duplicated()]['Name / Team Name'].unique().tolist()
    if duplicate_names:
        st.warning(
            "Duplicate names found. The org chart works best when each Name / Team Name is unique: "
            + ", ".join(duplicate_names)
        )

    loops = detect_loops(clean_df)
    if loops:
        st.error(
            "There is a circular reporting line. Please fix these rows before exporting/viewing: "
            + ", ".join(loops)
        )
    else:
        root_name = get_root_name(clean_df)
        tree_data = build_tree(root_name, clean_df)

        options = {
            "tooltip": {
                "trigger": "item",
                "triggerOn": "click",
                "formatter": "{c}",
                "backgroundColor": "rgba(255, 255, 255, 0.95)",
                "borderColor": "#ccc",
                "borderWidth": 1,
                "textStyle": {"color": "#333"}
            },
            "toolbox": {
                "show": True,
                "right": "30px",
                "top": "15px",
                "feature": {
                    "saveAsImage": {
                        "name": "TC_Org_Chart",
                        "title": "Download as PNG",
                        "pixelRatio": 3
                    }
                }
            },
            "series": [
                {
                    "type": "tree",
                    "data": [tree_data],
                    "orient": "TB",
                    "top": "5%",
                    "left": "2%",
                    "bottom": "5%",
                    "right": "2%",
                    "symbol": "rect",
                    "symbolSize": [node_width, node_height],
                    "edgeShape": "polyline",
                    "roam": True,
                    "initialTreeDepth": -1,
                    "expandAndCollapse": True,
                    "animationDuration": 550,
                    "animationDurationUpdate": 750,
                    "label": {
                        "position": "insideLeft",
                        "offset": [10, 0],
                        "rich": {
                            "name_active": {
                                "fontSize": name_font_size,
                                "fontWeight": "bold",
                                "color": "#ffffff",
                                "lineHeight": name_font_size + 6
                            },
                            "role_active": {
                                "fontSize": role_font_size,
                                "color": "#f8f9fa",
                                "lineHeight": role_font_size + 5
                            },
                            "time_active": {
                                "fontSize": time_font_size,
                                "color": "#e9ecef",
                                "lineHeight": time_font_size + 4
                            },
                            "name_faded": {
                                "fontSize": name_font_size,
                                "fontWeight": "bold",
                                "color": "#6c757d",
                                "lineHeight": name_font_size + 6
                            },
                            "role_faded": {
                                "fontSize": role_font_size,
                                "color": "#adb5bd",
                                "lineHeight": role_font_size + 5
                            },
                            "time_faded": {
                                "fontSize": time_font_size,
                                "color": "#ced4da",
                                "lineHeight": time_font_size + 4
                            }
                        }
                    }
                }
            ]
        }

        st_echarts(options=options, height=f"{chart_height}px", width=f"{chart_width}px")

        st.markdown("### 📥 Download Full-Scale Chart")

        if REPORTLAB_AVAILABLE:
            try:
                pdf_bytes = make_full_org_chart_pdf(tree_data)
                file_stamp = datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y%m%d_%H%M")
                st.download_button(
                    label="Download Whole Org Chart as PDF",
                    data=pdf_bytes,
                    file_name=f"TC_Org_Chart_Full_{file_stamp}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.caption("This PDF is generated from the full org chart data, so it is not limited to the visible/scrollable screen area.")
            except Exception as e:
                st.error(f"Unable to generate PDF: {e}")
        else:
            st.error(
                "PDF download needs the reportlab package. Add `reportlab` to your requirements.txt, then reboot the Streamlit app."
            )

else:
    st.warning("The table is empty. Please add at least one person to generate the chart.")
