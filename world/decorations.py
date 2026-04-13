# re-export config
from .decoration.config import *

# re-export draw
from .decoration.draw import (
    draw_decoration,
    draw_rock_snow,
    draw_ice_chunk,
    draw_snow_pine,
    draw_snow_crack,
    draw_ice_crack_big,
    draw_iceberg,
    draw_cliff_ice,
    draw_toxic_barrel,
    draw_trash_pile,
    draw_oil_stain,
    draw_warning_sign,
    draw_igloo,
)

# re-export generation
from .decoration.generator import (
    generate_zone_decorations,
    add_fixed_pollution_details,
    add_edge_icebergs,
)