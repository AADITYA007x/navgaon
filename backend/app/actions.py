import random
from faker import Faker
from sqlalchemy import select
from .models import City, Neighborhood, Building, Resident, Event
from .generate import SHOP_TYPES, JOBS

fake = Faker("en_IN")

ACTIONS = {
    "festival": {"name": "Fund a festival", "description": "Every shop gets a boost in sales."},
    "storm": {"name": "Summon a storm", "description": "One neighbourhood's shops lose money."},
    "new_shop": {"name": "Open a new shop", "description": "A new shop opens and hires locals."},
    "job_fair": {"name": "Hold a job fair", "description": "Up to 5 unemployed people find work."},
    "matchmaker": {"name": "Play matchmaker", "description": "Two single residents get married."},
    "rumor": {"name": "Start a rumour", "description": "Spread juicy gossip about someone."},
}

RUMORS = [
    "{a} was seen sneaking out of {b}'s house at midnight.",
    "{a} is secretly planning to run for mayor.",
    "{a} claims to have found buried treasure near the river.",
    "{a} and {b} had a loud argument over a cricket match.",
    "{a} has apparently been feeding every stray cow in town.",
    "{a} won the lottery but is telling no one.",
    "{a} has been taking secret cooking lessons from {b}.",
]


def used_today(db, city):
    query = select(Event).where(Event.day == city.day + 1, Event.kind.like("player_%"))
    return db.scalar(query) is not None


def list_actions(db):
    city = db.scalar(select(City))
    return {
        "available": not used_today(db, city),
        "actions": [{"key": k, **v} for k, v in ACTIONS.items()],
    }


def apply_action(db, key):
    if key not in ACTIONS:
        return {"error": "Unknown action."}

    city = db.scalar(select(City))
    if used_today(db, city):
        return {"error": "You've already made today's decision. Advance to the next day first."}

    day = city.day + 1
    neighborhoods = list(db.scalars(select(Neighborhood)))
    shops = list(db.scalars(select(Building).where(Building.kind == "shop", Building.is_open == True)))
    civic = list(db.scalars(select(Building).where(Building.kind == "civic")))
    living = list(db.scalars(select(Resident).where(Resident.alive == True)))
    unemployed = [r for r in living if r.job == "Unemployed"]
    n = random.choice(neighborhoods)

    if key == "festival":
        for s in shops:
            s.money += 150
        msg = f"The town council funded a grand festival in {n.name}. Shops across {city.name} reported booming sales."

    elif key == "storm":
        hit = [s for s in shops if s.neighborhood_id == n.id]
        for s in hit:
            s.money -= random.randint(200, 400)
        msg = f"A violent storm battered {n.name}, damaging {len(hit)} shops."

    elif key == "new_shop":
        shop = Building(
            kind="shop",
            name=f"{fake.last_name()} {random.choice(SHOP_TYPES)}",
            x=n.x + random.randint(5, 90),
            y=n.y + random.randint(5, 90),
            neighborhood_id=n.id,
            is_open=True,
            money=1000,
        )
        db.add(shop)
        db.flush()
        hired = random.sample(unemployed, min(2, len(unemployed)))
        for r in hired:
            r.job = "Shopkeeper"
            r.workplace_id = shop.id
        msg = f"{shop.name} opened its doors in {n.name}."
        if hired:
            msg += " New staff: " + ", ".join(r.name for r in hired) + "."

    elif key == "job_fair":
        workplaces = shops + civic
        hired = random.sample(unemployed, min(5, len(unemployed))) if workplaces else []
        for r in hired:
            w = random.choice(workplaces)
            r.job = random.choice(JOBS)
            r.workplace_id = w.id
        if hired:
            msg = f"A job fair at the Town Hall found work for {len(hired)} residents."
        else:
            msg = "A job fair was held at the Town Hall, but nobody was looking for work."

    elif key == "matchmaker":
        singles = [r for r in living if r.partner_id is None and 21 <= r.age <= 45]
        men = [r for r in singles if r.gender == "male"]
        women = [r for r in singles if r.gender == "female"]
        if men and women:
            m, w = random.choice(men), random.choice(women)
            m.partner_id, w.partner_id = w.id, m.id
            w.home_id = m.home_id
            msg = f"With a little help from the town matchmaker, {m.name} and {w.name} got married."
        else:
            msg = "The town matchmaker searched everywhere but found no suitable match."

    else:
        if len(living) >= 2:
            a, b = random.sample(living, 2)
            msg = "Rumour has it: " + random.choice(RUMORS).format(a=a.name, b=b.name)
        else:
            msg = "Someone tried to start a rumour, but there was nobody left to gossip about."

    db.add(Event(day=day, kind=f"player_{key}", description=msg))
    db.commit()
    return {"message": msg, "day": day}