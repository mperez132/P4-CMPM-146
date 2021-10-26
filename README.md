README for HTN Planning for Minecraft assignment, CMPM146

Moises Perez (mperez86)
Edwin Wang ()

-----------------------------------------------------

Code files: autoHTN.py, manualHTN.py, README.md

----------------------------------------------------

Our autoHTN.py works for all the cases besides the last 2 within the given time.
We ARE finishing these cases just not under the specific time. 

i. Given {}, achieve {'cart': 1, 'rail': 10} [time <= 175]    (finishing when [time <= 188])
j. Given {}, achieve {'cart': 1, 'rail': 20} [time <= 250]    (finishing when [time <= 255])


Heuristics: 
The core heuristics for this program are the used to check if we have too much of an item or we have no time. 
Before we call too_much_of_item in our heuristics. We update the item_maxes in set_up_state by one for all our 
tools and update the initial values if we start off with any. We initially had a problem where we'd be making 
too much of a certain item and do nothing else. Our other heuristic is the no_time definition. It checks whether 
the current states time is less than zero. If it's less than zero then we prune the branch. 
