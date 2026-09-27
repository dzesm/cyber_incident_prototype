from src.phishing_model import PhishingModel


model = PhishingModel()


legitimate_email = """
From: lecturer@university.edu
Subject: Lecture timetable

Hello,

Tomorrow's lecture will begin at 10:00 in Room 204.

The slides will be uploaded to the course page after
the lecture.

Kind regards,
Course Lecturer
"""


print(model.analyse(legitimate_email))