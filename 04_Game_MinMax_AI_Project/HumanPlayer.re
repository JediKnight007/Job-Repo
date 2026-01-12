open Game;

module HumanPlayer = (MyGame: Game) => {
  module PlayerGame = MyGame;

  let getInputJSLine: unit => string = {
    %bs.raw
    {|
      function() {
        const readlineSync = require('readline-sync');
        const rl = readlineSync;
        var ans = rl.question('What move do you want to make? ');
        return ans;
    }|};
  };

  let rec nextMove = s => {
    let input: string = getInputJSLine();
    switch (input) {
    | "exit" => failwith("Exiting Game REPL")
    | _ => try(PlayerGame.moveOfString(input, s)) {
      | Failure(msg) => {
        print_endline(msg);
        nextMove(s)
        };
      | _ => failwith("Unexpected Error, Closing Game REPL");
      };
    };
  };

  let playerName = "Alex"
};


open Player;
module TestGame = Connect4.Connect4;
module TestHumanPlayer = HumanPlayer(TestGame);
module MyHumanPlayer:Player = TestHumanPlayer;
open! TestHumanPlayer;
