from xml.dom import Node
import logging


def get_child(parent_node, tag_name):
	if parent_node is None:
		# logging.warn("get_child: no parent_node")
		return None
	node = ( n for n in parent_node.childNodes if n.nodeType == Node.ELEMENT_NODE and n.tagName == tag_name )
	# if not node:
	# 	logging.warn("get_child: no %s node in %s", tag_name, parent_node)
	return next(node, None)


def list_children(parent_node, tag_name):
	if parent_node is None:
		# logging.warn("list_children: no parent_node")
		return []
	return [ n for n in parent_node.childNodes if n.nodeType == Node.ELEMENT_NODE and n.tagName == tag_name ]

def iter_children(parent_node, tag_name):
	if parent_node is None:
		# logging.warn("iter_children: no parent_node")
		pass
	else:
		for n in parent_node.childNodes:
			if n.nodeType == Node.ELEMENT_NODE and n.tagName == tag_name:
				yield n

def add_child(parent_node, tag_name, text_value = None):
	if parent_node is None:
		# logging.warn("add_child: no parent_node")
		return None
	node = parent_node.ownerDocument.createElement(tag_name)
	parent_node.appendChild(node)
	if text_value is not None:
		node_text = parent_node.ownerDocument.createTextNode(str(text_value))
		node.appendChild(node_text)
	return node


def set_text(tag_node, text_value = None):
	if not tag_node:
		logging.warn("set_text: no tag_node")
		return False
	tnode = tag_node.firstChild
	if tnode is None:
		if text_value is not None:
			tnode = tag_node.ownerDocument.createTextNode(str(text_value))
			tag_node.appendChild(tnode)
		return True
	if tnode.nodeType == Node.TEXT_NODE:
		if text_value is None:
			tagName.removeChild(tnode)
		else:
			tnode.data = str(text_value)
		return True
	logging.warn("can't handle %s child node %s", tag_node, tnode)
	return False


def get_text(tag_node):
	if not tag_node:
		logging.warn("get_text: no tag_node")
		return None
	tnode = tag_node.firstChild
	if tnode is None:
		return None
	if tnode.nodeType == Node.TEXT_NODE:
		return tnode.data
	logging.warn("get_node found no text node in %s", tag_node)
	return None


def remove_whitespace(tag_node):
	"""removes irrelevant whitespace children"""
	if not tag_node:
		return True
	was_modified = False
	for n in list(tag_node.childNodes):
		if n.nodeType == Node.TEXT_NODE and not n.data.strip():
			tag_node.removeChild(n)
			was_modified = True
	return was_modified
