#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_aiohttp_swaggerify

Tests for `aiohttp_swaggerify` module.
"""
import pytest

from aiohttp_swaggerify import document, swaggerify
from aiohttp_validate import validate
from jsonschema import validate as schema_validate
from aiohttp import web
import json


__author__ = "Dmitry Chaplinsky"
__copyright__ = "Copyright 2016, Dmitry Chaplinsky"
__credits__ = ["Test Testov", "Dmitry Chaplinsky"]
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Test Testov"
__email__ = "chaplinsky.dmitry@gmail.com"


TOKENIZE_TEXT_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
    },
    "required": ["text"],
    "additionalProperties": False
}

TOKENIZE_TEXT_OUTPUT_SCHEMA = {
    "type": "array",
    "items": {
        "type": "array",
        "items": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}


@document(
    info={
        "tags": ["test1", "test2"],
        "x-microservice-taxonomy": ["whatever"]
    },
    input={
        "description": "Just a test of input"
    },
    output={
        "description": "just a test of output"
    },
)
async def demo_handler(request, *args):
    """
    Test of docstring

    And here is the description
    """
    return ""


@validate(
    request_schema=TOKENIZE_TEXT_INPUT_SCHEMA,
    response_schema=TOKENIZE_TEXT_OUTPUT_SCHEMA,
)
@document(
    input={
        "description": "Just a test of input2"
    },
    output={
        "description": "just a test of output2"
    },
)
async def demo_handler_with_validation(request, *args):
    """
    Test of docstring2

    And here is the description2
    """
    return ""



@validate(
    request_schema=TOKENIZE_TEXT_INPUT_SCHEMA,
    response_schema=TOKENIZE_TEXT_OUTPUT_SCHEMA,
)
@document(
    info={
        "tags": ["test1", "test2"],
        "x-microservice-taxonomy": ["whatever"]
    },
    input={
        "description": "Just a test of input"
    },
    output={
        "description": "just a test of output"
    },
)
async def full_fledged_handler(request, *args):
    """
    Test of everything

    in heres
    """
    return ""


async def test_basic_documentation(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_get('/', demo_handler)
    app.router.add_post('/', demo_handler)
    app = swaggerify(
        app,
        basePath="/",
        host="127.0.0.1:8080"
    )

    client = await test_client(app)
    resp = await client.get('/swagger.json')
    assert resp.status == 200
    text = await resp.json()

    assert text["info"]["title"] == "test_aiohttp_swaggerify"
    assert text["info"]["description"]
    assert text["host"] == "127.0.0.1:8080"
    assert text["basePath"] == "/"
    assert text["info"]["version"] == __version__
    assert text["info"]["contact"]["name"] == __maintainer__
    assert text["info"]["license"]["name"] == __license__
    assert text["info"]["contact"]["email"] == __email__

    for meth in ["get", "post"]:
        assert text["paths"]["/"][meth]["responses"]
        assert text["paths"]["/"][meth]["summary"] == "Test of docstring"
        assert text["paths"]["/"][meth]["description"] == "And here is the description"
        assert text["paths"]["/"][meth]["responses"]["200"]["description"] == "just a test of output"
        assert text["paths"]["/"][meth]["parameters"][0]["description"] == "Just a test of input"
        assert "schema" not in text["paths"]["/"][meth]["parameters"][0]
        assert "schema" not in text["paths"]["/"][meth]["responses"]["200"]

        assert text["paths"]["/"][meth]["tags"]
        assert text["paths"]["/"][meth]["x-microservice-taxonomy"]


async def test_with_validation(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_get('/', demo_handler_with_validation)
    app.router.add_post('/', demo_handler_with_validation)
    app = swaggerify(
        app,
        basePath="/",
        host="127.0.0.1:8080"
    )

    client = await test_client(app)
    resp = await client.get('/swagger.json')
    assert resp.status == 200
    text = await resp.json()

    assert text["info"]["title"] == "test_aiohttp_swaggerify"
    assert text["info"]["description"]
    assert text["host"] == "127.0.0.1:8080"
    assert text["basePath"] == "/"
    assert text["info"]["version"] == __version__
    assert text["info"]["contact"]["name"] == __maintainer__
    assert text["info"]["license"]["name"] == __license__
    assert text["info"]["contact"]["email"] == __email__

    for meth in ["get", "post"]:
        assert text["paths"]["/"][meth]["responses"]
        assert text["paths"]["/"][meth]["summary"] == "Test of docstring2"
        assert text["paths"]["/"][meth]["description"] == "And here is the description2"
        assert text["paths"]["/"][meth]["responses"]["200"]["description"] == "just a test of output2"
        assert text["paths"]["/"][meth]["parameters"][0]["description"] == "Just a test of input2"
        assert text["paths"]["/"][meth]["parameters"][0]["schema"]
        assert text["paths"]["/"][meth]["responses"]["200"]["schema"]
        assert "tags" not in text["paths"]["/"][meth]
        assert "x-microservice-taxonomy" not in text["paths"]["/"][meth]


async def test_validate_fullfledged(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_get('/', full_fledged_handler)
    app.router.add_post('/', full_fledged_handler)
    app = swaggerify(
        app,
        basePath="/",
        host="127.0.0.1:8080"
    )

    client = await test_client(app)
    resp = await client.get('/swagger.json')
    assert resp.status == 200
    text = await resp.json()

    with open("tests/validate_swagger.json", "r") as fp:
        assert schema_validate(text, json.load(fp)) is None
