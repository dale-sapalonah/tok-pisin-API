from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel

jsonfile = 'tokpisin-english.json'

app = FastAPI()

with open(jsonfile, 'r') as f:
    data = json.load(f)


class PostSchema(BaseModel):
    """Schema for user defined values to be passed in from the front end"""
    english: str
    tokpisin: str

    def __repr__(self) -> str:
        return f'PostSchema(tokpisin="{self.tokpisin}", english="{self.english}")'


@app.get("/translate/{t_word}")
def translate(t_word: str):
    for key, value in data.items():
        if t_word.lower() == key:
            return {"english": value}
        elif t_word.lower() not in data.keys():
            raise HTTPException(status_code=404, detail=f"{t_word} does not exist")


@app.post("/post")
def update_dict(post: PostSchema):  # <- post = PostSchema(tokpisin={}, english={})
    if post.tokpisin.lower() in data.keys():
        return {"data": f"{post.tokpisin} already exists"}
    print(post)
    return {"data": post}

    # create a data class for the schema for this post operation
