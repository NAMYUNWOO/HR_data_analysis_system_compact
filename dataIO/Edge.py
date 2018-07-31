import pandas as pd

class Edge:
    def __init__(self, n_from, n_to, weight):
        self.n_from = n_from
        self.n_to = n_to
        self.weight = weight

    def __eq__(self, other):
        return (other.n_from == self.n_from and other.n_to == self.n_to)

    def __neg__(self):
        return Edge(self.n_to, self.n_from, 0)

    def __str__(self):
        return "edge(" + str(self.n_from) + "," + str(self.n_to) + ")"

    def __repr__(self):
        return "edge(" + str(self.n_from) + "," + str(self.n_to) + ")"

    def __gt__(self, other):
        if self.n_from == other.n_from:
            return self.n_to > other.n_to
        return self.n_from > other.n_from

    def __lt__(self, other):
        if self.n_from == other.n_from:
            return self.n_to < other.n_to
        return self.n_from < other.n_from

    def __hash__(self):
        return hash(self.n_from) ^ hash(self.n_to)


class Mon_node_size:
    def __init__(self):
        self._dict = {}

    def nodes_sizes_(self):
        temp_df = pd.DataFrame(pd.Series([k.n_from for k in self._dict.keys() if self._dict[k] == 1]).value_counts())
        temp_df["node"] = temp_df.index
        temp_df.columns = ["n_size", "node"]
        temp_df.index = range(len(temp_df))
        return temp_df

    def nodes_sizes(self):
        temp_df = pd.DataFrame([[k.n_from, k.n_to, self._dict[k]] for k in self._dict.keys() if self._dict[k] > 0])
        temp_df.columns = ["node_1", "node_2", "conn_size"]
        temp_df.index = range(len(temp_df))
        return temp_df


def monthly_node_size(series):
    mon_node_size = Mon_node_size()
    for edge in series:
        come = mon_node_size._dict.get(-edge, None)
        mon_node_size._dict[edge] = -edge.weight
        if come != None:
            # check come edge
            # if go and come both exists, there is bi-direction
            val = min(edge.weight, -come)
            mon_node_size._dict[-edge] = val
            mon_node_size._dict[edge] = val
    return mon_node_size

def q1_3iqr(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.76)
    return q1-3*(q3-q1)