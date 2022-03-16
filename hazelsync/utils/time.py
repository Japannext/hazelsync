'''
Some time utilities
'''

from datetime import timedelta

import pyparsing as pp
from pyparsing import pyparsing_common as ppc

FACTORS = {
    'd': 1,
    'w': 7,
    'm': 30,
    'y': 365,
}

DAY = (pp.Literal('d') | pp.CaselessKeyword('day') | pp.CaselessKeyword('days')).setParseAction(lambda: 'd')
WEEK = (pp.Literal('w') | pp.CaselessKeyword('week') | pp.CaselessKeyword('weeks')).setParseAction(lambda: 'w')
MONTH = (pp.Literal('m') | pp.CaselessKeyword('month') | pp.CaselessKeyword('months')).setParseAction(lambda: 'm')
YEAR = (pp.Literal('y') | pp.CaselessKeyword('year') | pp.CaselessKeyword('years')).setParseAction(lambda: 'y')
UNIT = (DAY | WEEK | MONTH | YEAR).setParseAction(lambda t: FACTORS[t.asList()[0]])

SINGLE_DURATION = (ppc.integer('value') + UNIT('unit')).setParseAction(lambda t : t['value'] * t['unit'])

DURATIONS = pp.OneOrMore(SINGLE_DURATION).setParseAction(sum)

def duration_parser(string):
    '''Parse a duration string a return the associated timedelta'''
    day_duration = DURATIONS.parseString(string).asList()[0]
    return timedelta(days=day_duration)
