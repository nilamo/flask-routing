def index() -> "/":
    # routing is handled through an annotation
    # you can read it "function_name 'maps to' url_route"
    return "hi"


def user(id: int = None) -> "/user/{id}":
    # annotations in arguments causes web.py to auto-cast url args
    # cast failrues (id: int = "bob") get redirected to the namespaced 404
    # urls are written in pseudo-string format syntax...
    # ...web.py converts the pseudo-string to a regex for speed
    return repr(id)


def all_users() -> "/users":
    # Controllers (I refer to them as Handlers a lot) can be plain functions, or coroutines
    # plain functions will be wrapped into coroutines by asyncio.
    # probably best to just define your controllers as async, unless that's too ugly for you
    # TODO: test if async has any speed impact, or if wrapping native
    # functions is Actively Bad
    return "admin users"


def not_found(error):
    return "derp", 404


if __name__ == "__main__":
    import routing
    from flask import Flask

    # make a website!
    app = Flask(__name__)
    with routing.Root(app) as root:
        # / -> index()
        root.route(index)
        # /user/12345 -> user(12345)
        root.route(user)
        # /does-not-exist -> not_found()
        root.error(404, not_found)

        # bind some handlers to a "namespace"
        # ...all routes will be attached under this top-level-uri
        with root.namespace("/admin") as admin_area:
            # /admin/users -> all_users()
            admin_area.route(all_users)

    # run the flask app!
    app.run()
