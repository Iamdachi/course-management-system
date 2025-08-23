It is assumed that Django/DRF frameworks will be used. All application logic must be implemented and accessible via an API (NOT via the Django admin module). You may optionally add an admin panel if you wish.

All users in the system have the following capabilities:

    Registration (during registration, the user chooses their role — Teacher or Student)
    Authentication


Teachers have the following capabilities:

    CRUD operations for their own courses
    Add/Remove a student to/from their course
    Add a new teacher to their course
    CRUD operations for lectures in their courses (A lecture consists of a topic and a presentation file)
    Add homework assignments (text information) to each lecture
    View completed homework submissions
    Assign or change grades for each student who has submitted homework
    Add comments to each grade


Students have the following capabilities:

    View available courses
    View available lectures within a selected available course
    View homework for an available lecture
    Submit homework for review
    View their own homework submissions
    View grades for their homework
    View/Add comments to a grade


Additional requirements:

    Data security (permissions for all CRUD actions)
    API documentation (OpenAPI)
