from typing import (Type,
                    Union)

from ground.hints import (Empty,
                          Linear,
                          Maybe,
                          Mix,
                          Multipoint,
                          Shaped)

MIN_MIX_NON_EMPTY_COMPONENTS = 2


def pack_mix(discrete: Maybe[Multipoint],
             linear: Maybe[Linear],
             shaped: Maybe[Shaped],
             empty: Empty,
             mix_cls: Type[Mix]
             ) -> Union[Empty, Linear, Mix, Multipoint, Shaped]:
    return (mix_cls(discrete, linear, shaped)
            if (((discrete is not empty)
                 + (linear is not empty)
                 + (shaped is not empty))
                >= MIN_MIX_NON_EMPTY_COMPONENTS)
            else (discrete
                  if discrete is not empty
                  else (linear
                        if linear is not empty
                        else shaped)))
