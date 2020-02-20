
import matplotlib.pyplot as plt
import networkx as nx
import re


class Decomposition(object):
    def __init__(self, decomposition_list):
        self.decomposition_list = [str(step) for step in decomposition_list]

    def _get_graph_edges(self):
        edges = []
        for i, step in enumerate(self.decomposition_list):
            references = [int(x) for x in re.findall(r"@@(\d)@@", step)]
            step_edges = [(i+1, ref) for ref in references]
            edges.extend(step_edges)

        return edges

    def to_string(self):
        return " @@SEP@@ ".join([x.replace("  ", " ").strip() for x in self.decomposition_list])

    def to_graph(self, nodes_only=False):
        # initiate a directed graph
        graph = nx.DiGraph()

        # add edges
        if nodes_only:
            edges = []
        else:
            edges = self._get_graph_edges()
        graph.add_edges_from(edges)

        # add nodes
        nodes = self.decomposition_list
        for i in range(len(nodes)):
            graph.add_node(i+1, label=nodes[i])

        # handle edge cases where artificial nodes need to be added
        for node in graph.nodes:
            if 'label' not in graph.nodes[node]:
                graph.add_node(node, label='')

        return graph

    def draw_decomposition(self):
        graph = self.to_graph(False)
        draw_decomposition_graph(graph)


def draw_decomposition_graph(graph, title=None):
    options = {
        'node_color': 'lightblue',
        'node_size': 400,
        'width': 1,
        'arrowstyle': '-|>',
        'arrowsize': 14,
    }

    pos = nx.spring_layout(graph, k=0.5)
    nx.draw_networkx(graph, pos=pos, arrows=True, with_labels=True, **options)
    for node in graph.nodes:
        plt.text(pos[node][0], pos[node][1]-0.1,
                 s=graph.nodes[node]['label'],
                 bbox=dict(facecolor='red', alpha=0.5),
                 horizontalalignment='center',
                 wrap=True)

    if title:
        plt.title(title)

    plt.axis("off")
    plt.show()
    plt.clf()


def get_decomposition_from_string(decomposition_str):
    decomposition = [d.strip() for d in decomposition_str.split("@@SEP@@")]
    return Decomposition(decomposition)


def get_decomposition_from_tokens(decomposition_tokens):
    decomposition_str = ' '.join(decomposition_tokens)
    return get_decomposition_from_string(decomposition_str)
