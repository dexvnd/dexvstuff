from javascript import require
import json, requests

class JsdomRuntime:
    def __init__(self, url: str = None, virtual_console=None) -> None:
        self.jsdom = require('jsdom')
        self.vm = require("vm").Script
        self.vc = virtual_console or self.jsdom.VirtualConsole()
        self.init(url)

    def init(self, url: str = None) -> None:
        try:
            html = requests.get(url, timeout=10).content.decode("utf-8", errors="replace") if url else "<title>jsdom</title>"
        except Exception:
            raise RuntimeError(f"Failed to fetch {url}")

        self.dom = self.jsdom.JSDOM(html, {
            "url": url, "runScripts": "dangerously", "resources": "usable",
            "pretendToBeVisual": True, "virtualConsole": self.vc
        })
        self.runtime = self.dom.getInternalVMContext()

    def eval(self, data: str, promise: bool = False, byte_array: bool = False, suppress: bool = False) -> str:
        script = (
            f"{data}.then(r => JSON.stringify(Array.from(r)))" if byte_array and promise else
            f"JSON.stringify(Array.from(({data})))" if byte_array else
            f"{data}.then(r => JSON.stringify(r))" if promise else data
        )
        try:
            result = self.vm(script).runInContext(self.runtime)
            return json.loads(result) if byte_array else result
        except Exception as e:
            if not suppress: raise e