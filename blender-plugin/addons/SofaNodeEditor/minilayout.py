class MiniDAGLayout:
    """Chat GPT"""
    COLUMN_WIDTH = 400
    ROW_HEIGHT = 180

    def __init__(self, tree):
        self.tree = tree

    def compute_levels(self):
        levels = {}
        visited = set()

        def dfs(node):
            if node in levels:
                return levels[node]

            incoming = [link.from_node for link in node.inputs[0].links] if node.inputs else []
            
            if not incoming:
                levels[node] = 0
            else:
                levels[node] = max(dfs(parent) for parent in incoming) + 1

            return levels[node]

        for node in self.tree.nodes:
            dfs(node)

        return levels

    def apply(self):
        levels = self.compute_levels()

        columns = {}
        for node, level in levels.items():
            columns.setdefault(level, []).append(node)

        for level, nodes in columns.items():
            count = len(nodes)
            for i, node in enumerate(nodes):
                y = (count - 1) * self.ROW_HEIGHT / 2 - i * self.ROW_HEIGHT
                node.location = (
                    level * self.COLUMN_WIDTH,
                    y
                )