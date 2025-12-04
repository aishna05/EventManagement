# PR: PYTHONIIP01010.md

# **Event Management System - Assignment**

## **Overview**

This assignment focuses on building an **Event Management API** using Django and Django REST Framework (DRF). The API will allow users to create events, RSVP, and leave reviews. This assignment tests your understanding of key DRF and Django concepts like serializers, viewsets, permissions, and authentication.

### **Objective**

Demonstrate your ability to build RESTful APIs using Django REST Framework, manage relationships between models, and implement authentication, permissions, and validations.

---

## **Assignment Requirements**

### 1. **Models**:

- **UserProfile**: Extends Django’s built-in `User` model with fields such as `full_name`, `bio`, `location`, and `profile_picture`.
- **Event**: Contains `title`, `description`, `organizer`, `location`, `start_time`, `end_time`, `is_public` (Boolean), `created_at`, and `updated_at`.
- **RSVP**: Handles user RSVPs for events with fields like `event`, `user`, and `status` ('Going', 'Maybe', 'Not Going').
- **Review**: Allows users to leave a review for an event with fields like `event`, `user`, `rating`, and `comment`.

### 2. **API Endpoints**:

- **Event API**:
  - `POST /events/`: Create a new event (authenticated users only).
  - `GET /events/`: List all public events (with pagination).
  - `GET /events/{id}/`: Get details of a specific event.
  - `PUT /events/{id}/`: Update an event (only the organizer can edit).
  - `DELETE /events/{id}/`: Delete an event (only the organizer).

- **RSVP API**:
  - `POST /events/{event_id}/rsvp/`: RSVP to an event.
  - `PATCH /events/{event_id}/rsvp/{user_id}/`: Update RSVP status.

- **Review API**:
  - `POST /events/{event_id}/reviews/`: Add a review for an event.
  - `GET /events/{event_id}/reviews/`: List all reviews for an event.

### 3. **Core Features**:

- **Custom Permissions**:
  - Only the organizer of an event can edit or delete it.
  - Implement a permission to restrict access to private events to invited users only.

- **Pagination, Filtering & Search(optional) try if you can**:
  - Paginate the event and review listings.
  - Implement search and filter functionality for events (by `title`, `location`, or `organizer`).

### 4. **Authentication & Security**:

- Use **JWT Authentication** for securing all API endpoints.
- Ensure private events are only visible to invited users (use permissions).

---

## **Submission Guidelines**

1. Fork the provided repository and complete the assignment.
2. Commit your changes regularly with clear commit messages.
3. Add a `README.md` file with setup instructions.
4. Submit the GitHub repository link once you’ve completed the project.

---

## **Evaluation Criteria**

### **1. Django REST Framework Proficiency**:
   - Effective use of serializers, viewsets, and routing.
   - Managing relationships between models (Events, RSVPs, Reviews).

### **2. Core Python Concepts**:
   - Object-oriented programming: proper use of classes and methods.
   - Handling exceptions and edge cases.

### **3. Code Quality**:
   - Clean, maintainable code.
   - Proper use of Django and DRF conventions.

### **4. Authentication & Permissions**:
   - Correct implementation of JWT authentication.
   - Appropriate permissions for actions like editing/deleting events.

### **5. Bonus point**:
   - if you can write unit test for testing
   - if you can implement asynchronous task using celery for email updates of event

---

## **Good Luck!**

This assignment is designed to test your understanding of Django REST Framework and core Python concepts. Be sure to implement all required features and submit a working API.

---