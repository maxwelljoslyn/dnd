import web

import dnd

app = web.application(
    __name__, db=True, args={"tradegood": ".*", "town": ".*", "testing": ".*"}
)


@app.control("")
class Home:
    """Profile and primary feed."""

    def get(self):
        """Render a profile summary and a reverse chronological feed of public posts."""
        return app.view.index(dnd.towns, dnd.registry)


@app.control("towns/{town}")
class Town:
    def get(self, town):
        info = dnd.towns.get(town)
        if not info:
            raise web.BadRequest
        has_market = "markets" in dnd.original_towns[town]["references"]
        if has_market:
            vendors = dnd.vendors
        else:
            vendors = dnd.limited_vendors
        return app.view.town(town, info, dnd.registry, has_market, vendors)

