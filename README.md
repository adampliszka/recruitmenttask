# recruitmenttask

Not 100% done, ran out of time just barely. The heuristic uses around 1.5x the allowed moves. I expect that simply doing a dry run to anticipate how many runs can be performed in advance would fix it, not 100% sure though. I actually want to come back to this in the future and finally finish it.

Task:
Imagine that you are playing a snake game on your old Nokia phone that has a screen that has width A and height B. You have a small 1x1 snake that can move up, dow, left, and right, and you start from some random point on your screen. Also, there is some apple (also sized 1x1) in some other random place on the screen. If you hit the right border of the screen and try to move right, your snake will appear on the left border in a symmetrical position. A similar thing would happen if your hit the top border of the screen (your snake will appear at the bottom), left border of the screen (it will appear on the right), and bottom border (it will teleport to the top). Your goal is to eat the apple as in the usual "Snake" game, BUT there are some important limitations of the game:

You are playing blindly (with closed eyes).
You don't know the size of the screen (A is unknown, B is unknown, and the area S=AB is ALSO unknown).
All you can do is only to send commands to the game by pressing "up", "down", "left", and "right" buttons.
You don't know your initial position.
You don't know your current position in any point in time in the game.
You don't know the position of the apple.
You can't cheat in the game and can't look at the screen at all.
You only know when you find the apple (your snake's position hits the apple's position) -- because your phone would signal a sound (your ears are not closed).
Once you find 1 apple, the game immediately finishes and you win.
If you use more than 35S left/right/up/down commands (where S = A*B -- also UNKNOWN value to you, BUT known to the game engine), you loose the game.
Please note that while you don't know the size of the screen, it can be literally any size, for example: 1x20, 100x1, 5000x5000 -- are all correct screen sizes. The only limitation is that A and B are positive integers.

You have to write a program that plays such game (in any programming language that you prefer) and always wins! Or at least try to win in as many situations as possible and explain why your winning strategy is really good. A textual explanation of your strategy is very important, and it's required to leave it in the comments.

For the simplicity, your program can call some pre-defined method (for example the method called "sendSignal") and pass your chosen command to it ("LEFT", "RIGHT", "UP", "DOWN"). This method would return you a Boolean result -- true if you have won the game, or false if you still haven't won the game. Feel free to leave the implementation of the sendSignal method empty as it would be a part of the game engine that you interact with.

Important notes and limitations of this task:

You can assume that S = A * B is always less than 1000000 (10^6)
Please note that you must never use more than 35 * S steps regardless of the field shape (please, make sure, your solution doesn't make too many unnecessary steps for the fields 1x1000000, 1000000x1, 1000x1000, etc.)
You don't receive any extra notifications from the gaming environment (you never know when you reach one of the borders)
You can never "hit" any border because once you reach a border and attempt to "cross" it, your snake would be teleported to the opposite border immediately (you are effectively playing a "Snake" game on a Torus).
A solution of this task that never makes more than 35 * S steps might be complex to come up with, so "partial" solutions will be also considered depending on how effective they are. Feel free and encouraged to implement some "baseline solution" that solves the problem somehow (maybe spending O(S^2) steps instead of O(S) or O(S*logS), for example), and then try to improve it as much as you can. Any interesting improvements will be considered (for example, if you can come up with a solution that uses O(S * sqrt(S)) steps or with some notable heuristic that doesn't change the complexity of your solution in terms of the steps used, but it significantly improves it for some specific classes of the screen shapes, or "in average")
    Please note, that if you invent some notable heuristic or some algorithm that improves the number of steps used significantly we would like to read some theoretical proof or just an explanation why it works well.

