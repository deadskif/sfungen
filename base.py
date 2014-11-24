# Copyright (c) 2014, Vladimir Badaev. All rights reserved.
#
# This file is part of SFunGen.
# 
# SFunGen is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
# 
# SFunGen is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library.
# If not, see <http://www.gnu.org/licenses/>.
#
import functools
import types
import string
from multimethod import multimethod

DEFAULT_INDENT = '    '
from functools import wraps

def code_generators(*generators):

    def decorator(cls):
        for g in generators:
            gens_name = '_get_%s_generators' % g
            def _get_generators(cls):
                return (a for a in dir(cls) if g in getattr(getattr(cls,a), '_i_am_code_generator', []))
                #attrs = (getattr(cls, an) for an in dir(cls))
                #return (a for a in attrs if g in getattr(a, '_i_am_code_generator', []))
                #return filter(lambda a: g in getattr(a, '_i_am_code_generator', []), attrs)
                        
            def _get_generated(self):
                return (getattr(self, g)() for g in getattr(self, gens_name)())
            setattr(cls, gens_name, classmethod(_get_generators))
            setattr(cls, '_get_%s_generated' % g,_get_generated)
        return cls
    return decorator

def code_generator(*generators):
    def decorator(func):
        func._i_am_code_generator = generators
        return func
    return decorator

def unzip(a):
    return tuple(map(list, zip(*a)))
# Base generatirs
def template(temps, d):
    """
    Apply d to templates.
    """
    def _t(x):
        try:
            return x % d
        except TypeError as te:
            print x, " and ", d
            raise te

    #return map(lambda x: x % d, temps)
    return map(_t, temps)

class NoIndentStr(str):
    pass

def indent_str(s):
    """Indent string, but not NoIndentStr or empty string."""
    if isinstance(s, NoIndentStr) or s == '':
        return s
    else:
        return DEFAULT_INDENT + s

def indent(code):
    """Indent strings."""
    #print code
    return map(indent_str, code)

def block(left, code, right):
    """
    Make code block in form:
    <left>
        <code>
    <right>
    """
    return [left] + indent(code) + [right]

def join(code):
    """
    Transform strings list in one code string.
    """
    code = flat_code(code)
    try:
        return "\n".join(code) + '\n'
    except TypeError as te:
        print "%s (%s)" % (te.message, code)
        raise te

def generate(f, code):
    """
    Writes strings list into the file.
    """
    f.write(join(code))

def curly_brackets(code):
    """
    Transform code into '{' code '}'
    """
    return block('{', code, '}')

def square_brackets(code):
    """
    Transform code into '[' code ']'
    """
    return block('[', code, ']')

def angle_brackets(code):
    """
    Transform code into '<' code '>'
    """
    return block('<', code, '>')

def round_brackets(code):
    """
    Transform code into '(' code ')'
    """
    return block('(', code, ')')


def concat2(a,b):
    """Transforms ['a','b','c'],['one','two','free'] -> ['a','b','cone','two','free']"""
    f_b = b.pop(0)
    a[-1] += f_b
    return a + b
concat = functools.partial(reduce, concat2)

def last_line_affix(code, s):
    """
    Add s to last line of code.
    """
    code[-1]+=s
    return code

def modify_if(expr, mod_cb):
    return lambda val: mod_cb(val) if expr else val

#modify_if_not_str = functools.partial(lambda x: not isinstance(x, str))

#comma_separated = modify_if_not_str(lambda val: ", ".join(val))
def comma_separated(val_list):
    """
    Generates comma-separated string from val_list, or just returns val_list string.
    """
    print val_list
    return val_list if isinstance(val_list, str) else ", ".join(val_list)

def loop(pre, post=[]):
    """
    Returns function, which transforms its argument into loop <pre> <loop_body> <post>.
    """
    def f(code):
        """
        Make %s code %s loop.
        """ % (pre, post)
        if code == None:
            return pre + post
        elif isinstance(code, str):
            return pre + indent([code]) + post
        else:
            return pre + curly_brackets(flat_code(code)) + post
    return f

def ifelse(if_gen, elif_gen, else_gen, endif_gen=lambda:[]):
    def f(expr_codes, else_code=[]):
        #print "expr_codes=%s, else_code=%s" % (expr_codes, else_code)
        if type(expr_codes) == tuple:
            code = if_gen(expr_codes[0], expr_codes[1])
        else:
            first = expr_codes.pop(0)
            code = if_gen(first[0], first[1])
            code += map(elif_gen, expr_codes)
        if len(else_code) != 0:
            code += else_gen(else_code)
        code += endif_gen()
        #print "\nifelse.f(%s, %s) = %s" % (expr_codes, else_code, code)
        return code
    return f

def code(*args):
    return flat_code([a for a in args])

def flat_code(lst):
    """
    Transform list of lists/strings into strings list.
    """
    if isinstance(lst, str):
        return [lst]
    elif isinstance(lst, list):
        try:
            return reduce(lambda x,y: x+y, [flat_code(x) for x in lst], [])
        except TypeError as te:
            print "Some fuck up with %s" % lst
            raise te
    elif isinstance(lst, (types.FunctionType, types.MethodType)):
        @wraps(lst)
        def wrapper(*args, **kwargs):
            return flat_code(lst(*args, **kwargs))
        return wrapper
    else:
        TypeError("Bad type for flat_code(%s)" % type(lst))



#def _ss(x,y):
#    try:
#        return x+['']+y
#    except TypeError as te:
#        raise te
def string_separated(arr):
    """
    Transform list of strings list into strings list, separate them with empty strings.
    """
    #print arr
    return reduce(lambda x,y: flat_code(x) + [''] + flat_code(y), arr)
    #return functools.reduce(_ss, arr)
