import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import re

# 1. Page Configuration
st.set_page_config(page_title="Editable T&C Org Chart", layout="wide")
st.title("🏢 Editable T&C Organizational Chart")

# 2. Default Data
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

# 3. Initialise Session State
if 'org_data' not in st.session_state:
    st.session_state.org_data = default_data.copy()

# Protect against old Streamlit sessions missing columns
required_columns = {
    'Name / Team Name': '',
    'Type': 'Person',
    'Job Title': '',
    'Reports To': 'None',
    'Color Group': 'Group',
    'Time Period': ''
}

for col, default_value in required_columns.items():
    if col not in st.session_state.org_data.columns:
        st.session_state.org_data[col] = default_value

st.session_state.org_data = st.session_state.org_data[list(required_columns.keys())]

# 4. Helper Function to Clean Data
def clean_org_data(df):
    clean_df = df.copy()

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

    # IMPORTANT FIX: prevents NoneType vs string sorting error
    clean_df['Color Group'] = (
        clean_df['Color Group']
        .fillna('Group')
        .astype(str)
        .str.strip()
        .replace(['', 'None', 'nan', 'NaN'], 'Group')
    )

    clean_df['Time Period'] = clean_df['Time Period'].fillna('').astype(str).str.strip()

    clean_df['Role Group'] = clean_df['Job Title'].apply(
        lambda x: re.sub(r'\s*\d+$', '', str(x)).strip()
    )

    return clean_df

# 5. Default Colour Palette
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

# 6. Data Editor
st.markdown("### ✏️ Edit Data Directly")
st.write(
    "Click any cell to edit. Scroll to the bottom row to add a new person. "
    "Use *Reports To* to decide where the person or team box sits."
)

temp_clean_df = clean_org_data(st.session_state.org_data)
all_possible_managers = sorted(temp_clean_df['Name / Team Name'].unique().tolist() + ['None'])

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
        "Time Period": st.column_config.TextColumn(
            "Time Period"
        )
    }
)

st.session_state.org_data = edited_df
clean_df = clean_org_data(st.session_state.org_data)

st.markdown("***")

# 7. Sidebar - View Options
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

# 8. Sidebar - Custom Colours
st.sidebar.header("🎨 Customise Team Colors")

color_map = {}

with st.sidebar.expander("Click to change colors"):
    for dept in sorted(clean_df['Color Group'].dropna().astype(str).unique()):
        default_c = default_palette.get(dept, '#ced4da')
        color_map[dept] = st.color_picker(f"{dept}", default_c)

# 9. Sidebar - Spacing
st.sidebar.header("📐 Adjust Chart Spacing")

with st.sidebar.expander("Layout Settings"):
    chart_width = st.slider("Horizontal Width", 1000, 5000, 1800, 100)
    chart_height = st.slider("Vertical Height", 500, 3000, 1000, 100)

# 10. Build and Render Chart
if not clean_df.empty:
    default_color = '#ced4da'

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

            display_text = f"{{name_faded|{current_name}}}"

            if entry_type == 'Person' and str(role).strip() != '':
                display_text += f"\n{{role_faded|{role}}}"

            if str(time_period).strip() != '':
                display_text += f"\n{{time_faded|{time_period}}}"

        else:
            item_style = {
                "color": node_color,
                "borderColor": node_color,
                "borderWidth": 1
            }

            display_text = f"{{name_active|{current_name}}}"

            if entry_type == 'Person' and str(role).strip() != '':
                display_text += f"\n{{role_active|{role}}}"

            if str(time_period).strip() != '':
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
            "children": []
        }

        # Check whether this is the bottom level
        is_bottom_level = True

        for report in real_direct_reports:
            if not df[df['Reports To'] == report].empty:
                is_bottom_level = False
                break

        # Vertical stacking logic for bottom-level nodes
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

    # Find top-level root
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
                "left": "2%",
                "bottom": "5%",
                "right": "2%",
                "symbol": "rect",
                "symbolSize": [150, 60],
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
                            "fontSize": 12,
                            "fontWeight": "bold",
                            "color": "#ffffff",
                            "lineHeight": 18
                        },
                        "role_active": {
                            "fontSize": 10,
                            "color": "#f8f9fa",
                            "lineHeight": 14
                        },
                        "time_active": {
                            "fontSize": 9,
                            "color": "#e9ecef",
                            "lineHeight": 12
                        },
                        "name_faded": {
                            "fontSize": 12,
                            "fontWeight": "bold",
                            "color": "#6c757d",
                            "lineHeight": 18
                        },
                        "role_faded": {
                            "fontSize": 10,
                            "color": "#adb5bd",
                            "lineHeight": 14
                        },
                        "time_faded": {
                            "fontSize": 9,
                            "color": "#ced4da",
                            "lineHeight": 12
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

# 11. Optional Reset Button
st.markdown("***")

if st.button("Reset to Default Data"):
    st.session_state.org_data = default_data.copy()
    st.rerun()
