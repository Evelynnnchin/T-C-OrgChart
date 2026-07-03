import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Editable Org Chart", layout="wide")
st.title("🏢 Directly Editable Organizational Chart")

if "org_data" not in st.session_state:
    st.session_state.org_data = pd.DataFrame({
        "Name": ["Alice (CEO)", "Bob", "Charlie", "David", "Eve", "Frank"],
        "Role": ["CEO", "VP Engineering", "VP Sales", "Lead Dev", "Backend Dev", "Sales Rep"],
        "Department": ["Management", "Engineering", "Sales", "Engineering", "Engineering", "Sales"],
        "Supervisor": ["None", "Alice (CEO)", "Alice (CEO)", "Bob", "David", "Charlie"]
    })

st.markdown("### ✏️ Edit Data Directly")
st.write(
    "Click inside the table to edit. Add new rows at the bottom. "
    "Select a row and press delete to remove someone."
)

edited_df = st.data_editor(
    st.session_state.org_data,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True
)

color_map = {
    "Management": "#d9534f",
    "Engineering": "#5bc0de",
    "Sales": "#5cb85c",
    "Testing": "#f0ad4e",
    "Planning": "#9b59b6"
}
default_color = "#7f8c8d"

def build_tree(current_name, df, visited=None):
    if visited is None:
        visited = set()

    if current_name in visited:
        return None

    visited.add(current_name)

    person_data = df[df["Name"] == current_name]

    if person_data.empty:
        return None

    person = person_data.iloc[0]

    role = person.get("Role", "Unknown")
    dept = person.get("Department", "Unknown")
    supervisor = person.get("Supervisor", "None")

    direct_reports = df[df["Supervisor"] == current_name]["Name"].tolist()
    reports_str = ", ".join(direct_reports) if direct_reports else "None"

    tooltip_value = (
        f"<b>Role:</b> {role}<br/>"
        f"<b>Department:</b> {dept}<br/>"
        f"<b>Supervisor:</b> {supervisor}<br/>"
        f"<b>Direct Reports:</b> {reports_str}"
    )

    node = {
        "name": current_name,
        "value": tooltip_value,
        "itemStyle": {
            "color": color_map.get(dept, default_color)
        },
        "children": []
    }

    for report in direct_reports:
        child_node = build_tree(report, df, visited)
        if child_node:
            node["children"].append(child_node)

    return node

clean_df = edited_df.copy()
clean_df = clean_df.dropna(subset=["Name"])
clean_df["Supervisor"] = clean_df["Supervisor"].fillna("None")

st.markdown("---")

if not clean_df.empty:
    top_level = clean_df[
        clean_df["Supervisor"].astype(str).str.lower() == "none"
    ]

    if not top_level.empty:
        root_name = top_level.iloc[0]["Name"]
    else:
        root_name = clean_df.iloc[0]["Name"]

    tree_data = build_tree(root_name, clean_df)

    options = {
        "tooltip": {
            "trigger": "item",
            "triggerOn": "mousemove",
            "formatter": "{b}<br/><br/>{c}",
            "backgroundColor": "rgba(255, 255, 255, 0.95)",
            "borderColor": "#ccc",
            "borderWidth": 1,
            "textStyle": {
                "color": "#333"
            }
        },
        "toolbox": {
            "feature": {
                "saveAsImage": {
                    "name": "Org_Chart",
                    "title": "Save as PNG"
                }
            }
        },
        "series": [
            {
                "type": "tree",
                "data": [tree_data],
                "top": "5%",
                "left": "15%",
                "bottom": "5%",
                "right": "20%",
                "symbolSize": 15,
                "roam": True,
                "initialTreeDepth": 3,
                "label": {
                    "position": "left",
                    "verticalAlign": "middle",
                    "align": "right",
                    "fontSize": 14,
                    "fontWeight": "bold"
                },
                "leaves": {
                    "label": {
                        "position": "right",
                        "verticalAlign": "middle",
                        "align": "left"
                    }
                },
                "expandAndCollapse": True,
                "animationDuration": 550,
                "animationDurationUpdate": 750
            }
        ]
    }

    st_echarts(options=options, height="600px")

else:
    st.warning("The table is empty. Please add at least one person.")
