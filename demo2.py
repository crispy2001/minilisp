#!/usr/bin/python3
import sys, os

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


# the class to all features which defined by question
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


def evalu(statement, oper, level = 0):
	if isinstance(statement, tuple):

		primary = statement[0]
		

		if primary == 'if':
			_, cond, true, false = statement
			if evalu(cond, oper, level + 1):
				return evalu(true, oper, level + 1)
			else:
				return evalu(false, oper, level + 1)

		if primary == 'fun':
			# return func 
			_, arg_names, *defines, exp = statement
			n_args = len(arg_names)
			static_oper = oper.copy() 
			for define in defines:
				evalu(define, static_oper, level + 1)

			def _func(*args):
				func_oper = static_oper.copy() 
				for arg_name, arg in zip(arg_names, args):
					func_oper[arg_name] = evalu(arg, oper, level + 1)
				return evalu(exp, func_oper, level + 1)
			return Function(func=_func, n_args=f'== {n_args}')

		if primary == 'define':
			# define a var in oper
			_, name, value = statement
			if type(value) is tuple:
				tmp= oper.copy()
				tmp[name] = Function(name)
				tmp[name].locked = True
				temp = evalu(value, tmp, level + 1)
				if callable(temp) and temp != tmp[name]:
					tmp[name].locked = False
					tmp[name].func = temp.func
					tmp[name].n_args = temp.n_args
					oper[name] = tmp[name]
					return
			oper[name] = evalu(value, oper, level + 1)
			return

		# check is func
		if isinstance(primary, tuple):
			primary = evalu(primary, oper, level + 1)
			statement = (primary, *statement[1:])
			return evalu(statement, oper, level)

		func = None

		if isinstance(primary, Function):
			func, *args = statement
		
		elif type(primary) is str and primary in oper:
			func_name, *args = statement
			func = oper[func_name]
		
		if func is not None:
			args = [evalu(arg, oper, level + 1) for arg in args]
			value = func(*args)
			return value
		


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
	
	def _sub(*args):
		x = args[0]
		for i in args[1:]:
			x -= i
		return x

	def _mul(*args):
		n = 1
		for i in args:
			n *= i
		return n

	def _div(*args):
		x = args[0]
		for i in args[1:]:
			x /= i
		return int(x)
	
	def _mod(*args):
		x = args[0]
		for i in args[1:]:
			x %= i
		return x
	
	def _equ(*args):
		for n in args[1:]:
			if args[0] != n:
				return False
		return True

	def _and(*args):
		return all(args)
	
	def _or(*args):
		return any(args)

	def _not(arg):
		return(not arg)

	def _pn(*args):
		print(args[0])

	def _pb(arg):
		if arg == True:
			print("#t")
		elif arg == False:
			print("#f")

	return {
		'+':			Function('+', _add,						int, '>= 2'),
		'-':			Function('-', _sub,						int, '>= 2'),
		'*':			Function('*', _mul,						int, '>= 2'),
		'/':			Function('/', _div,						int, '>= 2'),
		'mod':		  	Function('mod', _mod,					int, '>= 2'),
		'=':			Function('=', _equ,					 'same', '>= 2'),
		'>':			Function('>', lambda x, y: x > y,		int, '== 2'),
		'<':			Function('<', lambda x, y: x < y,		int, '== 2'),
		'and':		    Function('and', _and,					    bool, '>= 2'),
		'or':		    Function('or', _or,					        bool, '>= 2'),
		'not':		    Function('not', _not,						bool, '== 1'),
		'print-num':	Function('print-num', _pn   ,  				int, '== 1'),
		'print-bool':   Function('print-bool', _pb, 				bool, '== 1')
	}
	
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

def run(code, oper=initOper()):
	try:
		statements = parseTree(code)
	except:
		print('invalid syntax')
		return
	for statement in statements:		# do the recurrence
		try:
			retval = evalu(statement, oper)
			#if retval != None:	
				#print( "retval", retval)
		except :
				print('invalid syntax')



if __name__ == '__main__':

	x = ""
	while True:
		try:
			x += input()
		except:
			break
	#print(x)
	run(x)
		
