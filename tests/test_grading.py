"""Tests for gym brands, locked grade scales, route kinds and the seed data."""

import pytest
import sqlalchemy as sa

from app.models.gym import Gym
from app.models.grading import Grade, GymBrand
from app.seed.catalogue import GYMS, seed_catalogue


@pytest.fixture
def seeded(db):
    seed_catalogue(db)
    db.commit()
    return db


def gym_id(db, name):
    return db.query(Gym).filter(Gym.name == name).one().id


def grade_id(db, scale_prefix, label):
    return (
        db.query(Grade)
        .join(Grade.scale)
        .filter(Grade.label == label, Grade.scale.has(name=scale_prefix))
        .one()
        .id
    )


def route_payload(gym, **extra):
    return {"gym_id": gym, "route_name": "Test Route", **extra}


# --- seed ------------------------------------------------------------------


def test_seed_creates_brands_scales_and_gyms(seeded):
    brands = {b.name: b for b in seeded.query(GymBrand).all()}

    assert set(brands) == {"Batuu", "Boulder Story", "Camp 5"}
    assert [g.label for g in brands["Batuu"].grade_scale.grades] == [
        str(n) for n in range(1, 16)
    ]
    assert len(brands["Boulder Story"].grade_scale.grades) == 12
    assert [g.label for g in brands["Camp 5"].grade_scale.grades] == [
        "Pink", "Light Blue", "Yellow", "Orange",
        "Green", "Purple", "Red", "Black",
    ]
    assert brands["Batuu"].allowed_route_kinds == ["wildcard"]
    assert sorted(brands["Boulder Story"].allowed_route_kinds) == [
        "gym_project", "signature_send", "wildcard",
    ]
    assert brands["Camp 5"].allowed_route_kinds == []


def test_seed_creates_all_nine_locations_with_addresses(seeded):
    camp5 = seeded.query(Gym).filter(Gym.name.like("Camp5 %")).all()

    assert len(camp5) == 7
    assert len(seeded.query(Gym).all()) == len(GYMS) == 9
    assert all(g.address and g.brand.name for g in seeded.query(Gym).all())
    # Locations of one chain share one brand and so one scale.
    assert len({g.brand_id for g in camp5}) == 1


def test_seed_is_idempotent(seeded):
    before = (
        seeded.query(Gym).count(),
        seeded.query(Grade).count(),
        seeded.query(GymBrand).count(),
    )

    seed_catalogue(seeded)
    seeded.commit()

    assert before == (
        seeded.query(Gym).count(),
        seeded.query(Grade).count(),
        seeded.query(GymBrand).count(),
    )


def test_seed_links_existing_gym_without_overwriting(db):
    db.add(Gym(name="camp5 eco city", location="Typed by a person"))
    db.commit()

    seed_catalogue(db)
    db.commit()

    existing = db.query(Gym).filter(sa.func.lower(Gym.name) == "camp5 eco city").one()

    assert db.query(Gym).filter(sa.func.lower(Gym.name) == "camp5 eco city").count() == 1
    assert existing.name == "camp5 eco city"
    assert existing.location == "Typed by a person"
    assert existing.brand.name == "Camp 5"
    assert existing.address is not None


def test_camp5_tiers_keep_overlapping_ranges_as_text_only(seeded):
    yellow = seeded.query(Grade).filter(Grade.label == "Yellow").one()
    orange = seeded.query(Grade).filter(Grade.label == "Orange").one()

    assert yellow.v_range_label == "V1 - V3"
    assert orange.v_range_label == "V2 - V4"
    assert yellow.order < orange.order


def test_numeric_scales_have_no_invented_equivalents_or_bands(seeded):
    seven = seeded.query(Grade).filter(
        Grade.label == "7", Grade.scale.has(name="Batuu 1-15")
    ).one()

    assert seven.v_range_label is None
    assert seven.font_range_label is None
    assert seven.band is None


# --- read endpoints --------------------------------------------------------


def test_list_brands(admin_client, seeded):
    resp = admin_client.get("/brands/")

    assert resp.status_code == 200
    assert [b["name"] for b in resp.json()] == ["Batuu", "Boulder Story", "Camp 5"]


def test_brand_detail_includes_ordered_grades(admin_client, seeded):
    brand_id = seeded.query(GymBrand).filter(GymBrand.slug == "camp-5").one().id

    body = admin_client.get(f"/brands/{brand_id}").json()

    assert [g["label"] for g in body["grade_scale"]["grades"]][:2] == ["Pink", "Light Blue"]
    assert body["grade_scale"]["kind"] == "colour_tier"


def test_missing_brand_is_404(admin_client):
    assert admin_client.get("/brands/999").status_code == 404


def test_gym_grades_endpoint_for_branded_gym(admin_client, seeded):
    body = admin_client.get(f"/gyms/{gym_id(seeded, 'Boulder Story')}/grades").json()

    assert body["grade_required"] is True
    assert len(body["scale"]["grades"]) == 12
    assert "signature_send" in body["allowed_route_kinds"]


def test_gym_grades_endpoint_for_unbranded_gym(admin_client, db):
    db.add(Gym(name="Plain Gym", location="Penang"))
    db.commit()
    plain = db.query(Gym).one().id

    body = admin_client.get(f"/gyms/{plain}/grades").json()

    assert body == {
        "gym_id": plain,
        "brand_id": None,
        "scale": None,
        "allowed_route_kinds": [],
        "grade_required": False,
    }


def test_gym_response_includes_address_fields(admin_client, seeded):
    body = admin_client.get(f"/gyms/{gym_id(seeded, 'Batuu')}").json()

    assert body["brand_id"] is not None
    assert "Damansara Utama" in body["address"]
    assert body["city"] == "Petaling Jaya"


# --- route validation ------------------------------------------------------


def test_route_with_locked_grade_mirrors_label(admin_client, seeded):
    gid = gym_id(seeded, "Camp5 Ombak")
    yellow = grade_id(seeded, "Camp 5 Colour Tiers", "Yellow")

    resp = admin_client.post("/routes/", json=route_payload(gid, grade_id=yellow))

    assert resp.status_code == 201
    assert resp.json()["grade"] == "Yellow"
    assert resp.json()["grade_id"] == yellow


def test_locked_grade_overrides_conflicting_free_text(admin_client, seeded):
    gid = gym_id(seeded, "Batuu")
    seven = grade_id(seeded, "Batuu 1-15", "7")

    resp = admin_client.post("/routes/", json=route_payload(gid, grade_id=seven, grade="V9"))

    assert resp.status_code == 201
    assert resp.json()["grade"] == "7"


def test_branded_gym_rejects_free_text_grade(admin_client, seeded):
    resp = admin_client.post(
        "/routes/", json=route_payload(gym_id(seeded, "Batuu"), grade="V3")
    )

    assert resp.status_code == 422
    assert "grade_id" in resp.json()["detail"]


def test_grade_from_another_brand_is_rejected(admin_client, seeded):
    camp5_yellow = grade_id(seeded, "Camp 5 Colour Tiers", "Yellow")

    resp = admin_client.post(
        "/routes/",
        json=route_payload(gym_id(seeded, "Batuu"), grade_id=camp5_yellow),
    )

    assert resp.status_code == 422


def test_unknown_grade_id_is_rejected(admin_client, seeded):
    resp = admin_client.post(
        "/routes/",
        json=route_payload(gym_id(seeded, "Batuu"), grade_id=99999),
    )

    assert resp.status_code == 422


def test_grade_id_on_unbranded_gym_is_rejected(admin_client, seeded, db):
    db.add(Gym(name="Plain Gym", location="Penang"))
    db.commit()
    plain = gym_id(db, "Plain Gym")

    resp = admin_client.post(
        "/routes/",
        json=route_payload(plain, grade_id=grade_id(db, "Batuu 1-15", "3")),
    )

    assert resp.status_code == 422


def test_unbranded_gym_keeps_free_text_grades(admin_client, db):
    db.add(Gym(name="Plain Gym", location="Penang"))
    db.commit()

    resp = admin_client.post(
        "/routes/",
        json=route_payload(db.query(Gym).one().id, grade="V4"),
    )

    assert resp.status_code == 201
    assert resp.json()["grade"] == "V4"
    assert resp.json()["grade_id"] is None


def test_unbranded_gym_still_requires_a_grade(admin_client, db):
    db.add(Gym(name="Plain Gym", location="Penang"))
    db.commit()

    resp = admin_client.post("/routes/", json=route_payload(db.query(Gym).one().id))

    assert resp.status_code == 422


def test_wildcard_route_needs_no_grade(admin_client, seeded):
    resp = admin_client.post(
        "/routes/",
        json=route_payload(gym_id(seeded, "Batuu"), route_kind="wildcard"),
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["route_kind"] == "wildcard"
    assert body["grade_id"] is None
    assert body["grade"] == "Wildcard"


def test_route_kind_must_be_allowed_for_brand(admin_client, seeded):
    # Batuu only has wildcard.
    resp = admin_client.post(
        "/routes/",
        json=route_payload(gym_id(seeded, "Batuu"), route_kind="signature_send"),
    )
    assert resp.status_code == 422

    # Camp 5 has none.
    resp = admin_client.post(
        "/routes/",
        json=route_payload(gym_id(seeded, "Camp5 Jumpa"), route_kind="wildcard"),
    )
    assert resp.status_code == 422


def test_boulder_story_gym_project_can_carry_its_own_grade(admin_client, seeded):
    resp = admin_client.post(
        "/routes/",
        json=route_payload(
            gym_id(seeded, "Boulder Story"),
            route_kind="gym_project",
            grade_id=grade_id(seeded, "Boulder Story 1-12", "9"),
        ),
    )

    assert resp.status_code == 201
    assert resp.json()["route_kind"] == "gym_project"
    assert resp.json()["grade"] == "9"


def test_unknown_route_kind_is_422(admin_client, seeded):
    resp = admin_client.post(
        "/routes/",
        json=route_payload(gym_id(seeded, "Batuu"), route_kind="nonsense"),
    )

    assert resp.status_code == 422


# --- route updates ---------------------------------------------------------


@pytest.fixture
def batuu_route(admin_client, seeded):
    resp = admin_client.post(
        "/routes/",
        json=route_payload(
            gym_id(seeded, "Batuu"),
            grade_id=grade_id(seeded, "Batuu 1-15", "4"),
        ),
    )
    assert resp.status_code == 201
    return resp.json()


def test_update_to_another_locked_grade(admin_client, seeded, batuu_route):
    new = grade_id(seeded, "Batuu 1-15", "10")

    resp = admin_client.put(f"/routes/{batuu_route['id']}", json={"grade_id": new})

    assert resp.status_code == 200
    assert resp.json()["grade"] == "10"


def test_update_with_free_text_on_branded_gym_is_rejected(admin_client, batuu_route):
    resp = admin_client.put(f"/routes/{batuu_route['id']}", json={"grade": "V9"})

    assert resp.status_code == 422


def test_update_not_touching_grade_leaves_it_alone(admin_client, batuu_route):
    resp = admin_client.put(f"/routes/{batuu_route['id']}", json={"wall": "Cave"})

    assert resp.status_code == 200
    assert resp.json()["grade"] == "4"
    assert resp.json()["grade_id"] == batuu_route["grade_id"]


def test_moving_route_to_another_brand_requires_a_matching_grade(
    admin_client, seeded, batuu_route
):
    resp = admin_client.put(
        f"/routes/{batuu_route['id']}",
        json={"gym_id": gym_id(seeded, "Camp5 Jumpa")},
    )

    assert resp.status_code == 422


def test_legacy_route_can_be_edited_without_touching_grade(admin_client, db):
    """A route that predates grade scales keeps working for other edits."""
    gym = Gym(name="Old Gym", location="Penang")
    db.add(gym)
    db.commit()
    created = admin_client.post(
        "/routes/", json=route_payload(gym.id, grade="V3")
    ).json()

    resp = admin_client.put(f"/routes/{created['id']}", json={"colour": "red"})

    assert resp.status_code == 200
    assert resp.json()["grade"] == "V3"


# --- gyms ------------------------------------------------------------------


def test_create_gym_with_brand_and_address(admin_client, seeded):
    brand = seeded.query(GymBrand).filter(GymBrand.slug == "camp-5").one().id

    resp = admin_client.post(
        "/gyms/",
        json={
            "name": "Camp5 New",
            "location": "Somewhere",
            "brand_id": brand,
            "address": "1 Test Road",
        },
    )

    assert resp.status_code == 201
    assert resp.json()["brand_id"] == brand
    assert resp.json()["address"] == "1 Test Road"


def test_create_gym_with_unknown_brand_is_400(admin_client):
    resp = admin_client.post(
        "/gyms/",
        json={"name": "X", "location": "Y", "brand_id": 999},
    )

    assert resp.status_code == 400


def test_update_gym_with_unknown_brand_is_400(admin_client, db):
    db.add(Gym(name="Plain Gym", location="Penang"))
    db.commit()

    resp = admin_client.put(f"/gyms/{db.query(Gym).one().id}", json={"brand_id": 999})

    assert resp.status_code == 400


# --- mapping existing routes -----------------------------------------------


def test_mapping_links_exact_matches_and_reports_the_rest(seeded, db):
    from app.models.route import Route
    from app.seed.map_route_grades import apply_mapping, plan_mapping

    gid = gym_id(seeded, "Camp5 Ombak")
    db.add_all(
        [
            Route(gym_id=gid, route_name="a", grade=" yellow "),
            Route(gym_id=gid, route_name="b", grade="V3"),
        ]
    )
    db.commit()

    matches, unmatched = plan_mapping(db)

    assert [r.route_name for r, _ in matches] == ["a"]
    assert [r.route_name for r in unmatched] == ["b"]

    apply_mapping(db, matches)

    linked = db.query(Route).filter(Route.route_name == "a").one()
    assert linked.grade == "Yellow"
    assert linked.grade_id is not None
    assert db.query(Route).filter(Route.route_name == "b").one().grade_id is None


def test_mapping_ignores_gyms_without_a_brand(db):
    from app.models.route import Route
    from app.seed.map_route_grades import plan_mapping

    gym = Gym(name="Plain Gym", location="Penang")
    db.add(gym)
    db.commit()
    db.add(Route(gym_id=gym.id, route_name="a", grade="V3"))
    db.commit()

    assert plan_mapping(db) == ([], [])
