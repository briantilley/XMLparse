#! /usr/bin/python3

# Parse a target structure and XML source to check if the target structure
# is contained within the source. Print structural matches on separate lines.
#
# note: A "friend" is a child of a source node that matches (structurally)
# a child of the target node.

# ---------------------------------- IMPORTS ----------------------------------

import sys
import re
import xml.etree.ElementTree as ET

# --------------------------------- FUNCTIONS ---------------------------------

# return a list of subtrees of root
def listify_children(root):
	child_list = []

	for child in root:
		child_list.append(child)

	return child_list

# ensure target children are a subset of root children
# matching is order-sensitive (third target child must be third-matched source child)
def setwise_match(source_root, target_root):
	source_size = len(source_root)
	target_size = len(target_root)

	# base case
	if target_size == 0:
		return True

	# need more potential friends than target children
	if source_size < target_size:
		return False

	# list children from each tree
	source_children = listify_children(source_root)
	target_children = listify_children(target_root)

	# keep source nodes from being checked more than once
	j = 0

	# find a friend for each target child
	for i in range(0, target_size):
		friend_found = False

		# seek the first available friend
		while j < source_size:
			if match_structures(source_children[j], target_children[i]):
				friend_found = True
				j += 1
				break
			j += 1

		# all target children require friends
		# fail if too few potential friends remain
		if not friend_found or source_size - j < target_size - (i + 1):
			return False

	# all target children have found friends
	return True

# match root-level structure
match_call_counter = 0
def match_structures(source_root, target_root):
	global match_call_counter
	match_call_counter += 1

	return (source_root.tag == target_root.tag) and setwise_match(source_root, target_root)

# return a list of all first-order children of each element in the provided list
def one_level_in(parent_list):
	children = []
	for parent in parent_list:
		for child in parent:
			children.append(child)
	return children

# (breadth-first) seek target structure anywhere within the source
def exhaustive_match_bfs(source_root, target_root):
	parent_list = list(source_root)
	while len(parent_list) > 0:
		for parent in parent_list:
			if match_structures(parent, target_root):
				return True

		parent_list = one_level_in(parent_list)

	return False

# (depth-first) seek target structure anywhere within the source
def exhaustive_match(source_root, target_root):
	if match_structures(source_root, target_root):
		return True

	for child in source_root:
		if exhaustive_match(child, target_root):
			return True

	return False

# (breadth-first) return the roots of all structures matching the target
def exhaustive_search_bfs(source_root, target_root):
	parent_list = list(source_root)
	match_list = []

	while len(parent_list) > 0:
		for parent in parent_list:
			if match_structures(parent, target_root):
				match_list.append(parent)

		parent_list = one_level_in(parent_list)

	return match_list

# (depth-first) return the roots of all structures matching the target
def exhaustive_search(source_root, target_root, match_list=[]):
	if match_structures(source_root, target_root):
		match_list.append(source_root)

	for child in source_root:
		exhaustive_search(child, target_root, match_list)

	return match_list

# print the tree given with indentation
stindent = 0
def show_tree(root):
	global stindent

	print("  " * stindent + root.tag)

	stindent += 1
	for child in root:
		show_tree(child)
	stindent -= 1

# process argument and load XML from text
def get_root_from_arg(arg):
	if re.match(".*[.].*", arg):
		return ET.parse(arg).getroot()
	return ET.fromstring(arg)

# --------------------------------- PROCEDURE ---------------------------------

# usage check
if len(sys.argv) != 3:
	print("usage:", sys.argv[0], "source_XML target_structure")
	sys.exit(1)

# obtain XML trees
source_root = get_root_from_arg(sys.argv[1])
target_root = get_root_from_arg(sys.argv[2])

# obtain all matches present, then print each on its own line
matches = exhaustive_search(source_root, target_root)
for match in matches:
	print(ET.tostring(match, encoding="UTF-8").decode())