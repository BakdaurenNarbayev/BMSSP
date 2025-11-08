# source: https://builtin.com/data-science/python-linked-list

class BNode:
  
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.next = None
        
    def get_key(self):
        return self.key
      
    def set_key(self, key):
        self.key = key

    def get_val(self):
        return self.val
    
    def set_val(self, val):
        self.val = val
 
    def get_next(self):
        return self.next
 
    def set_next(self, next):
        self.next = next


class Block:

    def __init__(self, B, head = None):
        # each block is a linked list containing at most M key/value pairs
        self.head = head
        self.count = 0 if head is None else 1
        self.B = B

    def insert(self, key, val):
        """
        Create a new node at the Head of the Block
        """ 
        # create a new node to hold the data
        new_node = BNode(key, val)
        
        # set the next of the new node to the current head
        new_node.set_next(self.head)
        
        # set the head of the Block to the new head
        self.head = new_node
        
        # add 1 to the count
        self.count += 1

    def search(self, key):
        """
        Search for item in the Block with matching key
        
        Time complexity is O(n) as in worst case scenario
        have to iterate over whole Block
        """
        # start with the first item in the Block
        item = self.head
        # then iterate over the next nodes
        # but if item = None then end search
        while item != None:
           
           # if the data in item matched key
           # then return item
           if item.get_key() == key:
               return item
           
           # otherwise we get the next item in the list
           else:
                item = item.get_next()
              
        # if while loop breaks with None then nothing found
        # so we return None
        return None
    
    def delete(self, key):
        """
        Remove Node with matching key
        Time complexity is O(n) as in the worst case we have to 
        iterate over the whole Block
        """
        
        # set the current node starting with the head
        current = self.head
        # create a previous node to hold the one before
        # the node we want to remove
        previous = None
        
        # while current is note None then we can search for it
        while current is not None:
            # if current has matching key then we can break
            if current.get_key() == key:
                break
            # otherwise we set previous to current and 
            # current to the next node in block
            previous = current
            current = current.get_next()
            
        # if the current is None then key is not in the block
        if current is None:
            raise ValueError(f"{key} is not in the block")
        # if previous None then the key is at the head
        if previous is None:
            self.head = current.get_next()
            self.count -= 1
        # otherwise then we remove that node from the block
        else:
             previous.set_next(current.get_next())
             self.count -= 1

    def get_count(self):
        """
        Return the length of the Block
        Time complexity O(1) as only returning a single value
        """
        return self.count
      
    def is_empty(self):
        """
        Returns whether the Block is empty or not
        Time complexity O(1) as only returns True or False
        """
        # we only have to check the head if is None or not
        return self.head == None