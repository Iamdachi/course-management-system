# Course Management API
It is assumed that Django/DRF frameworks will be used. All application logic must be implemented and accessible via an API (NOT via the Django admin module). You may optionally add an admin panel if you wish.


## Features

### Common
- Register as **Teacher** or **Student**
- JWT Authentication

### Teachers
- Manage their own courses (CRUD)
- Add/remove students
- Add other teachers
- Manage lectures (topic + presentation file)
- Add homework assignments to lectures
- View submissions
- Assign/change grades
- Comment on grades

### Students
- View available courses and lectures
- View homework per lecture
- Submit homework
- View own submissions
- View grades
- Add comments to grades

### Other
- Permissions enforced for all actions
- Auto-generated API docs (OpenAPI/Swagger)

## Installation
```bash
git clone https://github.com/yourname/course-api.git
cd leverx-courses
uv sync
```

## Environment
Create a .env file (see .env.example):
```ini
SECRET_KEY=your-secret
DEBUG=True
```

## Running
```bash
uv run python manage.py runserver
```

## Testing
```bash
cd courses/tests/
uv run pytest
```

