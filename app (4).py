import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import re
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# =========================================================
# 1. Page Configuration
# =========================================================
st.set_page_config(page_title="Editable T&C Org Chart", layout="wide")
st.title("🏢 Editable T&C Organizational Chart")

DATA_FILE = "org_data_saved.csv"
SG_TIMEZONE = ZoneInfo("Asia/Singapore")

# Wider page + wider sidebar so color picker is not cut off
st.markdown(
    """
    <style>
    /* Make main page full width */
    .block-container {
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* Make sidebar wider so color picker is not cut off */
    section[data-testid="stSidebar"] {
        min-width: 420px !important;
        width: 420px !important;
        overflow: visible !important;
    }

    section[data-testid="stSidebar"] > div {
        min-width: 420px !important;
        width: 420px !important;
        overflow: visible !important;
    }

    /* Make color picker popover appear above everything */
    div[data-baseweb="popover"] {
        z-index: 999999 !important;
    }

    /* Allow main content / chart to scroll horizontally */
    div[data-testid="stVerticalBlock"] {
        overflow-x: auto !important;
    }

    div[data-testid="stElementContainer"] {
        overflow-x: auto !important;
    }

    iframe {
        min-width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 2. Helper Functions
# =========================================================
def parse_month_year(text, is_end=False):
    if pd.isna(text) or str(text).strip() == "":
        return pd.NaT

    dt = pd.to_datetime("01 " + str(text).strip(), format="%d %b %y", errors="coerce")

    if pd.notna(dt) and is_end:
        dt = dt + pd.offsets.MonthEnd(0)

    return dt


def parse_time_period(period):
    if pd.isna(period) or str(period).strip() == "":
        return pd.NaT, pd.NaT

    parts = str(period).split(" to ")

    if len(parts) != 2:
        return pd.NaT, pd.NaT

    start_date = parse_month_year(parts[0], is_end=False)
    end_date = parse_month_year(parts[1], is_end=True)

    return start_date, end_date


def format_period(start_date, end_date):
    start_date = pd.to_datetime(start_date, errors="coerce")
    end_date = pd.to_datetime(end_date, errors="coerce")

    if pd.notna(start_date) and pd.notna(end_date):
        return f"{start_date.strftime('%b %y')} to {end_date.strftime('%b %y')}"
    elif pd.notna(start_date):
        return f"From {start_date.strftime('%b %y')}"
    elif pd.notna(end_date):
        return f"Until {end_date.strftime('%b %y')}"
    else:
        return ""


def wrap_text(text, box_width, font_size=10):
    text = str(text).strip()

    if text == "":
        return ""

    max_chars = max(8, int((box_width - 20) / (font_size * 0.6)))

    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(word) > max_chars:
            if current_line:
                lines.append(current_line)
                current_line = ""

            for i in range(0, len(word), max_chars):
                lines.append(word[i:i + max_chars])

        else:
            test_line = f"{current_line} {word}".strip()

            if len(test_line) <= max_chars:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)


def safe_text(text):
    return str(text).replace("{", "(").replace("}", ")").replace("|", "/")


def save_data(df):
    save_df = df.copy()

    if "Delete?" in save_df.columns:
        save_df = save_df.drop(columns=["Delete?"])

    if "Start Date" in save_df.columns:
        save_df["Start Date"] = pd.to_datetime(
            save_df["Start Date"],
            errors="coerce"
        ).dt.strftime("%Y-%m-%d")

    if "End Date" in save_df.columns:
        save_df["End Date"] = pd.to_datetime(
            save_df["End Date"],
            errors="coerce"
        ).dt.strftime("%Y-%m-%d")

    save_df.to_csv(DATA_FILE, index=False)


def load_saved_data(default_df):
    if os.path.exists(DATA_FILE):
        try:
            saved_df = pd.read_csv(DATA_FILE)

            if "Delete?" in saved_df.columns:
                saved_df = saved_df.drop(columns=["Delete?"])

            if "Start Date" in saved_df.columns:
                saved_df["Start Date"] = pd.to_datetime(saved_df["Start Date"], errors="coerce")

            if "End Date" in saved_df.columns:
                saved_df["End Date"] = pd.to_datetime(saved_df["End Date"], errors="coerce")

            return saved_df

        except Exception as e:
            st.warning(f"Could not load saved data. Using default data instead. Error: {e}")
            return default_df.copy()

    return default_df.copy()


def get_last_saved_text():
    if os.path.exists(DATA_FILE):
        last_saved_time = datetime.fromtimestamp(os.path.getmtime(DATA_FILE), tz=SG_TIMEZONE)
        return last_saved_time.strftime("%d %b %Y, %I:%M %p SGT")

    return "Not saved yet"


# =========================================================
# 3. Default Data
# =========================================================
default_data = pd.DataFrame({
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
        '', '', 'OSIT Manager', 'T&C Engineer 2', 'ATS T&C Engineer 1', 'Mainline T&C Manager',
        'T&C Coordinator', 'T&C Coordinator', 'ATC T&C Engineer 2',
        'ATC T&C Engineer 1', 'ATC T&C Engineer 1', 'ATC T&C Engineer 1',
        'ATC/ATS T&C Engineer 3', 'ATC/ATS T&C Engineer 1', 'ATS T&C Engineer 3',
        'ATS T&C Engineer', 'ATS T&C Engineer 2', 'Sig T&C Engineer 2',
        'ATS T&C Engineer 3', 'Comms T&C Engineer 3', 'RCS/Network Engineer',
        'Sig T&C Engineer 1', 'Sig T&C Engineer 4', 'Subcon 4', 'Subcon 1', 'Subcon 1',
        'Subcon 3', 'Subcon 2', 'Subcon 2', 'Subcon 4', 'Subcon 2', 'Subcon 1',
        'Subcon 3', 'Subcon', 'Train Engineer 1', 'Train Engineer 2'
    ],
    'Reports To': [
        'None', 'Eric Tan', 'Eric Tan', 'Project Based', 'Project Based', 'Project Based',
        'Shared T&C Pool', 'Shared T&C Pool', 'Shared T&C Pool', 'Shared T&C Pool',
        'Shared T&C Pool', 'Shared T&C Pool', 'Shared T&C Pool',
        'Shared T&C Pool', 'Shared T&C Pool', 'CRL / OSIT', 'CRL / OSIT', 'CRL / OSIT',
        'CRL / OSIT', 'JRL Mainline', 'RTS', 'ATC',
        'ATC', 'ATC', 'ATC', 'ATC / ATS', 'ATC / ATS', 'ATC / ATS', 'ATS', 'ATS', 'ATS',
        'ATS', 'Comms / DCS / RCS / Network', 'Comms / DCS / RCS / Network',
        'Signalling', 'Signalling', 'Subcon', 'Subcon', 'Subcon', 'Subcon',
        'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon',
        'Train', 'Train'
    ],
    'Color Group': [
        'Management', 'Group', 'Group', 'CRL / OSIT', 'JRL Mainline', 'RTS', 'ATC',
        'ATC / ATS', 'ATS', 'ATC', 'Comms / DCS / RCS / Network', 'Group',
        'Signalling', 'Subcon', 'Train', 'CRL / OSIT', 'CRL / OSIT', 'CRL / OSIT',
        'CRL / OSIT', 'JRL Mainline', 'RTS', 'ATC',
        'ATC', 'ATC', 'ATC', 'ATC / ATS', 'ATC / ATS', 'ATC / ATS', 'ATS', 'ATS', 'ATS',
        'ATS', 'Comms / DCS / RCS / Network', 'Comms / DCS / RCS / Network',
        'Signalling', 'Signalling', 'Subcon', 'Subcon', 'Subcon', 'Subcon',
        'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon',
        'Train', 'Train'
    ],
    'Time Period': [
        'Feb 25 to Dec 29', '', '', '', '', '',
        '', '', '', '', '', '', '',
        '', '', 'Jul 25 to Dec 35', 'Jun 26 to Jul 26', 'Oct 26 to Jun 28', '',
        'May 25 to Dec 29', 'Jan 26 to Dec 26', 'Jan 26 to Oct 26',
        'Apr 26 to Nov 26', 'Jan 26 to Oct 26', 'Oct 27 to Dec 27',
        'Dec 25 to Sep 28', 'Jan 27 to Sep 28', 'Aug 25 to Sep 28',
        'Jul 26 to Sep 26', 'Apr 26 to Nov 26', 'Dec 25 to Sep 27',
        'Jul 26 to Jul 27', 'Aug 25 to Feb 27', 'Jun 26 to Jul 26',
        'Aug 25 to Jul 27', 'Apr 26 to Nov 26', 'Aug 26 to Nov 26',
        'Dec 25 to Sep 26', 'Oct 26 to Sep 28', 'Aug 26 to Nov 26',
        'Oct 26 to Sep 28', 'Aug 25 to Jul 27', 'Oct 26 to Dec 27',
        'Dec 25 to Sep 26', 'Aug 25 to Jul 27', 'Oct 26 to Dec 27',
        '', 'Jan 26 to Dec 28', 'Jan 26 to Dec 28'
    ]
})

parsed_dates = default_data['Time Period'].apply(parse_time_period)
default_data['Start Date'] = parsed_dates.apply(lambda x: x[0])
default_data['End Date'] = parsed_dates.apply(lambda x: x[1])
default_data = default_data.drop(columns=['Time Period'])


# =========================================================
# 4. Initialise Session State
# =========================================================
if 'org_data' not in st.session_state:
    st.session_state.org_data = load_saved_data(default_data)

if 'Time Period' in st.session_state.org_data.columns:
    parsed_dates = st.session_state.org_data['Time Period'].apply(parse_time_period)

    if 'Start Date' not in st.session_state.org_data.columns:
        st.session_state.org_data['Start Date'] = parsed_dates.apply(lambda x: x[0])

    if 'End Date' not in st.session_state.org_data.columns:
        st.session_state.org_data['End Date'] = parsed_dates.apply(lambda x: x[1])

    st.session_state.org_data = st.session_state.org_data.drop(columns=['Time Period'])

required_columns = {
    'Name / Team Name': '',
    'Type': 'Person',
    'Job Title': '',
    'Reports To': 'None',
    'Color Group': 'Group',
    'Start Date': pd.NaT,
    'End Date': pd.NaT
}

for col, default_value in required_columns.items():
    if col not in st.session_state.org_data.columns:
        st.session_state.org_data[col] = default_value

st.session_state.org_data = st.session_state.org_data[list(required_columns.keys())]


# =========================================================
# 5. Clean Data Function
# =========================================================
def clean_org_data(df):
    clean_df = df.copy()

    if "Delete?" in clean_df.columns:
        clean_df = clean_df.drop(columns=["Delete?"])

    clean_df['Name / Team Name'] = clean_df['Name / Team Name'].fillna('').astype(str).str.strip()
    clean_df = clean_df[clean_df['Name / Team Name'] != '']

    clean_df['Type'] = (
        clean_df['Type']
        .fillna('Person')
        .astype(str)
        .str.strip()
        .replace('', 'Person')
    )

    clean_df['Job Title'] = clean_df['Job Title'].fillna('').astype(str).str.strip()

    clean_df['Reports To'] = (
        clean_df['Reports To']
        .fillna('None')
        .astype(str)
        .str.strip()
        .replace('', 'None')
    )

    clean_df['Color Group'] = (
        clean_df['Color Group']
        .fillna('Group')
        .astype(str)
        .str.strip()
        .replace(['', 'None', 'nan', 'NaN'], 'Group')
    )

    clean_df['Start Date'] = pd.to_datetime(clean_df['Start Date'], errors='coerce')
    clean_df['End Date'] = pd.to_datetime(clean_df['End Date'], errors='coerce')

    clean_df['Time Period'] = clean_df.apply(
        lambda row: format_period(row['Start Date'], row['End Date']),
        axis=1
    )

    clean_df['Role Group'] = clean_df['Job Title'].apply(
        lambda x: re.sub(r'\s*\d+$', '', str(x)).strip()
    )

    return clean_df


# =========================================================
# 6. Default Colour Palette
# =========================================================
default_palette = {
    'Management': '#0081a7',
    'Group': '#00afb9',
    'Project Based': '#00afb9',
    'Shared T&C Pool': '#00afb9',
    'Shared Pool': '#00afb9',
    'CRL / OSIT': '#00afb9',
    'JRL Mainline': '#00afb9',
    'RTS': '#00afb9',
    'ATC': '#00afb9',
    'ATC / ATS': '#00afb9',
    'ATS': '#00afb9',
    'CBI': '#00afb9',
    'Comms / DCS / RCS / Network': '#00afb9',
    'CSF': '#00afb9',
    'Signalling': '#00afb9',
    'Subcon': '#ffb703',
    'Train': '#00afb9'
}


# =========================================================
# 7. Data Editor
# =========================================================
st.markdown("### ✏️ Edit Data Directly")
st.write(
    "Edit the table below. To delete rows, tick **Delete?** for the rows you want to remove, "
    "then click **Delete Selected Rows**. Click **Save Changes** to keep the changes for everyone using the app link."
)

temp_clean_df = clean_org_data(st.session_state.org_data)
all_possible_managers = sorted(set(temp_clean_df['Name / Team Name'].unique().tolist() + ['None']))

editor_df = st.session_state.org_data.copy()
editor_df.insert(0, "Delete?", False)

edited_df = st.data_editor(
    editor_df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    height=350,
    column_config={
        "Delete?": st.column_config.CheckboxColumn(
            "Delete?",
            help="Tick this row, then click Delete Selected Rows below.",
            default=False
        ),
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
            help="Select the person or team this row sits under.",
            options=all_possible_managers,
            required=True
        ),
        "Color Group": st.column_config.SelectboxColumn(
            "Color Group",
            help="Select which department colour to apply to the box.",
            options=list(default_palette.keys()),
            required=True
        ),
        "Start Date": st.column_config.DateColumn(
            "Start Date",
            help="Choose the start date from the calendar.",
            format="DD MMM YYYY"
        ),
        "End Date": st.column_config.DateColumn(
            "End Date",
            help="Choose the end date from the calendar.",
            format="DD MMM YYYY"
        )
    }
)

button_col1, button_col2, button_col3, info_col = st.columns([1.4, 1.2, 1.5, 4])

with button_col1:
    delete_clicked = st.button("🗑️ Delete Selected Rows", use_container_width=True)

with button_col2:
    save_clicked = st.button("💾 Save Changes", use_container_width=True)

with button_col3:
    load_clicked = st.button("🔄 Load Latest Saved Data", use_container_width=True)

if delete_clicked:
    delete_count = int(edited_df["Delete?"].fillna(False).sum())

    edited_df = edited_df[edited_df["Delete?"] != True].copy()
    edited_df = edited_df.drop(columns=["Delete?"], errors="ignore").reset_index(drop=True)

    st.session_state.org_data = edited_df
    st.success(f"Deleted {delete_count} row(s). Click Save Changes to keep this for everyone.")
    st.rerun()

else:
    st.session_state.org_data = edited_df.drop(columns=["Delete?"], errors="ignore").reset_index(drop=True)

if save_clicked:
    save_data(st.session_state.org_data)
    st.success("Saved! Everyone using this app link can load this latest version.")

if load_clicked:
    st.session_state.org_data = load_saved_data(default_data)
    st.rerun()

with info_col:
    st.caption(
        f"Last saved: {get_last_saved_text()} | "
        "Time shown in Singapore time. Saved file is shared by everyone using this app link."
    )

clean_df = clean_org_data(st.session_state.org_data)

st.markdown("***")


# =========================================================
# 8. Sidebar - View Options
# =========================================================
st.sidebar.header("🔍 View Options")

filter_type = st.sidebar.radio(
    "Select a view:",
    [
        "Show All (No Filters)",
        "Highlight by Name",
        "Highlight by Role Group",
        "Highlight by Color Group"
    ]
)

selected_person = "All"
selected_role_group = "All"
selected_dept = "All"

if filter_type == "Highlight by Name":
    selected_person = st.sidebar.selectbox(
        "Select Name:",
        sorted(clean_df['Name / Team Name'].dropna().astype(str).unique().tolist())
    )

elif filter_type == "Highlight by Role Group":
    valid_roles = sorted([
        r for r in clean_df['Role Group'].dropna().astype(str).unique().tolist()
        if r.strip() != ''
    ])

    if valid_roles:
        selected_role_group = st.sidebar.selectbox("Select Role Group:", valid_roles)
        role_count = len(clean_df[clean_df['Role Group'] == selected_role_group])
        st.sidebar.success(f"👥 Total {selected_role_group} count: **{role_count}**")
    else:
        st.sidebar.warning("No role groups available yet.")

elif filter_type == "Highlight by Color Group":
    selected_dept = st.sidebar.selectbox(
        "Select Color Group:",
        sorted(clean_df['Color Group'].dropna().astype(str).unique().tolist())
    )

filter_active = filter_type != "Show All (No Filters)"


# =========================================================
# 9. Sidebar - Custom Colours
# =========================================================
st.sidebar.header("🎨 Customise Team Colors")

color_map = {}

with st.sidebar.expander("Click to change colors"):
    for dept in sorted(clean_df['Color Group'].dropna().astype(str).unique()):
        default_c = default_palette.get(dept, '#ced4da')
        color_map[dept] = st.color_picker(f"{dept}", default_c)


# =========================================================
# 10. Sidebar - Layout and Font Settings
# =========================================================
st.sidebar.header("📐 Adjust Chart Layout")

with st.sidebar.expander("Layout Settings"):
    chart_width = st.slider("Horizontal Width", 1500, 12000, 5000, 100)
    chart_height = st.slider("Vertical Height", 700, 5000, 1800, 100)
    box_width = st.slider("Box Width", 100, 350, 170, 10)
    box_height = st.slider("Box Height", 50, 260, 90, 5)

    st.markdown("#### Font Size")
    name_font_size = st.slider("Name Font Size", 8, 24, 12, 1)
    role_font_size = st.slider("Role Font Size", 7, 20, 10, 1)
    time_font_size = st.slider("Time Period Font Size", 6, 18, 9, 1)


# =========================================================
# 11. Build and Render Chart
# =========================================================
if not clean_df.empty:
    default_color = '#ced4da'

    def build_styled_text(name, role, time_period, entry_type, is_faded):
        wrapped_name = wrap_text(safe_text(name), box_width, font_size=name_font_size)
        wrapped_role = wrap_text(safe_text(role), box_width, font_size=role_font_size)
        wrapped_time = wrap_text(safe_text(time_period), box_width, font_size=time_font_size)

        if is_faded:
            name_style = "name_faded"
            role_style = "role_faded"
            time_style = "time_faded"
        else:
            name_style = "name_active"
            role_style = "role_active"
            time_style = "time_active"

        display_text = "\n".join([
            f"{{{name_style}|{line}}}"
            for line in wrapped_name.split("\n")
            if line.strip() != ""
        ])

        if entry_type == 'Person' and str(role).strip() != "":
            display_text += "\n" + "\n".join([
                f"{{{role_style}|{line}}}"
                for line in wrapped_role.split("\n")
                if line.strip() != ""
            ])

        if str(time_period).strip() != "":
            display_text += "\n" + "\n".join([
                f"{{{time_style}|{line}}}"
                for line in wrapped_time.split("\n")
                if line.strip() != ""
            ])

        return display_text

    def build_tree(current_name, df, visited=None, real_supervisor=None):
        if visited is None:
            visited = set()

        if current_name in visited:
            return None

        visited.add(current_name)

        person_data = df[df['Name / Team Name'] == current_name]

        if person_data.empty:
            return None

        person = person_data.iloc[0]

        role = person.get('Job Title', '')
        role_group = person.get('Role Group', '')
        time_period = person.get('Time Period', '')
        dept = person.get('Color Group', 'Group')
        entry_type = person.get('Type', 'Person')

        actual_supervisor = person.get('Reports To', 'None')
        display_supervisor = real_supervisor if real_supervisor else actual_supervisor

        real_direct_reports = df[df['Reports To'] == current_name]['Name / Team Name'].tolist()
        reports_str = ", ".join(real_direct_reports) if real_direct_reports else "None"

        is_match = True

        if filter_active:
            if filter_type == "Highlight by Name" and current_name != selected_person:
                is_match = False
            elif filter_type == "Highlight by Role Group" and role_group != selected_role_group:
                is_match = False
            elif filter_type == "Highlight by Color Group" and dept != selected_dept:
                is_match = False

        node_color = color_map.get(dept, default_color)

        if filter_active and not is_match:
            item_style = {
                "color": "#f8f9fa",
                "borderColor": "#ced4da",
                "borderWidth": 1
            }
            display_text = build_styled_text(
                current_name,
                role,
                time_period,
                entry_type,
                is_faded=True
            )

        else:
            item_style = {
                "color": node_color,
                "borderColor": node_color,
                "borderWidth": 1
            }
            display_text = build_styled_text(
                current_name,
                role,
                time_period,
                entry_type,
                is_faded=False
            )

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
            "children": []
        }

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

    top_level_matches = clean_df[clean_df['Reports To'].str.lower() == 'none']

    if not top_level_matches.empty:
        root_name = top_level_matches.iloc[0]['Name / Team Name']
    else:
        root_name = clean_df.iloc[0]['Name / Team Name']

    tree_data = build_tree(root_name, clean_df)

    options = {
        "tooltip": {
            "trigger": "item",
            "triggerOn": "click",
            "formatter": "{c}",
            "backgroundColor": "rgba(255, 255, 255, 0.95)",
            "borderColor": "#ccc",
            "borderWidth": 1,
            "textStyle": {
                "color": "#333"
            }
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
                "left": "1%",
                "bottom": "5%",
                "right": "1%",
                "symbol": "rect",
                "symbolSize": [box_width, box_height],
                "edgeShape": "polyline",
                "roam": True,
                "initialTreeDepth": -1,
                "expandAndCollapse": True,
                "animationDuration": 550,
                "animationDurationUpdate": 750,
                "label": {
                    "position": "insideLeft",
                    "offset": [8, 0],
                    "rich": {
                        "name_active": {
                            "fontSize": name_font_size,
                            "fontWeight": "bold",
                            "color": "#ffffff",
                            "lineHeight": name_font_size + 4
                        },
                        "role_active": {
                            "fontSize": role_font_size,
                            "color": "#f8f9fa",
                            "lineHeight": role_font_size + 3
                        },
                        "time_active": {
                            "fontSize": time_font_size,
                            "color": "#e9ecef",
                            "lineHeight": time_font_size + 3
                        },
                        "name_faded": {
                            "fontSize": name_font_size,
                            "fontWeight": "bold",
                            "color": "#6c757d",
                            "lineHeight": name_font_size + 4
                        },
                        "role_faded": {
                            "fontSize": role_font_size,
                            "color": "#adb5bd",
                            "lineHeight": role_font_size + 3
                        },
                        "time_faded": {
                            "fontSize": time_font_size,
                            "color": "#ced4da",
                            "lineHeight": time_font_size + 3
                        }
                    }
                }
            }
        ]
    }

    st_echarts(
        options=options,
        height=f"{chart_height}px",
        width=f"{chart_width}px"
    )

else:
    st.warning("The table is empty. Please add at least one person or team box to generate the chart.")
