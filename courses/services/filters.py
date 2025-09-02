def filters_for_course(user):
    return {"teachers": user}, {"students": user}

def filters_for_lecture(user):
    return {"course__teachers": user}, {"course__students": user}

def filters_for_homework(user):
    return {"lecture__course__teachers": user}, {"lecture__course__students": user}

def filters_for_submission(user):
    return {"homework__lecture__course__teachers": user}, {"student": user}

def filters_for_grade(user):
    return {"submission__homework__lecture__course__teachers": user}, {"submission__student": user}

def filters_for_comment(user):
    return {
        "grade__submission__homework__lecture__course__teachers": user
    }, {
        "grade__submission__student": user
    }