"""KnowledgeGraph - manages a knowledge graph."""

from typing import Any, Dict, List, Optional


class KnowledgeGraph:
    """Manages a knowledge graph of entities and relations."""

    def __init__(self) -> None:
        """Initialize the knowledge graph."""
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: List[Dict[str, Any]] = []

    def add_node(self, node_id: str, data: Dict[str, Any]) -> None:
        """Add a node to the graph.

        Args:
            node_id: Node identifier.
            data: Node data.
        """
        self._nodes[node_id] = data

    def add_edge(self, source: str, target: str, relation: str) -> None:
        """Add an edge to the graph.

        Args:
            source: Source node ID.
            target: Target node ID.
            relation: Relation type.
        """
        self._edges.append({"source": source, "target": target, "relation": relation})

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node.

        Args:
            node_id: Node identifier.

        Returns:
            Optional[Dict[str, Any]]: Node data or None.
        """
        return self._nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        """Get neighbors of a node.

        Args:
            node_id: Node identifier.

        Returns:
            List[Dict[str, Any]]: Neighbor edges.
        """
        return [e for e in self._edges if e["source"] == node_id or e["target"] == node_id]

</final_file_content>
</write_to_file></tool_call>