from ground.hints import Segment

MIN_MIX_NON_EMPTY_COMPONENTS = 2


def is_segment_horizontal(segment: Segment) -> bool:
    return segment.start.y == segment.end.y


def is_segment_vertical(segment: Segment) -> bool:
    return segment.start.x == segment.end.x
