import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

# 1. Page Configuration
st.set_page_config(page_title="Editable T&C Org Chart", layout="wide")
st.title("🏢 Editable T&C Organizational Chart")

# 2. Pre-load your specific T&C Diagram Data
if 'org_data' not in st.session_state:
    st.session_state.org_data = pd.DataFrame({
        'Name': [
            'Eric Tan', 'Project-based', 'Shared T&C Pool', 'CRL / OSIT', 'JRL Mainline', 'RTS', 
            'ATC', 'ATC / ATS', 'ATS', 'CBI', 'Comms / DCS / RCS / Network', 'CSF', 'Signalling', 
            'Subcon', 'Train', 'Augustine', 'Eric', 'Helmi', 'TBC', 'Diyana', 'Teerapat', 'Erwin', 
            'Keri', 'Unal', 'YC (from DTL)', 'Aceline', 'YC', 'Zhonghan', 'Adib', 'Apurva', 'Jack', 
            'Raymond', 'Damuel', 'Marek', 'Farid', 'Manish', 'Irfan', 'Khai', 'Mohan', 'Nazmi', 
            'Sam', 'Sufian', 'Syafiq', 'Vincent', 'Zaki', 'Zul', 'Akmal', 'Irwan', 'Richter'
        ],
        'Role': [
            'T&C Manager', 'Group', 'Group', 'Sub-Group', 'Sub-Group', 'Sub-Group', 
            'Sub-Group', 'Sub-Group', 'Sub-Group', 'Sub-Group', 'Sub-Group', 'Sub-Group', 'Sub-Group', 
            'Sub-Group', 'Sub-Group', 'OSIT Manager', 'T&C Engineer 2', 'ATS T&C Engineer 1', 'Mainline T&C Manager', 'T&C Coordinator', 'T&C Coordinator', 'ATC T&C Engineer 2', 
            'ATC T&C Engineer 1', 'ATC T&C Engineer 1', 'ATC T&C Engineer 1', 'ATC/ATS T&C Engineer 3', 'ATC/ATS T&C Engineer 1', 'ATS T&C Engineer 3', 'ATS T&C Engineer', 'ATS T&C Engineer 2', 'Sig T&C Engineer 2', 
            'ATS T&C Engineer 3', 'Comms T&C Engineer 3', 'RCS/Network Engineer', 'Sig T&C Engineer 1', 'Sig T&C Engineer 4', 'Subcon 4', 'Subcon 1', 'Subcon 1', 'Subcon 3', 
            'Subcon 2', 'Subcon 2', 'Subcon 4', 'Subcon 2', 'Subcon 1', 'Subcon 3', 'Subcon', 'Train Engineer 1', 'Train Engineer 2'
        ],
        'Time Period': [
            'Feb-25 to Dec-29', '', '', '', '', '', 
            '', '', '', '', '', '', '', 
            '', '', 'Jul-25 to Dec-35', 'Jun-26 to Jul-26', 'Oct-26 to Jun-28', '', 'May-25 to Dec-29', 'Jan-26 to Dec-26', 'Jan-26 to Oct-26', 
            'Apr-26 to Nov-26', 'Jan-26 to Oct-26', 'Oct-27 to Dec-27', 'Dec-25 to Sep-28', 'Jan-27 to Sep-28', 'Aug-25 to Sep-28', 'Jul-26 to Sep-26', 'Apr-26 to Nov-26', 'Dec-25 to Sep-27', 
            'Jul-26 to Jul-27', 'Aug-25 to Feb-27', 'Jun-26 to Jul-26', 'Aug-25 to Jul-27', 'Apr-26 to Nov-26', 'Aug-26 to Nov-26', 'Dec-25 to Sep-26', 'Oct-26 to Sep-28', 'Aug-26 to Nov-26', 
            'Oct-26 to Sep-28', 'Aug-25 to Jul-27', 'Oct-26 to Dec-27', 'Dec-25 to Sep-26', 'Aug-25 to Jul-27', 'Oct-26 to Dec-27', '', 'Jan-26 to Dec-28', 'Jan-26 to Dec-28'
        ],
        'Department': [
            'Management', 'Group', 'Group', 'Project-based', 'Project-based', 'Project-based', 
            'Shared Pool', 'Shared Pool', 'Shared Pool', 'Shared Pool', 'Shared Pool', 'Shared Pool', 'Shared Pool', 
            'Shared Pool', 'Shared Pool', 'CRL / OSIT', 'CRL / OSIT', 'CRL / OSIT', 'CRL / OSIT', 'JRL Mainline', 'RTS', 'ATC', 
            'ATC', 'ATC', 'ATC', 'ATC / ATS', 'ATC / ATS', 'ATC / ATS', 'ATS', 'ATS', 'ATS', 
            'ATS', 'Comms / DCS / RCS / Network', 'Comms / DCS / RCS / Network', 'Signalling', 'Signalling', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 
            'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Train', 'Train'
        ],
        'Supervisor': [
            'None', 'Eric Tan', 'Eric Tan', 'Project-based', 'Project-based', 'Project-based', 
            'Shared T&C Pool', 'Shared T&C Pool', 'Shared T&C Pool', 'Shared T&C Pool', 'Shared T&C Pool', 'Shared T&C Pool', 'Shared T&C Pool', 
            'Shared T&C Pool', 'Shared T&C Pool', 'CRL / OSIT', 'CRL / OSIT', 'CRL / OSIT', 'CRL / OSIT', 'JRL Mainline', 'RTS', 'ATC', 
            'ATC', 'ATC', 'ATC', 'ATC / ATS', 'ATC / ATS', 'ATC / ATS', 'ATS', 'ATS', 'ATS', 
            'ATS', 'Comms / DCS / RCS / Network', 'Comms / DCS / RCS / Network', 'Signalling', 'Signalling', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 
            'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Subcon', 'Train', 'Train'
        ]
    })

# 3. Sidebar for Search and Filters
st.sidebar.header("🔍 Search & Filter")
all_names = sorted(st.session_state.org_data['Name'].dropna().unique().tolist())
all_roles = sorted(st.session_state.org_data['Role'].dropna().unique().tolist())
all_depts = sorted(st.session_state.org_data['Department'].dropna().unique().tolist())

search_mode = st.sidebar.radio("Search by:", ["Name", "Role"])
if search_mode == "Name":
    selected_person = st.sidebar.selectbox("Select Employee:", ["All"] + all_names)
    selected_role = "All"
else:
    selected_role = st.sidebar.selectbox("Select Role:", ["All"] + all_roles)
    selected_person = "All"

selected_dept = st.sidebar.selectbox("Filter by Department:", ["All"] + all_depts)

# 4. Direct Editor Table
st.markdown("### ✏️ Edit Data Directly")
edited_df = st.data_editor(
    st.session_state.org_data,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    height=250
)

# Clean the edited data
clean_df = edited_df.dropna(subset=['Name']).copy()
clean_df['Name'] = clean_df['Name'].astype(str).str.strip()
clean_df['Supervisor'] = clean_df['Supervisor'].fillna('None').astype(str).str.strip()

st.markdown("***")

# 5. Build and Render Chart
if not clean_df.empty:
    
    # Custom Color Coding matching your T&C setup
    color_map = {
        'Management': '#d9534f',
        'Group': '#34495e',
        'Project-based': '#9b59b6',
        'Shared Pool': '#f39c12',
        'CRL / OSIT': '#2980b9',
        'JRL Mainline': '#27ae60',
        'RTS': '#16a085',
        'ATC': '#8e44ad',
        'ATC / ATS': '#c0392b',
        'ATS': '#e67e22',
        'Comms / DCS / RCS / Network': '#f1c40f',
        'Signalling': '#d35400',
        'Subcon': '#7f8c8d',
        'Train': '#2c3e50'
    }
    default_color = '#bdc3c7'

    def build_tree(current_name, df, visited=None):
        if visited is None:
            visited = set()
        
        if current_name in visited:
            return None
        visited.add(current_name)

        person_data = df[df['Name'] == current_name]
        if person_data.empty:
            return None
        
        person = person_data.iloc[0]
        role = person.get('Role', 'N/A')
        time_period = person.get('Time Period', '')
        dept = person.get('Department', 'N/A')
        supervisor = person.get('Supervisor', 'None')
        
        direct_reports = df[df['Supervisor'] == current_name]['Name'].tolist()
        reports_str = ", ".join(direct_reports) if direct_reports else "None"
        
        # Build the multi-line text to display INSIDE the box
        display_text = f"{current_name}"
        if role not in ['Group', 'Sub-Group']:
            display_text += f"\n{role}"
        if time_period and str(time_period).strip() != '':
            display_text += f"\n{time_period}"

        # HTML formatted tooltip for when you click the box
        tooltip_value = (
            f"<b>Name:</b> {current_name}<br/>"
            f"<b>Role:</b> {role}<br/>"
            f"<b>Department:</b> {dept}<br/>"
            f"<b>Time Period:</b> {time_period if str(time_period).strip() != '' else 'N/A'}<br/>"
            f"<b>Supervisor:</b> {supervisor}<br/>"
            f"<b>Direct Reports ({len(direct_reports)}):</b> {reports_str}"
        )

        node = {
            "name": display_text,
            "value": tooltip_value,
            "itemStyle": {"color": color_map.get(dept, default_color)},
            "children": []
        }

        for report in direct_reports:
            child_node = build_tree(report, df, visited)
            if child_node:
                node["children"].append(child_node)

        return node

    # Apply Sidebar Filters to find the top of the tree
    top_level_matches = clean_df[clean_df['Supervisor'].str.lower() == 'none']
    top_level_person = top_level_matches.iloc[0]['Name'] if not top_level_matches.empty else clean_df.iloc[0]['Name']

    if selected_person != "All":
        root_name = selected_person
    elif selected_dept != "All":
        dept_people = clean_df[clean_df['Department'] == selected_dept]
        root_name = dept_people.iloc[0]['Name'] if not dept_people.empty else top_level_person
    elif selected_role != "All":
        role_people = clean_df[clean_df['Role'] == selected_role]
        root_name = role_people.iloc[0]['Name'] if not role_people.empty else top_level_person
    else:
        root_name = top_level_person

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
            "feature": {
                "saveAsImage": {"name": "TC_Org_Chart", "title": "Save as PNG"}
            }
        },
        "series": [
            {
                "type": "tree",
                "data": [tree_data],
                "orient": "TB", # Top to bottom
                "top": "5%",
                "left": "5%",
                "bottom": "5%",
                "right": "5%",
                "symbol": "roundRect", # Box shape
                "symbolSize": [160, 65],
                "edgeShape": "polyline", # Straight right-angle lines
                "roam": True,
                "initialTreeDepth": 3, 
                "label": {
                    "position": "inside",
                    "verticalAlign": "middle",
                    "align": "center",
                    "fontSize": 11,
                    "color": "white",
                    "lineHeight": 16,
                    "fontWeight": "bold"
                },
                "expandAndCollapse": True,
                "animationDuration": 550,
                "animationDurationUpdate": 750
            }
        ]
    }

    st_echarts(options=options, height="850px")
else:
    st.warning("The table is empty. Please add at least one person to generate the chart.")
