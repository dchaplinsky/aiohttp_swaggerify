#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_aiohttp_swaggerify
----------------------------------

Tests for `aiohttp_swaggerify` module.
"""

import pytest


from aiohttp_swaggerify import document, swaggerify
from aiohttp import web


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
    """
    return ""


async def test_wrong_response_format(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_get('/', demo_handler)
    app = swaggerify(
        app,
        basePath="/",
        host="127.0.0.1:8080"
    )

    client = await test_client(app)
    resp = await client.get('/swagger.json')
    assert resp.status == 200
