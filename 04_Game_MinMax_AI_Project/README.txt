Instructions:
In Referee.re line 42, type the board size manually. For example:
  CurrentGame.initialState("5 7")
will create a board with 5 rows and 7 columns. Use two numbers separated by 
a space. After the game starts, simply enter in the row number that you want 
to place your checker in as a solo integer, regardless of whether 
you are playing against another human or the AI.


How the program functions: 
  initialState
    The very first thing that gets called is initialState(), who creates
    the first state for the game. It calls parseBoardDims(), a function 
    involving string operations, to parse the board dimensions that users 
    input, then pass that info to buildMatrix(). buildMatrix() then 
    builds a zero matrix with the exact dimensions.
  
  stringOfState
    When a state is "established", stringOfState() gets called to visualize
    that state in terminal. stringOfState() calls stringOfBoard(), a helper,
    to print the board matrix. Our board matrix is a matrix consisting of 
    0, 1, and -1. 0 indicates an empty spot, 1 indicates Player 1's checker, 
    and -1 indicates Player 2's checker. Knowing this, essentially what 
    stringOfBoard() does is that it turns every 1 in the matrix to " 1 ",
    every -1 to " 2 ", and every 0 to " _ ". Additionally, it also 
    formats these string pieces by "|" and "\n" so the board gets printed 
    out in a tidy manner.
  
  legalMoves
    Before receiving the user input, the game checks if that move is legal. So 
    it calls legalMoves() to generate a list of legal moves based on 
    the current game state. Based on our knowledge about how Connect4 
    is played, we know that a player can place a checker to a column 
    as long as that column is not fully occupied. That means, if the "top 
    row" of the board is unoccupied, then the move is legal. Note that
    we chose to keep the actual board in the reverse order in matrix form,
    so the "top row" that users see is actually the bottom row of the 
    matrix. So legalMoves() just checks if any of the spots in the bottom 
    row is occupied or not. The matrix entry should be 0 if it is unoccupied.

  moveOfString
    After seeing the board, the player starts to make their move. They 
    type a solo integer in the terminal, and moveOfString() converts that 
    input into a move (which is essentially an int) after checking that 
    the move is indeed in the list of legal moves given by legalMoves().
  
  nextState
    Now that the user's made their move, the game calculates its state 
    by calling nextState(). nextState() does several things. First, it modifies
    the board matrix according to the player's move. Then, it calls 
    estimateValue() to check how good this new board matrix is for a player.
    As we'll introduce later, estimateValue() outputs a float value 
    ranging from -200. to +200.. If nextState() sees a -200., then it 
    updates the next state as "P2 wins". If it sees a +200., then 
    "P1 wins". It should be emphasized that how it checks for a draw is 
    totally different (due to how we designed estimateValue). Instead of 
    calling estimateValue(), it calls legalMoves(), and if there is 
    no legal move available, we say there's a draw.
  
  estimateValue
    What's our motivation to design estimateValue in the first place?
    Well, 
    to win Connect4, you have to have 4 checkers in a line. If a player 
    has a 4, then that's extremely good for them. If a player has a 3,
    then it's quite good for them. If a player has a 2, then not so bad,
    etc. So estimateValue's output depends on the maximum number of 
    checkers in a line.

    We also notice that if we have something like "| _ 1 2 2 _ _ _ |"
    on the game board, that two 2s in a row is not that "threatening" 
    compared to "| _ _ 2 2 _ _ _ |". So somehow, that " 1 " cancels 
    something out.

    We chose to store these checkers using 1 and -1 coincidentally. Then,
    "how threatening" or "how good" the situation is can be calculated 
    by "summing up" the checkers. This idea led us to using convolution.

    Suppose we have a 2d board matrix. And we have the following matrices 
    defined:
      /* checker patterns in matrix form */
      let _leftDiagonal: matrix = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
      ];
      let _rightDiagonal: matrix = [
        [0, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [1, 0, 0, 0],
      ];
      let _horizontal: matrix = [[1, 1, 1, 1]];
      let _vertical: matrix = [[1], [1], [1], [1]];
    Then, we calculate the convolution between the board matrix and 
    these 4 matrices, obtaining 4 smaller matrices, each one 
    representing "how many checkers lined up" locally. Suppose 
    we see a 4 in any of these smaller matrices, then "P1 wins", because 
    that means locally we have four " 1 " checkers in a line. At this point,
    our estimateValue seems promising enough that it'll prompt the AI to 
    make good moves. However, it doesn't quite catch several important
    intricacies of the game. Consider the following game board:
      "| _ _ 1 1 _ _ 2 2 _ _ |"
    "How good is this for Player 1 or Player 2," you might ask. Well it 
    actually depends on whose turn it is. If it's P1's turn, then 
    it's very good for P1, because they can make the move at column 2,
    and there's no way to stop them from winning. On the other hand,
    if it's P2's turn, then it's very bad for P1, for the same reason as 
    stated above. This led to the idea that we need to have some kind of 
    weight mapping that is asymmetric. For P1, we have:
        List.map(
          i => 
            switch (i) {
            | 4 => 200.; 
            | 3 => 100.; 
            | 2 => 60.; 
            | 1 => 0.5;
            | 0 => 0.0;
            | -1 => -0.2;
            | -2 => -50.;
            | -3 => -90.;
            | -4 => -200.;
            | _ => failwith("Unrecognized convolution pattern")
            },
          allConv
        );
    where all 1, 2, and 3 has weights slightly larger than -1, -2, and -3.
    The same thing happens for P2, but with a negative sign.

    Finally, we concat the 4 smaller matrices, apply the weighing,
    and then add up the minimum value and the maximum value. We need to 
    do this because a player would always pay attention to what 
    their opponent is doing. Note that if we detect a +200. or -200.,
    then we use that value as the output immediately, because when 
    one has won, it doesn't matter "how good that win exactly is".
  
  AIPlayer
    We use alphabeta pruning to make our AI run faster and search deeper.
    Each time AIPlayer.nextMove() is called, it calls Connect4.legalMoves()
    to obtain a list of possible moves, then for each move, it calls 
    Connect4.nextState() to get the next possible state. The process repeats 
    for several times until it reaches the depth limit, where it calls 
    Connect4.estimateValue(), or it reaches a win/lose/draw terminal state.
    It uses alphabeta pruning and finds its best move. 

    Actually, we've done something a bit different. Usual alphabeta pruning 
    is just a means to make minimax more efficient and does not *modify* 
    any values during the upward propagation. Here, we manually make 
    it multiply the node value by 0.9 per propagation, so nodes from 
    the very deep of the tree are valued less good. We did this because 
    even the AI might find a way out, we want it to take less risk i.e. 
    follow shorter paths down the tree to a winning node where possible.
    In fact, without this 0.9 multiplication, the AI would often value 
    many moves as "equally good", though some wins may take more steps to reach.
    This step gives him some preference over it.

Potential Bugs/Problems: 
After many rounds of testing with another player and with the AI, we 
seem to have found no potential bugs or issues with the program's functionality.

List of Collaborators: 
Outside of our partnership, no one.

Extra Features: 
The AI now can express how he "feels" (i.e. how good the game state is for him) 
through some nice and cute emojis!