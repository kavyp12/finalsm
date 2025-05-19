from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER = (
        (1, 'HOD'),
        (2, 'STAFF'),
        (3, 'STUDENT'),
        (4, 'PARENT'),
    )
    user_type = models.CharField(choices=USER, max_length=50, default=1)
    profile_pic = models.ImageField(upload_to='media/profile_pic')

    def __str__(self):
        return self.first_name if self.first_name else self.username

class Course(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Session_Year(models.Model):
    session_start = models.CharField(max_length=100)
    session_end = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.session_start} To {self.session_end}"

class Student(models.Model):
    SEMESTER_CHOICES = (
        (1, '1st Semester'),
        (2, '2nd Semester'),
        (3, '3rd Semester'),
        (4, '4th Semester'),
        (5, '5th Semester'),
        (6, '6th Semester'),
        (7, '7th Semester'),
        (8, '8th Semester'),
    )
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    gender = models.CharField(max_length=100)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    session_year_id = models.ForeignKey(Session_Year, on_delete=models.CASCADE)
    enrollment_no = models.CharField(max_length=50, unique=True, null=True)
    semester = models.IntegerField(choices=SEMESTER_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.admin.first_name

class Parent(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parents')
    relationship = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.admin.first_name} ({self.relationship} of {self.student.admin.first_name})"

class Staff(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    gender = models.CharField(max_length=100)
    subjects = models.ManyToManyField('Subject', blank=True, related_name='staff_members')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.admin.username

class Subject(models.Model):
    CREDIT_CHOICES = (
        (1, '1 Credit'),
        (2, '2 Credits'),
        (3, '3 Credits'),
        (4, '4 Credits'),
    )
    name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    credit = models.IntegerField(choices=CREDIT_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject_code} - {self.name}" if self.subject_code else self.name

class StudyMaterial(models.Model):
    MATERIAL_TYPES = (
        ('syllabus', 'Syllabus'),
        ('notes', 'Notes'),
        ('assignment', 'Assignment'),
        ('other', 'Other'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='study_materials/')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='notes')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

    class Meta:
        ordering = ['-uploaded_at']

class Note(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Staff_Notification(models.Model):
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(null=True, default=0)

    def __str__(self):
        return f"{self.staff_id.admin.first_name} - Notification"

class Student_Notification(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(null=True, default=0)

    def __str__(self):
        return f"{self.student_id.admin.first_name} - Notification"

class GeneralNotification(models.Model):
    TARGET_TYPES = (
        ('ALL', 'All Users'),
        ('STAFF', 'All Staff'),
        ('STUDENT', 'All Students'),
        ('BOTH', 'Staff and Students'),
    )
    target_type = models.CharField(max_length=10, choices=TARGET_TYPES, default='ALL')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='sent_notifications')

    def __str__(self):
        return f"{self.target_type} Notification - {self.created_at}"

class Staff_leave(models.Model):
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField(null=True)
    message = models.TextField(null=True, blank=True)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff_id.admin.first_name} - Leave"

class Student_leave(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(null=True)
    message = models.TextField(null=True, blank=True)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_id.admin.first_name} - Leave"

class Staff_Feedback(models.Model):
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.staff_id.admin.first_name} - Feedback"

class Student_Feedback(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.student_id.admin.first_name} - Feedback"

class Attendance(models.Model):
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    attendance_data = models.DateField()
    session_year_id = models.ForeignKey(Session_Year, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attendance for {self.subject_id.name} on {self.attendance_data}"

class Attendance_Report(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_id.admin.first_name} - {self.attendance_id}"

class StudentResult(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    assignment_mark = models.IntegerField(null=True, blank=True)
    exam_mark = models.IntegerField(null=True, blank=True)
    ia1_mark = models.FloatField(null=True, blank=True)
    ia2_mark = models.FloatField(null=True, blank=True)
    attendance_mark = models.FloatField(null=True, blank=True)
    midsem_mark = models.FloatField(null=True, blank=True)
    end_sem_mark = models.FloatField(null=True, blank=True)
    total_mark = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_marks(self):
        marks = [
            self.ia1_mark or 0,
            self.ia2_mark or 0,
            self.attendance_mark or 0,
            self.midsem_mark or 0,
            self.end_sem_mark or 0
        ]
        total = sum(marks)
        self.total_mark = total
        return total

    def calculate_cgpa(self):
        total_marks = self.calculate_total_marks()
        max_marks = 100
        if total_marks > 0:
            percentage = (total_marks / max_marks) * 100
            cgpa = percentage / 9.5
            return round(cgpa, 2) if cgpa <= 10 else 10.0
        return None

    def save(self, *args, **kwargs):
        self.calculate_total_marks()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id.admin.first_name} - {self.subject_id.name}"