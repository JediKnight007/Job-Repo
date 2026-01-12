from classes import ListNode, TreeNode
from queue import PriorityQueue
import heapq

def equal_encoding(s1: str, s2: str) -> bool:
    """
    Given two strings s1 and s2 of equal length, determine whether they are equal under a simple 
    character-based encoding that replaces each character in s1 with another character to turn it into s2.

    Each appearance of a character in s1 must be replaced with the same character. No two characters in s1
    can be replaced with the same character in s2. A character is allowed to be replaced with itself.

    Args:
    - s1 (str): The first string.
    - s2 (str): The second string.

    Returns:
    - bool: True if the strings can be encoded as described, False otherwise.

    Time Complexity Requirement:
    - O(n), where n is the length of string s1 (and s2).

    Space Complexity Requirement:
    - O(n), where n is the length of string s1 (and s2).
    """
    if(s1 is s2):
        return True
    
    set1 = set(s1.lower())
    set2 = set(s2.lower())

    if(len(set1) == len(set2)):
        return True
    
    return False
    

def sum_pair(nums: list[int], target: int) -> set[int]:
    """
    Given a sequence of numbers and a target number, return the indices (positions in the input list) 
    of the two numbers that add to the target number (in the form of a set). 
    You may assume that there is exactly one pair of indices meeting this criterion. 

    Args:
    - nums (list[int]): The input list of integers.
    - target (int): The target sum.

    Returns:
    - set[int]: A set containing the indices of the two numbers whose values sum to the target.

    Time Complexity Requirement:
    - O(n), where n is the length of the input list.

    Space Complexity Requirement:
    - O(n), where n is the length of the input list.
    """
    
    history = dict()
    
    for i in range (len(nums)):
        if nums[i] in history:
            return set([history[nums[i]], i])
        else: 
            history[target - nums[i]] = i
    

def merge_k(lists: list[ListNode]) -> ListNode:
    """
    Given a list of sorted Singly Linked Lists, weave them together into a single sorted Singly Linked List.
    
    Retains duplicates; the length of the returned list equals the sum of the lengths of the inner input lists.

    Args:
    - lists (list[ListNode]): List of sorted Singly Linked Lists.

    Returns:
    - ListNode: The head of the merged sorted Singly Linked List.

    Time Complexity Requirement:
    - O(n * log(k)), where k is the number of input Linked Lists (i.e. the length of the outer list), 
    and n is the total number of nodes across all lists.

    Space Complexity Requirement:
    - At most O(k), where k is the number of input Linked Lists (i.e. the length of the outer list).

    For testing, you may convert list[int] to a ListNode (Singly Linked List) using the arr_to_listnode method.
    """
    heap = []
    for i,j in enumerate(lists):
        if(j is not None):
            heapq.heappush(heap,(j.val,i))
    
    dummy = ListNode(-1)
    head = dummy
    while len(heap) != 0:
        term, index = heapq.heappop(heap)
        head.next = lists[index]
        lists[index] = lists[index].next
        head = head.next
        if lists[index] is not None:
            heapq.heappush(heap,(head.next.val,index))
            
    return dummy.next
      
            
    #Maybe using some form of recursion?

def ll_modes(nums_list: ListNode) -> set[int]:
    """
    Computes the mode (or modes, in case of ties) of a sorted Singly Linked List.

    Args:
    - nums_list (ListNode): The head of the sorted Singly Linked List.

    Returns:
    - set[int]: A set containing all modes of the linked list.

    For testing, you may convert list[int] to a ListNode (Singly Linked List) using the arr_to_listnode method.
    """
    storage = dict()
    frequency = 0
    current = nums_list 
    if(current == None):
        return set()
    mode = set()
      
    while current != None: 
        storage[current.val] = storage.get(current.val, 0) + 1
        if(frequency < storage[current.val]):
            frequency = storage[current.val]
        current = current.next

    current = nums_list 
    while current != None: 
        if storage[current.val] == frequency: 
            mode.add(current.val)
        current = current.next
    print(mode)
    return mode 

def bst_modes(root: TreeNode) -> set[int]:
    """
    Computes the mode (or modes, in case of ties) of a Binary Search Tree (BST).

    Args:
    - root (TreeNode): The root of the Binary Search Tree.

    Returns:
    - set[int]: A set containing all modes of the BST.

    Time Complexity Requirement:
    - O(n), where n is the total number of nodes in the BST.

    Space Complexity Requirement:
    - O(n), where n is the total number of nodes in the BST.

    For testing, you may convert list[int] to a TreeNode using the arr_to_bst method.
    """
    if root == None:
        return set()
    def tree_traversal(root: TreeNode):
        tree_list = []
        if root:
                tree_list = tree_traversal(root.left)
                tree_list.append(root.val)
                tree_list += tree_traversal(root.right)
        return tree_list
    
    tree = tree_traversal(root)
    tree.append(None)
    curr_streak = 0
    curr_element = None
    max_streak = -1
    max_elt = []
    curr = 0
    for elt in tree:
        curr = elt
        if curr is not curr_element:
            if(curr_streak > max_streak):
                max_streak = curr_streak
                if(curr_element != None):
                    max_elt.clear()
                    max_elt.append(curr_element)
            elif(curr_streak == max_streak):
                max_streak = curr_streak
                if(curr_element != None):
                    max_elt.append(curr_element)
            curr_element = curr
            curr_streak = 1
        else:
            curr_element = curr
            curr_streak+=1
            max_elt = max_elt
    return set(max_elt)
    
            



    





        
    

