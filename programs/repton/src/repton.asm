ORG &1100

\\ ============================================================
\\ Repton — BBC Micro / Acorn Electron (1985)
\\ Adapted for uCode pipeline (6502 assembly)
\\ ============================================================

\\ Memory-mapped hardware
VIA_PORTB EQU &FE40
VIA_PORTA EQU &FE41
OSWRCH   EQU &FFEE
OSBYTE   EQU &FFF4

\\ ---- Game State Variables ----
SCORE_LO      EQU &0900    ; Score (16-bit)
SCORE_HI      EQU &0901
LIVES         EQU &0902    ; Lives remaining (3-0)
LEVEL_NUM     EQU &0903    ; Current level (1-12)
REPTOL_STATE  EQU &0904    ; Reptol status: 0=idle, 1=collecting, 2=ate
TIME_REMAINING EQU &0905   ; Level timer (ticks)
PUZZLE_STATUS EQU &0906    ; Puzzle state: 0=unsolved, 1=solved, 2=complete
DIAMONDS_COLL EQU &0907    ; Diamonds collected
EARTH_COLL    EQU &0908    ; Earth collected (for filling traps)

\\ ---- Player Position ----
PLAYER_X      EQU &0910
PLAYER_Y      EQU &0911
PLAYER_DIR    EQU &0912    ; 0=up, 1=right, 2=down, 3=left

\\ ---- Level Data Pointer ----
LEVEL_PTR_LO  EQU &0920
LEVEL_PTR_HI  EQU &0921

\\ ---- Enemy State (4 enemies, 8 bytes each) ----
ENEMY_START   EQU &0930    ; 32 bytes: 8 bytes x 4 enemies

\\ ---- Diamond Positions (max 30) ----
DIAMOND_DATA  EQU &0980    ; 60 bytes: x,y pairs

\\ ---- Trap Positions (max 10) ----
TRAP_DATA     EQU &09C0    ; 20 bytes: x,y pairs

\\ ============================================================
\\ Entry Point
\\ ============================================================
.MainEntry
JSR InitGame
JMP MainLoop

\\ ============================================================
\\ Initialize game state
\\ ============================================================
.InitGame
LDA #3
STA LIVES         ; Start with 3 lives
LDA #1
STA LEVEL_NUM     ; Start at level 1
LDA #0
STA SCORE_LO      ; Score = 0
STA SCORE_HI
STA DIAMONDS_COLL
STA EARTH_COLL
LDA #0
STA REPTOL_STATE  ; Reptol idle
LDA #&FF
STA TIME_REMAINING ; Max time
JSR LoadLevel
RTS

\\ ============================================================
\\ Load current level data from ROM
\\ ============================================================
.LoadLevel
LDX LEVEL_NUM
DEX              ; 0-based index
TXA
ASL A            ; x2 for word table
TAX
LDA LevelTable,X ; Low byte
STA LEVEL_PTR_LO
LDA LevelTable+1,X ; High byte
STA LEVEL_PTR_HI
JSR ParseLevelData
JSR PlaceDiamonds
JSR PlaceTraps
JSR SpawnEnemies
JSR SetPlayerStart
RTS

\\ ============================================================
\\ Main game loop
\\ ============================================================
.MainLoop
JSR ReadKeyboard
JSR MovePlayer
JSR MoveEnemies
JSR CheckDiamondCollision
JSR CheckTrapCollision
JSR CheckEnemyCollision
JSR UpdateTimer
JSR UpdateDisplay
LDA REPTOL_STATE
BEQ .checkGameOver
JSR UpdateReptol
.checkGameOver
LDA LIVES
BEQ .gameOver
LDA PUZZLE_STATUS
CMP #2            ; Complete?
BEQ .levelComplete
JMP MainLoop

.gameOver
JSR ShowGameOver
RTS

.levelComplete
JSR ShowLevelComplete
INC LEVEL_NUM
JSR LoadLevel
JMP MainLoop

\\ ============================================================
\\ Keyboard Input
\\ ============================================================
.ReadKeyboard
JSR OSBYTE
CMP #&81          ; Up arrow
BEQ .moveUp
CMP #&82          ; Down arrow
BEQ .moveDown
CMP #&83          ; Left arrow
BEQ .moveLeft
CMP #&84          ; Right arrow
BEQ .moveRight
CMP #&20          ; Space — dig/use
BEQ .doAction
RTS
.moveUp
LDA #0
STA PLAYER_DIR
RTS
.moveDown
LDA #2
STA PLAYER_DIR
RTS
.moveLeft
LDA #3
STA PLAYER_DIR
RTS
.moveRight
LDA #1
STA PLAYER_DIR
RTS
.doAction
JSR PlayerAction
RTS

\\ ============================================================
\\ Move Player
\\ ============================================================
.MovePlayer
LDA PLAYER_DIR
CMP #0
BEQ .tryUp
CMP #1
BEQ .tryRight
CMP #2
BEQ .tryDown
CMP #3
BEQ .tryLeft
RTS

.tryUp
DEC PLAYER_Y
JSR CheckSolid
BCS .undoUp
RTS
.undoUp
INC PLAYER_Y
RTS

.tryRight
INC PLAYER_X
JSR CheckSolid
BCS .undoRight
RTS
.undoRight
DEC PLAYER_X
RTS

.tryDown
INC PLAYER_Y
JSR CheckSolid
BCS .undoDown
RTS
.undoDown
DEC PLAYER_Y
RTS

.tryLeft
DEC PLAYER_X
JSR CheckSolid
BCS .undoLeft
RTS
.undoLeft
INC PLAYER_X
RTS

\\ ============================================================
\\ Player Action (dig / push boulder)
\\ ============================================================
.PlayerAction
RTS

\\ ============================================================
\\ Check if position is solid (wall or boulder)
\\ ============================================================
.CheckSolid
SEC             ; Default: solid
RTS

\\ ============================================================
\\ Parse level data into working memory
\\ ============================================================
.ParseLevelData
RTS

\\ ============================================================
\\ Place diamonds on level map
\\ ============================================================
.PlaceDiamonds
RTS

\\ ============================================================
\\ Place traps (skulls) on level map
\\ ============================================================
.PlaceTraps
RTS

\\ ============================================================
\\ Initialize enemy positions
\\ ============================================================
.SpawnEnemies
RTS

\\ ============================================================
\\ Set player start position from level data
\\ ============================================================
.SetPlayerStart
LDA #10
STA PLAYER_X
LDA #5
STA PLAYER_Y
RTS

\\ ============================================================
\\ Move enemies (AI)
\\ ============================================================
.MoveEnemies
RTS

\\ ============================================================
\\ Check if player collected a diamond
\\ ============================================================
.CheckDiamondCollision
RTS

\\ ============================================================
\\ Check if player triggered a trap
\\ ============================================================
.CheckTrapCollision
RTS

\\ ============================================================
\\ Check if player hit an enemy
\\ ============================================================
.CheckEnemyCollision
RTS

\\ ============================================================
\\ Update level timer
\\ ============================================================
.UpdateTimer
DEC TIME_REMAINING
BNE .timerOk
LDA #1
STA REPTOL_STATE  ; Reptol starts eating!
.timerOk
RTS

\\ ============================================================
\\ Reptol AI (moves after timer expires)
\\ ============================================================
.UpdateReptol
RTS

\\ ============================================================
\\ Render screen
\\ ============================================================
.UpdateDisplay
RTS

\\ ============================================================
\\ Show scoreboard overlay
\\ ============================================================
.ShowScoreboard
RTS

\\ ============================================================
\\ Game Over screen
\\ ============================================================
.ShowGameOver
RTS

\\ ============================================================
\\ Level Complete screen
\\ ============================================================
.ShowLevelComplete
RTS

\\ ============================================================
\\ Level data pointer table (12 levels, ROM address)
\\ ============================================================
.LevelTable
EQUW &4000  ; Level 1
EQUW &4100  ; Level 2
EQUW &4200  ; Level 3
EQUW &4300  ; Level 4
EQUW &4400  ; Level 5
EQUW &4500  ; Level 6
EQUW &4600  ; Level 7
EQUW &4700  ; Level 8
EQUW &4800  ; Level 9
EQUW &4900  ; Level 10
EQUW &4A00  ; Level 11
EQUW &4B00  ; Level 12

\\ ============================================================
\\ Screen memory buffer
\\ ============================================================
.ScreenBuf
SKIP 1024    ; 32x32 character display buffer

\\ ============================================================
\\ Score display buffer (BCD)
\\ ============================================================
.ScoreDisplay
EQUB 0,0,0,0,0,0  ; "000000"

\\ ============================================================
\\ High score table
\\ ============================================================
.HighScoreTable
EQUB 0,0,0,0,0,0  ; "000000"
EQUB 0,0,0,0,0,0
EQUB 0,0,0,0,0,0
EQUB 0,0,0,0,0,0
EQUB 0,0,0,0,0,0