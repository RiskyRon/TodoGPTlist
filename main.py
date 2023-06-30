import json
import os
import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Keep track of files. Does not persist if Python session is restarted.
_FILES = []

@app.post("/files")
async def add_file():
    request = await quart.request.get_json(force=True)
    _FILES.append({"filename": request["filename"], "content": request["file"]})
    return quart.Response(response='OK', status=200)

@app.get("/files")
async def get_files():
    return quart.Response(response=json.dumps(_FILES), status=200)

@app.delete("/files")
async def delete_file():
    request = await quart.request.get_json(force=True)
    file_idx = request["file_idx"]
    # fail silently, it's a simple plugin
    if 0 <= file_idx < len(_FILES):
        _FILES.pop(file_idx)
    return quart.Response(response=json.dumps(_FILES), status=200)

@app.post("/upload")
async def upload_files():
    UPLOAD_FOLDER = 'UPLOAD'
    filenames = []  # list to store filenames
    for filename in os.listdir(UPLOAD_FOLDER):
        try:
            with open(os.path.join(UPLOAD_FOLDER, filename), 'r') as file:
                content = file.read()
                _FILES.append({"filename": filename, "content": content})
                filenames.append(filename)  # add filename to the list
        except UnicodeDecodeError:
            print(f"Could not read file {filename} as text. Skipping.")
    return quart.Response(response=json.dumps(filenames), status=200)  # return only filenames


@app.post("/download")
async def download_files():
    DOWNLOAD_FOLDER = 'DOWNLOAD'
    request_data = await quart.request.get_json(force=True)
    filename = request_data.get("filename")
    if filename:
        files = [file for file in _FILES if file["filename"] == filename]
    else:
        files = _FILES
    for file_dict in files:
        with open(os.path.join(DOWNLOAD_FOLDER, file_dict["filename"]), 'w') as file:
            file.write(file_dict["content"])
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
