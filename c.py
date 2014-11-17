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

from base import *

# C specific generators

def curly_brackets_semicolon(code):
    return last_line_affix(curly_brackets(code), ';')

def c_enum_initializer(val_list_tuple):
    return [comma_separated(['%s = %s' % (var, init) for var, init in val_list_tuple])]

def c_enum(val_list, name=''):
    return ['enum ' + name] + curly_brackets_semicolon(c_enum_initializer(val_list))

def str_c_array_declaration(c_type, name, size=''):
    return "%s %s[%s]" % (c_type, name, size)

def c_array_declaration(c_type, name, size='', init_values=[]):
    return ['extern ' + str_c_array_declaration(c_type, name, size) + ';']

def c_array_definition(c_type, name, size='', init_values=[]):
    return concat2([str_c_array_declaration(c_type, name, size) + '='], curly_brackets_semicolon([comma_separated(init_values)]))

def c_function_signature(ret_type, name, arg_list):
    return "%s %s(%s)" % (ret_type, name, comma_separated(arg_list))

def c_function_declaration(ret_type, name, arg_list=[], comment=''):
    return c_comment(comment) + ['extern ' + c_function_signature(ret_type, name, arg_list) + ';']

def c_function_definiton(ret_type, name, arg_list=[], comment=''):
    return lambda code: c_comment(comment) + concat2([c_function_signature(ret_type, name, arg_list)], curly_brackets(flat_code(code)))


def c_for(init, cond, update):
    return loop(['for(%s; %s; %s)' % (init, cond, update)])

def c_while(cond):
    return loop(['while(%s)' % (cond)])

def c_do_while(cond):
    return loop(['do'], ['while(%s)' % cond])

def c_comment(c):
    if isinstance(c, str):
        if c == '':
            return []
        return ['/* %s */' % c]
    else:
        return ['/*'] + [' * %s' % s for s in c] + [' */']

#def c_asm(
        
# c_ifelse([(expr0, code0), (expr1, code1),...(exprN, codeN)], code_else)
#def c_ifelse(expr_codes, else_code=[]):
#    def c_elif(code):
#        return ['else if(%s)' + code[0]] + code[1]
#    first = expr_codes.pop(0)
#    code = ['if(%s)' % first[0]] + first[1]
#    code += map(c_elif, expr_codes)
#    if len(else_code) != 0:
#        code += ['else'] + else_code
#    return code
c_ifelse = ifelse(lambda e, c: ['if(%s)' % e] + indent(c),
        lambda ec: ['else if(%s)' % ec[0]] + indent(ec[1]),
        lambda c: ['else'] + indent(c))
def c_if(cond):
    def _f(code):
        return c_ifelse((cond,code))

def c_struct_definition(name,fields):
    return concat2('struct %s' % name, ['%s %s;' % (t, n) for t, n in fields])

def c_typedef():
    pass

#def c_mifelse(expr_codes, else_code=[]):
#    def melif(code):
#        return [NoIndentStr('#elif ' + code[0])] + code[1]
#    first = expr_codes.pop(0)
#    code = [NoIndentStr('#if ' + first[0])] + first[1]
#    code += map(melif, expr_codes)
#    if len(else_code) != 0:
#        code += [NoIndentStr('#else')] + else_code
#    return code
c_mifelse = ifelse(lambda e, c: [NoIndentStr('#if ' + e)] + c,
        lambda ec: [NoIndentStr('#if ' + ec[0])] + ec[1],
        lambda c: [NoIndentStr('#else')] + c,
        lambda: [NoIndentStr('#endif')])

def c_include(name, system=True):
    if system:
        name = '<%s>' % name
    else:
        name = '"%s"' % name
    return [NoIndentStr('#include ' + name)]
#def c_mifdefelse(expr_codes, else_code=[], defined=True):
#    def definize(ec):
#        return ('defined(%s)' % ec[0], ec[1])
#    if type(expr_codes) == tuple:
#        expr_codes = definize(expr_codes)
#    else:
#        expr_codes = map(lambda ec: definize, expr_codes)
#    return c_mifelse(expr_codes, else_code)

def c_mdefine(name, val=''):
    return [NoIndentStr('#define %s %s' % (name, val))]
def c_mdefine_do(name, val=[]):
    val = indent(c_do_while(0)(val))
    last_line = val.pop()
    val = map(lambda x: x + ' \\', val)
    val.append(last_line)
    return map(NoIndentStr, concat2(['#define %s ' % name], val))
def c_mDefine(name, val=''):
    return c_mdefine(name.upper(), val)

def c_mdef_ifn(name, val=''):
    return c_mifelse(('!defined(%s)' % name, c_mdefine(name, val)))

def c_header_guard(name):
    def f(code):
        guard = c_mdef_ifn(name)
        eif = guard.pop()
        return guard + code + [eif]
    return f


def c_char_literal(c):
    return "'%c'" % c if c in string.printable else hex(c)
