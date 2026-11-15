# Gym brands, locations and locked grades

## What this adds

- **Gym brands.** A brand groups the locations of one chain (Camp 5 has seven).
  Batuu, Boulder Story and Camp 5 are seeded.
- **Locked grade scales.** Each brand has one fixed, ordered list of grades.
  Routes at a branded gym must pick from it.
  - Batuu: `1` to `15`
  - Boulder Story: `1` to `12`
  - Camp 5: eight colour tiers (Pink, Light Blue, Yellow, Orange, Green, Purple, Red, Black)
- **Route kinds.** Wildcard, Signature Send and Gym Project are route types, not
  grades. A brand lists which ones it uses. They are separate from a climber's
  own `project` attempt result.
- **Gym details.** Address, city, state, optional coordinates, phone, opening
  hours and an active flag, all optional.

## Rules

- Camp 5 tiers overlap in V-scale (Yellow is V1 to V3, Orange is V2 to V4). The
  colour is the grade. The V and Font ranges are stored as display text only and
  are never used to order or compare.
- Numeric scales have no V or Font equivalents and no bands, because the gyms do
  not publish them. They are left empty rather than guessed.
- Grades only compare within one gym or brand, never across brands.
- Bands (beginner to expert) exist for Camp 5 as a proposal. They are not used
  for anything yet.

## API changes (all additive)

| Endpoint | Change |
|---|---|
| `GET /brands/`, `GET /brands/{id}` | New. A brand with its grade scale and allowed route kinds. |
| `GET /gyms/{id}/grades` | New. Everything a client needs to build a grade picker for one gym. |
| `GET/POST/PUT /gyms` | Extra optional fields: `brand_id`, `address`, `city`, `state`, `latitude`, `longitude`, `phone`, `opening_hours`, `is_active`. |
| `POST/PUT /routes` | New optional `grade_id` and `route_kind`. Responses include both. |

How route grades are validated:

- Gym **with** a brand: `grade_id` is required (or a `route_kind` that the brand
  allows, which needs no grade). Free-text `grade` is rejected with 422.
- Gym **without** a brand: free-text `grade` works exactly as before.
- `grade_id` must belong to the gym's brand scale.
- The legacy `routes.grade` text is always filled in (the grade label, or
  `Wildcard`, `Signature` or `Project` for kind-only routes), so existing
  clients keep reading it.

## Existing data

Nothing is deleted or rewritten. The migration:

1. Creates the new tables and nullable columns.
2. Seeds brands, scales, grades and nine gym locations.
3. If a gym with the same name already exists (ignoring case), it is linked to
   the brand and its empty fields are filled. Its name, location and routes are
   never changed.

Routes created before this change keep their free-text grade. To link them to
locked grades, run the helper, which only matches exact labels and never guesses:

```
python -m app.seed.map_route_grades           # dry run, prints what it would do
python -m app.seed.map_route_grades --apply   # writes the matches
```

Routes it cannot match are listed, to be fixed by hand.

## Deploying this

Merging only changes the code. The database changes when `alembic upgrade head`
runs against it.

1. In the Neon console, create a **branch** of the production database (an
   instant copy). This is the backup.
2. Optional dry run: run `alembic upgrade head` with `DATABASE_URL` set to that
   branch.
3. Run `alembic upgrade head` with `DATABASE_URL` set to production. Alembic now
   reads the URL from the environment, not `alembic.ini`.
4. Deploy the new code. The migration is additive, so the previous code keeps
   working against the migrated database.
5. Optional: run `python -m app.seed.map_route_grades` (dry run first).

Rollback: `alembic downgrade -1` removes the new tables and columns. Gym rows
created by the seed are kept, because sessions may reference them.

## Testing

- `pytest` covers the seed, brand and grade endpoints, route validation and
  updates, and the mapping helper.
- The migration was run on PostgreSQL 16 over a database holding legacy gyms and
  routes: upgrade, downgrade and upgrade again, and a second seed run added
  nothing.
