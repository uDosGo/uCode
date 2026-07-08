ORG &1100

\\ ============================================================
\\ Elite — BBC Micro (1984)
\\ Adapted for uCode pipeline (6502 assembly)
\\ ============================================================

\\ Memory-mapped hardware
VIA_PORTB EQU &FE40
VIA_PORTA EQU &FE41
OSWRCH   EQU &FFEE
OSBYTE   EQU &FFF4

\\ ---- Game State (LENS-extractable) ----
SHIP_STATUS     EQU &0222    ; 0=docked, 1=in flight, 2=docking, 3=jumping
SHIP_LOC_X      EQU &0234    ; Current system X coordinate (16-bit)
SHIP_LOC_Y      EQU &0236    ; Current system Y coordinate (16-bit)
CREDITS_LO      EQU &0200    ; Credit balance low byte (tenths of credit)
CREDITS_HI      EQU &0201    ; Credit balance high byte
INVENTORY_START EQU &0240    ; 12 commodity slots (1 byte each: tonnes)
FUEL            EQU &024C    ; Hyperspace fuel (0-70 light years)
SHIP_ENERGY     EQU &0250    ; Energy banks (0-255)
SHIP_SHIELDS    EQU &0251    ; Shield strength
LASER_TEMP      EQU &0252    ; Laser temperature
MISSILE_COUNT   EQU &0253    ; Missiles remaining (0-4)

\\ ---- Current System ----
SYSTEM_SEED_0   EQU &0260    ; Galaxy seed (6 bytes)
SYSTEM_SEED_1   EQU &0261
SYSTEM_SEED_2   EQU &0262
SYSTEM_SEED_3   EQU &0263
SYSTEM_SEED_4   EQU &0264
SYSTEM_SEED_5   EQU &0265
GOVERNMENT      EQU &0270    ; Government type (0-7)
ECONOMY         EQU &0271    ; Economy type (0-7)
TECH_LEVEL      EQU &0272    ; Tech level (0-14)

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
LDA #0
STA SHIP_STATUS     ; Docked
LDA #&64            ; 100 decicredits = 10 credits
STA CREDITS_LO
LDA #0
STA CREDITS_HI
LDA #70             ; Full fuel tanks
STA FUEL
LDA #&FF            ; Full energy
STA SHIP_ENERGY
LDA #&80            ; Full shields
STA SHIP_SHIELDS
LDA #4              ; 4 missiles
STA MISSILE_COUNT
LDA #0
STA LASER_TEMP
JSR InitCommodities
JSR GenerateSystem
RTS

\\ ============================================================
\\ Initialize commodity prices for current system
\\ ============================================================
.InitCommodities
LDX #11
.comLoop
LDA CommodityTable,X
STA INVENTORY_START,X
DEX
BPL comLoop
RTS

\\ ============================================================
\\ Main game loop
\\ ============================================================
.MainLoop
JSR ReadInput
JSR UpdateUniverse
JSR UpdateShipStatus
JSR CheckDocking
JSR RenderView
JMP MainLoop

\\ ============================================================
\\ Read keyboard/joystick input
\\ ============================================================
.ReadInput
JSR OSBYTE
RTS

\\ ============================================================
\\ Update universe (NPC ships, stations, planets)
\\ ============================================================
.UpdateUniverse
JSR MoveShips
JSR RotateShips
JSR UpdatePlanetPositions
RTS

\\ ============================================================
\\ Move NPC ships
\\ ============================================================
.MoveShips
RTS

\\ ============================================================
\\ Rotate ship wireframe models
\\ ============================================================
.RotateShips
RTS

\\ ============================================================
\\ Update planet/sun positions in 3D view
\\ ============================================================
.UpdatePlanetPositions
RTS

\\ ============================================================
\\ Update ship status (energy, shields, temperature)
\\ ============================================================
.UpdateShipStatus
LDA SHIP_ENERGY
BEQ .shipDestroyed
LDA LASER_TEMP
CMP #&80
BCS .overheating
RTS
.shipDestroyed
JSR ShipExplosion
RTS
.overheating
DEC LASER_TEMP
RTS

\\ ============================================================
\\ Ship explosion sequence
\\ ============================================================
.ShipExplosion
LDA #0
STA SHIP_STATUS     ; Destroyed
RTS

\\ ============================================================
\\ Check if player is in docking range of station
\\ ============================================================
.CheckDocking
RTS

\\ ============================================================
\\ Dock with space station
\\ ============================================================
.DockShip
LDA #2
STA SHIP_STATUS      ; Docking
JSR AnimateDocking
LDA #0
STA SHIP_STATUS      ; Docked
JSR RefuelShip
JSR SaveCommander
RTS

.AnimateDocking
RTS

\\ ============================================================
\\ Refuel and repair at station
\\ ============================================================
.RefuelShip
LDA #70
STA FUEL
LDA #&FF
STA SHIP_ENERGY
STA SHIP_SHIELDS
RTS

\\ ============================================================
\\ Save commander data (LENS capture point)
\\ ============================================================
.SaveCommander
RTS

\\ ============================================================
\\ Hyperspace jump
\\ ============================================================
.JumpWarp
LDA FUEL
BEQ .noFuel
LDA #3
STA SHIP_STATUS      ; Jumping
JSR AnimateJump
JSR GenerateSystem
LDA #0
STA SHIP_STATUS      ; In flight
DEC FUEL             ; Consume fuel
RTS
.noFuel
RTS

.AnimateJump
RTS

\\ ============================================================
\\ Generate new star system
\\ ============================================================
.GenerateSystem
JSR SeedToSystem
JSR CalculatePrices
RTS

\\ ============================================================
\\ Convert galaxy seed to system properties
\\ ============================================================
.SeedToSystem
RTS

\\ ============================================================
\\ Calculate commodity prices for system
\\ ============================================================
.CalculatePrices
RTS

\\ ============================================================
\\ Buy commodity at station
\\ ============================================================
.BuyCommodity
RTS

\\ ============================================================
\\ Sell commodity at station
\\ ============================================================
.SellCommodity
RTS

\\ ============================================================
\\ Launch from station
\\ ============================================================
.LaunchShip
LDA #1
STA SHIP_STATUS      ; In flight
RTS

\\ ============================================================
\\ Initiate combat with target ship
\\ ============================================================
.EngageTarget
RTS

\\ ============================================================
\\ Render 3D wireframe view
\\ ============================================================
.RenderView
RTS

\\ ============================================================
\\ Draw wireframe line (3D to 2D projection)
\\ ============================================================
.DrawLine
RTS

\\ ============================================================
\\ Clear screen buffer
\\ ============================================================
.ClearScreen
RTS

\\ ============================================================
\\ Display HUD (scanner, compass, status)
\\ ============================================================
.DisplayHUD
RTS

\\ ============================================================
\\ Scanner (top-down view of nearby ships)
\\ ============================================================
.UpdateScanner
RTS

\\ ============================================================
\\ Compass (direction to station/planet)
\\ ============================================================
.UpdateCompass
RTS

\\ ============================================================
\\ Game Over sequence
\\ ============================================================
.GameOver
JSR ShowGameOverScreen
RTS

\\ ============================================================
\\ Show Game Over screen
\\ ============================================================
.ShowGameOverScreen
RTS

\\ ============================================================
\\ Show title screen
\\ ============================================================
.ShowTitleScreen
RTS

\\ ============================================================
\\ Commodity table (default prices in decicredits)
\\ ============================================================
.CommodityTable
EQUB 19  ; Food
EQUB 20  ; Textiles
EQUB 65  ; Radioactives
EQUB 40  ; Slaves
EQUB 83  ; Liquor/Wines
EQUB 196 ; Luxuries
EQUB 235 ; Narcotics
EQUB 154 ; Computers
EQUB 117 ; Machinery
EQUB 78  ; Alloys
EQUB 252 ; Firearms
EQUB 44  ; Furs

\\ ============================================================
\\ Ship wireframe data pointers
\\ ============================================================
.ShipDataTable
EQUW &3000  ; Cobra Mk III
EQUW &3100  ; Adder
EQUW &3200  ; Viper
EQUW &3300  ; Python
EQUW &3400  ; Thargoid

\\ ============================================================
\\ Planet description table (teletext pages)
\\ ============================================================
.PlanetDescriptions
EQUW &5000  ; Lave
EQUW &5100  ; Diso
EQUW &5200  ; Riedquat
EQUW &5300  ; Zaonce

\\ ============================================================
\\ Screen buffer (mode 4, 256x256 monochrome)
\\ ============================================================
.ScreenBuffer
SKIP 8192    ; 32 columns x 256 rows