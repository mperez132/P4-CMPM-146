# python autoHTN.py
import pyhop
import json
from collections import OrderedDict

item_maxes = {}


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
		return_val = []
		fail_recipe = rule[0][1]
		for recipe_name, recipe in sorted(rule, key=lambda item: item[1].get("Time"), reverse=False):
			recipe_works = True
			if not recipe.get("Consumes") is None:
				for item in recipe.get("Consumes").keys():
					if recipe_works and getattr(state, item)[ID] < recipe.get("Consumes").get(item):
						recipe_works = False
			if not recipe.get("Requires") is None:
				for item in recipe.get("Requires").keys():
					if recipe_works and getattr(state, item)[ID] < recipe.get("Requires").get(item):
						recipe_works = False
			if recipe_works:
				return_val = [("op_" + recipe_name.replace(" ", "_"), ID)]
				break
			else:
				fail_recipe = recipe
		if return_val == []:
			if not fail_recipe.get('Consumes') is None:
				for elem in fail_recipe.get('Consumes').keys():
					return_val.insert(0, ('have_enough', ID, elem, fail_recipe['Consumes'].get(elem)))
			if not fail_recipe.get('Requires') is None:
				for elem in fail_recipe.get('Requires').keys():
					return_val.insert(0, ('have_enough', ID, elem, fail_recipe['Requires'].get(elem)))
		return return_val
	method.__name__ = name
	return method


def declare_methods (data):
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first

	# your code here
	# sort the json on input
	created_methods = []
	for key, _ in sorted(data['Recipes'].items(), key=lambda item: item[1]["Time"], reverse=False):
		result_item = list(data['Recipes'].get(key).get('Produces').keys())[0]
		method_name = "produce_" + result_item
		if not method_name in created_methods:
			if result_item == "rail":
				print("RESULT ITEM IS RAIL")
			recipe_dict_list = []
			for recipe in data['Recipes'].items():
				if list(recipe[1].get('Produces').keys())[0] == result_item:
					recipe_dict_list.append(recipe)
			pyhop.declare_methods(method_name, make_method(method_name, recipe_dict_list))
		created_methods.append(method_name)


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
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)
	for key, value in sorted(data['Recipes'].items(), key=lambda item: item[1]["Time"], reverse=False):
		pyhop.declare_operators(make_operator(key, data['Recipes'].get(key)))


def add_heuristic (data, ID):
	# prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)
	# depth_visits = {}
	# def depth_visited_too_much (state, curr_task, tasks, plan, depth, calling_stack):
	# 	if depth_visits.get(depth) is None:
	# 		depth_visits.update({depth: 1})
	# 	else:
	# 		depth_visits.update({depth: depth_visits.get(depth) + 1})
	# 	return depth_visits.get(depth) > 500

	def too_much_of_item (state, curr_task, tasks, plan, depth, calling_stack):
		for item_name in item_maxes.keys():
			if getattr(state, item_name)[ID] > item_maxes.get(item_name):
				return True
		return False
		
		
	def no_time (state, curr_task, tasks, plan, depth, calling_stack):
		if state.time[ID] < 0:
			return True
		return False # if True, prune this branch
	
	# pyhop.add_check(depth_visited_too_much)
	pyhop.add_check(too_much_of_item)
	pyhop.add_check(no_time)


def set_up_state (data, ID, time=0):
	state = pyhop.State('state')
	state.time = {ID: time}

	for item in data['Items']:
		setattr(state, item, {ID: 0})

	for item in data['Tools']:
		setattr(state, item, {ID: 0})
		item_maxes.update({item: 1})

	for item, num in data['Initial'].items():
		setattr(state, item, {ID: num})
		if item_maxes.get(item) is not None and num > item_maxes.get(item):
			item_maxes.update({item: num})

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

	state = set_up_state(data, 'agent', time=255) # allot time here
	goals = set_up_goals(data, 'agent')

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	# pyhop.print_operators()
	# pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	pyhop.pyhop(state, goals, verbose=3)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)
