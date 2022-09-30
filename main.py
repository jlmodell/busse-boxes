import json

from pydantic import BaseModel, Field

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

class Box(BaseModel):
    length: int = Field(...)
    width: int = Field(...)
    height: int = Field(...)


boxes_json = json.loads(open("boxes.json").read())

boxes: list[Box] = [
    Box(length=x["length"], width=x["width"], height=x["height"])
    for x in boxes_json
]

def find_box_with_padding(box: Box, padding: int = 0, boxes: list[Box] = boxes) -> list[Box]:
    """find a box that will fit the box with padding within boxes list"""
    return [b for b in boxes if b.length >= box.length + padding and b.width >= box.width + padding and b.height >= box.height + padding]

@app.post("/api/boxes/add")
async def add_boxes(length: str = Form(...), width: str = Form(...), height: str = Form(...)):
    global boxes # this is bad practice, but it's just an example
    global boxes_json # this is bad practice, but it's just an example

    box_dict = dict(
        id="{0}x{1}x{2}".format(length, width, height),
        length=int(length),
        width=int(width),
        height=int(height),
        volume=int(length) * int(width) * int(height),
    )

    box = Box(length=length, width=width, height=height)

    boxes.append(box)
    boxes_json.append(box_dict)

    with open("boxes.json", "w") as f:
        json.dump(boxes_json, f)

    return {
        "message": "{0}x{1}x{2} Box added".format(length, width, height),
        "box": box,
        "boxes": boxes,
    }

@app.post("/api/boxes/will_fit")
async def post_boxes_will_fit(length: str = Form(...), width: str = Form(...), height: str = Form(...), padding: str = Form(...)):

    box = Box(length=int(length), width=int(width), height=int(height))
    return {
        "box": box,
        "padding": int(padding),
        "boxes_that_will_work": find_box_with_padding(box, int(padding))
    }

@app.get("/add", response_class=HTMLResponse)
async def get_boxes_add():
    global boxes

    ul = """
    <ul>
"""    
    for box in boxes:
        ul += """
        <li>{0}x{1}x{2}</li>
""".format(box.length, box.width, box.height)
    
    ul += """</ul>"""

    return f"""
    <html>
        <head>
            <title>Add Box</title>
        </head>
        <body>
            <h1>Boxes</h1>
            <h5>(LxWxH)</h5>
            {ul}
            <hr>
            <h3>Add Box</h3>
            <form action="/api/boxes/add" method="post">
                <label for="length">Length:</label><br>
                <input type="number" id="length" name="length" value="0"><br>
                <label for="width">Width:</label><br>
                <input type="number" id="width" name="width" value="0"><br>
                <label for="height">Height:</label><br>
                <input type="number" id="height" name="height" value="0"><br><br>
                <input type="submit" value="Add Box">
            </form>
            <hr>
            <a href="/">Find a box that will fit</a>
            </body>
        </body>
    </html>
    """

@app.get("/")
async def get_box_dimensions():
    global boxes

    ul = """
    <ul>
"""    
    for box in boxes:
        ul += """
        <li>{0}x{1}x{2}</li>
""".format(box.length, box.width, box.height)
    
    ul += """</ul>"""

    html = f"""
    <html>
    <head>
    <title>Find a box that will fit</title>
    </head>
    <body>    
    <h1>Boxes</h1>
    {ul}
    <hr>
    <br>
    <h1>Find a box that will fit</h1>
    <br>
    <form action="/api/boxes/will_fit" method="post">
        <label for="length">Length:</label><br>
        <input type="number" id="length" name="length" value="0"><br>
        <label for="width">Width:</label><br>
        <input type="number" id="width" name="width" value="0"><br>
        <label for="height">Height:</label><br>
        <input type="number" id="height" name="height" value="0"><br>
        <label for="padding">Padding:</label><br>
        <input type="number" id="padding" name="padding" value="0"><br><br>
        <input type="submit" value="Find Box">
    </form>
    <hr>
        <a href="/add">Add a box</a>
    </body>
    </html>
"""
    return HTMLResponse(content=html, status_code=200)



if __name__ == "__main__":
    length = int(input("Enter length: "))
    width = int(input("Enter width: "))
    height = int(input("Enter height: "))

    padding = int(input("Enter padding: "))

    box = Box(length=length, width=width, height=height)
    
    if len(box) == 0:
        print("No boxes found")
    else:
        for box in find_box_with_padding(box, padding):
            print(box)
    
    
        