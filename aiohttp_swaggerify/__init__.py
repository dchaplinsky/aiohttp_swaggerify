import sys
import inspect
from collections import defaultdict
from aiohttp import web

__author__ = """Dmitry Chaplinsky"""
__email__ = 'chaplinsky.dmitry@gmail.com'
__version__ = '0.1.0'


def parse_docstring(s):
    title = []
    description = []
    strings = inspect.cleandoc(s).split("\n")

    for i, x in enumerate(strings):
        if x:
            title.append(x)
        else:
            if title:
                description = strings[i + 1:]
                break
            else:
                continue

    return {
        "title": " ".join(title),
        "description": " ".join(description)
    }


def swaggerify(app, parse_module_info=True, **kwargs):
    """
    Parse information from given app, it's path handlers and callee module
    itself to populate swagger definition file

    Any part of swagger definition can be overriden with kwargs
    """

    async def swagger_handler(request):
        """
        Request handler to serve swagger json config for given app
        """
        return web.json_response(app["_swagger_config"])

    # Populate configs for paths from app routes
    paths_config = defaultdict(dict)
    for r in app.router.routes():
        # Title and description are retrieved from docstring of a handler
        docstrings = parse_docstring(r.handler.__doc__ or "")
        if len(docstrings["title"]) > 120:
            # TODO: logging
            docstrings["title"] = docstrings["title"][:120]

        # Some information is just hardcoded as we have strict requirements
        # to input and output format of ws endpoints
        desc = {
            "summary": docstrings["title"],
            "description": docstrings["description"],
            "consumes": ["application/json"],
            "produces": ["application/json"],
            "responses": {
                "400": {"description": "Request is malformed or invalid"},
                "500": {"description": "Response malformed or invalid"},
                "405": {"description": "Method is not allowed"},
            }
        }

        if hasattr(r.handler, "_request_schema"):
            desc["parameters"] = [{
                "in": "body",
                "name": "body",
                "required": True,
                "schema": r.handler._request_schema
            }]
        else:
            desc["parameters"] = [{
                "in": "body",
                "name": "body"
            }]

        if hasattr(r.handler, "_swg_input"):
            desc["parameters"][0].update(r.handler._swg_input)

        if hasattr(r.handler, "_response_schema"):
            desc["responses"]["200"] = {
                # TODO: think how to override
                "description": "Results of the request",
                "schema": r.handler._response_schema
            }
        else:
            desc["responses"]["200"] = {
                "description": "Results of the request"
            }

        if hasattr(r.handler, "_swg_output"):
            desc["responses"]["200"].update(r.handler._swg_output)

        if hasattr(r.handler, "_swg_info"):
            desc.update(r.handler._swg_info)

        paths_config[r._resource._path][r.method.lower()] = desc

    # Populate complete config

    # Get optional information that overrides info part of the config
    swagger_config_info = kwargs.pop("info", {})
    # Some sane defaults
    swagger_config = {
        "swagger": "2.0",
        "schemes": ["http"],
        "paths": paths_config
    }

    # That can be overriden with kwargs
    swagger_config.update(kwargs)

    # Some sane defaults for info part of the config
    swagger_config_info_default = {
        "version": "1.0.0",
    }

    # Which we now can try to extend using introspection, docstrings and
    # global variables of the main module of the app
    if parse_module_info:
        try:
            caller = inspect.currentframe().f_back
            mod = sys.modules[caller.f_globals['__name__']]

            # Try to pull information from docstrings
            swagger_config_info_default.update(parse_docstring(mod.__doc__))

            # As well as global variables
            if hasattr(mod, "__version__"):
                swagger_config_info_default["version"] = mod.__version__

            if hasattr(mod, "__license__"):
                swagger_config_info_default["license"] = {
                    "name": mod.__license__
                    # TODO: add urls for well-known licenses
                }

            # And map it to swagger definitions
            contact_info = {}
            if hasattr(mod, "__author__"):
                contact_info["name"] = mod.__author__
            if hasattr(mod, "__maintainer__"):
                contact_info["name"] = mod.__maintainer__
            if hasattr(mod, "__email__"):
                contact_info["email"] = mod.__email__

            if contact_info:
                swagger_config_info_default["contact"] = contact_info
        except:
            # TODO: logging
            pass

    swagger_config["info"] = swagger_config_info_default

    # override it with data from kwargs["info"]
    swagger_config["info"].update(swagger_config_info)

    app["_swagger_config"] = swagger_config

    app.router.add_route("GET", "/swagger.json", swagger_handler)

    return app


def document(info=None, input=None, output=None):
    """
    Add extra information about request handler and its params
    """
    def wrapper(func):
        if info is not None:
            setattr(func, "_swg_info", info)
        if input is not None:
            setattr(func, "_swg_input", input)
        if output is not None:
            setattr(func, "_swg_output", output)
        return func

    return wrapper


__all__ = ["swaggerify", "document"]
