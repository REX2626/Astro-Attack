# Astro-Attack


TODO:


Add rotation acceleration, so red_ship doesn't immediately stop rotating

Add ship colliding with asteroids

Add asteroid class

Add alien class

DONE:
Fix angle, so it is between +180 and -180

CHUNKS is globalled in objects.py

When updating entities, don't update every entity's chunk 
In entity.update(), if the entity moved, put entity into it's new chunk