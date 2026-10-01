import random
from faker import Faker
from .database import Base, engine, SessionLocal
from .models import City, Neighborhood, Building, Resident, Event

fake = Faker("en_IN")

NEIGHBORHOOD_NAMES = ["Old Market", "Riverside", "Station Road", "Hill View", "Civil Lines", "Mill Colony"]
SHOP_TYPES = ["Bakery", "Tea Stall", "Kirana Store", "Tailor", "Pharmacy", "Barber", "Sweet Shop", "Hardware Store"]
CIVIC = ["School", "Hospital", "Police Station", "Town Hall", "Library", "Temple"]
JOBS = ["Teacher", "Doctor", "Farmer", "Clerk", "Driver", "Engineer", "Shopkeeper", "Nurse", "Police Officer", "Mechanic"]
TRAITS = ["kind", "stubborn", "ambitious", "lazy", "honest", "gossipy", "generous", "grumpy", "cheerful", "shy"]


def generate_city(name="Navgaon", population=200, seed=None):
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = SessionLocal()

    db.add(City(name=name, day=1))

    neighborhoods = []
    for i, n in enumerate(NEIGHBORHOOD_NAMES):
        nb = Neighborhood(name=n, x=(i % 3) * 100, y=(i // 3) * 100)
        db.add(nb)
        neighborhoods.append(nb)
    db.flush()

    def add_building(kind, bname):
        nb = random.choice(neighborhoods)
        b = Building(
            kind=kind,
            name=bname,
            x=nb.x + random.randint(5, 90),
            y=nb.y + random.randint(5, 90),
            neighborhood_id=nb.id,
        )
        db.add(b)
        return b

    homes = [add_building("home", f"House {i + 1}") for i in range(population // 3)]
    shops = [add_building("shop", f"{fake.last_name()} {random.choice(SHOP_TYPES)}") for _ in range(15)]
    civic = [add_building("civic", c) for c in CIVIC]
    [add_building("park", f"{fake.last_name()} Park") for _ in range(3)]
    db.flush()

    workplaces = shops + civic

    for _ in range(population):
        age = random.randint(1, 85)
        gender = random.choice(["male", "female"])
        first = fake.first_name_male() if gender == "male" else fake.first_name_female()

        if age < 18:
            job, work = "Student", None
        elif age >= 65:
            job, work = "Retired", None
        else:
            job, work = random.choice(JOBS), random.choice(workplaces).id

        db.add(Resident(
            name=f"{first} {fake.last_name()}",
            age=age,
            gender=gender,
            job=job,
            traits=",".join(random.sample(TRAITS, 2)),
            home_id=random.choice(homes).id,
            workplace_id=work,
        ))

    db.add(Event(day=1, kind="founding", description=f"The city of {name} was founded with {population} residents."))
    db.commit()
    db.close()


if __name__ == "__main__":
    generate_city(seed=42)
    print("City generated")