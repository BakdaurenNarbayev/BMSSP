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
        # Shared sentinel NIL node (represents all leaves)
        self.NIL = RBNode(None, color='black')
        self.NIL.left = self.NIL
        self.NIL.right = self.NIL
        self.NIL.parent = None

        # When empty, root == self.NIL (not None)
        self.root = self.NIL
        self._size = 0

    # function to search a value in RB Tree
    def search(self, value):
        curr_node = self.root
        while curr_node != self.NIL:
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
        while curr_node != self.NIL:
            if curr_node.value > value:
                candidate = curr_node.value
                curr_node = curr_node.left
            else:
                curr_node = curr_node.right
        return candidate

    # function to insert a node in RB Tree, similar to BST insertion
    def insert(self, value):
        new_node = RBNode(value)
        new_node.color = 'red'
        new_node.left = self.NIL
        new_node.right = self.NIL
        new_node.parent = None

        parent = None
        curr_node = self.root

        # Standard BST insert
        while curr_node != self.NIL:
            parent = curr_node
            if value < curr_node.value:
                curr_node = curr_node.left
            else:
                curr_node = curr_node.right

        new_node.parent = parent
        if parent is None:
            # Tree was empty
            self.root = new_node
        elif value < parent.value:
            parent.left = new_node
        else:
            parent.right = new_node

        self._size += 1
        self.insert_fix(new_node)

    # Function to fix RB tree properties after insertion
    def insert_fix(self, z):
        # CLRS-style insert fix-up
        while z.parent is not None and z.parent.color == 'red':
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right  # uncle
                if y.color == 'red':
                    # Case 1
                    z.parent.color = 'black'
                    y.color = 'black'
                    z.parent.parent.color = 'red'
                    z = z.parent.parent
                else:
                    if z == z.parent.right:
                        # Case 2
                        z = z.parent
                        self.rotate_left(z)
                    # Case 3
                    z.parent.color = 'black'
                    z.parent.parent.color = 'red'
                    self.rotate_right(z.parent.parent)
            else:
                y = z.parent.parent.left  # uncle (mirror)
                if y.color == 'red':
                    # Mirror Case 1
                    z.parent.color = 'black'
                    y.color = 'black'
                    z.parent.parent.color = 'red'
                    z = z.parent.parent
                else:
                    if z == z.parent.left:
                        # Mirror Case 2
                        z = z.parent
                        self.rotate_right(z)
                    # Mirror Case 3
                    z.parent.color = 'black'
                    z.parent.parent.color = 'red'
                    self.rotate_left(z.parent.parent)

        self.root.color = 'black'

    def delete(self, value):
        z = self.search(value)
        if z is None:
            return

        self._size -= 1

        y = z
        y_original_color = y.color

        # Choose node x to move up
        if z.left == self.NIL:
            x = z.right
            self._replace_node(z, z.right)
        elif z.right == self.NIL:
            x = z.left
            self._replace_node(z, z.left)
        else:
            # successor
            y = self._find_min(z.right)
            y_original_color = y.color
            x = y.right

            if y.parent == z:
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
            # parent argument is kept for signature compatibility, but not used.
            self.delete_fix(x, parent=None)

    def delete_fix(self, x, parent=None):
        """
        Fix double-black violations after deletion.
        The 'parent' parameter is kept only to preserve the original method signature.
        All logic uses x.parent, as in standard CLRS fix-up.
        """
        while x != self.root and x.color == "black":
            if x == x.parent.left:
                sibling = x.parent.right

                if sibling.color == "red":
                    # Case 1
                    sibling.color = "black"
                    x.parent.color = "red"
                    self.rotate_left(x.parent)
                    sibling = x.parent.right

                if sibling.left.color == "black" and sibling.right.color == "black":
                    # Case 2
                    sibling.color = "red"
                    x = x.parent
                else:
                    if sibling.right.color == "black":
                        # Case 3
                        sibling.left.color = "black"
                        sibling.color = "red"
                        self.rotate_right(sibling)
                        sibling = x.parent.right

                    # Case 4
                    sibling.color = x.parent.color
                    x.parent.color = "black"
                    sibling.right.color = "black"
                    self.rotate_left(x.parent)
                    x = self.root
            else:
                sibling = x.parent.left

                if sibling.color == "red":
                    # Mirror Case 1
                    sibling.color = "black"
                    x.parent.color = "red"
                    self.rotate_right(x.parent)
                    sibling = x.parent.left

                if sibling.right.color == "black" and sibling.left.color == "black":
                    # Mirror Case 2
                    sibling.color = "red"
                    x = x.parent
                else:
                    if sibling.left.color == "black":
                        # Mirror Case 3
                        sibling.right.color = "black"
                        sibling.color = "red"
                        self.rotate_left(sibling)
                        sibling = x.parent.left

                    # Mirror Case 4
                    sibling.color = x.parent.color
                    x.parent.color = "black"
                    sibling.left.color = "black"
                    self.rotate_right(x.parent)
                    x = self.root

        x.color = "black"

    # Function for left rotation of RB Tree
    def rotate_left(self, node):
        right_child = node.right
        if right_child == self.NIL:
            return  # nothing to rotate

        node.right = right_child.left
        if right_child.left != self.NIL:
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
        if left_child == self.NIL:
            return  # nothing to rotate

        node.left = left_child.right
        if left_child.right != self.NIL:
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
        """
        Transplant subtree rooted at new_node into old_node's position.
        If new_node is None, it is treated as the NIL sentinel.
        """
        if new_node is None:
            new_node = self.NIL

        if old_node.parent is None:
            self.root = new_node
        elif old_node == old_node.parent.left:
            old_node.parent.left = new_node
        else:
            old_node.parent.right = new_node

        new_node.parent = old_node.parent

    # function to find node with minimum value in a subtree
    def _find_min(self, node):
        if node is None or node == self.NIL:
            return None
        while node.left != self.NIL:
            node = node.left
        return node
    
    # function to find node with maximum value in a subtree
    def _find_max(self, node):
        if node is None or node == self.NIL:
            return None
        while node.right != self.NIL:
            node = node.right
        return node

    # function to perform inorder traversal
    def _inorder_traversal(self, node):
        if node is None or node == self.NIL:
            return
        self._inorder_traversal(node.left)
        print(node.value, end=" ")
        self._inorder_traversal(node.right)

    # function to return values in inorder traversal
    def _inorder_traversal_values(self, node, values):
        if node is None or node == self.NIL:
            return values
        values = self._inorder_traversal_values(node.left, values)
        values.append(node.value)
        values = self._inorder_traversal_values(node.right, values)
        return values
    
    def get_size(self):
        return self._size

    def is_empty(self):
        return self._size == 0
