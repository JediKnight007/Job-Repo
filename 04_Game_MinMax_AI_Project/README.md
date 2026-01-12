# Connect 4 Game with MinMax AI (ReasonML)

## Project Overview
This project implements a sophisticated Connect 4 game with an intelligent AI opponent using the minimax algorithm with alpha-beta pruning. Built in ReasonML (OCaml), it features an advanced evaluation function using convolution-based board analysis and optimized search tree pruning.

## Technical Skills Demonstrated

### Artificial Intelligence
- **Minimax Algorithm**: Optimal game-tree search for two-player games
- **Alpha-Beta Pruning**: Optimization technique reducing search space by ~50%
- **Heuristic Evaluation**: Custom board evaluation using convolution
- **Game Tree Search**: Depth-limited search with value propagation

### Advanced Techniques
- **Convolution-Based Analysis**: Using 2D convolution to detect winning patterns
- **Asymmetric Weight Mapping**: Different evaluation weights based on game state
- **Risk Minimization**: 0.9 decay factor favoring shorter winning paths
- **Pattern Recognition**: Detecting horizontal, vertical, and diagonal patterns

## Project Structure
```
├── Connect4.re          # Core game logic and state management
├── Game.re              # Game interface and abstract definitions
├── AIPlayer.re          # AI implementation with minimax + alpha-beta
├── HumanPlayer.re       # Human player interface
├── Player.re            # Player interface definition
├── Referee.re           # Game orchestration and flow control
├── CS17SetupGame.re     # Game initialization
├── README.txt           # Comprehensive documentation
└── metadata.yml         # Project metadata
```

## Key Features

### 1. Intelligent AI with Multiple Strategies
- **Alpha-Beta Pruning**: Efficient search tree traversal
- **Configurable Search Depth**: Adjustable difficulty levels
- **Value Decay**: 0.9 multiplication per level to prefer shorter wins
- **Emotional Feedback**: AI expresses "feelings" through emojis based on board evaluation

### 2. Advanced Board Evaluation (estimateValue)
The evaluation function uses **2D convolution** to analyze board patterns:

```reasonml
Convolution Kernels:
- Horizontal:     [1, 1, 1, 1]
- Vertical:       [[1], [1], [1], [1]]
- Left Diagonal:  [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]
- Right Diagonal: [[0,0,0,1], [0,0,1,0], [0,1,0,0], [1,0,0,0]]
```

### 3. Asymmetric Weight Mapping (Player 1)
```
4 in a row:    +200  (Win)
3 in a row:    +100  (Very good)
2 in a row:    +60   (Good)
1 piece:       +0.5  (Neutral)
-1 opponent:   -0.2  (Slightly bad)
-2 opponents:  -50   (Bad)
-3 opponents:  -90   (Very bad)
-4 opponents:  -200  (Loss)
```

### 4. Turn-Aware Evaluation
The evaluation considers whose turn it is - having three in a row is much more valuable on your turn (imminent winning move) than on opponent's turn.

### 5. Game Features
- **Customizable Board Size**: User-defined rows and columns
- **Legal Move Validation**: Ensures only valid moves are accepted
- **Win Detection**: Automatic detection of 4-in-a-row patterns
- **Draw Handling**: Detects when board is full
- **State Visualization**: Clean board representation in terminal

## Technical Implementation

### Game State Management
```reasonml
type state = {
  board: matrix,      // 2D matrix (0=empty, 1=P1, -1=P2)
  currentPlayer: int, // 1 or -1
  status: gameStatus  // InProgress | P1Win | P2Win | Draw
};
```

### Minimax with Alpha-Beta Pruning
```
function alphabeta(state, depth, alpha, beta, maximizing):
    if depth == 0 or game_over:
        return evaluate(state)
    
    if maximizing:
        for each legal move:
            value = alphabeta(next_state, depth-1, alpha, beta, false)
            alpha = max(alpha, value * 0.9)  // Value decay
            if alpha >= beta:
                break  // Prune
        return alpha
    else:
        // Similar for minimizing player
```

### Convolution-Based Pattern Detection
The system convolves the board matrix with pattern kernels to detect:
- Immediate wins (4 in a row)
- Threats (3 in a row with space)
- Potential developments (2 in a row)
- Blocking requirements

## Technical Environment
- **Language**: ReasonML (OCaml syntax)
- **Paradigm**: Functional Programming
- **Type System**: Strong static typing
- **Build System**: dune/esy

## Skills & Technologies
- **ReasonML/OCaml**: Advanced functional programming
- **Game Theory**: Understanding of minimax and game trees
- **Algorithm Optimization**: Alpha-beta pruning implementation
- **Pattern Matching**: Functional pattern matching for game logic
- **Recursion**: Deep recursive tree search
- **Linear Algebra**: Matrix operations and convolution
- **Type-Safe Programming**: Leveraging strong type systems

## Algorithmic Complexity
- **Without Pruning**: O(b^d) where b=7 (avg branches), d=depth
- **With Alpha-Beta**: O(b^(d/2)) in best case
- **Memory**: O(d) stack depth for recursion

## AI Difficulty Levels
Adjustable by changing search depth:
- Depth 1-2: Beginner (reactive)
- Depth 3-4: Intermediate (tactical)
- Depth 5-7: Advanced (strategic)
- Depth 8+: Expert (very slow but nearly optimal)

## Game Flow
1. **Initialize**: User specifies board dimensions
2. **Display**: Board state rendered in terminal
3. **Legal Moves**: Generate valid moves (non-full columns)
4. **Input**: Player enters column number
5. **Validation**: Check move legality
6. **Update**: Apply move and update board
7. **Evaluate**: Check for win/draw using convolution
8. **AI Turn**: Minimax selects optimal move
9. **Repeat**: Continue until game ends

## Innovative Features

### 1. Convolution for Game AI
Using computer vision techniques (convolution) for board game analysis is a creative approach that:
- Efficiently detects all patterns in O(n²) time
- Naturally handles diagonal patterns
- Scales to different board sizes
- Provides smooth evaluation gradients

### 2. Value Decay (0.9 Factor)
Multiplying evaluation by 0.9 per level makes AI prefer:
- Faster wins over delayed wins
- Immediate threat blocking
- Lower-risk strategies
- More aggressive play

### 3. Emotional AI
AI displays emojis based on board evaluation, making the game more engaging and providing insight into AI's "thought process".

## Learning Outcomes
This project demonstrates:
- Advanced AI algorithm implementation
- Functional programming mastery
- Game theory understanding
- Optimization techniques (pruning)
- Creative problem-solving (convolution approach)
- Type-safe software design

## Real-World Applications
- **Game Development**: Implementing AI opponents
- **Decision Making**: Tree search for optimal decisions
- **Robotics**: Path planning and decision trees
- **Automated Trading**: Minimax for adversarial scenarios
- **Theorem Proving**: Search-based proof finding

## Potential Enhancements
- Iterative deepening for time-bounded moves
- Transposition tables for memoization
- Opening book for first moves
- Neural network evaluation function
- Monte Carlo Tree Search (MCTS) alternative

## Testing Results
After extensive testing:
- No bugs found in game logic
- AI plays competitively at depth 5+
- Handles all board sizes correctly
- Proper win/draw detection
- Clean error handling

