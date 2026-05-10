from contextlib import asynccontextmanager
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

DATA_FILE = Path(__file__).parent / "tokpisin-english.json"

data: dict[str, str] = {}
english_index: dict[str, list[str]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    with DATA_FILE.open("r", encoding="utf-8") as f:
        data.update(json.load(f))
    for tok_word, eng_word in data.items():
        english_index.setdefault(eng_word.lower().strip(), []).append(tok_word)
    yield


app = FastAPI(
    title="Tok Pisin API",
    description="A dictionary API for translating between Tok Pisin and English.",
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


@app.get("/reverse/{word}")
def reverse_translate(word: str):
    key = word.lower().strip()
    matches = english_index.get(key)
    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{word}' was not found in the dictionary",
        )
    return {"english": key, "tokpisin": matches}


@app.post("/words", status_code=status.HTTP_201_CREATED)
def add_word(entry: WordEntry):
    key = entry.tokpisin.lower().strip()
    if key in data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{entry.tokpisin}' already exists",
        )
    data[key] = entry.english
    english_index.setdefault(entry.english.lower().strip(), []).append(key)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return {"tokpisin": key, "english": entry.english}
