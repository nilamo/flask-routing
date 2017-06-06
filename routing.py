import flask


class Route:
    def __init__(self, path="/", handler=None, formatters={}):
        self.path = self.translate(path, formatters)
        self.handler = handler if handler else lambda: None

    # flask expects url params to be wrapped in angle brackets.
    # we allow for string formatting syntax, and translate into something flask understands.
    # furthermore, if there's an annotation, we add the flask-compatable type
    # to the url
    def translate(self, path, formatters):
        type_map = {
            int: "int",
            float: "float",
            str: "string",
            #"path": "path",
            #"any": "any",
            #"uuid": "uuid"
        }

        for url_param in formatters:
            formatter = formatters[url_param]
            if formatter in type_map:
                formatter = type_map[formatter]
            _from = "{{{0}}}".format(url_param)
            to = "<{0}:{1}>".format(formatter, url_param)
            path = path.replace(_from, to)

        return path

    def __repr__(self):
        return "{0} => {1}".format(self.path, self.handler)


class Namespace:
    # what we call a namespace, other frameworks refer to as "apps" or "modules"
    # a namespace is a self-contained collection of endpoints, bound to a url
    # path
    def __init__(self, site=None, attached="/"):
        self.site = site
        self.attachment_point = attached
        self.routes = []
        self.errors = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.site.register_namespace(self.attachment_point, self.routes)

    def error(self, error_code, handler):
        self.errors.append({"code": error_code, "handler": handler})

    def route(self, route):
        path = None
        anno = route.__annotations__
        if "return" in anno:
            path = anno["return"]
            del anno["return"]

        # TODO: lists should be allowed in annotations so a controller can
        # listen to multiple uris
        self.routes.append(Route(path=path, handler=route, formatters=anno))

        # allow for route chaining
        return self

    def namespace(self, base):
        return Namespace(self, base)

    def register_namespace(self, attachment_point, routes):
        for route in routes:
            new_path = "{0}{1}".format(attachment_point, route.path)
            new_route = Route(
                path=new_path,
                handler=route.handler
            )
            self.routes.append(new_route)


class Root:
    def __init__(self, app: flask.Flask):
        self.app = app
        self.root = None

    def __enter__(self):
        self.root = Namespace()
        return self.root

    def __exit__(self, *_):
        for route in self.root.routes:
            # flask uses decorators for the routing.
            # so let flask's routing know what would-have-been decorated.
            self.app.route(route.path)(route.handler)
        for err in self.root.errors:
            self.app.errorhandler(err["code"])(err["handler"])
