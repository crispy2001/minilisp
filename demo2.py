#!/usr/bin/python3

def parseTree(code):
	# split tokens to recurrence
	tokens = code.replace('(', ' ( ').replace(')', ' ) ').split()
	tree_token = []
	for token in tokens:
		if token not in ['(', ')']:
			tree_token.append(f'"{token}"')
		else:
			tree_token.append(token)
		if token != '(':
			tree_token.append(',')
	return eval(''.join(['(', *tree_token, ')']))

# check is ID or not
def isID(s):
	# digit = 0-9, letter = a-z
	# definition of ID: letter(letter | - | digit)*
	c, *r = s
	if not c.islower():
		return False
	for c in r:
		if not (c.islower() or c == '-' or(int(c) >= int('0') and int(c) <= int('9'))):
			return False
	return True


class Function:
	def __init__(self, name = '', func = None, arg_type = None, n_args=''):
		self.name = name
		self.func = func
		self.arg_type = arg_type
		self.n_args = n_args
		self.locked = False

	def __call__(self, *args):
		self._check_args(args)
		return self.func(*args)
	
	def _check_args(self, args):
		n_args = len(args)
		assert eval(f'{n_args} {self.n_args}'), (
			f' expect number of arguments {self.n_args}, got {n_args}')
		if self.arg_type is not None:
			if self.arg_type == 'same':
				arg_type = type(args[0])
			else:
				arg_type = self.arg_type
			for i, arg in enumerate(args):
				if type(arg) != arg_type:
					n = i + 1
					t1 = getattr(arg_type, '__name__', arg_type).lower()
					t2 = getattr(type(arg), '__name__', type(arg)).lower()

def evaluate(statement, oper, level = 0):
	if isinstance(statement, tuple):

		primary = statement[0]
		
		if primary == 'define':
			# Define a variable in oper
			_, name, value = statement
			if type(value) is tuple:

				temp_oper = oper.copy()
				temp_oper[name] = Function(name)
				temp_oper[name].locked = True
				temp = evaluate(value, temp_oper, level + 1)
				if callable(temp) and temp != temp_oper[name]:
					temp_oper[name].locked = False
					temp_oper[name].func = temp.func
					temp_oper[name].n_args = temp.n_args
					oper[name] = temp_oper[name]
					return
			oper[name] = evaluate(value, oper, level + 1)
			return

		if primary == 'fun':
			# return function 
			_, arg_names, *defines, exp = statement
			n_args = len(arg_names)
			static_oper = oper.copy() # copy oper for static var
			for define in defines:
				# define static local var in copied oper
				evaluate(define, static_oper, level + 1)

			def _func(*args):
				# copy static oper to add args in it
				func_oper = static_oper.copy() 
				for arg_name, arg in zip(arg_names, args):
					func_oper[arg_name] = evaluate(arg, oper, level + 1)
				return evaluate(exp, func_oper, level + 1)
			return Function(func=_func, n_args=f'== {n_args}')

		if primary == 'if':
			_, cond, true, false = statement
			if evaluate(cond, oper, level + 1):
				return evaluate(true, oper, level + 1)
			else:
				return evaluate(false, oper, level + 1)
		

		if isinstance(primary, tuple):
			# eval the primary to see if it's a function
			primary = evaluate(primary, oper, level + 1)
			#assert type(primary) == Function, (
			#	f'expect a function but got {type(primary).__name__}')
			statement = (primary, *statement[1:])
			return evaluate(statement, oper, level)

		func = None

		if isinstance(primary, Function):
			func, *args = statement
		
		elif type(primary) is str and primary in oper:
			func_name, *args = statement
			func = oper[func_name]
		
		if func is not None:
			args = [evaluate(arg, oper, level + 1) for arg in args]
			value = func(*args)
			return value
		

		#assert not isID(primary), f'undefined function: {primary}'
		#assert False, f'invalid function name: {primary}'

	else:
		if callable(statement):
			return statement

		try:
			return int(statement)
		except:
			pass
		
		try:
			return {'#t': True, '#f': False}[statement]
		except:
			pass
			
		try:
			return oper[statement]
		except:
			pass
		
		#assert not isID(statement), f'undefined variable: {statement}'
		#assert False, f'invalid syntax: {statement}'


def initOper():
	# init oper for the definition
	def _add(*args):
		return sum(args)

	def _mul(*args):
		n = 1
		for i in args:
			n *= i
		return n
	def _sub(*args):
		x = args[0]
		for i in args[1:]:
			x -= i
		return x
	def _div(*args):
		x = args[0]
		for i in args[1:]:
			x /= i
		return int(x)
	def _equ(*args):
		for n in args[1:]:
			if args[0] != n:
				return False
		return True
	
	def _and(*args):
		return all(args)
	
	def _or(*args):
		return any(args)
	
	return {
		'+':			Function('+', _add,						int, '>= 2'),
		'-':			Function('-', _sub,						int, '>= 2'),
		'*':			Function('*', _mul,						int, '>= 2'),
		'/':			Function('/', _div,						int, '>= 2'),
		'mod':		  	Function('mod', lambda x, y: x % y,		int, '== 2'),
		'=':			Function('=', _equ,					 'same', '>= 2'),
		'>':			Function('>', lambda x, y: x > y,		int, '== 2'),
		'<':			Function('<', lambda x, y: x < y,		int, '== 2'),
		'and':		    Function('and', _and,					    bool, '>= 2'),
		'or':		    Function('or', _or,					        bool, '>= 2'),
		'not':		    Function('not', lambda x: not x,			bool, '== 1'),
		'print-num':	Function('print-num',   lambda x: print(x),  int, '== 1'),
		'print-bool':   Function('print-bool', lambda x: print({True: '#t', False: '#f'}[x]), bool, '== 1')
	}


def run(code, oper=initOper()):
	try:
		statements = parseTree(code)
	except:
		print('invalid syntax')
		return
	for statement in statements:		# do the recurrence
		try:
			retval = evaluate(statement, oper)
			#if retval != None:	
				#print( "retval", retval)
		except :
				print('invalid syntax')


if __name__ == '__main__':
	import sys, os, readline

	if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
		run(open(sys.argv[1]).read())

	else:
		x = ""
		while True:
			try:
				x += input()
				#print("x = ", x)
			except:
				break
		#print(x)
		run(x)
		
