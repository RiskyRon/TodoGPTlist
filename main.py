import json
import os
import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Keep track of scripts. Does not persist if Python session is restarted.
_SCRIPTS = []

@app.post("/scripts")
async def add_script():
    request = await quart.request.get_json(force=True)
    _SCRIPTS.append({"filename": request["filename"], "content": request["script"]})
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

@app.post("/upload")
async def upload_files():
    UPLOAD_FOLDER = 'UPLOAD'
    for filename in os.listdir(UPLOAD_FOLDER):
        try:
            with open(os.path.join(UPLOAD_FOLDER, filename), 'r') as file:
                content = file.read()
                _SCRIPTS.append({"filename": filename, "content": content})
        except UnicodeDecodeError:
            print(f"Could not read file {filename} as text. Skipping.")
    return quart.Response(response=json.dumps(_SCRIPTS), status=200)

@app.post("/download")
async def download_files():
    DOWNLOAD_FOLDER = 'DOWNLOAD'
    request_data = await quart.request.get_json(force=True)
    filename = request_data.get("filename")
    if filename:
        scripts = [script for script in _SCRIPTS if script["filename"] == filename]
    else:
        scripts = _SCRIPTS
    for script in scripts:
        with open(os.path.join(DOWNLOAD_FOLDER, script["filename"]), 'w') as file:
            file.write(script["content"])
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
