import random
from faker import Faker
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import City, Neighborhood, Building, Resident, Event
from .generate import TRAITS
from .jobs import SHOP_TYPES, assign_job, with_article

fake = Faker("en_IN")
DAYS_PER_YEAR = 30
ORIGIN_CITIES = ["Pune", "Nashik", "Mumbai", "Nagpur", "Surat", "Indore", "Kolhapur", "Aurangabad"]


CITY_EVENTS = [
    "Heavy rain flooded the streets of {n}.",
    "A wedding procession in {n} blocked traffic for two hours.",
    "A small fire broke out in {n}, but no one was hurt.",
    "{n} held a lively street festival.",
    "A power cut left {n} in darkness for the evening.",
    "A stray cow wandered into a shop in {n}, causing chaos.",
    "Residents of {n} complained to the Town Hall about potholes.",
    "A cricket match in {n} ended in a heated argument.",
]


def log(db, day, kind, description):
    db.add(Event(day=day, kind=kind, description=description))


def last_name(name):
    return name.split()[-1]


def advance_day(db: Session):
    city = db.scalar(select(City))
    city.day += 1
    day = city.day

    residents = list(db.scalars(select(Resident).where(Resident.alive == True)))
    by_id = {r.id: r for r in residents}
    neighborhoods = list(db.scalars(select(Neighborhood)))
    shops = list(db.scalars(select(Building).where(Building.kind == "shop")))
    civic = list(db.scalars(select(Building).where(Building.kind == "civic")))

    if day % DAYS_PER_YEAR == 0:
        for r in residents:
            r.age += 1
            if r.age == 5 and r.job == "Child":
                r.job = "Student"
            elif r.age == 18 and r.job == "Student":
                r.job = "Unemployed"
            elif r.age == 65 and r.job not in ("Student", "Retired", "Child"):
                r.job = "Retired"
                r.workplace_id = None
        log(db, day, "new_year", f"A new year begins in {city.name}. Everyone is one year older.")

    for r in residents:
        chance = 0.0002 if r.age < 60 else 0.002 if r.age < 80 else 0.01
        if random.random() < chance:
            r.alive = False
            r.workplace_id = None
            partner = by_id.get(r.partner_id)
            if partner:
                partner.partner_id = None
            log(db, day, "death", f"{r.name}, aged {r.age}, passed away.")

    living = [r for r in residents if r.alive]

    if random.random() < 0.15:
        singles = [r for r in living if r.partner_id is None and 21 <= r.age <= 45]
        men = [r for r in singles if r.gender == "male"]
        women = [r for r in singles if r.gender == "female"]
        if men and women:
            m, w = random.choice(men), random.choice(women)
            m.partner_id, w.partner_id = w.id, m.id
            w.home_id = m.home_id
            log(db, day, "marriage", f"{m.name} and {w.name} got married.")

    for w in living:
        if w.gender == "female" and w.partner_id and 20 <= w.age <= 40 and random.random() < 0.012:
            father = by_id.get(w.partner_id)
            if not father or not father.alive:
                continue
            gender = random.choice(["male", "female"])
            first = fake.first_name_male() if gender == "male" else fake.first_name_female()
            baby_name = f"{first} {last_name(father.name)}"
            db.add(Resident(
                name=baby_name,
                age=0,
                gender=gender,
                job="Child",
                traits=",".join(random.sample(TRAITS, 2)),
                home_id=w.home_id,
            ))
            log(db, day, "birth", f"{w.name} and {father.name} welcomed a baby named {baby_name}.")
    homes = list(db.scalars(select(Building).where(Building.kind == "home")))
    if homes and neighborhoods and len(living) / len(homes) > 4:
        n = random.choice(neighborhoods)
        house = Building(
            kind="home",
            name=f"House {len(homes) + 1}",
            x=n.x + random.randint(5, 90),
            y=n.y + random.randint(5, 90),
            neighborhood_id=n.id,
        )
        db.add(house)
        db.flush()
        homes.append(house)
        log(db, day, "new_house", f"A new house was built in {n.name} as the town keeps growing.")

    if homes and random.random() < 0.1:
        home = random.choice(homes)
        surname = fake.last_name()
        origin = random.choice(ORIGIN_CITIES)
        size = random.choice([1, 2, 2, 3, 4])
        jobs_open = [s for s in shops if s.is_open] + civic
        newcomers = []

        for i in range(size):
            if i == 0:
                age = random.randint(22, 45)
                gender = random.choice(["male", "female"])
            elif i == 1:
                age = max(20, newcomers[0].age + random.randint(-4, 4))
                gender = "female" if newcomers[0].gender == "male" else "male"
            else:
                age = random.randint(1, 15)
                gender = random.choice(["male", "female"])

            if age < 5:
                job, work = "Child", None
            elif age < 18:
                job, work = "Student", None
            else:
                job, work = assign_job(jobs_open)

            first = fake.first_name_male() if gender == "male" else fake.first_name_female()
            person = Resident(
                name=f"{first} {surname}",
                age=age,
                gender=gender,
                job=job,
                traits=",".join(random.sample(TRAITS, 2)),
                home_id=home.id,
                workplace_id=work,
            )
            db.add(person)
            newcomers.append(person)

        db.flush()
        if size >= 2:
            a, b = newcomers[0], newcomers[1]
            a.partner_id, b.partner_id = b.id, a.id

        if size == 1:
            p = newcomers[0]
            msg = f"{p.name} moved to {city.name} from {origin} to work as {with_article(p.job)}."
        else:
            msg = f"The {surname} family of {size} moved to {city.name} from {origin}."
        log(db, day, "migration", msg)
    for s in shops:
        if not s.is_open:
            continue
        s.money += random.randint(-60, 55)
        if s.money <= 0:
            s.is_open = False
            log(db, day, "shop_closed", f"{s.name} shut down after running out of money.")
            for r in living:
                if r.workplace_id == s.id:
                    r.workplace_id = None
                    r.job = "Unemployed"

    closed = [s for s in shops if not s.is_open]
    if closed and random.random() < 0.05:
        s = random.choice(closed)
        old_name = s.name
        s.name = f"{fake.last_name()} {random.choice(SHOP_TYPES)}"
        s.money = 1000
        s.is_open = True
        log(db, day, "shop_opened", f"{s.name} opened where {old_name} used to be.")

    open_workplaces = [s for s in shops if s.is_open] + civic
    by_building = {b.id: b for b in open_workplaces}
    for r in living:
        if r.job == "Unemployed" and random.random() < 0.05:
            r.job, r.workplace_id = assign_job(open_workplaces)
            w = by_building.get(r.workplace_id)
            where = f" at {w.name}" if w else ""
            log(db, day, "new_job", f"{r.name} started work{where} as {with_article(r.job)}.")

    if neighborhoods and random.random() < 0.15:
        n = random.choice(neighborhoods)
        log(db, day, "city", random.choice(CITY_EVENTS).format(n=n.name))

    db.commit()
    return day