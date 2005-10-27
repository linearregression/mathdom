from distutils.core import setup
setup(
    name='mathdom',
    version='0.6.1',
    packages=['mathml', 'mathml.utils', 'mathml.pmathml'],
    package_data = {
    'mathml'       : ['schema/mathml2.rng.gz'],
    'mathml.utils' : ['mathmlc2p.xsl', 'ctop.xsl']
    },

    description='MathDOM - Content MathML in Python',
    long_description="""MathDOM - Content MathML in Python

**MathDOM** is a set of Python 2.4 modules (using PyXML_ or lxml_, and
pyparsing_) that import mathematical terms as a `Content MathML`_
DOM. It currently parses MathML and literal infix terms into a DOM
document and writes out MathML and literal infix/prefix/postfix/Python
terms. The DOM elements are enhanced by domain specific methods that
make using the DOM a little easier. Implementations based on PyXML and
lxml/libxml2 are available.

.. _lxml:                  http://codespeak.net/lxml/
.. _pyparsing:             http://pyparsing.sourceforge.net/
.. _PyXML:                 http://pyxml.sourceforge.net/
.. _`Content MathML`:      http://www.w3.org/TR/MathML2/chapter4.html
.. _MathML:                http://www.w3.org/TR/MathML2/
.. _PyMathML:              http://pymathml.sourceforge.net/

You can call it the shortest way between different term
representations and a Content MathML DOM. Ever noticed the annoying
differences between terms in different programming languages? Build
your application around the DOM and stop caring about the term
representation that users prefer or that your machine can execute. If
you need a different representation, add a converter, but don't change
the model of your application. Literal terms are connected through an
intermediate AST step that makes writing converters for
SQL/Java/Lisp/*your-favourite* easy.

New in version 0.6.1:

- integration of the PyMathML_ renderer (untested!)
- more generic integration of XSLT scripts

New in version 0.6:

- RelaxNG validation
- Presentation MathML export (based on XSLT)
- stricter spec conformance (encloses MathML output in <math> tag

The first two require lxml, PyXML does not support them.
""",

    author='Stefan Behnel',
    author_email='scoder@users.sourceforge.net',
    url='http://mathdom.sourceforge.net/',
    download_url='http://www.sourceforge.net/projects/mathdom',

    classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Topic :: Text Processing :: Markup :: XML',
    'Topic :: Scientific/Engineering :: Mathematics',
    ],

    keywords = "MathML xml DOM math parser validator"
    )
