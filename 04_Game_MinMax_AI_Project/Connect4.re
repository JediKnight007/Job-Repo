open CS17SetupGame;   
open Game; 


module Connect4 = {

    /* player 1 is P1, player 2 is P2 */
    type whichPlayer =
      | P1
      | P2;

    /* either a player has won, it's a draw, or it's ongoing */
    type status =
      | Win(whichPlayer)
      | Draw
      | Ongoing(whichPlayer);
    
    type matrix = list(list(int));
    /* A matrix is a list of list of ints.
     * 
     * The game board can be represented as a matrix consisting of
     * only 1s, -1s, and 0s. where 1s represent P1's checkers, 
     * -1s represent P2's checkers, and 0s represent empty spots.
     * The top row of the game board matrix is the bottom row of 
     * the board when printed out.
     * 
     * Every entry in a matrix has index (row, column), and the top
     * left entry of the matrix is said to have index (0, 0).
     * 
     * Examples:
     * [[1, 0, 0, 0],
     *  [0, 1, 0, 0],
     *  [0, 0, 1, 0]
     *  [1, 0, 0, 0]]
     * 
     * [[1, -1, 0, 0, 0],
     *  [0, 1, 0, 0, 0],
     *  [0, 0, 0, 0, 0],
     *  [0, 0, 0, 0, 0]]
     */
    
    /* whose turn it is (status), and params describing the board */
    type state = 
    | State(status, matrix);
    
    type move = int;
    /* A move denotes which column for the checker to be placed on.
     * It's an integer starting from 0, because we say the first 
     * element in a matrix has index (0, 0). 
     */
    


    /* accessIndexList: (list('a), int) => 'a
     * input: lst, a list of data
     *        id, the desired index of a piece of data in the list.
     *        The index starts from 0.
     * output: the id-th data piece in the list. failwith if 
     *         id doesn't exist.
     * 
     * Recursion diagram
     * OI: ([1, 2, 3], 1)
     *   RI: ([2, 3], 0)
     *   RO: 2
     *   Ideation: when id == 0, return the head
     * OO: 2
     */
    let rec accessIndexList: (list('a), int) => 'a = 
      (lst, id) =>
        switch (lst, id) {
        | ([], _) => failwith("Index out of range.")
        | ([hd, ..._tl], 0) => hd
        | ([_hd, ...tl], n) => accessIndexList(tl, (n - 1))
        };
    
    /* accessIndexMatrix: (matrix, (int, int)) => int
     * input: mt, a matrix
     *        (row, col), an int tuple describing the position of entries.
     *        The top left entry has index (0, 0).
     * output: the entry on row-th row and col-th column.
     * 
     * Ideation: access the target column, from which extract the n-th item 
     */
    let accessIndexMatrix: (matrix, (int, int)) => int = 
      (mt, (row, col)) =>
        accessIndexList(accessIndexList(mt, row), col);
    
    /* changeListByIndex: (list(int), int, int) => list(int)
     * input: lst, a list of ints
     *        i, an int describing the target index. Indices start from 0.
     *        v, a new int value to be put into lst
     * output: a new list of ints where the i-th element is replaced by v,
     *         everywhere else unchanged
     * 
     * Recursion diagram
     * OI: ([1, 2, 3], 1, 3)
     *   RI: ([2, 3], 0, 3)
     *   RO: [3, 3]
     *   Ideation: when id == 0, cons the new value to the tail
     * OO: [1, 3, 3]
     */
    let rec changeListByIndex: (list(int), int, int) => list(int) =
      (lst, i, v) =>
        switch (lst, i) {
        | ([_hd, ...tl], 0) => [v, ...tl]
        | ([hd, ...tl], _) => [hd, ...changeListByIndex(tl, i-1, v)]
        | _ => failwith("Index out of range, unable to modify the given list")
        };

    /* changeMatrixByIndex: (matrix, (int, int), int) => matrix
     * input: mt, a matrix
     *        (i, j), an int tuple describing the index of target entry.
     *        The top left entry has index (0, 0)
     *        v, a new int value to be put into mt
     * output: a new matrix where the entry on i-th row and j-th column is 
     *         replaced by v, everywhere else unchanged.
     * 
     * Recursion diagram:
     * OI: ([[1, 2], [3, 4]], (1, 0), 4)
     *   RI: ([[3, 4]], (0, 0), 4)
     *   RO: [[4, 4]]
     *   Ideation: got target row when the second argument is (0, _), 
     *             then call changeListByIndex
     * OO: [[1, 2], [4, 4]]
     */
    let rec changeMatrixByIndex: (matrix, (int, int), int) => matrix = 
      (mt, (i, j), v) =>
        switch (mt, i, j) {
        | ([hdr, ...tlr], 0, _) => 
          [changeListByIndex(hdr, j, v), ...tlr]
        | ([hdr, ...tlr], _, _) =>
          [hdr, ...changeMatrixByIndex(tlr, (i-1, j), v)]
        | _ => failwith("Index out of range, unable to modify the given matrix")
        };

    /* convolution part */
    /* matrixRowLength: matrix => int
     * input: a matrix
     * output: the number of rows of the matrix
     */
    let matrixRowLength: matrix => int = m => List.length(m);

    /* matrixColumnLength: matrix => int
     * input: a matrix
     * output: the number of columns of the matrix
     */
    let matrixColumnLength: matrix => int =
      m =>
        switch (m) {
        | [hd, ..._tl] => List.length(hd)
        | [] => 0
        };

    /* fast convolution designed specifically for this game */
    /* conv2dFastLeftDiagonal: matrix => matrix
     * input: m, a matrix
     * output: the convolution of m and a 4x4 left diagonal matrix, 
     *         defined as 
     *         [[1, 0, 0, 0],
     *          [0, 1, 0, 0],
     *          [0, 0, 1, 0],
     *          [0, 0, 0, 1]]
     * 
     * Note:
     * No multiplication of any form is involved in this procedure.
     * It is done by pure index-based operations, because all the kernals
     * involved consist of only zeros and ones.
     * No padding of any form is involved, because what's on the board
     * is the only concern.
     * 
     * Ideation:
     * Consider a helper conv2dHorizontal. The helper sticks the kernal
     * to the top of the matrix so the "upper boundaries" of both matrices
     * overlap. conv2dHorizontal also accepts an additional integer argument,
     * which tells it where, horizontally, should the kernal be placed on.
     * Passing 0 would make it put the kernal on the top left of the matrix.
     * Each time, conv2dHorizontal calculates the dot product between the
     * matrix and the kernal, then call it self on the same matrix but with
     * the second argument added 1, so effectively the kernal moves rightward.
     * 
     * conv2dHorizontal processes the "top most possible" row per call (
     * this row is not necessarily the first row of the matrix due to we
     * have no padding.) So conv2dFastLeftDiagonal call it multiple times 
     * recursively on List.tl(the matrix) for all of it to be processed.
     */
    let rec conv2dFastLeftDiagonal: matrix => matrix = 
      m => {
        let rec conv2dHorizontal: (matrix, int) => list(int) = 
          (m, s) =>
            /* s denotes which column the kernal is currently at */
            switch (matrixColumnLength(m) > s + 3) {
            | true =>  /* changes in the index reflect the leftDiagonal matrix */
              let thisSum = accessIndexMatrix(m, (0, s)) 
                          + accessIndexMatrix(m, (1, s+1))
                          + accessIndexMatrix(m, (2, s+2)) 
                          + accessIndexMatrix(m, (3, s+3));
              [thisSum, ...conv2dHorizontal(m, s + 1)]
            /* add this result to list, then move the kernal rightward */
            | false => []
            };
        switch (matrixRowLength(m) >= 4) {
        | true => [conv2dHorizontal(m, 0),...conv2dFastLeftDiagonal(List.tl(m))]
                  /* after finishing this row, move the kernal down */
        | false => []
        };
      };

    /* conv2dFastRightDiagonal: matrix => matrix
     * input: m, a matrix
     * output: the convolution of m and a 4x4 right diagonal matrix, 
     *         defined as 
     *         [[0, 0, 0, 1],
     *          [0, 0, 1, 0],
     *          [0, 1, 0, 0],
     *          [1, 0, 0, 0]]
     * Note: same as conv2dFastLeftDiagonal.
     */
    let rec conv2dFastRightDiagonal: matrix => matrix = 
      m => {
        let rec conv2dHorizontal: (matrix, int) => list(int) = 
          (m, s) =>
            /* s denotes which column the kernal is currently at */
            switch (matrixColumnLength(m) > s + 3) {
            | true => /* changes in the index reflect the rightDiagonal matrix */
              let thisSum = accessIndexMatrix(m, (0, s+3)) 
                          + accessIndexMatrix(m, (1, s+2))
                          + accessIndexMatrix(m, (2, s+1)) 
                          + accessIndexMatrix(m, (3, s));
              [thisSum, ...conv2dHorizontal(m, s+1)]
            /* move rightward */
            | false => []
            };

        switch (matrixRowLength(m) >= 4) {
        | true => [conv2dHorizontal(m, 0),...conv2dFastRightDiagonal(List.tl(m))]
                  /* move the kernal down */
        | false => []
        };
      };

    /* conv2dFastVertical: matrix => matrix
     * input: m, a matrix
     * output: the convolution of m and a 4x1 matrix filled with ones, 
     *         defined as 
     *         [[1],
     *          [1],
     *          [1],
     *          [1]]
     * Note: same as conv2dFastLeftDiagonal.
     */
    let rec conv2dFastVertical: matrix => matrix = 
      m => {
        let rec conv2dHorizontal: (matrix, int) => list(int) = 
          (m, s) =>
            /* s denotes which column the kernal is currently at */
            switch (matrixColumnLength(m) > s) {
            | true => /* changes in the index reflect the vertical matrix */
              let thisSum = accessIndexMatrix(m, (0, s)) 
                          + accessIndexMatrix(m, (1, s))
                          + accessIndexMatrix(m, (2, s)) 
                          + accessIndexMatrix(m, (3, s));
              [thisSum, ...conv2dHorizontal(m, s+1)]
            /* move the kernal rightward */
            | _ => []
            };

        switch (matrixRowLength(m)) {
        | a when a < 4 => []
        | _ => [conv2dHorizontal(m, 0),...conv2dFastVertical(List.tl(m))]
               /* move the kernal down */
        };
      };

    /* conv2dFastHorizontal: matrix => matrix
     * input: m, a matrix
     * output: the convolution of m and a 1x4 matrix filled with ones, 
     *         defined as 
     *         [[1, 1, 1, 1]]
     * Note: same as conv2dFastLeftDiagonal.
     */
    let rec conv2dFastHorizontal: matrix => matrix = 
      m => {
        let rec conv2dHorizontal: (matrix, int) => list(int) = 
          (m, s) => 
            /* changes in the index reflect the horizontal matrix */
            switch (matrixColumnLength(m) > s+3) {
            | true => 
              let thisSum = accessIndexMatrix(m, (0, s)) 
                          + accessIndexMatrix(m, (0, s+1))
                          + accessIndexMatrix(m, (0, s+2)) 
                          + accessIndexMatrix(m, (0, s+3));
              [thisSum, ...conv2dHorizontal(m, s+1)]
            /* move rightward */
            | false => []
            };

        switch (matrixRowLength(m) >= 1) {
        | true => [conv2dHorizontal(m, 0),...conv2dFastHorizontal(List.tl(m))]
                  /* move down */
        | false => []
        };
      };
    /* convolution part ends here*/

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


    /* printing functions */
    /* stringOfPlayer: whichPlayer => string
     * input: a player identity of type whichPlayer
     * output: a string representing the same player identity
     */
    let stringOfPlayer: whichPlayer => string = 
      fun
      | P1 => "Player 1"
      | P2 => "Player 2";
    
    /* stringOfList: list(int) => string
     * input: a list of ints consisting of only 1, -1, and 0
     * output: a string where 1 is replaced by " 1 ", -1 is replaced by
     *         " 2 ", 0 is replaced by " _ "
     * 
     * Recursion diagram
     * OI: [1, -1, 0, 0]
     *   RI: [-1, 0, 0]
     *   RO: " 2  _  _ "
     *   Ideation: process the head per call, then recur on the tail
     * OO: " 1  2  _  _ "
     */
    let rec stringOfList: list(int) => string = 
      fun
      | [1, ...tl] => " 1 " ++ stringOfList(tl)
      | [-1, ...tl] => " 2 " ++ stringOfList(tl)
      | [0, ...tl] => " _ " ++ stringOfList(tl)
      | [] => ""
      | _ => failwith("Incompatible data, expecting board as a matrix");

    /* stringOfBoard: matrix => string
     * input: a matrix consisting of only 1, -1, and 0, representing the board
     * output: a string illustrating the board, where 1 looks like " 1 "
     *         (checkers of P1), -1 is represented by " 2 " (checkers of P2),
     *         and 0 now is " _ " (empty place on the board). The left and 
     *         right boundaries are represented by "|".
     * 
     * Recursion diagram
     * OI: [[1, -1], [0, 0]]
     *   RI: [[0, 0]]
     *   RO: "| _  _ |"
     *   Ideation: process the head by calling stringOfList per call, then
     *             recur on the tail
     * OO: "| 1  2 | \n| _  _ |"
     */
    let rec stringOfBoard: matrix => string = 
      m =>
        switch (m) {
        | [] => failwith("Expecting a board with non-zero dimensions")
        | [hd] => "|" ++ stringOfList(hd) ++ "|"
        | [hd, ...tl] => "|" ++ stringOfList(hd) ++ "| \n" ++ stringOfBoard(tl)
        };
    
    /* stringOfState: state => string
     * input: a state
     * output: a ready-to-get-printed string representing the board,
     *         where the top row of the board matrix is printed as 
     *         the bottom of the board users see.
     */
    let stringOfState: state => string = 
      s => {
        let State(_status, board) = s;
        stringOfBoard(List.rev(board)) ++ "\n"
      };

    /* stringOfMove: move => string
     * input: a move
     * output: a string representing the same move
     */
    let stringOfMove: move => string = 
      fun
      | a => string_of_int(a + 1);
    
    /* intListOfString: (string, string) => list(int)
     * input: s, a string consisting of integer numbers separated by
     *           space. For example, "1 2" and "4 10 22".
     * output: a list of ints containing the same numbers in their order
     * 
     * Note: when parsing a user input, always call intListOfString
     *       with "" as the second argument.
     * 
     * Recursion diagram:
     * OI: ("5 6 12", "")
     *   RI: (" 6 12", "5")
     *   RO: [5, 6, 12]
     *   Ideation: if the head is " ", convert the accumulator to int
     * OO: [5, 6, 12]
     */
    let rec intListOfString: (string, string) => list(int) =
      (s, acc) =>
        switch (s) {
        | "" => [int_of_string(acc)] /* if s is "", convert the accumulator */
        | _ =>
          switch (s.[0]) {
          | ' ' => 
            [int_of_string(acc),
              ...intListOfString(String.sub(s, 1, String.length(s) - 1),"")]
            /* if s begins with a space, convert the accumulator, add it
             * to output list, then empty the accumulator, and recur on
             * the result of the input */
          | _ =>
            intListOfString(
              String.sub(s, 1, String.length(s) - 1),
              acc ++ Char.escaped(s.[0]),
            )
            /* if s doesn't begin with a space, string add its first character 
             * to accumulator, then recur on the rest of the input.
             */
          }
         };

    /* listToTuple: list(int) => (int, int)
     * input: a list of ints
     * output: a tuple of the ints in the same order. Raise error if
     *         cannot form a tuple.
     */
    let listToTuple: list(int) => (int, int) =
      fun
      | [a, b] => (a, b)
      | _ => failwith("Invalid input, expecting 2D dimensions");


    /* Game Logic */
    /* parseBoardDims: string => (int, int)
     * input: a user-typed string consisting of two ints separated by a space
     * output: a tuple of ints representing the same input, in its order
     */
    let parseBoardDims: string => (int, int) =
      s => {
        try (listToTuple(intListOfString(s, ""))) {
        | _ =>
          failwith(
            "Invalid input, expecting board dimensions "
            ++ "in the form rows space columns",
          )
        };
      };

    /* getBoardHeight: ((int, int)) => int
     * input: an int tuple where the first number represents the height 
     *        of the board, and the second represents the width
     * output: the height of the board
     */
    let getBoardHeight: ((int, int)) => int = 
      ((a, _b)) => a;
    
    /* getBoardWidth: ((int, int)) => int
     * input: an int tuple where the first number represents the height
     *        of the board, and the second represents the width
     * output: the width of the board
     */
    let getBoardWidth: ((int, int)) => int = 
      ((_a, b)) => b;

    /* buildMatrix: (int, int) => matrix
     * input: (a, b), an int tuple where a represents the height of the
     *        desired matrix, and b represents the width of it
     * output: a zero matrix with a rows and b columns.
     */
    let buildMatrix: (int, int) => matrix =
      (a, b) => {
        let rec duplicate = (n, e) =>
          switch (n, e) {
          | (0, _) => []
          | (_, e) => [e, ...duplicate(n - 1, e)]
          };
        duplicate(a, duplicate(b, 0));
      };

    /* initialState: string => state
     * input: a user-input string consisting of two integers separated by 
     *        a space, indicating the desired board dimension. The first
     *        number input by the user denotes the height of the board,
     *        the second denotes the width. Both numbers must be at
     *        least 4, otherwise would raise an error.
     * output: a beginning state of the game, at which point the board
     *         is a zero matrix with the desired dimension, and where P1 
     *         gets to place the checker first.
     */
    let initialState: string => state =
      s => {
        let boardDims = parseBoardDims(s);
        let boardHeight = getBoardHeight(boardDims);
        let boardWidth = getBoardWidth(boardDims);
        if (boardHeight >= 4 || boardWidth >= 4) {
          State(Ongoing(P1), buildMatrix(boardHeight, boardWidth));
        } else {
          failwith("Board dimensions must be at least 4x4");
        };
      };

    /* legalMoves: state => list(move)
     * input: a game state
     * output: the list of legal and possible moves at this state
     * 
     * Note: this procedure is done by checking the bottom row
     *       of the game board matrix. If the bottom entry of any
     *       column is nonzero, then it's impossible to place a new
     *       checker to that column. Remember that the board matrix 
     *       and the printed board are upside-down.
     */
    let legalMoves: state => list(move) =
      s => {
        let State(status, board) = s;
        switch (status) {
        | Ongoing(_) =>
          let boardTopRow = List.hd(List.rev(board));
          let rec legalMovesHelper: (list(int), int) => list(int) = 
            (lst, n) =>
              switch (lst) {
              | [] => []
              | [0, ...tlt] => [n, ...legalMovesHelper(tlt, n+1)]
              | [_, ...tlt] => legalMovesHelper(tlt, n+1)
              };
          legalMovesHelper(boardTopRow, 0);
        | _ => []
        }
        }
          
    /* gameStatus: state => status
     * input: a game state
     * output: the current status at the state
     */
    let gameStatus: state => status = 
      fun
      | State(s, _board) => s;
    
    /* currentPlayer: state => whichPlayer
     * input: a game state
     * output: the player identity at the state
     */
    let currentPlayer: state => whichPlayer = 
      fun
      | State(Ongoing(p), _) => p
      | State(Win(p), _) => p
      | State(Draw, _) => failwith("Draw..Cannot get current player");
    
    /* otherPlayer: whichPlayer => whichPlayer
     * input: a player identity, either P1 or P2
     * output: P1 if the input is P2, and vice versa
     */
    let otherPlayer: whichPlayer => whichPlayer = 
      fun
      | P1 => P2
      | P2 => P1;

    /* moveOfString: (string, state) => move
     * input: a user-typed string indicating a move,
     *        and the current state of the game.
     * output: a move if the move is legal. Raise an error if not.
     * 
     * Note: the move user actually type is an integer starting from 1.
     *       i.e. 1 means 1st column user sees from the left, 
     *       2 means the 2nd, etc. However, a move type is an integer 
     *       defined to start from 0. So the user input, after parsed,
     *       is always subtracted by 1.
     */
    let moveOfString: (string, state) => move = 
      (input, s) => {
      let parseMove: (string, state) => move = 
        (input, s) => {
          let colCoordinate = int_of_string(input) -1
          if (List.mem(colCoordinate, legalMoves(s))) {
            colCoordinate
          } else {
            failwith("Illegal move, try a different column")
          }
        };

      parseMove(input, s)
      };
    
    /* listMax: list(float) => float
     * input: a list of floats
     * output: the max item among the list
     */
    let rec listMax: list(float) => float = 
      fun
      | [] => failwith("expecting non-empty list")
      | [a] => a
      | [hd, ...tl] => {
        let reMax = listMax(tl);
        switch (hd > reMax) {
        | true => hd
        | false => reMax
        };
      };
    
    /* listMin: list(float) => float
     * input: a list of floats
     * output: the min item among the list
     */
    let rec listMin: list(float) => float = 
      fun
      | [] => failwith("expecting non-empty list")
      | [a] => a
      | [hd, ...tl] => {
        let reMin = listMin(tl);
        switch (hd < reMin) {
        | true => hd
        | false => reMin
        };
      };

    /* estimateValue: state => float
     * input: a game state
     * output: a float between 200. and -200. indicating how "good" the
     *         current state is. Positive floats mean it is good for 
     *         P1, and negative floats mean it is good for P2. 0. means
     *         the state is equally good for both players.
     */
    let estimateValue: state => float = 
      s => {
      let State(_status, board) = s;
      
      let leftDiagonalConv = conv2dFastLeftDiagonal(board);
      let rightDiagonalConv = conv2dFastRightDiagonal(board);
      let vertConv = conv2dFastVertical(board);
      let horiConv = conv2dFastHorizontal(board);
      /* calculate the convolution with respect to four checker patterns */

      let allConv = 
        List.concat(leftDiagonalConv @ rightDiagonalConv @ vertConv @ horiConv);
      
      /* apply different weight mapping depending on the current player */
      switch (currentPlayer(s)) {
      | P1 =>
      let allConvWeighted = 
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
        /* If P1 has a 3, and it's P1's turn, then 
         * it doesn't matter that much if P2 has a 3. So the weights
         * are asymmetrical. Vice versa for P2.
         * 
         * If there's a 2 in the convolution result, that means there's a 
         * 2 with both sides open. So if the opponent has an open 2,
         * you must take action immediately.
         * 
         * If there's a 4, that means someone has won. So we return
         * 200. or -200. Otherwise, we add the max and the min value
         * so AI takes into account both players' moves
         */
        switch ((listMax(allConvWeighted), listMin(allConvWeighted))) {
        | (200., _) => 200.
        | (_, -200., ) => -200.
        | (x, y) => x +. y
        }
      | P2 =>
        let allConvWeighted = 
        List.map(
          i => 
            switch (i) {
            | 4 => 200.; 
            | 3 => 90.; 
            | 2 => 50.; 
            | 1 => 0.2;
            | 0 => 0.0;
            | -1 => -0.5;
            | -2 => -60.;
            | -3 => -100.;
            | -4 => -200.;
            | _ => failwith("Unrecognized convolution pattern")
            },
          allConv
        );
        switch ((listMax(allConvWeighted), listMin(allConvWeighted))) {
        | (200., _) => 200.
        | (_, -200., ) => -200.
        | (x, y) => x +. y
        }
        }
    };
    
    /* nextState: (state, move) => state
     * input: an Ongoing state, and a move
     * output: the state after the move is applied to the input state.
     *         Raise error if the input state is Win or Draw.
     * 
     * Note: nextState checks for a draw by checking if there is no legal 
     *       moves available. It checks for a win by calling estimateValue 
     *       and see if it produces a very large/small value. The trigger
     *       value is 200. and -200..
     */
    let nextState: (state, move) => state = 
      (s, m) => {
        /* rollingUp: given a move, i.e. desired column, find the corresponding
         * row index so that the checker can be placed by changing the
         * matrix entry at the given index
         */
        let rec rollingUp: (matrix, (int, int)) => int = 
          (m, (row, col)) =>
            switch (accessIndexMatrix(m, (row, col)) == 0) {
            | true => row /* 0 entry means an unoccupied spot */
            | false => rollingUp(m, (row+1, col))
            };
        
        switch (s) {
        | State(Ongoing(p), board) =>
          let targetIndex = (rollingUp(board, (0, m)), m);
          let weight = if (p == P1) {1;} else {-1;};
          let newBoard = changeMatrixByIndex(board, targetIndex, weight);
          let howGood = estimateValue(State(Ongoing(otherPlayer(p)), newBoard));

          switch (howGood) {
          | x when x <= -200. => State(Win(P2), newBoard)
          | x when x >= 200. => State(Win(P1), newBoard)
          | _ => 
            /* assemble a state to be passed to legalMoves.  
             * The player identity doesn't matter here.
             */
            switch (legalMoves(State(Ongoing(P1), newBoard)) == []) {
            | true => State(Draw, newBoard)
            | false => State(Ongoing(otherPlayer(p)), newBoard)
            }
          };
        | _ => failwith("The game has ended, unable to make a move")
        };
      }
};

module MyGame : Game = Connect4;
open Connect4;


/* test cases */
checkExpect(
  moveOfString("1", initialState("5 7")),
  0,
  "moveOfString passed!"
);
checkExpect(
  moveOfString("7", initialState("5 7")),
  6,
  "moveOfString passed!"
);
checkExpect(
  stringOfMove(0),
  "1",
  "stringOfMove passed!"
);
checkExpect(
  stringOfMove(1),
  "2",
  "stringOfMove passed!"
);
checkExpect(
  intListOfString("1 2", ""),
  [1, 2],
  "intListOfString passed!"
);
checkExpect(
  intListOfString("11 34 2", ""),
  [11, 34, 2],
  "intListOfString passed!"
);
checkExpect(
  listMax([1., 2., 3., 4., 0., 9., -1.1]),
  9.,
  "listMax passed!"
);
checkExpect(
  listMax([1.]),
  1.,
  "listMax passed!"
);
checkExpect(
  listMin([-1., 2., -100.2, 114514.]),
  -100.2,
  "listMin passed!"
);
checkExpect(
  listMin([-100.2]),
  -100.2,
  "listMin passed!"
);
checkExpect(
  changeMatrixByIndex(
    [[1, 2, 3]],
    (0, 2),
    -1
  ),
  [[1, 2, -1]],
  "changeMatrixByIndex passed!"
);
checkExpect(
  changeMatrixByIndex(
    [[1, 2, 3, 4],
     [5, 6, 7, 8],
     [9, 10, 11, 0]],
    (2, 1),
    -1
  ),
  [[1, 2, 3, 4],
   [5, 6, 7, 8],
   [9, -1, 11, 0]],
  "changeMatrixByIndex passed!"
);
checkExpect(
  conv2dFastHorizontal([[0, -1, 0, 1, 2], [1, -3, 0, 2, 0]]),
  [[0, 2], [0, -1]],
  "conv2dFastHorizontal passed!"
);
checkExpect(
  conv2dFastLeftDiagonal([[2, 3, 4, -1, 3],
                          [1, -1, 2, 1, 2],
                          [2, 0, -3, 2, 2],
                          [0, 1, 2, 4, 2],
                          [-12, 0, 2, 4, 2]]),
  [[2, 9],
   [7, 2]],
  "conv2dFastLeftDiagonal passed!"
);
checkExpect(
  conv2dFastVertical([[22, 34, 56, 1, 79],
                      [4, 5, 36, 92, 64],
                      [38, 70, 79, 70, 70],
                      [0, 89, 14, 53, 81],
                      [21, 39, 46, 10, 4]]),
  [[64, 198, 185, 216, 294],
   [63, 203, 175, 225, 219]],
  "conv2dFastVertical passed!"
);
checkExpect(
  conv2dFastRightDiagonal([[13, 68, 72, 99, 42],
                           [10, 44, -96, 82, 31],
                           [69, -70, -50, 21, 66],
                           [92, 3, 71, -71, 59],
                           [-8, 69, 19, 5, 24]]),
  [[25, 77],
   [27, 192]],
   "conv2dFastRightDiagonal passed!"
);
checkExpect(
  initialState("4 6"),
  State(Ongoing(P1), [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], 
                      [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]),
  "initialState and buildMatrix passed!"
);
checkExpect(
  initialState("4 4"),
  State(Ongoing(P1), [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
  "initialState and buildMatrix passed!"
);
checkExpect(
  nextState(initialState("4 4"), 0),
  State(Ongoing(P2), [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
  "nextState passed!"
);
checkExpect(
  nextState(initialState("4 4"), 2),
  State(Ongoing(P2), [[0, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
  "nextState passed!"
);
checkExpect(
  nextState(
    State(Ongoing(P2), [[0, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
    1
  ),
  State(Ongoing(P1), [[0, -1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
  "nextState passed!"
);
checkExpect(
  nextState(
    State(Ongoing(P2), [[0, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
    2
  ),
  State(Ongoing(P1), [[0, 0, 1, 0], [0, 0, -1, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
  "nextState passed!"
);
checkExpect(
  nextState(
    State(Ongoing(P2), [[1, 1, 1, -1], 
                        [-1, -1, -1, 1], 
                        [-1, -1, 1, 1],
                        [1, 1, -1, 0]]),
    3
  ),
  State(Draw, [[1, 1, 1, -1], 
               [-1, -1, -1, 1], 
               [-1, -1, 1, 1],
               [1, 1, -1, -1]]),
  "nextState passed!"
);
checkExpect(
  nextState(
    State(Ongoing(P1), [[0, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
    0
  ),
  State(Win(P1), [[1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
  "nextState and conv2dpassed!"
);
checkExpect(
  nextState(
    State(Ongoing(P2), [[1, 1, 1, -1], 
                        [1, 1, -1, 0], 
                        [1, -1, 0, 0],
                        [0, 0, 0, 0]]),
    0
  ),
  State(Win(P2), [[1, 1, 1, -1], 
                  [1, 1, -1, 0], 
                  [1, -1, 0, 0],
                  [-1, 0, 0, 0]]),
  "nextState and conv2d passed!"
);
checkExpect(
  nextState(
    State(Ongoing(P2), [[1, 1, 1, -1], 
                        [1, 1, -1, 0], 
                        [1, -1, 0, 0],
                        [0, 0, 0, 0]]),
    moveOfString(
      "1",
      State(Ongoing(P2), [[1, 1, 1, -1], 
                          [1, 1, -1, 0], 
                          [1, -1, 0, 0],
                          [0, 0, 0, 0]]),
    )
  ),
  State(Win(P2), [[1, 1, 1, -1], 
                  [1, 1, -1, 0], 
                  [1, -1, 0, 0],
                  [-1, 0, 0, 0]]),
  "nextState and conv2d and moveOfString passed!"
);
checkExpect(
  legalMoves(initialState("5 7")),
  [0, 1, 2, 3, 4, 5, 6],
  "legalMoves passed!"
);
checkExpect(
  legalMoves(
    State(Ongoing(P2), [[1, 1, 1, -1], 
                        [1, 1, -1, 0], 
                        [-1, -1, 0, 0],
                        [1, 0, 0, 0]]),
  ),
  [1, 2, 3],
  "legalMoves passed!"
);
checkExpect(
  legalMoves(
    State(Ongoing(P1), [[1, 1, 1, -1], 
                        [1, 1, -1, -1], 
                        [-1, -1, 1, 1],
                        [1, 1, -1, -1]]),
  ),
  [],
  "legalMoves passed!"
);