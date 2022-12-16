class Graph:
    def __init__(self):
        self.adj_list = {}
        self.node_info = {}
        
    def add_edge(self, node1, node2): # node1 --> node2
        try:
            self.adj_list[node1].append(node2)
        except:
            self.adj_list[node1] = [node2]
    
    def add_node(self, key, val):
        self.node_info[key] = val
        
    def print_graph(self):
        for key, val in self.adj_list.items():
            print("Node {} is connected to {}".format(key, val))