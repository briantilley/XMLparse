#! /usr/bin/python3

# Parse a target structure and XML source to check if the target structure
# is contained within the source. Print structural matches on separate lines.
#
# note: A "friend" is a child of a source node that matches (structurally)
# a child of the target node.

# ---------------------------------- IMPORTS ----------------------------------

import sys
import re
import xml.etree.ElementTree as et
from xml.dom import minidom

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

# verify whether all attributes from target_node are present and matching in source_node
# target attribute values are interpreted as regex
def attribute_subset_match(source_node, target_node):
	target_size = len(target_node.attrib)

	if target_size == 0:
		return True

	if len(source_node.attrib) < target_size:
		return False

	try:
		for key in target_node.attrib:
			# target attribute values surrounded in "re{...}" are interpreted as regex patterns
			if re.match("re\{.*\}", target_node.attrib[key]):
				attribute_matches = re.match(target_node.attrib[key][3:-1], source_node.attrib[key])
			else:
				attribute_matches = (target_node.attrib[key] == source_node.attrib[key])

			if not attribute_matches:
				return False
	except KeyError: # key does not exist in source
		return False

	return True

# match root-level structure
def match_structures(source_root, target_root):

	return (source_root.tag == target_root.tag) and attribute_subset_match(source_root, target_root) and setwise_match(source_root, target_root)

# return a list of all first-order children of each element in the provided list
def one_level_in(parent_list):
	children = []
	for parent in parent_list:
		for child in parent:
			children.append(child)
	return children

# (breadth-first or depth-first) seek target structure anywhere within the source
def exhaustive_match(source_root, target_root, mode="bfs"):
	if mode is "bfs":
		parent_list = list(source_root)
		while len(parent_list) > 0:
			for parent in parent_list:
				if match_structures(parent, target_root):
					return True

			parent_list = one_level_in(parent_list)

	elif mode is "dfs":
		if match_structures(source_root, target_root):
			return True

		for child in source_root:
			if exhaustive_match(child, target_root, "dfs"):
				return True

	return False

# (breadth-first or depth-first) return the roots of all structures matching the target
def exhaustive_search(source_root, target_root, mode= "dfs", match_list=[]):
	if mode == "dfs":
		if match_structures(source_root, target_root):
			match_list.append(source_root)

		for child in source_root:
			exhaustive_search(child, target_root, "dfs", match_list)

	elif mode == "bfs":
		parent_list = list(source_root)

		while len(parent_list) > 0:
			for parent in parent_list:
				if match_structures(parent, target_root):
					match_list.append(parent)

			parent_list = one_level_in(parent_list)

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
		return et.parse(arg).getroot()
	return et.fromstring(arg)

# return the XML text equivalent of a tree
def get_source(node):
	return minidom.parseString(et.tostring(node, encoding="UTF-8").decode()).toprettyxml()

# --------------------------------- PROCEDURE ---------------------------------

if __name__ == "__main__":

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
		print(get_source(match))