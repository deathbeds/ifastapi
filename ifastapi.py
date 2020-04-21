#!/usr/bin/env python
# coding: utf-8

# In[7]:


"""> Running [fastapi](https://github.com/tiangolo/fastapi) under [uvicorn](https://github.com/encode/uvicorn) inside [IPython](https://github.com/ipython/ipython)"""
__version__ = "0.1.0"


# In[3]:


import asyncio
import atexit
import os

import fastapi
import IPython
import pydantic
import tornado.ioloop
import ujson
import uvicorn

server = None
IN_HUB = "JUPYTERHUB_SERVICE_PREFIX" in os.environ


# In[4]:


def main(port=8000, **kwargs):
    global server
    app_args = {}
    uvi_args = dict(port=port)
    IN_HUB = "JUPYTERHUB_SERVICE_PREFIX" in os.environ
    prefix = "/"
    if IN_HUB:
        prefix = f"""{os.environ["JUPYTERHUB_SERVICE_PREFIX"]}proxy/{port}"""
        app_args.update(openapi_prefix=prefix)
        uvi_args.update(root_path=prefix)
    if not server:
        app = fastapi.FastAPI(title="IFastAPI", **kwargs)
        config = uvicorn.Config(app, **uvi_args)
        server = uvicorn.Server(config=config)
        task = asyncio.ensure_future(server.serve())
        atexit.register(tornado.ioloop.IOLoop.current().add_callback, server.shutdown)
    return server


# ## Make a route

# In[6]:


def load_ipython_extension(shell):
    main()
    return show_route("/docs")


def unload_ipython_extension(shell):
    atexit.unregister(tornado.ioloop.IOLoop.current().add_callback, server.shutdown)
    tornado.ioloop.IOLoop.current().add_callback(server.shutdown)
    return show_route("/docs")


# In[7]:


def show_route(route, height="400px"):
    url = (
        f"{prefix}{route}"
        if IN_HUB
        else f"http://localhost:{server.config.port}{route}"
    )
    display(IPython.display.Markdown(f"[`{url}`]({url})"))
    display(IPython.display.IFrame(url, width="100%", height=height))


# In[2]:


if __name__ == "__main__" and "__file__" not in globals():
    get_ipython().system(
        "jupyter nbconvert --to python --stdout IFastAPI.ipynb > ifastapi.py"
    )
    get_ipython().system("isort ifastapi.py ")
    get_ipython().system("black ifastapi.py")


# In[ ]:
