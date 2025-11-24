# source: https://www.geeksforgeeks.org/python/red-black-tree-in-python

# class to implement node of RB Tree
class RBNode:
    # constructor
    def __init__(self, value, color='red'):
        self.value = value
        self.color = color
        self.left = None
        self.right = None
        self.parent = None

    # function to get the grandparent of node
    def grandparent(self):
        if self.parent is None:
            return None
        return self.parent.parent

    # function to get the sibling of node
    def sibling(self):
        if self.parent is None:
            return None
        if self == self.parent.left:
            return self.parent.right
        return self.parent.left

    # function to get the uncle of node
    def uncle(self):
        if self.parent is None:
            return None
        return self.parent.sibling()


class RedBlackTree:
    # constructor to initialize the RB tree
    def __init__(self):
        self.root = None
        self._size = 0

    # function to search a value in RB Tree
    def search(self, value):
        curr_node = self.root
        while curr_node:
            if value == curr_node.value:
                return curr_node
            elif value < curr_node.value:
                curr_node = curr_node.left
            else:
                curr_node = curr_node.right
        return None
    
    # function to search a node which has a value just above the value of interest
    def search_bound(self, value):
        curr_node = self.root
        candidate = float('inf')
        while curr_node:
            if curr_node.value > value:
                candidate = curr_node.value
                curr_node = curr_node.left
            else:
                curr_node = curr_node.right
        return candidate

    # function to insert a node in RB Tree, similar to BST insertion
    def insert(self, value):
        # Regular insertion
        new_node = RBNode(value)
        if self.root is None:
            self.root = new_node
        else:
            curr_node = self.root
            while True:
                if value < curr_node.value:
                    if curr_node.left is None:
                        curr_node.left = new_node
                        new_node.parent = curr_node
                        break
                    else:
                        curr_node = curr_node.left
                else:
                    if curr_node.right is None:
                        curr_node.right = new_node
                        new_node.parent = curr_node
                        break
                    else:
                        curr_node = curr_node.right
        
        self._size += 1
        self.insert_fix(new_node)

    # Function to fix RB tree properties after insertion
    def insert_fix(self, new_node):
        while new_node.parent and new_node.parent.color == 'red':
            if new_node.parent == new_node.grandparent().left:
                uncle = new_node.uncle()
                if uncle and uncle.color == 'red':
                    new_node.parent.color = 'black'
                    uncle.color = 'black'
                    new_node.grandparent().color = 'red'
                    new_node = new_node.grandparent()
                else:
                    if new_node == new_node.parent.right:
                        new_node = new_node.parent
                        self.rotate_left(new_node)
                    new_node.parent.color = 'black'
                    new_node.grandparent().color = 'red'
                    self.rotate_right(new_node.grandparent())
            else:
                uncle = new_node.uncle()
                if uncle and uncle.color == 'red':
                    new_node.parent.color = 'black'
                    uncle.color = 'black'
                    new_node.grandparent().color = 'red'
                    new_node = new_node.grandparent()
                else:
                    if new_node == new_node.parent.left:
                        new_node = new_node.parent
                        self.rotate_right(new_node)
                    new_node.parent.color = 'black'
                    new_node.grandparent().color = 'red'
                    self.rotate_left(new_node.grandparent())
        self.root.color = 'black'

    def delete(self, value):
        z = self.search(value)
        if not z:
            return
        
        self._size -= 1

        y = z
        y_original_color = y.color

        # Choose node x to move up
        if z.left is None:
            x = z.right
            self._replace_node(z, z.right)

        elif z.right is None:
            x = z.left
            self._replace_node(z, z.left)

        else:
            # successor
            y = self._find_min(z.right)
            y_original_color = y.color
            x = y.right

            if y.parent == z:
                if x:
                    x.parent = y
            else:
                self._replace_node(y, y.right)
                y.right = z.right
                y.right.parent = y

            self._replace_node(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color

        # If we removed a black node, fix double-black
        if y_original_color == "black":
            self.delete_fix(x, parent=y.parent if x is None else x.parent)


    def delete_fix(self, x, parent):
        while (x != self.root) and (x is None or x.color == "black"):

            if x == (parent.left if parent else None):
                sibling = parent.right

                if sibling and sibling.color == "red":
                    sibling.color = "black"
                    parent.color = "red"
                    self.rotate_left(parent)
                    sibling = parent.right

                if (
                    (sibling is None) or
                    ((sibling.left is None or sibling.left.color == "black") and
                    (sibling.right is None or sibling.right.color == "black"))
                ):
                    if sibling:
                        sibling.color = "red"
                    x = parent
                    parent = x.parent
                else:
                    if sibling and (sibling.right is None or sibling.right.color == "black"):
                        if sibling.left:
                            sibling.left.color = "black"
                        sibling.color = "red"
                        self.rotate_right(sibling)
                        sibling = parent.right

                    if sibling:
                        sibling.color = parent.color
                    parent.color = "black"
                    if sibling and sibling.right:
                        sibling.right.color = "black"
                    self.rotate_left(parent)
                    x = self.root

            else:
                sibling = parent.left

                if sibling and sibling.color == "red":
                    sibling.color = "black"
                    parent.color = "red"
                    self.rotate_right(parent)
                    sibling = parent.left

                if (
                    (sibling is None) or
                    ((sibling.left is None or sibling.left.color == "black") and
                    (sibling.right is None or sibling.right.color == "black"))
                ):
                    if sibling:
                        sibling.color = "red"
                    x = parent
                    parent = x.parent
                else:
                    if sibling and (sibling.left is None or sibling.left.color == "black"):
                        if sibling.right:
                            sibling.right.color = "black"
                        sibling.color = "red"
                        self.rotate_left(sibling)
                        sibling = parent.left

                    if sibling:
                        sibling.color = parent.color
                    parent.color = "black"
                    if sibling and sibling.left:
                        sibling.left.color = "black"
                    self.rotate_right(parent)
                    x = self.root

        if x:
            x.color = "black"

    # Function for left rotation of RB Tree
    def rotate_left(self, node):
        right_child = node.right
        node.right = right_child.left

        if right_child.left is not None:
            right_child.left.parent = node

        right_child.parent = node.parent

        if node.parent is None:
            self.root = right_child
        elif node == node.parent.left:
            node.parent.left = right_child
        else:
            node.parent.right = right_child

        right_child.left = node
        node.parent = right_child

    # function for right rotation of RB Tree
    def rotate_right(self, node):
        left_child = node.left
        node.left = left_child.right

        if left_child.right is not None:
            left_child.right.parent = node

        left_child.parent = node.parent

        if node.parent is None:
            self.root = left_child
        elif node == node.parent.right:
            node.parent.right = left_child
        else:
            node.parent.left = left_child

        left_child.right = node
        node.parent = left_child

    # function to replace an old node with a new node
    def _replace_node(self, old_node, new_node):
        if old_node.parent is None:
            self.root = new_node
        else:
            if old_node == old_node.parent.left:
                old_node.parent.left = new_node
            else:
                old_node.parent.right = new_node
        if new_node is not None:
            new_node.parent = old_node.parent

    # function to find node with minimum value in a subtree
    def _find_min(self, node):
        if node is None:
            return None
        while node.left is not None:
            node = node.left
        return node
    
    # function to find node with maximum value in a subtree
    def _find_max(self, node):
        if node is None:
            return None
        while node.right is not None:
            node = node.right
        return node

    # function to perform inorder traversal
    def _inorder_traversal(self, node):
        if node is not None:
            self._inorder_traversal(node.left)
            print(node.value, end=" ")
            self._inorder_traversal(node.right)

    # function to return values in inorder traversal
    def _inorder_traversal_values(self, node, values):
        if node is not None:
            values = self._inorder_traversal_values(node.left, values)
            values.append(node.value)
            values = self._inorder_traversal_values(node.right, values)

        return values
    
    def get_size(self):
        return self._size

    def is_empty(self):
        return self._size == 0