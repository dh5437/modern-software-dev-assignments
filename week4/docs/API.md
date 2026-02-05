# API

Base URL: `/`

## Notes

- `GET /notes/`
  - Response: `200` list of notes
- `POST /notes/`
  - Body: `{ "title": string, "content": string }`
  - Response: `201` note
  - Errors: `400` if title/content empty
- `GET /notes/search/?q=...`
  - Query: `q` optional, case-insensitive search across title/content
  - Response: `200` list of notes
- `GET /notes/{note_id}`
  - Response: `200` note
  - Errors: `404` if not found
- `PUT /notes/{note_id}`
  - Body: `{ "title"?: string, "content"?: string }`
  - Response: `200` note
  - Errors: `400` if no fields or empty strings, `404` if not found
- `DELETE /notes/{note_id}`
  - Response: `204`
  - Errors: `404` if not found
- `POST /notes/{note_id}/extract`
  - Response: `200` list of action items created from note content
  - Errors: `404` if not found

## Action Items

- `GET /action-items/`
  - Response: `200` list of action items
- `POST /action-items/`
  - Body: `{ "description": string }`
  - Response: `201` action item
  - Errors: `400` if description empty
- `PUT /action-items/{item_id}/complete`
  - Response: `200` action item
  - Errors: `404` if not found
