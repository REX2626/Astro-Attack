# Astro-Attack


## TODO:
Give boost particles a velocity

Change colour of enemy bullets

Improve particle system

Make ships have a thruster animation

Add targeting icon (space engineers)

Add ammo system

Enemies drop ammo

Fix bullets going through asteroids

Edge of button boundaries are not clickable (click for button rectangle not text label)

Fix first full_screen click not moving the mouse properly

MOUSE_DOWN counts for scroll_wheel and right_click

Add button effect when hovered over

Add slider for menu buttons

Add padding ability to buttons

---
Improve Neutral ship functionality - better decision making in fights (who to shoot at, enemy or player)

Neutral ship when attacking, will only become passive again once the whole group of enemies or defeated

Attack state: make fighting seem more natural
    Aim to where the player is predicted to be in the future for more accurate shooting
    POTENTIAL: dodging either incoming bullets or for the enemy to have a random strafe

Retreat state: If enemy health is low and player health is high - retreat

---

### POTENTIAL

Have different shoot speed for enemy and player

Add money system, different currencies, get cash from killing

Add shop system

Add loot system

Add fuel system


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