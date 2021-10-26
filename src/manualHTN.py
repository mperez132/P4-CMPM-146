import pyhop

'''begin operators'''

#    "punch for wood": {
#      "Produces": {
#        "wood": 1
#      },
#      "Time": 4
#    },
def op_punch_for_wood (state, ID):
	if state.time[ID] >= 4:
		state.wood[ID] += 1
		state.time[ID] -= 4
		return state
	return False

#    "craft wooden_axe at bench": {
#      "Produces": {
#        "wooden_axe": 1
#      },
#      "Requires": {
#        "bench": 1
#      },
#      "Consumes": {
#        "plank": 3,
#        "stick": 2
#      },
#      "Time": 1
#    },
def op_craft_wooden_axe_at_bench (state, ID):
	if state.time[ID] >= 1 and state.bench[ID] >= 1 and state.plank[ID] >= 3 and state.stick[ID] >=2:
		state.wooden_axe[ID] += 1
		state.plank[ID] -= 3
		state.stick[ID] -= 2
		state.time[ID] -= 1
		return state
	return False

# TODO: Our code goes below
#    "wooden_axe for wood": {
#      "Produces": {
#        "wood": 1
#      },
#      "Requires": {
#        "wooden_axe": 1
#      },
#      "Time": 2
#    },
def op_wooden_axe_for_wood (state, ID):
	if state.time[ID] >= 2 and state.wooden_axe[ID] >= 1:
		state.wood[ID] += 1
		state.time[ID] -= 2
		return state
	return False

#    "craft bench": {
#      "Produces": {
#        "bench": 1
#      },
#      "Consumes": {
#        "plank": 4
#      },
#      "Time": 1
#    },
def op_craft_bench (state, ID):
	if state.time[ID] >= 1 and state.plank[ID] >= 4:
		state.bench[ID] += 1
		state.plank[ID] -= 4
		state.time[ID] -= 1
		return state
	return False

#    "craft plank": {
#      "Produces": {
#        "plank": 4
#      },
#      "Consumes": {
#        "wood": 1
#      },
#      "Time": 1
#    },
def op_craft_plank (state, ID):
	if state.time[ID] >= 1 and state.wood[ID] >= 1:
		state.plank[ID] += 4
		state.wood[ID] -= 1
		state.time[ID] -= 1
		return state
	return False

# 	   "craft stick": {
#      "Produces": {
#        "stick": 4
#      },
#      "Consumes": {
#        "plank": 2
#      },
#      "Time": 1
#    },
def op_craft_stick(state, ID):
	if state.time[ID] >= 1 and state.plank[ID] >= 2:
		state.stick[ID] += 4
		state.plank[ID] -= 2
		state.time[ID] -= 1
		return state
	return False

pyhop.declare_operators (op_punch_for_wood, op_craft_wooden_axe_at_bench, op_wooden_axe_for_wood, op_craft_bench, op_craft_plank, op_craft_stick)

'''end operators'''

def check_enough (state, ID, item, num):
	if getattr(state,item)[ID] >= num: return []
	return False

def produce_enough (state, ID, item, num):
	if item == 'wood':
		if state.made_wooden_axe[ID]:
			return [('produce', ID, item), ('have_enough', ID, item, num)]
		if state.made_bench[ID]:
			if state.stick[ID] >= 2:
				if state.plank[ID] >= 3: # If you have enough of everything it's always worth it
						return [('produce', ID, 'wooden_axe'), ('have_enough', ID, item, num)]
				else: # If you need planks and it's worth it
					if state.wood[ID] >= 1:
						return [('produce', ID, 'plank'), ('have_enough', ID, item, num)]
			# If you need sticks and it's worth it
			elif state.plank[ID] >= 5 or (state.plank[ID] >= 3 and num > 2):
				return [('produce', ID, 'stick'), ('have_enough', ID, item, num)]
		else:
			if state.stick[ID] >= 2:
				if state.plank[ID] >= 7 or (state.plank[ID] >= 4 and num > 1): # If you have enough of everything it's worth or with enough need
						return [('produce', ID, 'bench'), ('have_enough', ID, item, num)]
				else: # If you need planks and it's worth it
					if state.wood[ID] >= 1:
						return [('produce', ID, 'plank'), ('have_enough', ID, item, num)]
			# If you need sticks and it's worth it
			elif state.plank[ID] >= 9 or (state.plank[ID] >= 7 and state.wood[ID] >= 1 and num > 1) or (state.plank[ID] >= 2 and state.wood[ID] >= 2 and num > 1):
				return [('produce', ID, 'stick'), ('have_enough', ID, item, num)]
			else:
				if state.wood[ID] >= 1 and num > 5: # TODO: Fix this case
					return [('produce', ID, 'plank'), ('have_enough', ID, item, num)]
	elif item == 'stick': 
		pass
	elif item == 'plank':
		pass
	return [('produce', ID, item), ('have_enough', ID, item, num)]

# TODO: Our code goes in this method
def produce (state, ID, item):
	if item == 'wood': 
		if state.made_wooden_axe[ID]:
			return [('wooden_axe_wood', ID)]
		else:
			return [('produce_wood', ID)]
	elif item == 'wooden_axe':
		# this check to make sure we're not making multiple axes
		if state.made_wooden_axe[ID] is True:
			return False
		else:
			state.made_wooden_axe[ID] = True
		return [('produce_wooden_axe', ID)]
	elif item == 'bench':
		# this check to make sure we're not making multiple benches
		if state.made_bench[ID]:
			return False
		else:
			state.made_bench[ID] = True
		return [('produce_bench', ID)]
	elif item == 'plank':
		return [('produce_plank', ID)]
	elif item == 'stick':
		return [('produce_stick', ID)]
	else:
		return False

pyhop.declare_methods ('have_enough', check_enough, produce_enough)
pyhop.declare_methods ('produce', produce)

'''begin recipe methods'''

def punch_for_wood (state, ID):
	return [('op_punch_for_wood', ID)]

def craft_wooden_axe_at_bench (state, ID):
	return [('have_enough', ID, 'bench', 1), ('have_enough', ID, 'stick', 2), ('have_enough', ID, 'plank', 3), ('op_craft_wooden_axe_at_bench', ID)]

def wooden_axe_for_wood (state, ID):
	return [('have_enough', ID, 'wooden_axe', 1), ('op_wooden_axe_for_wood', ID)]

def craft_bench (state, ID):
	return [('have_enough', ID, 'plank', 4), ('op_craft_bench', ID)]

def craft_plank (state, ID):
	return [('have_enough', ID, 'wood', 1), ('op_craft_plank', ID)]

def craft_stick (state, ID):
	return [('have_enough', ID, 'plank', 2), ('op_craft_stick', ID)]

# TODO: Our code goes below
pyhop.declare_methods ('produce_wood', punch_for_wood)
pyhop.declare_methods ('wooden_axe_wood', wooden_axe_for_wood)
pyhop.declare_methods ('produce_wooden_axe', craft_wooden_axe_at_bench)
pyhop.declare_methods ('produce_bench', craft_bench)
pyhop.declare_methods ('produce_plank', craft_plank)
pyhop.declare_methods ('produce_stick', craft_stick)

'''end recipe methods'''

# declare state
state = pyhop.State('state')
state.wood = {'agent': 0}
#state.time = {'agent': 4}
state.time = {'agent': 46}
state.wooden_axe = {'agent': 0}
state.made_wooden_axe = {'agent': False}
# TODO: Our code goes below
state.bench = {'agent': 0}
state.made_bench = {'agent': False}
state.plank = {'agent': 0}
state.stick = {'agent': 0}

# pyhop.print_operators()
# pyhop.print_methods()

#pyhop.pyhop(state, [('have_enough', 'agent', 'wood', 1)], verbose=3)
pyhop.pyhop(state, [('have_enough', 'agent', 'wood', 12)], verbose=3)