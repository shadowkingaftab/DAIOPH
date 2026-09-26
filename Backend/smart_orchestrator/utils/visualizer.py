import streamlit as st
import json
import graphviz
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

def visualize_orchestration(data: dict):
    """Create an interactive visualization of the smart orchestration"""

    # 1. Original Prompt
    st.markdown("### 📝 Original Prompt")
    st.info(data['original_prompt'])

    # 2. Micro-Task Breakdown
    st.markdown("### 🔍 Micro-Task Analysis")
    for task in data['micro_tasks']:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.markdown(f"**Task {task['id']}**")
        with col2:
            st.write(task['task'])
        with col3:
            status = "✅ Cloud" if task['id'] in data['routing']['cloud'] else "📱 Device"
            st.markdown(f"**{status}**")

    # 3. Dependency Graph
    st.markdown("### 🔗 Task Dependencies")
    graph = graphviz.Digraph()
    graph.attr(rankdir='LR', size='10,10')

    for task in data['micro_tasks']:
        graph.node(str(task['id']), f"Task {task['id']}")

    for task in data['micro_tasks']:
        for dep in task.get('dependencies', []):
            graph.edge(str(dep), str(task['id']))

    st.graphviz_chart(graph)

    # 4. Execution Plan
    st.markdown("### 🚀 Execution Flow")
    for step in data['execution_plan']:
        executor = "Cloud" if "cloud" in step['executor'] else "Device"
        color = "#d1ecf1" if "cloud" in step['executor'] else "#d4edda"
        status_icon = "✅" if step['status'] == 'completed' else "⌛"

        st.markdown(f"""
        <div style="background-color: {color}; padding: 10px; border-radius: 5px; margin: 5px 0; color: black;">
            {status_icon} Task {step['task_id']} → {executor} ({step['status']})
        </div>
        """, unsafe_allow_html=True)

    # 5. Results
    st.markdown("### 🎯 Execution Results")
    for key, result in data['results'].items():
        source = "cloud" if "cloud" in key else "device"
        color = "#d1ecf1" if source == "cloud" else "#d4edda"
        
        # Get actual task id
        task_id = key.split('_')[-1]

        with st.expander(f"Task {task_id} ({source.capitalize()} Result)"):
            if result['status'] == 'completed':
                st.success(result['result'])
            else:
                st.error(f"Failed: {result.get('error', 'Unknown error')}")

    # 6. Raw Data
    with st.expander("📊 Full Orchestration Data"):
        st.json(data)
