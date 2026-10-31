# Admin roles and protected writes

## Breaking change

Until now anyone could create, edit and delete gyms and routes without logging
in. After this change those writes need a login and the right role. Reads are
unchanged and stay public.

Any client that writes gyms or routes must send `Authorization: Bearer <token>`.
Without one the API returns 401. With a token but without the right role it
returns 403.

## Roles

| Role | Can do |
|---|---|
| `user` (default) | Log sessions and attempts. Read everything. Cannot write gyms or routes. |
| `gym_admin` | Create, edit, retire and delete routes at the gyms linked to them. Edit those gyms' details (address, city, state, coordinates, phone, opening hours, location text). |
| `super_admin` | Everything: all gyms and routes, create and delete gyms, change a gym's name, brand or active flag, and grant roles. |

Rules:

- Nobody can change their own role. Registering always creates a plain `user`.
- A gym admin only has rights over the specific gyms (locations) linked to them.
  A role with no links manages nothing.
- A gym admin cannot change a gym's `name`, `brand_id` or `is_active`, and cannot
  move a route into a gym they do not manage.
- The last super admin cannot be demoted, so the system cannot lock itself out.
- Changing someone's role away from `gym_admin` removes their gym links.

## Endpoints

| Endpoint | Who |
|---|---|
| `POST /gyms/`, `DELETE /gyms/{id}` | super admin |
| `PUT /gyms/{id}` | super admin, or admin of that gym (limited fields) |
| `POST /routes/` | admin of the route's gym |
| `PUT /routes/{id}`, `DELETE /routes/{id}`, `PATCH /routes/{id}/retire` | admin of the route's gym (and of the target gym when moving) |
| `GET /auth/me` | any signed-in user. Now also returns `role` and `admin_gym_ids`. |
| `GET /admin/users?q=` | super admin. Search by part of an email or username. |
| `PUT /admin/users/{id}/role` | super admin. Body: `{"role": "user" \| "gym_admin" \| "super_admin"}` |
| `PUT /admin/users/{id}/gyms/{gym_id}` | super admin. The user must already be a `gym_admin`. |
| `DELETE /admin/users/{id}/gyms/{gym_id}` | super admin |

## Creating the first super admin

Nobody can promote themselves, so the first super admin is created from the
command line, with `DATABASE_URL` pointing at the target database:

```
python -m app.scripts.bootstrap_super_admin --user-id 1
```

It prints the user's id, username and email, and asks for confirmation before
changing anything. User IDs differ between databases, so check that the printed
account is the right person before answering `y`. It does nothing if that user
is already a super admin.

After that, the super admin grants roles through the `/admin` endpoints.

## Deploying this

This PR builds on the grade scales PR. Merge that one first.

1. Take a Neon branch of the production database as a backup.
2. Run `alembic upgrade head`. This adds `users.role` (every existing user
   becomes `user`) and the `user_gym_admins` table. Nobody is promoted.
3. Deploy the code.
4. Run the bootstrap script for the first super admin.
5. Make sure the clients that write gyms or routes send the token (the mobile app
   needs a small change for this) before or at the same time as step 3.

Rollback: `alembic downgrade -1` drops the role column and the links table.

## Testing

`tests/test_permissions.py` uses real bearer tokens and covers anonymous, plain
user, gym admin of one gym, and super admin against every protected endpoint,
plus role granting, the last-super-admin guard, self-promotion attempts and the
bootstrap helper. The migration was run on PostgreSQL 16 over existing users,
including a downgrade and a second upgrade, and the bootstrap script was run
end to end.
