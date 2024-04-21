import numpy as np
from pathlib import Path
from typing import Tuple


class Node:
    """ Node class used to build the decision tree"""
    def __init__(self, value=None):
        self.children = {}
        self.parent = None
        self.attribute = None
        self.value = value

    def classify(self, example):
        if self.value is not None:
            return self.value
        return self.children[example[self.attribute]].classify(example)


def plurality_value(examples: np.ndarray) -> int:
    """Implements the PLURALITY-VALUE (Figure 19.5)"""
    labels = examples[:, -1]
    value, count = 0, 0
    for label in np.unique(labels):
        label_count = np.count_nonzero(labels == label)
        if label_count > count:
            value = label
            count = label_count

    return value


def information_gain(p_total, n_total, p_split, n_split):
    def entropy(p, n):
        """Calculates entropy given the counts of positive (p = 1) and negative (n = 2) instances."""
        total = p + n
        if p == 0 or n == 0:
            return 0
        return -(p/total) * np.log2(p/total) - (n/total) * np.log2(n/total)

    def remainder(p_list, n_list):
        """Calculate the remainder using the lists of positive (p = 1) and negative (n = 2) instances."""
        total = sum(p_list) + sum(n_list)
        remainder_val = 0
        for p, n in zip(p_list, n_list):
            remainder_val += (p + n) / total * entropy(p, n)
        return remainder_val

    """Calculate the information gain given total counts and split counts."""
    return entropy(p_total, n_total) - remainder(p_split, n_split)


def importance(attributes: np.ndarray, examples: np.ndarray, measure: str) -> int:
    """
    This function should compute the importance of each attribute and choose the one with highest importance,
    A ← argmax a ∈ attributes IMPORTANCE (a, examples) (Figure 19.5)

    Parameters:
        attributes (np.ndarray): The set of attributes from which the attribute with highest importance is to be chosen
        examples (np.ndarray): The set of examples to calculate attribute importance from
        measure (str): Measure is either "random" for calculating random importance, or "information_gain" for
                        caulculating importance from information gain (see Section 19.3.3. on page 679 in the book)

    Returns:
        (int): The index of the attribute chosen as the test

    """

    # I have made a small alteration in the task's command.
    # Instead of allocating random numbers as importance to each attribute and then choosing the one with the highest imporatance value,
    # I chose to randomly choose one of the attributes as the splitting attribute.
    if measure == "random":
        random_index = np.random.randint(0, len(attributes) - 1)
        return attributes[random_index]
    elif measure == "information_gain":
        max_information_gain = float('-inf')
        best_attribute = 0
        p_total = (examples[:, -1] == 1).sum()
        n_total = (examples[:, -1] == 2).sum()

        for attribute in attributes:
            p_split = []
            n_split = []
            for value in np.unique(examples[:, attribute]):
                subset = examples[examples[:, attribute] == value]
                p_split.append((subset[:, -1] == 1).sum())
                n_split.append((subset[:, -1] == 2).sum())

            gain = information_gain(p_total, n_total, p_split, n_split)
            if gain > max_information_gain:
                max_information_gain = gain
                best_attribute = attribute
        return best_attribute


def learn_decision_tree(examples: np.ndarray, attributes: np.ndarray,
                        parent_examples: np.ndarray,
                        parent: Node, branch_value: int, measure: str):
    """
    This is the decision tree learning algorithm. The pseudocode for the algorithm can be
    found in Figure 19.5 on Page 678 in the book.

    Parameters:
        examples (np.ndarray): The set data examples to consider at the current node
        attributes (np.ndarray): The set of attributes that can be chosen as the test at the current node
        parent_examples (np.ndarray): The set of examples that were used in constructing the current node’s parent.
                                        If at the root of the tree, parent_examples = None
        parent (Node): The parent node of the current node. If at the root of the tree, parent = None
        branch_value (int): The attribute value corresponding to reaching the current node from its parent.
                        If at the root of the tree, branch_value = None
        measure (str): The measure to use for the Importance-function. measure is either "random" or "information_gain"

    Returns:
        (Node): The subtree with the current node as its root
    """

    node = Node()
    if parent is not None:
        parent.children[branch_value] = node
        node.parent = parent

    if len(examples) == 0:
        return Node(value=plurality_value(parent_examples))
    elif len(np.unique(examples[:, -1])) == 1:
        return Node(value=examples[0, -1])
    elif len(attributes) == 0:
        return Node(value=plurality_value(examples))
    else:
        best_attribute = importance(attributes, examples, measure)
        node.attribute = best_attribute
        for value in np.unique(examples[:, best_attribute]):
            exs = examples[examples[:, best_attribute] == value]
            index_to_delete = np.where(attributes == best_attribute)[0]
            next_attributes = np.delete(attributes, index_to_delete)
            subtree = learn_decision_tree(exs, next_attributes, examples, node, value, measure)
            node.children[value] = subtree

        return node


def accuracy(tree: Node, examples: np.ndarray) -> float:
    """ Calculates accuracy of tree on examples """
    correct = 0
    for example in examples:
        pred = tree.classify(example[:-1])
        correct += pred == example[-1]
    return correct / examples.shape[0]


def load_data() -> Tuple[np.ndarray, np.ndarray]:
    """ Load the data for the assignment,
    Assumes that the data files is in the same folder as the script"""
    with (Path.cwd() / "train.csv").open("r") as f:
        train = np.genfromtxt(f, delimiter=",", dtype=int)
    with (Path.cwd() / "test.csv").open("r") as f:
        test = np.genfromtxt(f, delimiter=",", dtype=int)
    return train, test


def visualize_predictions(tree: Node, examples: np.ndarray):
    """Visualizes the predictions made by the decision tree."""
    for example in examples:
        pred = tree.classify(example[:-1])
        correct = pred == example[-1]
        if correct:
            print('\033[92m' + ' '.join(map(str, example)) + ' (Predicted: ' + str(pred) + ')')
        else:
            print('\033[91m' + ' '.join(map(str, example)) + ' (Predicted: ' + str(pred) + ')')
        print('\033[0m', end='')


if __name__ == '__main__':

    train, test = load_data()

    measure_1 = "information_gain"
    tree = learn_decision_tree(examples=train,
                               attributes=np.arange(0, train.shape[1] - 1, 1, dtype=int),
                               parent_examples=None,
                               parent=None,
                               branch_value=None,
                               measure=measure_1)
    print("INFORMATION GAIN")
    visualize_predictions(tree, test)
    print(f"Training Accuracy {accuracy(tree, train)}")
    print(f"Test Accuracy {accuracy(tree, test)}")

    measure_2 = "random"
    tree = learn_decision_tree(examples=train,
                               attributes=np.arange(0, train.shape[1] - 1, 1, dtype=int),
                               parent_examples=None,
                               parent=None,
                               branch_value=None,
                               measure=measure_2)
    print("RANDOM")
    visualize_predictions(tree, test)
    print(f"Training Accuracy {accuracy(tree, train)}")
    print(f"Test Accuracy {accuracy(tree, test)}")
