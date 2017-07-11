#! /usr/bin/python3

# parse a target structure and XML source to check if the target structure
# is contained within the source
#
# note: a "friend" is a child of a source node that matches (structurally)
# a child of the target node

import sys
import re
import xml.etree.ElementTree as ET

recursive_call_counter = 0
indent_count = 0

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

	global indent_count
	indent_count += 1

	# list children from each tree
	src_childs = listify_children(source_root)
	tgt_childs = listify_children(target_root)

	# keep source nodes from being checked more than once
	j = 0

	# find a friend for each target child
	for i in range(0, target_size):
		friend_found = False

		# seek the first available friend
		while j < source_size:
			if match_structures(src_childs[j], tgt_childs[i]):
				friend_found = True
				j += 1
				break
			j += 1

		# all target children require friends
		# fail if too few potential friends remain
		if not friend_found or source_size - j < target_size - (i + 1):
			indent_count -= 1
			return False

	# all target children have found friends
	indent_count -= 1
	return True

def match_structures(source_root, target_root):
	global recursive_call_counter
	global indent_count

	recursive_call_counter += 1

	print("  " * indent_count + target_root.tag)
	smatch = setwise_match(source_root, target_root)
	return (source_root.tag == target_root.tag) and smatch


def get_root_from_arg(arg):
	if re.match(".*[.].*", arg):
		return ET.parse(arg).getroot()
	return ET.fromstring(arg)

stindent = 0
def showtree(root):
	global stindent

	print("  " * stindent + root.tag)

	stindent += 1
	for child in root:
		showtree(child)
	stindent -= 1

# --------------------------------- PROCEDURE ---------------------------------

if len(sys.argv) != 3:
	print("bad usage")
	sys.exit(1)

src_root = get_root_from_arg(sys.argv[1])
tgt_root = get_root_from_arg(sys.argv[2])

recursive_call_counter = 0

pre = ""
if not match_structures(src_root, tgt_root):
	pre = "non-"

print(pre + "match determined in %d recursive calls" % recursive_call_counter)

# -----------------------------------------------------------------------------

# # parse XML from document
# src_root = ET.parse(sys.argv[1]).getroot()

# # parse XML from string
# tgt_root = ET.fromstring(sys.argv[2])

# # print(listify_children(tgt_root))
# for child in listify_children(tgt_root):
# 	print(child.tag)

# -----------------------------------------------------------------------------

# # test recursive match_structures/setwise_match recursion
# source = "<a><b></b><b><c></c></b></a>"
# target = "<a><b><c></c></b></a>"
# print("should match")
# print(match_structures(ET.fromstring(source), ET.fromstring(target)))

# source = "<a><b></b><b><c></c></b></a>"
# target = "<a><c><b></b></c></a>"
# print("should not match")
# print(match_structures(ET.fromstring(source), ET.fromstring(target)))

# source = "<x></x>"
# target = "<x></x>"
# print("should match")
# print(match_structures(ET.fromstring(source), ET.fromstring(target)))

# source = "<a><b></b><b><c></c></b></a>"
# target = "<a><b><c></c></b><d></d><e></e></a>"
# print("should not match")
# print(match_structures(ET.fromstring(source), ET.fromstring(target)))