````markdown
# Event Planner REST API

A Django REST Framework–based backend for creating and managing events, RSVPs, and reviews with fine-grained permission control for public and private events.

---

##  Features

- **User registration**
  - Register new users via a simple `/auth/register/` endpoint.
- **User profiles**
  - `UserProfile` linked 1-to-1 with `User` (full name, bio, location, profile picture).
- **Events**
  - Create, update, delete events (title, description, location, start/end time).
  - Public/Private flag (`is_public`).
  - Metadata: `created_at`, `updated_at`.
  - Search, filter, and ordering support.
- **RSVPs**
  - Users can RSVP to events: `attending`, `maybe`, `not_going`.
  - Each user can RSVP only once per event.
- **Reviews**
  - Users can leave 1–5 star ratings + comments.
  - Each user can review an event only once.
  - Event serializer computes `average_rating`.
- **Permissions & Security**
  - Only event owners can edit/delete their events.
  - Private events are only visible to invited/RSVP’d users.
  - Only authenticated users can create events, RSVP, or review.

---

##  Tech Stack

- **Backend:** Django, Django REST Framework
- **Auth:** Django auth system (usable with Session/Token/JWT auth)
- **Filtering & Search:** `django-filter`, DRF `SearchFilter`, `OrderingFilter`
- **Media Handling:** `ImageField` for profile pictures (requires `Pillow`)

---

##  Project Structure (simplified)

```bash
project_root/
├── manage.py
├── config/                 # Django project settings (example name)
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── events/                 # App containing event logic
    ├── models.py           # UserProfile, Event, RSVP, Review
    ├── serializers.py      # EventSerializer, RSVPSerializer, ReviewSerializer, etc.
    ├── permissions.py      # IsOrganizerOrReadOnly, IsInvitedOrPublic
    ├── views.py            # EventViewSet, RSVPViewSet, ReviewViewSet
    ├── auth_views.py       # RegisterView (optional filename)
    ├── tests/              # API tests
    └── ...
```
````


---

##  Installation & Setup

### 1. Clone & enter the project

```bash
git clone https://github.com/aishna05/EventManagement.git
cd <your-project-folder>
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

_(Example – update based on your `requirements.txt`)_:

```bash
pip install django djangorestframework django-filter pillow
```

Or:

```bash
pip install -r requirements.txt
```

## API Endpoints
### 1. Auth

#### POST `/api/auth/register/`

Register a new user.

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "strongpassword123"
}
```

Response:

```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com"
}
```

---

### 2. Events

#### GET `/api/events/`

List **public** events.

#### POST `/api/events/` (authenticated)

Create a new event (owner is set automatically).

```json
{
  "title": "Hackathon 2025",
  "description": "24-hour coding event",
  "location": "Online",
  "start_time": "2025-12-10T10:00:00Z",
  "end_time": "2025-12-11T10:00:00Z",
  "is_public": true
}
```

#### GET `/api/events/{id}/`

Retrieve a single event.

- Public event → accessible to anyone.
- Private event (`is_public=false`) → only if user has RSVP.

#### PUT/PATCH `/api/events/{id}/` (authenticated organizer only)

Update event details.

#### DELETE `/api/events/{id}/` (authenticated organizer only)

Delete an event.

---

### 3. RSVP

#### POST `/api/events/{id}/rsvp/` (authenticated)

Create or update RSVP for an event.

```json
{
  "status": "attending" // one of: attending, maybe, not_going
}
```

Response includes user & event info.

#### PATCH `/api/rsvps/{id}/` (authenticated)

Update an existing RSVP for the current user.
`RSVPViewSet` only allows `PATCH` and filters RSVPs by `request.user`.

---

### 4. Reviews

#### GET `/api/events/{id}/reviews/`

List reviews for a specific event. Supports pagination if configured.

#### POST `/api/reviews/` (authenticated)

Create a review **only if user has RSVPed** to the event.

Request body:

```json
{
  "event_id": 3,
  "rating": 5,
  "comment": "Amazing event!"
}
```

If the user has not RSVPed to the event:

```json
{
  "detail": "You must RSVP to this event before leaving a review."
}
```
### 5. home page `/api/home/`
---

##  Extra: Computed Fields on Events

`EventSerializer` exposes:

- `rsvp_count` → number of RSVPs for the event.
- `average_rating` → average of all review ratings (1–5), rounded to 2 decimals.
  If there are no reviews, `average_rating` is `null`.

---

##  Running Tests

If test modules are configured (e.g. `events/tests/`):

```bash
python manage.py test
```

You can also run a specific test module:

```bash
python manage.py test events.test_api_permissions
```

---

##  Notes / TODOs

- Add authentication mechanism (Token/JWT) to protect API in production.
- Wire up `UserProfile` creation via signals or registration flow.
- Add pagination settings in `REST_FRAMEWORK` for listing endpoints.
- Extend tests to cover all permissions, especially private event access.

---


