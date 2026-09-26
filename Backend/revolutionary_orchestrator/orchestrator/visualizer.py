import streamlit as st
import graphviz
import json
from typing import Dict

def visualize_dag(dag: Dict, execution_results: Dict = None):
    """Render the DAG and execution flow."""
    # Create DAG visualization
    graph = graphviz.Digraph(graph_attr={"rankdir": "LR"})
    for node in dag["nodes"]:
        status = "✅" if execution_results and node["id"] in execution_results else "⌛"
        color = "#d4edda" if status == "✅" else "#f8d7da"
        graph.node(
            node["id"],
            f"{status} {node['id']}: {node['task'][:30]}...",
            style="filled",
            fillcolor=color
        )

    for node in dag["nodes"]:
        if "depends_on" in node:
            for dep in node["depends_on"]:
                graph.edge(dep, node["id"])

    st.graphviz_chart(graph)

    # Show execution results
    if execution_results:
        st.markdown("### 🎯 Execution Results")
        for task_id, result in execution_results.items():
            if isinstance(result, dict) and "error" in result:
                st.error(f"**Task {task_id}:** {result['error']}")
            else:
                st.success(f"**Task {task_id}:** {str(result)[:100]}...")

    # Show raw DAG
    with st.expander("📊 Raw DAG Data"):
        st.json(dag)
