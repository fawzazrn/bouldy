"""Seed data and loader for the Malaysian gym catalogue.

This module is used by an Alembic migration. Treat the DATA below as frozen
once the migration is merged: to change it later, write a new migration.

The loader only uses lightweight table definitions (not the ORM models), so it
keeps working even after the models evolve, and it can run on SQLite in tests.
It is idempotent: running it twice changes nothing the second time.
"""

import sqlalchemy as sa

# --- lightweight table definitions (only the columns the seed touches) -------

grade_scales = sa.table(
    "grade_scales",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("kind", sa.String),
    sa.column("version", sa.Integer),
)
grades = sa.table(
    "grades",
    sa.column("id", sa.Integer),
    sa.column("scale_id", sa.Integer),
    sa.column("label", sa.String),
    sa.column("order", sa.Integer),
    sa.column("colour_hex", sa.String),
    sa.column("v_range_label", sa.String),
    sa.column("font_range_label", sa.String),
    sa.column("description", sa.String),
    sa.column("band", sa.String),
)
gym_brands = sa.table(
    "gym_brands",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("slug", sa.String),
    sa.column("grade_scale_id", sa.Integer),
)
brand_route_kinds = sa.table(
    "brand_route_kinds",
    sa.column("brand_id", sa.Integer),
    sa.column("route_kind", sa.String),
)
gyms = sa.table(
    "gyms",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("location", sa.String),
    sa.column("brand_id", sa.Integer),
    sa.column("address", sa.Text),
    sa.column("city", sa.String),
    sa.column("state", sa.String),
)

# --- data ---------------------------------------------------------------------

# Camp 5 colour tiers. The V-scale and Font ranges overlap between tiers, so
# the colour is the grade and the ranges are display text only. Bands are a
# proposal (two tiers each) and can be revised in a later migration.
CAMP5_TIERS = [
    # label, hex, V range, Font range, description, band
    ("Pink", "#f4a6c0", "VB - V1", "3 - 5B", "Lower grades", "beginner"),
    ("Light Blue", "#7ec8e8", "V0 - V2", "4B - 5C", "Beginner/Intermediate", "beginner"),
    ("Yellow", "#f2d03b", "V1 - V3", "5A - 6A+", "Intermediate", "intermediate"),
    ("Orange", "#f28c28", "V2 - V4", "5B - 6B+", "Intermediate+", "intermediate"),
    ("Green", "#3fa34d", "V3 - V5", "5C+ - 6C+", "Advanced", "advanced"),
    ("Purple", "#7b4bb3", "V4 - V6", "6A+ - 7A", "Advanced+", "advanced"),
    ("Red", "#d8151e", "V5 - V7", "6C - 7B", "Expert", "expert"),
    ("Black", "#1a1a1a", "V6 - V8+", "6C+ - 7B+", "Elite", "expert"),
]

# Scale name -> (kind, list of grade rows). Numeric scales carry no V or Font
# equivalents and no bands, because the gyms do not publish them.
SCALES = {
    "Batuu 1-15": ("numeric", [(str(n), None, None, None, None, None) for n in range(1, 16)]),
    "Boulder Story 1-12": ("numeric", [(str(n), None, None, None, None, None) for n in range(1, 13)]),
    "Camp 5 Colour Tiers": (
        "colour_tier",
        [(label, hex_, v, font, desc, band) for label, hex_, v, font, desc, band in CAMP5_TIERS],
    ),
}

# Brand -> (slug, scale name, allowed route kinds)
BRANDS = {
    "Batuu": ("batuu", "Batuu 1-15", ["wildcard"]),
    "Boulder Story": (
        "boulder-story",
        "Boulder Story 1-12",
        ["wildcard", "signature_send", "gym_project"],
    ),
    "Camp 5": ("camp-5", "Camp 5 Colour Tiers", []),
}

# name, brand, short location, city, state, full address
GYMS = [
    (
        "Batuu", "Batuu", "Damansara Utama, Petaling Jaya", "Petaling Jaya", "Selangor",
        "G-28, Ground Floor, 3 Damansara, 3, Jalan SS 20/27, Damansara Utama, 47400 Petaling Jaya, Selangor",
    ),
    (
        "Boulder Story", "Boulder Story", "Damansara Jaya, Petaling Jaya", "Petaling Jaya", "Selangor",
        "F21-F23A, Atria Shopping Gallery, Jalan SS 22/23, Damansara Jaya, 47400 Petaling Jaya, Selangor",
    ),
    (
        "Camp5 1Utama", "Camp 5", "Bandar Utama, Petaling Jaya", "Petaling Jaya", "Selangor",
        "5th Floor, EZ501, 1 Utama Shopping Centre (New Wing), 1, Lebuh Bandar Utama, Bandar Utama, 47800 Petaling Jaya, Selangor",
    ),
    (
        "Camp5 Eco City", "Camp 5", "Bangsar, Kuala Lumpur", "Kuala Lumpur", "Kuala Lumpur",
        "Lot 07 & 08, 4th Floor, KL Eco City Mall, 3, Jalan Bangsar, Bangsar, 59200 Kuala Lumpur",
    ),
    (
        "Camp5 Utropolis", "Camp 5", "Shah Alam", "Shah Alam", "Selangor",
        "Lot UG-D1a, Utropolis Marketplace, Jalan Kontraktor U1/14, Seksyen U1, 40150 Shah Alam, Selangor",
    ),
    (
        "Camp5 Paradigm", "Camp 5", "Skudai, Johor Bahru", "Johor Bahru", "Johor",
        "7F-08 Level 7, Skudai Paradigm Mall, Skudai Hwy, 81200 Johor Bahru, Johor",
    ),
    (
        "Camp5 Jumpa", "Camp 5", "Bukit Bintang, Kuala Lumpur", "Kuala Lumpur", "Kuala Lumpur",
        "MUT-1 3rd Floor Sungai Wang Mall, Jln Sultan Ismail, Bukit Bintang, 59200 Kuala Lumpur",
    ),
    (
        "Camp5 KL East", "Camp 5", "Sunway Montana, Kuala Lumpur", "Kuala Lumpur", "Kuala Lumpur",
        "G3-22 & G3-23, KL East Mall, Jln Lingkaran Tengah 2, Sunway Montana (U/C), 53100 Kuala Lumpur, Federal Territory of Kuala Lumpur",
    ),
    (
        "Camp5 Ombak", "Camp 5", "KLCC, Kuala Lumpur", "Kuala Lumpur", "Kuala Lumpur",
        "G-13 & G-14, Ground Floor, Plaza Ombak KLCC, 20, Persiaran KLCC, Kuala Lumpur City Centre, 50088 Kuala Lumpur",
    ),
]


# --- loader -------------------------------------------------------------------


def _one(conn, stmt):
    return conn.execute(stmt).scalar()


def seed_catalogue(conn) -> None:
    """Insert scales, grades, brands and gyms that are not already there."""
    scale_ids: dict[str, int] = {}

    for scale_name, (kind, rows) in SCALES.items():
        scale_id = _one(
            conn,
            sa.select(grade_scales.c.id).where(grade_scales.c.name == scale_name),
        )
        if scale_id is None:
            conn.execute(
                sa.insert(grade_scales).values(name=scale_name, kind=kind, version=1)
            )
            scale_id = _one(
                conn,
                sa.select(grade_scales.c.id).where(grade_scales.c.name == scale_name),
            )
        scale_ids[scale_name] = scale_id

        for position, (label, hex_, v, font, desc, band) in enumerate(rows, start=1):
            exists = _one(
                conn,
                sa.select(grades.c.id).where(
                    grades.c.scale_id == scale_id, grades.c.label == label
                ),
            )
            if exists is None:
                conn.execute(
                    sa.insert(grades).values(
                        scale_id=scale_id,
                        label=label,
                        order=position,
                        colour_hex=hex_,
                        v_range_label=v,
                        font_range_label=font,
                        description=desc,
                        band=band,
                    )
                )

    brand_ids: dict[str, int] = {}

    for brand_name, (slug, scale_name, kinds) in BRANDS.items():
        brand_id = _one(
            conn,
            sa.select(gym_brands.c.id).where(gym_brands.c.slug == slug),
        )
        if brand_id is None:
            conn.execute(
                sa.insert(gym_brands).values(
                    name=brand_name,
                    slug=slug,
                    grade_scale_id=scale_ids[scale_name],
                )
            )
            brand_id = _one(
                conn,
                sa.select(gym_brands.c.id).where(gym_brands.c.slug == slug),
            )
        brand_ids[brand_name] = brand_id

        for kind in kinds:
            exists = _one(
                conn,
                sa.select(brand_route_kinds.c.brand_id).where(
                    brand_route_kinds.c.brand_id == brand_id,
                    brand_route_kinds.c.route_kind == kind,
                ),
            )
            if exists is None:
                conn.execute(
                    sa.insert(brand_route_kinds).values(
                        brand_id=brand_id, route_kind=kind
                    )
                )

    for name, brand_name, location, city, state, address in GYMS:
        row = conn.execute(
            sa.select(gyms.c.id, gyms.c.brand_id, gyms.c.address, gyms.c.city, gyms.c.state)
            .where(sa.func.lower(gyms.c.name) == name.lower())
        ).first()

        if row is None:
            conn.execute(
                sa.insert(gyms).values(
                    name=name,
                    location=location,
                    brand_id=brand_ids[brand_name],
                    address=address,
                    city=city,
                    state=state,
                )
            )
            continue

        # A gym with this name already exists: only fill in what is missing,
        # never overwrite what someone has entered.
        updates = {}
        if row.brand_id is None:
            updates["brand_id"] = brand_ids[brand_name]
        if row.address is None:
            updates["address"] = address
        if row.city is None:
            updates["city"] = city
        if row.state is None:
            updates["state"] = state
        if updates:
            conn.execute(sa.update(gyms).where(gyms.c.id == row.id).values(**updates))
