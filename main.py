import json

import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Keep track of scripts. Does not persist if Python session is restarted.
_SCRIPTS = []

@app.post("/scripts")
async def add_script():
    request = await quart.request.get_json(force=True)
    _SCRIPTS.append(request["script"])
    return quart.Response(response='OK', status=200)

@app.get("/scripts")
async def get_scripts():
    return quart.Response(response=json.dumps(_SCRIPTS), status=200)

@app.delete("/scripts")
async def delete_script():
    request = await quart.request.get_json(force=True)
    script_idx = request["script_idx"]
    # fail silently, it's a simple plugin
    if 0 <= script_idx < len(_SCRIPTS):
        _SCRIPTS.pop(script_idx)
    return quart.Response(response='OK', status=200)

@app.get("/logo2.png")
async def plugin_logo():
    filename = 'logo2.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
