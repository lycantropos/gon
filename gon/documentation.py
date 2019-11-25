import textwrap
from functools import partial
from typing import (Callable,
                    Optional,
                    TypeVar)

Documented = TypeVar('Documented', Callable, type)
indent = partial(textwrap.indent,
                 prefix=' ' * 4)


def setup(documented: Optional[Documented] = None,
          *,
          docstring: str,
          origin: Optional[str] = None,
          reference: Optional[str] = None,
          time_complexity: Optional[str] = None) -> Documented:
    if documented is None:
        return partial(setup,
                       docstring=docstring,
                       origin=origin,
                       reference=reference,
                       time_complexity=time_complexity)
    docstring += '\n'
    if origin is not None:
        docstring += ('\n'
                      'Based on:\n'
                      '{origin}.\n'
                      .format(origin=indent(origin)))
    if reference is not None:
        docstring += ('\n'
                      'Reference:\n'
                      '{reference}\n'
                      .format(reference=indent(reference)))
    if time_complexity is not None:
        docstring += ('\n'
                      'Time complexity:\n'
                      '{time_complexity}.\n'
                      .format(time_complexity=indent(time_complexity)))
    if documented.__doc__ is not None:
        docstring += '\n' + textwrap.dedent(documented.__doc__)
    documented.__doc__ = docstring
    return documented
