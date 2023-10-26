# import requests; exec(requests.get('https://raw.githubusercontent.com/mustafah/visualize-pandas/main/visualize_merge.py', headers={'Cache-Control': 'no-cache'}).text)

import pandas as pd
import inspect
import re
from IPython.core.display import display, HTML

def to_colored_html(df, color_map, merge_column=None, merge_values=None, maxHeight=200, theme='light'):
    text_color = 'white' if theme == 'light' else 'dark'
    html_str = f"<div class='visualized-df-container' style='max-height: {maxHeight}px; overflow: scroll;'>"
    html_str += '<table>'
    html_str += '<thead>'
    for col in df.columns:
        html_str += f"<th style='position: sticky; top: 0; background-color: #FB8C00; z-index: 1;'>{col}</th>"
    html_str += '</thead><tbody>'
    
    for _, row in df.iterrows():
        html_str += '<tr>'
        for col in df.columns:
            color = color_map.get(col, 'black')
            value = row[col]
            if (col == merge_column and value in merge_values):
                display_value = f"🔗 {value}"
                html_str += f"<td class='clickable' onclick=\"highlightCells('{display_value}')\" style='background-color: {color}; cursor: pointer; color: {text_color};'>{display_value}</td>"
            else:
                html_str += f"<td style='background-color: {color}; color: {text_color};'>{value}</td>"
        html_str += '</tr>'
    html_str += '</tbody></table>'
    html_str += f"</div>"
    return html_str


def highlight_cells_script(unique_id):
    return """
    <script>
        function highlightCells(value) {
            const rootElement = document.getElementById('""" + unique_id + """');
            let dfContainers = rootElement.querySelectorAll(".visualized-df-container");
            dfContainers.forEach((dfContainer) => {
                dfContainer.querySelectorAll(".highlight").forEach((cell) => {
                    cell.classList.remove("highlight");
                });
                dfContainer.querySelectorAll(`td`).forEach((cell) => {
                    if (cell.textContent.includes(value)) {
                        cell.classList.add("highlight");
                        dfContainer.scrollTop = 0;
                        setTimeout(function() {
                            let rect = cell.getBoundingClientRect();
                            let containerRect = dfContainer.getBoundingClientRect();
                            dfContainer.scrollTop = rect.top - containerRect.top - dfContainer.clientHeight / 2 + rect.height / 2;
                        }, 0);
                    }
                });
            });
        }
    </script>
    <style>
        .highlight {
            // border: 3px solid yellow !important;
            box-shadow: inset 0 0 4px yellow !important;
            position: relative;
            outline: 2px solid yellow;
            outline-offset: -2px;
        }
    </style>
    """

def visualize_merge(df1, df2, how, on, maxHeight = 200, theme='light'):
    merged_df = pd.merge(df1, df2, how=how, on=on)
    merge_values = set(merged_df[on])
    
    color_map_df1 = {col: '#1E88E5' for col in df1.columns}
    color_map_df2 = {col: '#E53935' for col in df2.columns}
    color_map_df2[on] = color_map_df1[on]  # Color the mergeOn column in df2 the same as in df1
    
    color_map_merged = {**color_map_df2, **color_map_df1}
    
    df1_html = to_colored_html(df1, color_map_df1, merge_column=on, merge_values=merge_values, maxHeight=maxHeight, theme=theme)
    df2_html = to_colored_html(df2, color_map_df2, merge_column=on, merge_values=merge_values, maxHeight=maxHeight, theme=theme)
    merged_html = to_colored_html(merged_df, color_map_merged, merge_column=on, merge_values=merge_values, maxHeight=maxHeight, theme=theme)
    
    # Extract the calling line
    stack = inspect.stack()
    calling_line = stack[1].code_context[0].strip()

    print(calling_line)
    # Parse the calling line to get variable names
    match = re.search(r"visualize_merge\(([^,]*), ([^,]*),", calling_line)
    if match:
        name_df1, name_df2 = match.groups()
    else:
        name_df1, name_df2 = "DataFrame 1", "DataFrame 2"

    unique_id = str(uuid.uuid4())
    script = highlight_cells_script(unique_id)
    
    template = f"""
    {script}
    <div id='{unique_id}'>
        <div class='visualized-merge-container' style="width:100%; display: flex; gap: 32px">
            <div style="">
                <h4>{name_df1}</h4>
                {df1_html}
            </div>
            <div style="">
                <h4>+ {name_df2}</h4>
                {df2_html}
            </div>
        </div>
        <br/>
        <div style="clear:both;">
            <h4>= Merged DataFrame (how='{how}', on='{on}')</h4>
            {merged_html}
        </div>
    </div>
    """
    
    display(HTML(template))

# df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
# df2 = pd.DataFrame({'A': [1, 3, 4], 'C': [7, 8, 9]})

# visualize_merge(df1, df2, how = 'inner', on = 'A', maxHeight=100)
