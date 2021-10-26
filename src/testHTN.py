

'''
FUCKING around file called testHTN.py instead of changing autoHTN.py

Tested the simple cases to see where we succeed as the TA told me to. 

Right now it works for most things that are wood based. 
This means we're able to craft wooden_axe, wooden_pickaxe, bench, and get more wood. 
But when we craft a wooden_axe and then want to craft a wooden_pickaxe. 
Instead of using the newly crafted axe to get more wood, we use punch_for_wood. 

This is when the goal is two wooden_axes, and one wooden_pickaxe
After we craft the wooden_axes, we still punch for wood. 
Would this be considered a heuristic we need to implement?

** result = [('op_punch_for_wood', 'agent'), ('op_craft_plank', 'agent'), 
('op_craft_bench', 'agent'), ('op_punch_for_wood', 'agent'), 
('op_craft_plank', 'agent'), ('op_craft_stick', 'agent'), 
('op_punch_for_wood', 'agent'), ('op_craft_plank', 'agent'), 
('op_craft_wooden_axe_at_bench', 'agent'), ('op_craft_wooden_axe_at_bench', 'agent'), 
('op_punch_for_wood', 'agent'), ('op_craft_plank', 'agent'), 
('op_craft_stick', 'agent'), ('op_punch_for_wood', 'agent'), 
('op_craft_plank', 'agent'), ('op_craft_wooden_pickaxe_at_bench', 'agent')]

'''

import pyhop
import json

def check_enough (state, ID, item, num):
	if getattr(state,item)[ID] >= num: return []
	return False

def produce_enough (state, ID, item, num):
	return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods ('have_enough', check_enough, produce_enough)

def produce (state, ID, item):
	return [('produce_{}'.format(item), ID)]

pyhop.declare_methods ('produce', produce)


def make_method (name, rule):
	def method (state, ID):
		return_val = [('op_' + name, ID)]
		if not rule.get('Consumes') is None:
			for elem in rule.get('Consumes').keys():
				#print ("We will consume ", elem)
				return_val.insert(0, ('have_enough', ID, elem, rule['Consumes'].get(elem)))
		if not rule.get('Requires') is None:
			for elem in rule.get('Requires').keys():
				return_val.insert(0, ('have_enough', ID, elem, rule['Requires'].get(elem)))
		return return_val
	make_method.__name__ = name
	return method


def declare_methods (data):
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first
    
	# sort the json on input
	for key, value in sorted(data['Recipes'].items(), key=lambda item: item[1]["Time"], reverse=False):
		string_of_interest = ""
		for string in key.split(" "):
			if "_" in string:
				string_of_interest = string
				break
		result_item = list(data['Recipes'].get(key).get('Produces').keys())[0]
		if string_of_interest == result_item or string_of_interest == "":
			method_name = "produce_" + result_item
		else:
			method_name = string_of_interest + "_" + result_item
		pyhop.declare_methods(method_name, make_method(key.replace(" ", "_"), value))	
		#print("PRINTING: KEY:", key, "  DATA:", data['Recipes'].get(key))
	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)				


def make_operator (name, rule):
	def operator (state, ID):
		if not rule.get('Consumes') is None:
			for elem in rule['Consumes'].keys():
				if not getattr(state, elem)[ID] >= rule['Consumes'].get(elem):
					return False
		if not rule.get('Requires') is None:
			for elem in rule['Requires'].keys():
				if not getattr(state, elem)[ID] >= rule['Requires'].get(elem):
					return False
		if not rule.get('Consumes') is None:
			for elem in rule['Consumes'].keys():
				setattr(state, elem, {ID: getattr(state, elem)[ID] - rule['Consumes'].get(elem)})
		for elem in rule['Produces']:
			setattr(state, elem, {ID: getattr(state, elem)[ID] + rule['Produces'].get(elem)})
		state.time[ID] -= rule['Time']
		return state
	operator.__name__ = "op_" + name.replace(" ", "_")
	return operator


def declare_operators (data):
	# your code here
    for key, value in sorted(data['Recipes'].items(), key=lambda item: item[1]["Time"], reverse=False):
        pyhop.declare_operators(make_operator(key, value))
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)


def add_heuristic (data, ID):
	# prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)
	def heuristic (state, curr_task, tasks, plan, depth, calling_stack):
		# your code here
		return False # if True, prune this branch

	pyhop.add_check(heuristic)


def set_up_state (data, ID, time=0):
	state = pyhop.State('state')
	state.time = {ID: time}

	for item in data['Items']:
		setattr(state, item, {ID: 0})

	for item in data['Tools']:
		setattr(state, item, {ID: 0})

	for item, num in data['Initial'].items():
		setattr(state, item, {ID: num})

	return state

def set_up_goals (data, ID):
	goals = []
	for item, num in data['Goal'].items():
		goals.append(('have_enough', ID, item, num))

	return goals

if __name__ == '__main__':
	rules_filename = 'crafting.json'

	with open(rules_filename) as f:
		data = json.load(f)

	state = set_up_state(data, 'agent', time=239) # allot time here
	goals = set_up_goals(data, 'agent')

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	# pyhop.print_operators()
	# pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	pyhop.pyhop(state, goals, verbose=3)
	#pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)
