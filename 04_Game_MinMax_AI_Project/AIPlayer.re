open! CS17SetupGame;
open Game; 

/* Adjust searchDepth in AIPlayer.nextMove !!!*/
/* Adjust searchDepth in AIPlayer.nextMove !!!*/

module AIPlayer = (MyGame: Game) => {
  module PlayerGame = MyGame;
  /* put your team name here! */
  let playerName = "Zephyr";
  
  /* argMax: (list('a), ('a, int), int) => int
   * input: lst, a list of data,
   *        (max, maxIndex), a tuple recording the max value and its index
   *        viewed so far,
   *        curIndex, an int indicating the current position in the original
   *        lst.
   * output: an int indicating the index of the max value of lst
   * 
   * Note: When calling argMax() on list(float), use (neg_infinity, -1)
   *       as the second argument. Always use 0 as the third because 
   *       you are starting from the 0th element.
   */
  let rec argMax: (list('a), ('a, int), int) => int = 
    (lst, (max, maxIndex), curIndex) =>
      switch (lst) {
      | [] => maxIndex
      | [hd, ...tl] => 
        if (hd > max) {
          argMax(tl, (hd, curIndex), curIndex+1);
        } else {
          argMax(tl, (max, maxIndex), curIndex+1)
        }
      };  

  /* accessListIndex: (list('a), int) => 'a
   * input: lst, a list of data
   *        index, an integer specifying an index of the list
   * output: return the index-th element in the list, or
   *         failwith if the index doesn't exist
   */
  let rec accessListIndex: (list('a), int) => 'a = 
    (lst, index) =>
      switch (lst, index) {
      | ([hd, ..._tl], 0) => hd
      | ([], _) => failwith("Index out of range")
      | ([_hd, ...tl], _) => accessListIndex(tl, index - 1)
      };
  
  /* nonzerosAndZeros: string => (int, int)
   * input: a string representing the board, i.e. 
   *        the output of PlayerGame.stringOfState()
   * output: a int tuple where the first number represents
   *         the number of places occupied by checkers and the 
   *         second number represents the number of empty places
   * 
   * Note: this is only compatible with Connect4.stringOfState()
   */
  let rec nonzerosAndZeros: string => (int, int) =
    s =>
      switch (String.length(s)) {
      | 0 => (0, 0)
      | 1 =>
        switch (String.sub(s, 0, 1)) {
        | c when c >= "1" && c <= "9" => (1, 0)
        | "_" => (0, 1)
        | _ => (0, 0)
        }
      | l =>
        switch (String.sub(s, 0, 1)) {
        | c when c >= "1" && c <= "9" =>
          let (nonzeros, zeros) = nonzerosAndZeros(String.sub(s, 1, l - 1));
          (1 + nonzeros, 0 + zeros);
        | "_" =>
          let (nonzeros, zeros) = nonzerosAndZeros(String.sub(s, 1, l - 1));
          (0 + nonzeros, 1 + zeros);
        | _ => nonzerosAndZeros(String.sub(s, 1, l - 1))
        }
      };
  
  /* printEmoji: float => unit
   * input: weight, a float indicating how good is the game status
   * output: unit. an emoji representing the "mood" of the AI gets printed out
   */
  let printEmoji: float => unit = 
    weight =>
      switch (weight) {
      | x when x > 150. => print_endline(playerName ++ ": o(*////v////*)q")
      | x when x > 100. => print_endline(playerName ++ ": :P")
      | x when x > 50. => print_endline(playerName ++ ": (>>>v<<<)")
      | x when x > 20. => print_endline(playerName ++ ": (.-v-.)")
      | x when x > 0. => print_endline(playerName ++ ": '_>`")
      | x when x > -20. => print_endline(playerName ++ ": (-- --; )")
      | x when x > -50. => print_endline(playerName ++ ": (O_O;;")
      | x when x > -100. => print_endline(playerName ++ ": TxT")
      | _ => print_endline(playerName ++ ": orz")
      };   

  /* nextMove: PlayerGame.state => PlayerGame.move
   * input: s, a PlayerGame.state
   * output: a PlayerGame.move which AI considers is the best
   */
  let nextMove: PlayerGame.state => PlayerGame.move =
    s => { 
      let startTime = Js.Date.now();
      let rec alphabeta: (PlayerGame.state, int, float, float) => float = 
        (node, remainingDepth, a, b) => {
          let possibleMoves = PlayerGame.legalMoves(node);
          let status = PlayerGame.gameStatus(node);
          switch (status, remainingDepth) {
          | (PlayerGame.Win(P1), _) => 200. 
            /* If P1 wins, we are at a terminal node, so return 200.
             * and we don't have to call estimateValue() 
             */
          | (PlayerGame.Win(P2), _) => -200.
          | (PlayerGame.Draw, _) => 0.
          | (_, 0) => PlayerGame.estimateValue(node)
          | (_, _) =>
            let possibleStates = 
              List.map(i => PlayerGame.nextState(node, i), possibleMoves);
            let p =
              switch (PlayerGame.gameStatus(node)) {
              | PlayerGame.Ongoing(player) => player
              | _ => failwith("")
              };
            alphabetaChild(possibleStates, remainingDepth, a, b, p);
          };
        }
      and alphabetaChild: 
        (list(PlayerGame.state), int, float, float, PlayerGame.whichPlayer) 
        => float = (lst, remainingDepth, a, b, p) =>
          switch (p) {
          | P1 =>
            switch (lst) {
            | [] => a *. 0.9
            | _ =>
              let a = 
                max(a, alphabeta(List.hd(lst), remainingDepth - 1, a, b));
              if (b <= a) {
                a *. 0.9; 
                /* If a >= b, we've found the largest possible minimum number!*/
              } else {
                alphabetaChild(List.tl(lst), remainingDepth, a, b, P1);
                /* move horizontally to next child*/
              };
            }
          | P2 =>
            switch (lst) {
            | [] => b *. 0.9
            | _ =>
              let b = 
                min(b, alphabeta(List.hd(lst), remainingDepth - 1, a, b));
              if (b <= a) {
                b *. 0.9;
              } else {
                alphabetaChild(List.tl(lst), remainingDepth, a, b, P2);
              };
            }
          };

      let possibleMoves = 
        PlayerGame.legalMoves(s);
      
      let (occupiedOnBoard, emptyOnBoard) = 
        nonzerosAndZeros(PlayerGame.stringOfState(s));
      


      /* searchDepth settings below */
      /* searchDepth settings below */
      /* searchDepth settings below */
      /* searchDepth settings below */


      /* Hi Spike! We're doing this dynamic search depth so that
       * when there are less checkers on the board, the depth is
       * smaller. Our AI runs fast under depth 4 and somewhat fast
       * under 5, and smarter under 6. 
       * 
       * Below is our dynamic depth splits. We've tested 
       * it on a 5x7 board and it works efficiently. On our end,
       * at searchComplexity = 7,
       * each step costs 0.521s on average when competing with
       * the same AI but with constant depth 6.
       * 
       * If you are running it on boards of larger size, please adjust
       * searchComplexity variable. It will automatically adjust
       * searchDepth splits. Lower value means higher speed.
       */
      let searchComplexity = 8; /* an int between 0 and 8 (inclusive) */

      let depthsCandidates = 
        switch (searchComplexity) {
        | 0 => [3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 5, 6, 6]
        | 1 => [3, 3, 3, 3, 3, 3, 4, 4, 4, 5, 6, 6, 6]
        | 2 => [3, 3, 3, 3, 3, 4, 4, 4, 5, 5, 6, 8, 8]
        | 3 => [3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 6, 8, 8]
        | 4 => [4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 6, 8, 10]
        | 5 => [4, 4, 4, 5, 5, 5, 6, 6, 6, 8, 8, 8, 10]
        | 6 => [4, 4, 5, 5, 5, 5, 6, 6, 6, 8, 8, 10, 12]
        | 7 => [4, 5, 5, 5, 5, 6, 6, 6, 6, 8, 8, 10, 12]
        | 8 => [4, 5, 5, 5, 6, 6, 6, 6, 8, 8, 8, 10, 12]
        | _ => failwith("searchComplexity has to be an int from 0 to 8")
        };

      let searchDepth = 
        switch (occupiedOnBoard, emptyOnBoard + occupiedOnBoard) {
        | (n, _t) when n <= 2 => accessListIndex(depthsCandidates, 0)
        | (n, _t) when n <= 3 => accessListIndex(depthsCandidates, 1)
        | (n, t) when n <= t * 1 / 10 => accessListIndex(depthsCandidates, 2)
        | (n, t) when n <= t * 2 / 10 => accessListIndex(depthsCandidates, 3)
        | (n, t) when n <= t * 3 / 10 => accessListIndex(depthsCandidates, 4)
        | (n, t) when n <= t * 4 / 10 => accessListIndex(depthsCandidates, 5)
        | (n, t) when n <= t * 5 / 10 => accessListIndex(depthsCandidates, 6)
        | (n, t) when n <= t * 6 / 10 => accessListIndex(depthsCandidates, 7)
        | (n, t) when n <= t * 7 / 10 => accessListIndex(depthsCandidates, 8)
        | (n, t) when n <= t * 8 / 10 => accessListIndex(depthsCandidates, 9)
        | (n, t) when n <= t * 9 / 10 => accessListIndex(depthsCandidates, 10)
        | (n, t) when n <= t * 10 / 10 => accessListIndex(depthsCandidates, 11)
        | _ => accessListIndex(depthsCandidates, 12)
        };

      /* a list of weights corresponding to different moves */
      let howGoodIsNextMove = 
        List.map(
          i => alphabeta(PlayerGame.nextState(s, i), 
                         searchDepth, 
                         neg_infinity, 
                         infinity), 
          possibleMoves
        );
      
      /* extract the current player of s*/
      let p = 
        switch (PlayerGame.gameStatus(s)) {
        | PlayerGame.Ongoing(p) => p
        | _ => failwith("")
        };
      let endTime = Js.Date.now();

      /* print out the AI status */

      print_endline("Depth " 
                    ++ string_of_int(searchDepth) 
                    ++ " Took " 
                    ++ string_of_float((endTime -. startTime)/.1000.) 
                    ++ "s");     


      /* makes THE move */
      switch (p) {
      | P1 => 
        let moveIndex = 
          argMax(howGoodIsNextMove, (neg_infinity, -1), 0);
        printEmoji(accessListIndex(howGoodIsNextMove, moveIndex));
        accessListIndex(possibleMoves, moveIndex);
      | P2 => 
        let moveIndex = 
          argMax(List.map(i => -.i, howGoodIsNextMove), (neg_infinity, -1), 0);
        printEmoji(-1. *. accessListIndex(howGoodIsNextMove, moveIndex));
        accessListIndex(possibleMoves, moveIndex);
      };
    };
};

module TestGame = Connect4.Connect4;
open Player;

module TestAIPlayer = AIPlayer(TestGame); 
module MyAIPlayer:Player = TestAIPlayer;
open TestAIPlayer; 

/* insert test cases for any procedures that don't take in 
 * or return a state here */


checkExpect(
  argMax([1., 2., 3., 4.], (neg_infinity, -1), 0),
  3,
  "argMax passed!"
);
checkExpect(
  argMax([1., -100., -3., 1.1], (neg_infinity, -1), 0),
  3,
  "argMax passed!"
);
checkExpect(
  argMax([20., -100.], (neg_infinity, -1), 0),
  0,
  "argMax passed!"
);
checkExpect(
  accessListIndex([1, 2, 3], 2),
  3,
  "accessListIndex passed!"
);
checkExpect(
  accessListIndex([1, 2, 3, 4, 5], 0),
  1,
  "accessListIndex passed!"
);
checkExpect(
  accessListIndex([1, 2, 3, 4, 56], 4),
  56,
  "accessListIndex passed!"
);
checkExpect(
  nonzerosAndZeros("| 1  2  1  1  _  2  1 |"),
  (6, 1),
  "nonzerosAndZeros passed!"
);
checkExpect(
  nonzerosAndZeros(
    "| 1  2  1  1  _  _  _ | 
    | 1  2  2  2  _  2  _ | 
    | 2  1  1  1  _  2  _ | 
    | 2  2  2  1  _  1  _ | 
    | 1  2  1  1  2  1  _ |"
  ),
  (25, 10),
  "nonzerosAndZeros passed!"
);