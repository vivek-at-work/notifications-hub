from __future__ import annotations

import strawberry


@strawberry.type
class PageInfo:
    page: int
    page_size: int
    total_count: int
    has_next_page: bool
    has_previous_page: bool
