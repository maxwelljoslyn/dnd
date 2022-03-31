import web

import dnd

app = web.application(__name__, db=True)


@app.control("")
class Home:
    """Profile and primary feed."""

    def get(self):
        """Render a profile summary and a reverse chronological feed of public posts."""
        return app.view.index(dnd.towns, dnd.registry)

