# Tree Data Structure Merger and Converter

## Project Overview
This project implements sophisticated tree data structure algorithms for converting between different tree representations and merging multiple trees. It demonstrates advanced understanding of tree algorithms, recursion, and data structure manipulation in Python.

## Technical Skills Demonstrated

### Data Structures & Algorithms
- **Tree Representations**: Multiple tree formats and conversions
- **Tree Traversal**: DFS, BFS, and custom traversal strategies
- **Tree Merging**: Combining multiple trees with conflict resolution
- **Recursion**: Complex recursive algorithms
- **Object-Oriented Design**: Clean class hierarchy

### Algorithm Design
- **Conversion Algorithms**: Transforming between representations
- **Merge Strategies**: Handling overlapping nodes and conflicts
- **Tree Comparison**: Structural and value-based comparison
- **Optimization**: Efficient tree operations

## Project Structure
```
├── imp_hw6.py          # Main implementation file
├── classes.py          # Tree class definitions and data structures
├── convert.py          # Conversion utilities between tree formats
├── test_hw6.py         # Comprehensive test suite
├── ans_hw6.pdf         # Answer document with analysis
└── metadata.yml        # Project metadata
```

## Key Features

### 1. Multiple Tree Representations

**Nested List Format**
```python
# [value, [left_child], [right_child]]
tree1 = [5, [3, None, None], [7, None, None]]
```

**Dictionary Format**
```python
# {'value': val, 'left': node, 'right': node}
tree2 = {
    'value': 5,
    'left': {'value': 3, 'left': None, 'right': None},
    'right': {'value': 7, 'left': None, 'right': None}
}
```

**Object Format**
```python
class TreeNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
```

### 2. Tree Conversion Operations
- **List to Dict**: Convert nested list representation to dictionary
- **Dict to Object**: Create node objects from dictionary
- **Object to List**: Serialize tree objects to lists
- **Any to Any**: Universal conversion between formats

### 3. Tree Merging Algorithm
Merge multiple trees with strategies:
- **Union**: Combine all nodes from all trees
- **Intersection**: Keep only common nodes
- **Priority**: Resolve conflicts by tree priority
- **Custom**: User-defined merge logic

### 4. Tree Operations
- **Insertion**: Add nodes maintaining structure
- **Deletion**: Remove nodes with child promotion
- **Search**: Find nodes by value or predicate
- **Traversal**: Inorder, preorder, postorder
- **Height**: Calculate tree depth
- **Balance**: Check and rebalance trees

## Technical Implementation

### Tree Class Definition
```python
class TreeNode:
    """Binary tree node with value and children."""
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f"TreeNode({self.value})"
    
    def is_leaf(self):
        return self.left is None and self.right is None
```

### Conversion: List to Tree Object
```python
def list_to_tree(lst):
    """Convert nested list to TreeNode objects."""
    if lst is None:
        return None
    
    value = lst[0]
    left = list_to_tree(lst[1]) if len(lst) > 1 else None
    right = list_to_tree(lst[2]) if len(lst) > 2 else None
    
    return TreeNode(value, left, right)
```

### Conversion: Tree to Dictionary
```python
def tree_to_dict(node):
    """Convert TreeNode to dictionary representation."""
    if node is None:
        return None
    
    return {
        'value': node.value,
        'left': tree_to_dict(node.left),
        'right': tree_to_dict(node.right)
    }
```

### Tree Merging Algorithm
```python
def merge_trees(tree1, tree2, strategy='sum'):
    """
    Merge two trees with specified strategy.
    
    Strategies:
    - 'sum': Add values when nodes overlap
    - 'first': Keep first tree's value
    - 'second': Keep second tree's value
    - 'max': Keep maximum value
    """
    if tree1 is None and tree2 is None:
        return None
    
    if tree1 is None:
        return copy_tree(tree2)
    
    if tree2 is None:
        return copy_tree(tree1)
    
    # Both nodes exist - merge based on strategy
    if strategy == 'sum':
        merged_value = tree1.value + tree2.value
    elif strategy == 'max':
        merged_value = max(tree1.value, tree2.value)
    else:
        merged_value = tree1.value  # Default to first
    
    # Recursively merge children
    merged = TreeNode(merged_value)
    merged.left = merge_trees(tree1.left, tree2.left, strategy)
    merged.right = merge_trees(tree1.right, tree2.right, strategy)
    
    return merged
```

### Tree Comparison
```python
def trees_equal(tree1, tree2):
    """Check if two trees are structurally identical."""
    if tree1 is None and tree2 is None:
        return True
    
    if tree1 is None or tree2 is None:
        return False
    
    return (tree1.value == tree2.value and
            trees_equal(tree1.left, tree2.left) and
            trees_equal(tree1.right, tree2.right))
```

### Tree Traversals
```python
def inorder_traversal(node, result=None):
    """Left -> Root -> Right"""
    if result is None:
        result = []
    
    if node is not None:
        inorder_traversal(node.left, result)
        result.append(node.value)
        inorder_traversal(node.right, result)
    
    return result

def preorder_traversal(node, result=None):
    """Root -> Left -> Right"""
    if result is None:
        result = []
    
    if node is not None:
        result.append(node.value)
        preorder_traversal(node.left, result)
        preorder_traversal(node.right, result)
    
    return result

def postorder_traversal(node, result=None):
    """Left -> Right -> Root"""
    if result is None:
        result = []
    
    if node is not None:
        postorder_traversal(node.left, result)
        postorder_traversal(node.right, result)
        result.append(node.value)
    
    return result
```

### Tree Utilities
```python
def tree_height(node):
    """Calculate height of tree."""
    if node is None:
        return 0
    return 1 + max(tree_height(node.left), tree_height(node.right))

def count_nodes(node):
    """Count total nodes in tree."""
    if node is None:
        return 0
    return 1 + count_nodes(node.left) + count_nodes(node.right)

def count_leaves(node):
    """Count leaf nodes."""
    if node is None:
        return 0
    if node.is_leaf():
        return 1
    return count_leaves(node.left) + count_leaves(node.right)

def is_balanced(node):
    """Check if tree is height-balanced."""
    def check_balance(node):
        if node is None:
            return 0, True
        
        left_height, left_balanced = check_balance(node.left)
        right_height, right_balanced = check_balance(node.right)
        
        balanced = (left_balanced and right_balanced and
                   abs(left_height - right_height) <= 1)
        
        return max(left_height, right_height) + 1, balanced
    
    _, balanced = check_balance(node)
    return balanced
```

## Technical Environment
- **Language**: Python 3.x
- **Paradigm**: Object-Oriented Programming
- **Testing**: pytest or unittest
- **Type Hints**: Optional static typing

## Skills & Technologies
- **Python Programming**: Advanced OOP and recursion
- **Data Structures**: Trees, graphs, recursive structures
- **Algorithm Design**: Conversion, merging, traversal
- **Recursion**: Complex recursive thinking
- **Testing**: Comprehensive test coverage
- **Design Patterns**: Visitor pattern, factory pattern

## Algorithmic Complexity

### Time Complexity
| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Conversion | O(n) | Visit each node once |
| Merge | O(n + m) | n, m = nodes in trees |
| Traversal | O(n) | Visit each node |
| Height | O(n) | Visit all nodes |
| Search | O(n) | Worst case (unbalanced) |
| Search (BST) | O(log n) | If balanced BST |

### Space Complexity
| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Recursion | O(h) | h = tree height |
| Conversion | O(n) | New tree created |
| Merge | O(n + m) | New merged tree |

## Use Cases & Applications

### Data Structure Libraries
- Implementing tree utilities
- Format conversion tools
- Tree serialization/deserialization

### Compiler Design
- Abstract Syntax Trees (AST)
- Parse trees
- Expression evaluation trees

### File Systems
- Directory structure representation
- File hierarchy merging
- Conflict resolution

### Database Systems
- B-trees and B+ trees
- Index structures
- Query optimization trees

### Machine Learning
- Decision trees
- Random forests
- Tree ensemble methods

### XML/HTML Processing
- DOM tree manipulation
- XML merging
- Document structure analysis

## Advanced Features

### 1. Generic Tree Types
Support for n-ary trees (not just binary):
```python
class NaryTreeNode:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children else []
```

### 2. Tree Serialization
```python
def serialize(node):
    """Serialize tree to string."""
    if node is None:
        return "null"
    
    return f"{node.value},{serialize(node.left)},{serialize(node.right)}"

def deserialize(data):
    """Deserialize string to tree."""
    def parse(values):
        val = next(values)
        if val == "null":
            return None
        node = TreeNode(int(val))
        node.left = parse(values)
        node.right = parse(values)
        return node
    
    return parse(iter(data.split(',')))
```

### 3. Tree Visualization
```python
def print_tree(node, prefix="", is_left=True):
    """Pretty print tree structure."""
    if node is None:
        return
    
    print(prefix + ("|-- " if is_left else "`-- ") + str(node.value))
    
    if node.left or node.right:
        if node.left:
            print_tree(node.left, prefix + ("|   " if is_left else "    "), True)
        if node.right:
            print_tree(node.right, prefix + ("|   " if is_left else "    "), False)
```

## Testing Strategy
Comprehensive tests covering:
- **Correctness**: All operations produce correct results
- **Edge Cases**: Empty trees, single nodes, large trees
- **Equivalence**: Different representations yield same results
- **Performance**: Large tree handling
- **Error Handling**: Invalid inputs, malformed trees

## Learning Outcomes
This project demonstrates:
- Mastery of tree data structures
- Advanced recursion techniques
- Algorithm design and analysis
- Object-oriented programming
- Software testing practices
- Data structure conversions

## Real-World Impact
Tree algorithms are fundamental to:
- **Compilers**: AST manipulation
- **Databases**: Index structures
- **AI**: Decision trees, game trees
- **Graphics**: Scene graphs, BSP trees
- **Networks**: Spanning trees, routing
- **Biology**: Phylogenetic trees

## Design Patterns

### Visitor Pattern
```python
class TreeVisitor:
    def visit(self, node):
        if node is None:
            return
        self.visit_node(node)
        self.visit(node.left)
        self.visit(node.right)
    
    def visit_node(self, node):
        raise NotImplementedError
```

### Iterator Pattern
```python
class TreeIterator:
    def __init__(self, root):
        self.stack = []
        self._push_left(root)
    
    def _push_left(self, node):
        while node:
            self.stack.append(node)
            node = node.left
    
    def __next__(self):
        if not self.stack:
            raise StopIteration
        
        node = self.stack.pop()
        if node.right:
            self._push_left(node.right)
        
        return node.value
```

## Optimization Techniques
- **Memoization**: Cache repeated subtree results
- **Tail Recursion**: Convert to iterative where possible
- **Lazy Evaluation**: Delay computation until needed
- **Path Copying**: Persistent data structures

## Future Enhancements
- **Self-Balancing Trees**: AVL, Red-Black
- **Threaded Trees**: Inorder threading
- **Persistent Trees**: Immutable versions
- **Parallel Algorithms**: Concurrent tree operations
- **GPU Acceleration**: Parallel traversals

