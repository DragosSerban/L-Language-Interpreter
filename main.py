from sys import argv
from .Lexer import Lexer

# we will create a parse tree
class Node:
	def __init__(self, value, children=[]):
		self.value = value
		self.children = children

	def __repr__(self, level=0):
        # Helper function to recursively print the tree
		ret = "\t" * level + repr(self.value) + "\n"
		for child in self.children:
			ret += child.__repr__(level + 1)
		return ret

	def parse_tokens(self, tokens):
		if tokens:
			if tokens[0][0] == "NUM":
				self.children.append(Node(tokens.pop(0))) # add num to the children list

			elif tokens[0][0] == "VAR":
				self.children.append(Node(tokens.pop(0))) # add var to the children list

			elif tokens[0][0] == "ADD" or tokens[0][0] == "CONCAT":
				# we encounter an add / concat function
				node = Node(tokens.pop(0), [])
				# create the tree recursively based on what follows in the tokens list
				while tokens:
					if (tokens[0][0] == "NUM"):
						node.children.append(Node(tokens.pop(0)))
					elif tokens[0][0] == "OPEN_BRACKET":
						node.parse_tokens(tokens)
					elif tokens[0][0] == "CLOSE_BRACKET":
						break
				self.children.append(node)

			elif tokens[0][0] == "OPEN_BRACKET":
				# if we encounter an open bracket, we create a new node,
				# we put all elements in the bracket in its children list
				node = Node(tokens.pop(0), [])
				while tokens:
					if (tokens[0][0] == "CLOSE_BRACKET"):
						# close the bracket for the list
						tokens.pop(0)
						break
					else:
						# else if we encounter something else (e.g. lambda function),
						# we call this recursive function again
						node.parse_tokens(tokens)
				self.children.append(node)

			elif tokens[0][0] == "LAMBDA":
				# we encounter a lambda function, so we create a new custom node in the tree
				# its value will be the lambda name and the name of the var
				string = tokens.pop(0)[1] + " " + tokens.pop(0)[1] + " "
				tokens.pop(0) # we pop the end of the lambda function (":")
				# if there are more lambda functions that follow it directly, we use them in order to create a single node
				# for all of these lambda functions
				while tokens[0][0] == "LAMBDA":
					string += tokens.pop(0)[1] + " " + tokens.pop(0)[1] + " "
					tokens.pop(0) # pop ":"
				lambda_node = Node(("LAMBDA", string), []) # create the lambda node
				# parse what follows the lambda definition (function body)
				if tokens[0][0] == "OPEN_BRACKET":
					lambda_node.parse_tokens(tokens)
				elif tokens[0][0] == "NUM" or tokens[0][0] == "VAR":
					lambda_node.children.append(Node(tokens[0], []))
					tokens.pop(0) # pop the token
				self.children.append(lambda_node)

# function that calcules the sum of some numbers / list of numbers
def calculate_sum(child):
	new_children_sum = 0 # initial value is 0

	# solve all lambda functions inside this add function's arguments
	child = solve_tree(child)

	# add all elements
	for i in range(len(child.children)):
		c = child.children[i]
		if c.value[0] == "NUM":
			new_children_sum += int(c.value[1]) # add number
		elif c.value[0] == "OPEN_BRACKET":
			new_children_sum += calculate_sum(c) # calculate sum of list elements
		elif c.value[0] == "ADD":
			new_children_sum += calculate_sum(c)
		elif c.value[0] == "CONCAT":
			# encountered a concat function, we solve it first, and then we add the resulting elements
			child = solve_tree(child)
			new_children_sum += calculate_sum(child)

	return new_children_sum

# function used to change a variable's name with its value (recursively)
def update_var(node, var_to_change, value_to_change):
	for i in range(len(node.children)):
		child = node.children[i]
		# if we encounter another lambda function that uses the same parameter name
		# we pass; dont update with value inside that function
		dont_update = False
		if child.value[0] == "LAMBDA":
			for j in range(1, len(child.value[1].split(" ")), 2):
				if child.value[1].split(" ")[j] == var_to_change:
					dont_update = True
		if dont_update:
			continue
		# we didnt find another function with the same parameter name => it's safe to update
		update_var(child, var_to_change, value_to_change) # recursivity
		if child.value[0] == "VAR" and child.value[1] == var_to_change:
			node.children[i] = value_to_change

# applies a lambda function
def apply_lambda(open_bracket_node):
	lambda_node = open_bracket_node.children[0] # get lambda node
	var = lambda_node.value[1].split(" ")[1] # get variable name
	if (len(lambda_node.value[1].split(" ")) > 3):
		# if there are more lambda functions, one after another
		# we verify if there are any more that use the same var name
		# if so, we won't apply the function
		for i in range (3, len(lambda_node.value[1].split(" ")), 2):
			if lambda_node.value[1].split(" ")[i] == var:
				var = ""

	if lambda_node.children[0].value[0] == "LAMBDA":
		# if next node is a lambda node update current lambda function variable inside
		# the following lambda function
		update_var(lambda_node, var, open_bracket_node.children[1])
		return lambda_node.children[0]

	if lambda_node.children[0].value[0] == "OPEN_BRACKET":
		# if next node is an open bracket
		update_var(lambda_node, var, open_bracket_node.children[1]) # update var with value
		return lambda_node.children[0]

	if lambda_node.children[0].value[0] == "VAR":
		# if the function body is a var, we verify if it is the var we are searching for
		# we return the argument of the lambda function as a result;
		# else we return the var as a result
		if lambda_node.children[0].value[1] == var:
			return open_bracket_node.children[1]
		return lambda_node.children[0]

	if lambda_node.children[0].value[0] == "NUM":
		# if the function body is a number, then its result is the same number
		return lambda_node.children[0]

def solve_tree(node):
	if node.value[0] == "OPEN_BRACKET":
		# case 1: empty list
		if not node.children:
			return node

		# case 2: concatenation
		if node.children[0].value[0] == "CONCAT":
			concat_arg = node.children[0].children[0] # arg for the concat func
			concat_result = []
			# concatenate elements
			for elem_to_concat in concat_arg.children:
				if (elem_to_concat.value[0] == "OPEN_BRACKET"):
					# we have a list of elements / function to concat
					for list_elem in elem_to_concat.children:
						concat_result.append(solve_tree(list_elem))
				else:
					# we concat a number
					concat_result.append(elem_to_concat)
			return Node(("OPEN_BRACKET", "("), concat_result) # return the concatenation result

		# case 3: addition
		if node.children[0].value[0] == "ADD":
			# calculate the sum and return it as a node
			sum_result = calculate_sum(node.children[0])
			return Node(("NUM", str(sum_result)), [])

		# case 4: lambda function
		if node.children[0].value[0] == "LAMBDA":
			# we encounter a lambda function / lambda functions
			words = node.children[0].value[1].split(" ")
			# verify if there are more lambda headers in this node
			if (len(words) > 3):
				# change current node's value (which is first lambda's open bracket) to the next
				# lambda function header and apply the current lambda function
				node.value = ("LAMBDA", " ".join(words[2:]))
				node.children = [apply_lambda(node)]
			else:
				# apply lambda on current node
				node = apply_lambda(node)
				node = solve_tree(node)
			return node

		# else update tree recursively for each of the children of this node (list)
		for i in range(len(node.children)):
			node.children[i] = solve_tree(node.children[i])

			# if solve_tree returned a non-called lambda function, we call it
			if node.children[i].value[0] == "LAMBDA":
				return solve_tree(node)

	else:
		# else update tree recursively for each of the children of this node
		for i in range(len(node.children)):
			node.children[i] = solve_tree(node.children[i])
	return node

def tree_contains_lambda(node):
	# search the parse tree for lambda functions
    if node.value[0] == "LAMBDA":
        return True  # lambda function found

    for child in node.children:
		# search recursively
        if tree_contains_lambda(child):
            return True

    return False # lambda function not found

def create_output_string(node, depth=0, output_string=""):
	# visit each node in the modified tree and save the value of the node to the output string
	if node.value[0] == "OPEN_BRACKET":
		# start the list
		if output_string != "":
			output_string += " "
		output_string += "("
	elif node.value[0] == "NUM":
		# save the number to the output
		if output_string != "":
			output_string += " "
		output_string += node.value[1]
	for child in node.children:
		# visit node's children recursively
		output_string = create_output_string(child, depth + 1, output_string)
	if node.value[0] == "OPEN_BRACKET":
		# close the list
		if output_string != "" and output_string[len(output_string) - 1] != "(":
			output_string += " "
		output_string += ")"

	return output_string

def main():
	if len(argv) != 2:
		return
	
	filename = argv[1]
	# define the specification using regex
	spec = [("SPACE", "(\\ *\n*\t*)+"), ("NUM", "[0-9]+"), ("OPEN_BRACKET", "\\("), ("CLOSE_BRACKET", "\\)"),
		 ("ADD", "\\+"), ("CONCAT", "\\+\\+"), ("LAMBDA", "lambda"), ("VAR", "([a-z]*[A-Z]*)+"), ("LAMBDA_START", ":")]

	with open(filename, 'r') as file:
		# open the file, read the content, use the lex function on a Lexer object to get the tokens (we skip SPACE matched strings)
		file_content = file.read()
		parsed_content = [token for token in Lexer(spec).lex(file_content) if token[0] != "SPACE"]

		# we will create a parse tree
		tree = Node(("START", "START"), []) # the root node will be "START"
		tree.parse_tokens(parsed_content) # create the tree using parse_tokens function

		# process the tree
		tree = solve_tree(tree)

		# create the output string and print it
		output_string = create_output_string(tree)
		print(output_string)

if __name__ == '__main__':
    main()
