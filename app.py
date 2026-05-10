from contextlib import asynccontextmanager
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

DATA_FILE = Path(__file__).parent / "tokpisin-english.json"

data: dict[str, str] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    with DATA_FILE.open("r", encoding="utf-8") as f:
        data.update(json.load(f))
    yield


app = FastAPI(
    title="Tok Pisin API",
    description="A dictionary API for translating Tok Pisin words to English.",
    version="1.0.0",
    lifespan=lifespan,
)


class WordEntry(BaseModel):
    tokpisin: str
    english: str


@app.get("/")
def root():
    return {"message": "Tok Pisin API", "total_entries": len(data)}


@app.get("/translate/{word}")
def translate(word: str):
    key = word.lower().strip()
    translation = data.get(key)
    if translation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{word}' was not found in the dictionary",
        )
    return {"tokpisin": key, "english": translation}


@app.post("/words", status_code=status.HTTP_201_CREATED)
def add_word(entry: WordEntry):
    key = entry.tokpisin.lower().strip()
    if key in data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{entry.tokpisin}' already exists",
        )
    data[key] = entry.english
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return {"tokpisin": key, "english": entry.english}
