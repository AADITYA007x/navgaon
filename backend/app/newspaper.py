import os
import json
from dotenv import load_dotenv
from groq import Groq
from sqlalchemy import select
from .models import City, Event, Newspaper

load_dotenv()

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

SYSTEM_PROMPT = """You are the editor of The {city} Herald, the local newspaper of {city}, a small Indian town.
Write a short, lively newspaper edition based ONLY on the events provided.
Do not invent major events, deaths, births, or people that are not listed.
You may add small colourful details, local reactions, and light humour.
Group small related events into one article.
Write 2 to 5 articles.
Respond ONLY with valid JSON and nothing else, in exactly this format:
{{"headline": "main headline", "articles": [{{"title": "article title", "body": "2 to 4 sentences"}}]}}"""


def fallback_edition(city_name, events):
    if not events:
        return {
            "headline": f"A quiet day in {city_name}",
            "articles": [{"title": "Nothing to report", "body": "The town went about its business peacefully."}],
        }
    return {
        "headline": events[0].description,
        "articles": [{"title": e.kind.replace("_", " ").capitalize(), "body": e.description} for e in events],
    }


def ai_edition(city_name, day, events):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    event_text = "\n".join(f"- {e.description}" for e in events)
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(city=city_name)},
            {"role": "user", "content": f"Day {day} events:\n{event_text}"},
        ],
    )
    text = response.choices[0].message.content.strip()
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


def write_edition(db, day):
    existing = db.scalar(select(Newspaper).where(Newspaper.day == day))
    if existing:
        return existing

    city = db.scalar(select(City))
    events = list(db.scalars(select(Event).where(Event.day == day).order_by(Event.id)))

    if events and os.getenv("GROQ_API_KEY"):
        try:
            data = ai_edition(city.name, day, events)
        except Exception as e:
            print("Newspaper AI error:", e)
            data = fallback_edition(city.name, events)
    else:
        data = fallback_edition(city.name, events)

    paper = Newspaper(
        day=day,
        headline=str(data.get("headline", ""))[:300],
        content=json.dumps(data.get("articles", [])),
    )
    db.add(paper)
    db.commit()
    return paper