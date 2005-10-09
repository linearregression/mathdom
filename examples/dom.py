try:
    import psyco
    psyco.full()
except ImportError:
    pass

import sys
from itertools import imap

try:
    from xml import xpath
    HAS_XPATH = True
except ImportError:
    HAS_XPATH = False

try:
    from mathml.mathdom     import MathDOM
    from mathml.termbuilder import tree_converters
    from mathml.termparser  import *
    from mathml.xmlterm     import *
except ImportError:
    # Maybe we are still before installation?
    sys.path.append('..')

    from mathdom     import MathDOM
    from termbuilder import tree_converters
    from termparser  import *
    from xmlterm     import *

infix_converter = tree_converters['infix']

def write_infix(doc):
    tree = dom_to_tree(doc)
    print "SERIALIZED:"
    print infix_converter.build(tree)


def handle_term(term):
    print "ORIGINAL:"
    print term
    print

    doc = None
    for term_type in term_parsers.known_types():
        print "Trying to parse '%s' ..." % term_type,
        try:
            doc = MathDOM.fromString(term, term_type)
            print "done."
            break
        except ParseException, e:
            print "Parsing as %s failed: %s" % (term_type, unicode(e).encode('UTF-8'))

    if doc is None:
        print "The term is not parsable."
        sys.exit(0)


    print "MathML parsing done."
    print
    write_infix(doc)

    print
    print "Exchanging '+' and '-' ..."
    print
    for apply_tag in doc.getElementsByTagName(u'apply'):
        operator = apply_tag.operatorname()
        if operator == u'plus':
            apply_tag.set_operator(u'minus')
        elif operator == u'minus' and apply_tag.operand_count() > 1:
            apply_tag.set_operator(u'plus')
    write_infix(doc)

    print
    if HAS_XPATH:
        print "Searching for negative numbers using XPath expression '//cn[number() < 0]' ..."
        print
        for cn_tag in xpath.Evaluate('//cn[number() < 0]', doc.documentElement):
            value = cn_tag.value()
            print "%s [%s]" % (value, type(value))

        print
        print "Serializing all sub-terms ..."
        print

        for apply_tag in xpath.Evaluate('//apply', doc.documentElement):
            print apply_tag.serialize(converter=infix_converter)

    else:
        print "XPath not installed. Skipping test."

    print
    print 'Done.'


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '-':
        handle_term( sys.stdin.read() )
    else:
        while True:
            print "Please enter an infix term or leave empty to proceed with an example term. 'exit' exits."
            try:
                term = raw_input('# ')
            except EOFError:
                sys.exit(0)

            if term.strip() in ('exit', 'quit'):
                sys.exit(0)

            if not term:
                term = ".1*pi+2E-4*(1+3i)-5.6-6*-1/sin(-45.5E6*a.b) * CASE WHEN 3|12 THEN 1+3 ELSE e^(4*1) END + 1"
                term = "%(term)s = 1 or %(term)s > 5 and true" % {'term':term}

            handle_term(term)
