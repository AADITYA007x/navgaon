import random

SHOP_TYPES = [
    "Bakery", "Tea Stall", "Kirana Store", "Tailor", "Pharmacy",
    "Barber", "Sweet Shop", "Hardware Store", "Garage",
]

SHOP_JOBS = {
    "Bakery": ["Baker", "Cashier"],
    "Tea Stall": ["Tea Seller"],
    "Kirana Store": ["Shopkeeper", "Delivery Boy"],
    "Tailor": ["Tailor"],
    "Pharmacy": ["Pharmacist", "Cashier"],
    "Barber": ["Barber"],
    "Sweet Shop": ["Halwai", "Cashier"],
    "Hardware Store": ["Shopkeeper", "Helper"],
    "Garage": ["Mechanic"],
}

CIVIC_JOBS = {
    "School": ["Teacher", "Teacher", "Principal", "Peon"],
    "Hospital": ["Doctor", "Nurse", "Nurse", "Ward Attendant"],
    "Police Station": ["Police Officer", "Constable", "Constable"],
    "Town Hall": ["Clerk", "Clerk", "Municipal Officer"],
    "Library": ["Librarian"],
    "Temple": ["Priest", "Caretaker"],
}

CIVIC_WEIGHT = {
    "School": 5,
    "Hospital": 5,
    "Police Station": 3,
    "Town Hall": 3,
    "Library": 1,
    "Temple": 1,
}

OUTDOOR_JOBS = [
    "Farmer", "Auto Driver", "Vegetable Vendor",
    "Construction Worker", "Fisherman", "Electrician", "Plumber",
]


def shop_type(name):
    for t in SHOP_TYPES:
        if name.endswith(t):
            return t
    return None


def jobs_for(building):
    if building.kind == "civic":
        return CIVIC_JOBS.get(building.name, ["Staff"])
    return SHOP_JOBS.get(shop_type(building.name), ["Shopkeeper"])


def weight(building):
    if building.kind == "civic":
        return CIVIC_WEIGHT.get(building.name, 1)
    return 1


def assign_job(workplaces, outdoor_chance=0.3):
    if not workplaces or random.random() < outdoor_chance:
        return random.choice(OUTDOOR_JOBS), None
    w = random.choices(workplaces, weights=[weight(b) for b in workplaces])[0]
    return random.choice(jobs_for(w)), w.id


def with_article(job):
    return ("an " if job[0].lower() in "aeiou" else "a ") + job.lower()