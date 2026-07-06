# Lesson 3: Snack Containers — Packaging & Publishing

**Level 4: Snack Containers & Publishing (8-10 hours)**
**Prerequisites:** Levels 1-3 (BASIC, Teletext, Sprites)

---

## What is a Snack?

A **Snack** is a self-contained, portable uCode program that bundles everything it needs — source code, sprites, sounds, and maps — into a single directory. Think of it as a lunchbox for your game.

```
my-adventure.snack/
├── main.ucode            # Entry point (required)
├── manifest.yaml         # Name, author, engine version
├── sprites/              # Player and enemy sprites
│   ├── hero.chr
│   └── goblin.chr
├── bobs/                 # Animated GIF objects
│   └── fireball.gif
├── sounds/               # WAV audio files
│   ├── coin.wav
│   └── death.wav
└── maps/                 # Level data
    └── dungeon.json
```

---

## Step 1: Create a Snack from Template

Open your terminal and run:

```bash
ucode snack create dungeon-escape --template game
```

This creates the directory structure and a template `main.ucode`:

```basic
10 REM Dungeon Escape — uCode Snack
20 MODE 7
30 COLOUR 3
40 PRINT TAB(12,10); "DUNGEON ESCAPE"
50 PRINT TAB(10,12); "Press any key to start"
60 IF GET
70 CLS
80 REM Your game code here...
90 END
```

---

## Step 2: Write the Manifest

Every snack needs a `manifest.yaml` file that describes it:

```yaml
name: "Dungeon Escape"
author: "your-name-here"
version: "1.0.0"
description: "Escape the dungeon by collecting 3 keys."
engine: "bbcsdl-1.36a"
entry: "main.ucode"
type: "game"
```

---

## Step 3: Build Your Game

Let's create a simple maze explorer using grid cells:

```basic
10 REM Dungeon Escape
20 MODE 7
30 INSTALL @lib$ + "gfxlib"
40 PROC_gfx_init(640, 480, 32)
50 
60 REM Load sprites
70 hero% = FN_load_sprite("sprites/hero.chr", 24, 24)
80 goblin% = FN_load_sprite("sprites/goblin.chr", 24, 24)
90 key_bob% = FN_load_gif("sprites/key.gif")
100 
110 REM Player position (grid coords)
120 px% = 5 : py% = 5
130 keys% = 0
140 
150 REM Load the dungeon map
160 DIM map$(24)
170 RESTORE 1000
180 FOR y% = 0 TO 23
190   READ map$(y%)
200 NEXT y%
210 
220 REM Game loop
230 REPEAT
240   CLS
250   
260   REM Draw map
270   COLOUR 6
280   FOR y% = 0 TO 23
290     PRINT TAB(0,y%); map$(y%)
300   NEXT y%
310   
320   REM Draw player
330   COLOUR 2
340   PRINT TAB(px%,py%); "@"
350   
360   REM Draw keys left to collect
370   COLOUR 3
380   FOR k% = 0 TO keys%
390     PROC_sprite_place(key_bob%, 100 + k% * 30, 450)
400   NEXT k%
410   
420   REM Read input
430   key$ = INKEY$(0)
440   oldx% = px% : oldy% = py%
450   
460   IF key$ = "w" THEN py% = py% - 1
470   IF key$ = "s" THEN py% = py% + 1
480   IF key$ = "a" THEN px% = px% - 1
490   IF key$ = "d" THEN px% = px% + 1
500   
510   REM Check walls
520   IF MID$(map$(py%), px%+1, 1) = "#" THEN
530     px% = oldx% : py% = oldy%
540   ENDIF
550   
560   REM Check keys
570   IF MID$(map$(py%), px%+1, 1) = "K" THEN
580     keys% = keys% + 1
590     MID$(map$(py%), px%+1, 1) = " "
600     SOUND 1, -15, 200, 5
610   ENDIF
620   
630   REM Check exit
640   IF MID$(map$(py%), px%+1, 1) = "E" AND keys% >= 3 THEN
650     CLS
660     COLOUR 2
670     PRINT TAB(10,10); "YOU ESCAPED!"
680     WAIT 300
690     END
700   ENDIF
710   
720   WAIT 5
730 UNTIL FALSE
740 
750 REM Dungeon map data (24 rows)
760 DATA "########################"
770 DATA "#K  #     #  K#     K #"
780 DATA "# # # ### # ## # ### #"
790 DATA "# # # # # #  # #   # #"
800 DATA "# #   # # ## # ### # #"
810 DATA "# ##### #  # #     # #"
820 DATA "#   #   # ## ##### # #"
830 DATA "### # ###  #     # # #"
840 DATA "#   #     ## # # #   #"
850 DATA "# ## #####  # # # ###"
860 DATA "# #      # ##   #   #"
870 DATA "# # #### #  ##### # #"
880 DATA "# # #  # #      # # #"
890 DATA "# # #  # ###### # # #"
900 DATA "# # #           # # #"
910 DATA "# # ######## ## # # #"
920 DATA "# #        # ##   # #"
930 DATA "# ######## #  ### # #"
940 DATA "#     #    #    # # #"
950 DATA "##### # #### ##   #E#"
960 DATA "#   # #  #   ###### #"
970 DATA "# #   #  # K    #   #"
980 DATA "# #####  ###### # ###"
990 DATA "########################"
```

---

## Step 4: Validate & Build

```bash
# Check that all assets are referenced
ucode snack validate dungeon-escape

# Build into a distributable .snack file
ucode snack build dungeon-escape

# Output: dungeon-escape.snack (compressed archive)
```

---

## Step 5: Publish & Share

```bash
# Create a shareable .snack file
ucode snack publish dungeon-escape.snack

# Your friend installs it:
ucode snack install dungeon-escape.snack

# And runs it:
ucode snack run dungeon-escape
```

---

## Exercise 4.1

Create a snack that displays a teletext menu screen with FASTEXT-style colored options. Use MODE 7, at least 4 colors, and include a sprite that bounces around the menu.

Save it as `menu-demo.snack`.

---

## Exercise 4.2

Take the dungeon escape game above and add:
1. An animated fireball BOB that patrols one corridor
2. A second enemy sprite (goblin) that chases the player
3. Sound effects for collecting keys and dying

---

## What You've Learned

- Snack directory structure and manifest format
- Loading assets from inside a snack (sprites, sounds, maps)
- Building and validating snacks with the CLI
- Publishing snacks for others to install and run

**Next: Level 5 — Grid Worlds & Spatial Algebra**