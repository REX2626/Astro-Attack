# Astro-Attack

### Package command:
Tips:
1: Delete all pyinstaller folders (ouput, spec, dist, build)
2: Run auto-py-to-exe
3: Set script location to main.py (C:/Users/rexat/Documents/Astro Attack/Astro-Attack/main.py)
4: Choose "One File" and "Window Based"
5: Choose icon "C:/Users/rexat/Downloads/red_ship.ico"
6: For additional files choose assets (C:/Users/rexat/Documents/Astro Attack/Astro-Attack/assets)
7: In advanced, set name to "Astro Attack [version]"
8: In advanced, enable --clean

If above doesn't work, try the command below
pyinstaller --noconfirm --onefile --windowed --icon "C:/Users/rexat/Downloads/red_ship.ico" --name "Astro Attack a1.2.0" --clean --add-data "C:/Users/rexat/Documents/Astro Attack/Astro-Attack/assets;assets/"  "C:/Users/rexat/Documents/Astro Attack/Astro-Attack/main.py"


## TODO:

### a1.3.0 (station)
More general attack_entity function for all ai ships

Improve Neutral ship functionality - better decision making in fights (who to shoot at, enemy or player)

Neutral ship when attacking, will only become passive again once the whole group of enemies are defeated

Enemy stations have weapons, can be destroyed for loot

Neutral stations can be traded with

New mothership image, large and powerful

Add missile and autoturret weapons

Change player health to armour, top 50% can be healed but lower 50% can only be repaired at a station

Add health regen at stations
Add something else to e menu

Stations can be docked with

Armour:
A few armour slots (5), but is a bar
You can repair a whole slot with some scrap, if slot is only still damaged, you still have to pay full slot price
When health is damaged, it effects how ships work, e.g. start smoking, visual screen effects, speed reduced, shield stops working, weapon not as effective
When bits of player ship stops working, message should come up
Some visual to show armour, and it breaking
Once armour is broken, all damage goes into health
Weapons have a certain amount of penetration, more penetration, more damage to health
Missile have low pen, sniper has high pen

CONSOLE FUNCTIONALITY TO ADD:
    better colour coordination
    display error message

### a1.4.0 (gameplay loop - difficulty, missions and saving)
Enemies become more difficult

Missions (stations will give a reward for completing a mission)

Saving and loading

### a1.5.0 (sound)

### a1.6.0 (bosses, ship customization, friendly ships)

### a1.7.0 (multiplayer)

### Other
Make bullets do less damage the further away they go (mainly for gatling gun)

Add bullet damage effect, when bullets hits something, blue sparks explode

Change colour of enemy bullets

Make ships have a thruster animation

Check / improve graphics.get_entities_to_draw performance
Fix issue with not rendering some objects right on edge of screen (strict rendering)

Fix first full_screen click not moving the mouse properly

If neutral ship cannot find patrol point - do something

NOTE: pygame.draw.circle uses integer for radius, e.g. diameter is always multiples of two
Do some caching for circles for particles to improve performance

### POTENTIAL

Strict Rendering (only rendering objects which will defo be on screen)

Think about doing rotozoom as it filters the image (AA), can be costly tho

Add friendly AI ship
Add some basic coding interface 

Add ammo system

Enemies drop ammo

Add radar upgrades so that mini map can be improved

At some point, lower the initial upgrade values (high atm so testing is easier)

Have different shoot speed for enemy and player

Add text interface (commands)

Add space stations
Enemy ships can spawn at enemy stations
Neutral ships can move from station to station
Player can interact with stations

Add money system, different currencies, get cash from killing

Add shop system

Add loot system

Add fuel system

Have different items (e.g. different types of guns)

One type of ammo
But different weapons use up a different amount of ammo (e.g. 0.2 for machine gun or 3 for missile)

---

One type of ship
You can collect / buy items, which you can use to upgrade your ship (e.g. scrap)
Example things you can upgrade: armour, weapon, engine, shield generator, radar etc...
Example: For engine you could upgrade: boost, acceleration, top speed...
You can also use money to buy consumables, repair ship and purchase small items that give you a buff or special ability
There are different types of weapons, each of which you can upgrade
Example weapons: gatling gun, laser beam, normal gun, sniper, missile launcher, autoturrets

---

Have a massive asteroid or moon, with tunnels that you can go through

## DONE:
Make Enemy ships move around

Fix angle, so it is between +180 and -180

CHUNKS is globalled in objects.py

When updating entities, don't update every entity's chunk 
In entity.update(), if the entity moved, put entity into it's new chunk

Add asteroid class

Add rotation acceleration, so red_ship doesn't immediately stop rotating

Make turning more snappy

Adjust ship accleration (so faster if forward, slower if side to side)

Make bullet fire from the front of the ship

Add Images file

Make ship more detailed, have cross in the centre
Make ship smaller

Add a constants file (maybe class), so that any file can use any constant (without any circular import shenanigans)

Add player health

Add enemy ship class

Make Enemy only shoot when close to red_ship

Add stars in background, layered, which move

Dampen intertia before moving, so that acceleration is dampened 1 tick later, not straight away

Improve star drawing code, so stars aren't brute force placed around the side

Improve bullet shooting, so that the position the bullet is spawned at is relative to the size of the ship

Add score counter

Stop spawning anything in starting chunks

Add zoom

Don't blit objects which will not be on the screen

Limit the zooming in and out based on the chunk distance
Make Enemy ships move around

Make all artwork the same scale

Improve asteroid image, add several asteroid images

Enemy Grouping

Add de-spawning, e.g. bullets

Add choice for ParticleSystem to spawn all particles at once

Enemy health: Add health to enemy ships

Added Neutral Ship

Neutral Ship Attacks enemies firing at it

Add chocie for particles to shrink over time

Add boost animation to ship and particle effect

Fix speed instant decellerating when stopping boosting

Add ship colliding with asteroids
Ship will bounce off
Ship will take damage proportional to speed^2

Add 2 more asteroid images

Add death screen

Patrol state: improve grouping with mothership

Enemies dont go too close to player

Enemies Strafe in a semi realistic manner

Upgrade menu system
Have a page system with buttons per page

Fix button select disappearing

Add escape functions to all the pages

Add image to menu

Edge of button boundaries are not clickable (click for button rectangle not text label)

Add padding ability to buttons

Change score to be number of enemies killed not damaged (more points for mothership)

MOUSE_DOWN counts for scroll_wheel and right_click

Attack state: make fighting seem more natural
    Aim to where the player is predicted to be in the future for more accurate shooting
    POTENTIAL: dodging either incoming bullets or for the enemy to have a random strafe

Add button effect when hovered over

Improve Menu performance

Retreat state: If enemy health is low and player health is high - retreat

Make new npc ai ship class which the ai ships will inherit from (cleans up code)

Add slider for menu buttons

Fix spawning in asteroid

Custom cursor

Fix bullets going through asteroids

Change custom cursor colour based on whether you are hovering over an enemy or not

FIX ENEMIES SPAWNING INSIDE ASTEROIDS NOW

Improve player movement (left and right doesn't work when moving forward)

Move UI code from main to ui.py

Add targeting icon (space engineers)

Enemy tracking for player

Level up, the ability to upgrade weapons, armour, engine etc

Add continue button to pause menu

Add "e" control to info menu (for systems)

Remove settings that are now changed with upgrades (e.g. health)

Add weapon upgrades: fire rate, damage, speed, range?


### a1.1.0 (upgrades and f3)
Add radar upgrades: max zoom out

Add armour image to systems menu

### a1.1.1 (bug fixes and F3 improvements)
Fix menu image scaling (so it is based on height and width)

Add 1% lows to F3 screen


### a1.2.0 (enemy improvements and player improvements)
Added seed map generation

Added minimap

Add player shield, can recharge

Add shield upgrades to armour

Fix the targeting, so that it works off current player bullet speed

Add spread range to weapons

Add new enemy types: missile, different fighter ship variants

Enemy Ships dont shoot each other

Change weapon system so that each weapon can be individually upgraded

Make damage effect proportional to damage taken

Improve enemy retreat state

Add Enemy weapons - shoot normally but might have small missiles to launch aswell

Add images for drone, missile ship and missile

Add screen shake

Make default weapons, and weapons for player and enemy

Add a weapon hotbar, so you can see which weapon is selected

Add weapon hotbar images

Add multiple player weapons: gatling gun, laser beam, normal gun, sniper, missile launcher, autoturrets

Add laser upgrades

Add zoom upgrade (and decrease max zoom)

### a1.2.1 (bug fixes and particle improvements)
Fix crash where missiles explode in the same frame that they were removed in

Fix smoke particles coming from centre of missiles

Add initial velocity to particles

Improve particle system

Add speed to ship rotation (ships don't rotate instantly)

### a1.3.0 (station)
Improve rendering images on top of each other (boost particles rendering order), possibly add z-layer

Change scrap drop to be proportional to enemy difficulty

Make scrap spawn with a random offset from dead ship

Add space stations

Better choosing of which station to go to for neutral ships

Enemies spawn from enemy stations

CONSOLE FUNCTIONALITY:
    arguements to functions
    up and down arrows to cycle previous functions
    clipboard functionality
    add transparent background
    console printing

Neutral ships travel between neutral stations

POSSIBLE: neutral ship grouping

New neutral ship image, cargo vessel

Accelerate onto position function