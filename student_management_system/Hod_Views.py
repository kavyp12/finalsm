from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from app.models import (
    Course, Session_Year, CustomUser, Student, Staff, Subject,
    Staff_Notification, Staff_leave, Staff_Feedback,
    Student_Notification, Student_Feedback, Student_leave,
    Attendance, Attendance_Report, Parent, GeneralNotification
)
from django.contrib import messages
from django.http import JsonResponse
import csv
from io import TextIOWrapper
from datetime import datetime

@login_required(login_url='/')
def HOME(request):
    student_count = Student.objects.all().count()
    staff_count = Staff.objects.all().count()
    course_count = Course.objects.all().count()
    subject_count = Subject.objects.all().count()
    parent_count = Parent.objects.all().count()
    student_gender_male = Student.objects.filter(gender='Male').count()
    student_gender_female = Student.objects.filter(gender='Female').count()
    pending_staff_leaves = Staff_leave.objects.filter(status=0).count()
    pending_student_leaves = Student_leave.objects.filter(status=0).count()
    context = {
        'student_count': student_count,
        'staff_count': staff_count,
        'course_count': course_count,
        'subject_count': subject_count,
        'parent_count': parent_count,
        'student_gender_male': student_gender_male,
        'student_gender_female': student_gender_female,
        'pending_staff_leaves': pending_staff_leaves,
        'pending_student_leaves': pending_student_leaves,
    }
    return render(request, 'Hod/home.html', context)

@login_required(login_url='/')
def ADD_STUDENT(request):
    course = Course.objects.all()
    session_year = Session_Year.objects.all()
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        full_name = request.POST.get('full_name')
        enrollment_no = request.POST.get('enrollment_no')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        course_id = request.POST.get('course_id')
        session_year_id = request.POST.get('session_year_id')
        semester = request.POST.get('semester')
        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email Is Already Taken')
            return redirect('add_student')
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username Is Already Taken')
            return redirect('add_student')
        if enrollment_no and Student.objects.filter(enrollment_no=enrollment_no).exists():
            messages.warning(request, 'Enrollment Number Is Already Taken')
            return redirect('add_student')
        user = CustomUser(
            first_name=full_name,
            last_name='',
            username=username,
            email=email,
            profile_pic=profile_pic,
            user_type=3
        )
        user.set_password(password)
        user.save()
        course_obj = Course.objects.get(id=course_id)
        session_year_obj = Session_Year.objects.get(id=session_year_id)
        student = Student(
            admin=user,
            address=address,
            session_year_id=session_year_obj,
            course_id=course_obj,
            gender=gender,
            enrollment_no=enrollment_no if enrollment_no else None,
            semester=semester if semester else None
        )
        student.save()
        messages.success(request, f"{user.first_name} Successfully Added!")
        return redirect('add_student')
    context = {
        'course': course,
        'session_year': session_year,
    }
    return render(request, 'Hod/add_student.html', context)

@login_required(login_url='/')
def VIEW_STUDENT(request):
    student = Student.objects.all()
    context = {
        'student': student,
    }
    return render(request, 'Hod/view_student.html', context)

@login_required(login_url='/')
def EDIT_STUDENT(request, id):
    try:
        student_user = CustomUser.objects.get(id=id, user_type=3)
        student_profile = Student.objects.get(admin=student_user)
    except (CustomUser.DoesNotExist, Student.DoesNotExist):
        messages.error(request, "Student not found.")
        return redirect('view_student')
    course = Course.objects.all()
    session_year = Session_Year.objects.all()
    context = {
        'student': student_profile,
        'course': course,
        'session_year': session_year,
    }
    return render(request, 'Hod/edit_student.html', context)

@login_required(login_url='/')
def UPDATE_STUDENT(request):
    if request.method == "POST":
        student_admin_id = request.POST.get('student_id')
        profile_pic = request.FILES.get('profile_pic')
        full_name = request.POST.get('full_name')
        enrollment_no = request.POST.get('enrollment_no')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address Pfeiffer')
        gender = request.POST.get('gender')
        course_id = request.POST.get('course_id')
        session_year_id = request.POST.get('session_year_id')
        semester = request.POST.get('semester')
        try:
            user = CustomUser.objects.get(id=student_admin_id)
            user.first_name = full_name
            user.email = email
            user.username = username
            if password and password.strip():
                user.set_password(password)
            if profile_pic:
                user.profile_pic = profile_pic
            user.save()
            student = Student.objects.get(admin=user)
            if enrollment_no and enrollment_no != student.enrollment_no and Student.objects.filter(enrollment_no=enrollment_no).exists():
                messages.warning(request, 'Enrollment Number Is Already Taken')
                return redirect('edit_student', id=user.id)
            student.address = address
            student.gender = gender
            student.enrollment_no = enrollment_no if enrollment_no else student.enrollment_no
            course_obj = Course.objects.get(id=course_id)
            student.course_id = course_obj
            session_year_obj = Session_Year.objects.get(id=session_year_id)
            student.session_year_id = session_year_obj
            student.semester = int(semester) if semester else student.semester
            student.save()
            messages.success(request, 'Record Successfully Updated!')
            return redirect('view_student')
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found for update.")
            return redirect('view_student')
        except Student.DoesNotExist:
            messages.error(request, "Student profile not found for update.")
            return redirect('view_student')
        except Course.DoesNotExist:
            messages.error(request, "Selected course does not exist.")
            return redirect('edit_student', id=student_admin_id)
        except Session_Year.DoesNotExist:
            messages.error(request, "Selected session year does not exist.")
            return redirect('edit_student', id=student_admin_id)
    return redirect('view_student')

@login_required(login_url='/')
def DELETE_STUDENT(request, admin):
    try:
        student_user = CustomUser.objects.get(id=admin, user_type=3)
        student_user.delete()
        messages.success(request, 'Record Successfully Deleted!')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Student not found for deletion.')
    return redirect('view_student')

@login_required(login_url='/')
def ADD_COURSE(request):
    if request.method == "POST":
        course_name = request.POST.get('course_name')
        if course_name:
            course = Course(name=course_name)
            course.save()
            messages.success(request, 'Course Successfully Created')
            return redirect('view_course')
        else:
            messages.error(request, 'Course name cannot be empty.')
    return render(request, 'Hod/add_course.html')

@login_required(login_url='/')
def VIEW_COURSE(request):
    course = Course.objects.all()
    context = {
        'course': course,
    }
    return render(request, 'Hod/view_course.html', context)

@login_required(login_url='/')
def EDIT_COURSE(request, id):
    try:
        course = Course.objects.get(id=id)
        context = {
            'course': course,
        }
        return render(request, 'Hod/edit_course.html', context)
    except Course.DoesNotExist:
        messages.error(request, "Course not found.")
        return redirect('view_course')

@login_required(login_url='/')
def UPDATE_COURSE(request):
    if request.method == "POST":
        name = request.POST.get('name')
        course_id = request.POST.get('course_id')
        if name and course_id:
            try:
                course = Course.objects.get(id=course_id)
                course.name = name
                course.save()
                messages.success(request, 'Course Successfully Updated')
            except Course.DoesNotExist:
                messages.error(request, "Course not found for update.")
        else:
            messages.error(request, "Course name or ID missing.")
        return redirect('view_course')
    return redirect('view_course')

@login_required(login_url='/')
def DELETE_COURSE(request, id):
    try:
        course = Course.objects.get(id=id)
        course.delete()
        messages.success(request, 'Course Successfully Deleted')
    except Course.DoesNotExist:
        messages.error(request, 'Course not found for deletion.')
    return redirect('view_course')

@login_required(login_url='/')
def ADD_STAFF(request):
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email Is Already Taken!')
            return redirect('add_staff')
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username Is Already Taken!')
            return redirect('add_staff')
        user = CustomUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            profile_pic=profile_pic,
            user_type=2
        )
        user.set_password(password)
        user.save()
        staff = Staff(
            admin=user,
            address=address,
            gender=gender
        )
        staff.save()
        messages.success(request, 'Staff Successfully Added!')
        return redirect('add_staff')
    return render(request, 'Hod/add_staff.html')

@login_required(login_url='/')
def VIEW_STAFF(request):
    staff = Staff.objects.all()
    context = {
        'staff': staff,
    }
    return render(request, 'Hod/view_staff.html', context)

@login_required(login_url='/')
def EDIT_STAFF(request, id):
    try:
        staff_user = CustomUser.objects.get(id=id, user_type=2)
        staff_profile = Staff.objects.get(admin=staff_user)
    except (CustomUser.DoesNotExist, Staff.DoesNotExist):
        messages.error(request, "Staff not found.")
        return redirect('view_staff')
    subjects = Subject.objects.all()
    context = {
        'staff': staff_profile,
        'subjects': subjects,
    }
    return render(request, 'Hod/edit_staff.html', context)

@login_required(login_url='/')
def UPDATE_STAFF(request):
    if request.method == "POST":
        staff_admin_id = request.POST.get('staff_id')
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        subject_ids = request.POST.getlist('subject_id')
        try:
            user = CustomUser.objects.get(id=staff_admin_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            if password and password.strip():
                user.set_password(password)
            if profile_pic:
                user.profile_pic = profile_pic
            user.save()
            staff = Staff.objects.get(admin=user)
            staff.gender = gender
            staff.address = address
            staff.subjects.clear()
            if subject_ids:
                for sub_id in subject_ids:
                    try:
                        subject = Subject.objects.get(id=sub_id)
                        staff.subjects.add(subject)
                    except Subject.DoesNotExist:
                        messages.error(request, f"Subject with ID {sub_id} does not exist.")
            staff.save()
            messages.success(request, 'Staff Successfully Updated')
            return redirect('view_staff')
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found for update.")
        except Staff.DoesNotExist:
            messages.error(request, "Staff profile not found for update.")
        return redirect('edit_staff', id=staff_admin_id)
    return redirect('view_staff')

@login_required(login_url='/')
def DELETE_STAFF(request, admin):
    try:
        staff_user = CustomUser.objects.get(id=admin, user_type=2)
        staff_user.delete()
        messages.success(request, 'Record Successfully Deleted!')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Staff not found for deletion.')
    return redirect('view_staff')

@login_required(login_url='/')
def ADD_PARENT(request):
    students = Student.objects.all()
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        student_id = request.POST.get('student_id')
        relationship = request.POST.get('relationship')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email Is Already Taken!')
            return redirect('add_parent')
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username Is Already Taken!')
            return redirect('add_parent')
        try:
            student_obj = Student.objects.get(id=student_id)
            user = CustomUser(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                profile_pic=profile_pic,
                user_type=4
            )
            user.set_password(password)
            user.save()
            parent = Parent(
                admin=user,
                student=student_obj,
                relationship=relationship,
                phone_number=phone_number,
                address=address
            )
            parent.save()
            messages.success(request, 'Parent Added Successfully!')
            return redirect('add_parent')
        except Student.DoesNotExist:
            messages.error(request, "Selected student does not exist.")
            return redirect('add_parent')
    context = {
        'students': students,
    }
    return render(request, 'Hod/add_parent.html', context)

@login_required(login_url='/')
def VIEW_PARENT(request):
    parents = Parent.objects.all()
    context = {
        'parents': parents,
    }
    return render(request, 'Hod/view_parent.html', context)

@login_required(login_url='/')
def EDIT_PARENT(request, id):
    try:
        parent_user = CustomUser.objects.get(id=id, user_type=4)
        parent_profile = Parent.objects.get(admin=parent_user)
    except (CustomUser.DoesNotExist, Parent.DoesNotExist):
        messages.error(request, "Parent not found.")
        return redirect('view_parent')
    students = Student.objects.all()
    context = {
        'parent': parent_profile,
        'students': students,
    }
    return render(request, 'Hod/edit_parent.html', context)

@login_required(login_url='/')
def UPDATE_PARENT(request):
    if request.method == "POST":
        parent_admin_id = request.POST.get('parent_id')
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        student_id_fk = request.POST.get('student_id')
        relationship = request.POST.get('relationship')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        try:
            user = CustomUser.objects.get(id=parent_admin_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            if password and password.strip():
                user.set_password(password)
            if profile_pic:
                user.profile_pic = profile_pic
            user.save()
            parent = Parent.objects.get(admin=user)
            student_obj = Student.objects.get(id=student_id_fk)
            parent.student = student_obj
            parent.relationship = relationship
            parent.phone_number = phone_number
            parent.address = address
            parent.save()
            messages.success(request, 'Parent Updated Successfully!')
            return redirect('view_parent')
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found for update.")
        except Parent.DoesNotExist:
            messages.error(request, "Parent profile not found for update.")
        except Student.DoesNotExist:
            messages.error(request, "Selected student does not exist.")
        return redirect('edit_parent', id=parent_admin_id)
    return redirect('view_parent')

@login_required(login_url='/')
def DELETE_PARENT(request, admin):
    try:
        parent_user = CustomUser.objects.get(id=admin, user_type=4)
        parent_user.delete()
        messages.success(request, 'Parent Deleted Successfully!')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Parent not found for deletion.')
    return redirect('view_parent')

@login_required(login_url='/')
def ADD_SUBJECT(request):
    courses = Course.objects.all()
    if request.method == "POST":
        subject_name = request.POST.get('subject_name')
        subject_code = request.POST.get('subject_code')
        course_id = request.POST.get('course_id')
        credit = request.POST.get('credit')
        try:
            course = Course.objects.get(id=course_id)
            if subject_code and Subject.objects.filter(subject_code=subject_code).exists():
                messages.error(request, 'Subject Code is already taken.')
                return redirect('add_subject')
            subject = Subject(
                name=subject_name,
                subject_code=subject_code if subject_code else None,
                course=course,
                credit=int(credit) if credit else None
            )
            subject.save()
            messages.success(request, 'Subject Successfully Added!')
            return redirect('add_subject')
        except Course.DoesNotExist:
            messages.error(request, "Selected course does not exist.")
            return redirect('add_subject')
    context = {
        'courses': courses,
    }
    return render(request, 'Hod/add_subject.html', context)

@login_required(login_url='/')
def VIEW_SUBJECT(request):
    subject = Subject.objects.all()
    context = {
        'subject': subject,
    }
    return render(request, 'Hod/view_subject.html', context)

@login_required(login_url='/')
def EDIT_SUBJECT(request, id):
    try:
        subject = Subject.objects.get(id=id)
        course = Course.objects.all()
        context = {
            'subject': subject,
            'course': course,
        }
        return render(request, 'Hod/edit_subject.html', context)
    except Subject.DoesNotExist:
        messages.error(request, "Subject not found.")
        return redirect('view_subject')

@login_required(login_url='/')
def UPDATE_SUBJECT(request):
    if request.method == "POST":
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject_name')
        subject_code = request.POST.get('subject_code')
        course_id = request.POST.get('course_id')
        credit = request.POST.get('credit')
        try:
            course = Course.objects.get(id=course_id)
            subject = Subject.objects.get(id=subject_id)
            if subject_code and subject_code != subject.subject_code and Subject.objects.filter(subject_code=subject_code).exists():
                messages.error(request, 'Subject Code is already taken.')
                return redirect('edit_subject', id=subject_id)
            subject.name = subject_name
            subject.subject_code = subject_code if subject_code else subject.subject_code
            subject.course = course
            subject.credit = int(credit) if credit else subject.credit
            subject.save()
            messages.success(request, 'Subject Successfully Updated!')
            return redirect('view_subject')
        except Course.DoesNotExist:
            messages.error(request, "Selected course does not exist.")
            return redirect('edit_subject', id=subject_id)
        except Subject.DoesNotExist:
            messages.error(request, "Subject does not exist.")
            return redirect('view_subject')
    return redirect('view_subject')

@login_required(login_url='/')
def DELETE_SUBJECT(request, id):
    try:
        subject = Subject.objects.get(id=id)
        subject.delete()
        messages.success(request, 'Subject Successfully Deleted!')
    except Subject.DoesNotExist:
        messages.error(request, 'Subject not found for deletion.')
    return redirect('view_subject')

@login_required(login_url='/')
def ADD_SESSION(request):
    if request.method == "POST":
        session_year_start = request.POST.get('session_year_start')
        session_year_end = request.POST.get('session_year_end')
        if session_year_start and session_year_end:
            session = Session_Year(
                session_start=session_year_start,
                session_end=session_year_end,
            )
            session.save()
            messages.success(request, 'Session Successfully Created')
            return redirect('add_session')
        else:
            messages.error(request, "Session start and end years are required.")
    return render(request, 'Hod/add_session.html')

@login_required(login_url='/')
def VIEW_SESSION(request):
    session = Session_Year.objects.all()
    context = {
        'session': session,
    }
    return render(request, 'Hod/view_session.html', context)

@login_required(login_url='/')
def EDIT_SESSION(request, id):
    try:
        session = Session_Year.objects.get(id=id)
        context = {
            'session': session,
        }
        return render(request, 'Hod/edit_session.html', context)
    except Session_Year.DoesNotExist:
        messages.error(request, "Session not found.")
        return redirect('view_session')

@login_required(login_url='/')
def UPDATE_SESSION(request):
    if request.method == "POST":
        session_id = request.POST.get('session_id')
        session_year_start = request.POST.get('session_year_start')
        session_year_end = request.POST.get('session_year_end')
        if session_id and session_year_start and session_year_end:
            try:
                session = Session_Year.objects.get(id=session_id)
                session.session_start = session_year_start
                session.session_end = session_year_end
                session.save()
                messages.success(request, 'Session Successfully Updated!')
            except Session_Year.DoesNotExist:
                messages.error(request, "Session not found for update.")
        else:
            messages.error(request, "Missing data for session update.")
        return redirect('view_session')
    return redirect('view_session')

@login_required(login_url='/')
def DELETE_SESSION(request, id):
    try:
        session = Session_Year.objects.get(id=id)
        session.delete()
        messages.success(request, 'Session Successfully Deleted!')
    except Session_Year.DoesNotExist:
        messages.error(request, 'Session not found for deletion.')
    return redirect('view_session')

@login_required(login_url='/')
def STAFF_SEND_NOTIFICATION(request):
    staff = Staff.objects.all()
    see_notification = Staff_Notification.objects.all().order_by('-id')[:5]
    context = {
        'staff': staff,
        'see_notification': see_notification,
    }
    return render(request, 'Hod/staff_notification.html', context)

@login_required(login_url='/')
def SAVE_STAFF_NOTIFICATION(request):
    if request.method == "POST":
        message = request.POST.get('message')
        staff_admin_id = request.POST.get('staff_id')
        if not message:
            messages.error(request, "Notification message cannot be empty.")
            return redirect('staff_send_notification')
        if staff_admin_id == 'all':
            staff_members = Staff.objects.all()
            if not staff_members.exists():
                messages.warning(request, "No staff members to send notifications to.")
                return redirect('staff_send_notification')
            for staff_profile in staff_members:
                notification = Staff_Notification(
                    staff_id=staff_profile,
                    message=message,
                )
                notification.save()
            messages.success(request, 'Notification Successfully Sent to All Staff')
        else:
            try:
                staff_user = CustomUser.objects.get(id=staff_admin_id, user_type=2)
                staff_profile = Staff.objects.get(admin=staff_user)
                notification = Staff_Notification(
                    staff_id=staff_profile,
                    message=message,
                )
                notification.save()
                messages.success(request, f'Notification Successfully Sent to {staff_user.first_name}')
            except (CustomUser.DoesNotExist, Staff.DoesNotExist):
                messages.error(request, 'Selected staff not found.')
        return redirect('staff_send_notification')
    return redirect('staff_send_notification')

@login_required(login_url='/')
def STAFF_LEAVE_VIEW(request):
    staff_leave = Staff_leave.objects.all().order_by('-created_at')
    context = {
        'staff_leave': staff_leave,
    }
    return render(request, 'Hod/staff_leave.html', context)

@login_required(login_url='/')
def STAFF_APPROVE_LEAVE(request, id):
    try:
        leave = Staff_leave.objects.get(id=id)
        leave.status = 1
        leave.save()
        staff_profile = leave.staff_id
        message_to_staff = f"Your leave application for {leave.date.strftime('%Y-%m-%d') if leave.date else 'the specified date'} has been approved."
        Staff_Notification.objects.create(staff_id=staff_profile, message=message_to_staff)
        messages.success(request, 'Leave Approved and Notification Sent!')
    except Staff_leave.DoesNotExist:
        messages.error(request, "Leave application not found.")
    return redirect('staff_leave_view')

@login_required(login_url='/')
def STAFF_DISAPPROVE_LEAVE(request, id):
    try:
        leave = Staff_leave.objects.get(id=id)
        leave.status = 2
        leave.save()
        staff_profile = leave.staff_id
        message_to_staff = f"Your leave application for {leave.date.strftime('%Y-%m-%d') if leave.date else 'the specified date'} has been rejected."
        Staff_Notification.objects.create(staff_id=staff_profile, message=message_to_staff)
        messages.success(request, 'Leave Disapproved and Notification Sent!')
    except Staff_leave.DoesNotExist:
        messages.error(request, "Leave application not found.")
    return redirect('staff_leave_view')

@login_required(login_url='/')
def STUDENT_LEAVE_VIEW(request):
    student_leave = Student_leave.objects.all().order_by('-created_at')
    context = {
        'student_leave': student_leave,
    }
    return render(request, 'Hod/student_leave.html', context)

@login_required(login_url='/')
def STUDENT_APPROVE_LEAVE(request, id):
    try:
        student_leave_obj = Student_leave.objects.get(id=id)
        student_leave_obj.status = 1
        student_leave_obj.save()
        student_profile = student_leave_obj.student_id
        message_to_student = f"Your leave application for {student_leave_obj.date.strftime('%Y-%m-%d') if student_leave_obj.date else 'the specified date'} has been approved."
        Student_Notification.objects.create(student_id=student_profile, message=message_to_student)
        messages.success(request, 'Leave Approved and Notification Sent!')
    except Student_leave.DoesNotExist:
        messages.error(request, "Leave application not found.")
    return redirect('student_leave_view')

@login_required(login_url='/')
def STUDENT_DISAPPROVE_LEAVE(request, id):
    try:
        student_leave_obj = Student_leave.objects.get(id=id)
        student_leave_obj.status = 2
        student_leave_obj.save()
        student_profile = student_leave_obj.student_id
        message_to_student = f"Your leave application for {student_leave_obj.date.strftime('%Y-%m-%d') if student_leave_obj.date else 'the specified date'} has been rejected."
        Student_Notification.objects.create(student_id=student_profile, message=message_to_student)
        messages.success(request, 'Leave Disapproved and Notification Sent!')
    except Student_leave.DoesNotExist:
        messages.error(request, "Leave application not found.")
    return redirect('student_leave_view')

@login_required(login_url='/')
def STAFF_FEEDBACK(request):
    feedback = Staff_Feedback.objects.all().order_by('-created_at')
    context = {
        'feedback': feedback,
    }
    return render(request, 'Hod/staff_feedback.html', context)

@login_required(login_url='/')
def STAFF_FEEDBACK_SAVE(request):
    if request.method == "POST":
        feedback_id = request.POST.get('feedback_id')
        feedback_reply = request.POST.get('feedback_reply')
        if not feedback_id or not feedback_reply:
            messages.error(request, "Feedback ID and reply are required.")
            return redirect('staff_feedback')
        try:
            feedback_obj = Staff_Feedback.objects.get(id=feedback_id)
            feedback_obj.feedback_reply = feedback_reply
            feedback_obj.status = 1
            feedback_obj.save()
            messages.success(request, 'Reply Sent Successfully!')
        except Staff_Feedback.DoesNotExist:
            messages.error(request, 'Feedback not found.')
        return redirect('staff_feedback')
    return redirect('staff_feedback')

@login_required(login_url='/')
def STUDENT_FEEDBACK(request):
    feedback = Student_Feedback.objects.all().order_by('-created_at')
    context = {
        'feedback': feedback,
    }
    return render(request, 'Hod/student_feedback.html', context)

@login_required(login_url='/')
def REPLY_STUDENT_FEEDBACK(request):
    if request.method == "POST":
        feedback_id = request.POST.get('feedback_id')
        feedback_reply = request.POST.get('feedback_reply')
        if not feedback_id or not feedback_reply:
            messages.error(request, "Feedback ID and reply are required.")
            return redirect('student_feedback')
        try:
            feedback_obj = Student_Feedback.objects.get(id=feedback_id)
            feedback_obj.feedback_reply = feedback_reply
            feedback_obj.status = 1
            feedback_obj.save()
            messages.success(request, 'Reply Sent Successfully!')
        except Student_Feedback.DoesNotExist:
            messages.error(request, 'Feedback not found.')
        return redirect('student_feedback')
    return redirect('student_feedback')

@login_required(login_url='/')
def STUDENT_SEND_NOTIFICATION(request):
    students = Student.objects.all()
    recent_notifications = Student_Notification.objects.all().order_by('-id')[:5]
    context = {
        'student': students,
        'notification': recent_notifications,
    }
    return render(request, 'Hod/student_notification.html', context)

@login_required(login_url='/')
def SAVE_STUDENT_NOTIFICATION(request):
    if request.method == "POST":
        message = request.POST.get('message')
        student_admin_id = request.POST.get('student_id')
        if not message:
            messages.error(request, "Notification message cannot be empty.")
            return redirect('student_send_notification')
        if student_admin_id == 'all':
            student_profiles = Student.objects.all()
            if not student_profiles.exists():
                messages.warning(request, "No students to send notifications to.")
                return redirect('student_send_notification')
            for student_profile in student_profiles:
                notification = Student_Notification(
                    student_id=student_profile,
                    message=message,
                )
                notification.save()
            messages.success(request, 'Notification Successfully Sent to All Students')
        else:
            try:
                student_user = CustomUser.objects.get(id=student_admin_id, user_type=3)
                student_profile = Student.objects.get(admin=student_user)
                notification = Student_Notification(
                    student_id=student_profile,
                    message=message,
                )
                notification.save()
                messages.success(request, f'Notification Successfully Sent to {student_user.first_name}')
            except (CustomUser.DoesNotExist, Student.DoesNotExist):
                messages.error(request, 'Selected student not found.')
        return redirect('student_send_notification')
    return redirect('student_send_notification')

@login_required(login_url='/')
def GENERAL_NOTIFICATION(request):
    general_notifications = GeneralNotification.objects.all().order_by('-created_at')[:5]
    context = {
        'general_notifications': general_notifications,
    }
    return render(request, 'Hod/general_notification.html', context)

@login_required(login_url='/')
def SAVE_GENERAL_NOTIFICATION(request):
    if request.method == "POST":
        message = request.POST.get('message')
        target_type = request.POST.get('target_type')
        if not message or not target_type:
            messages.error(request, "Message and target type are required.")
            return redirect('general_notification')
        if target_type not in [choice[0] for choice in GeneralNotification.TARGET_TYPES]:
            messages.error(request, "Invalid target type selected.")
            return redirect('general_notification')
        try:
            general_notification = GeneralNotification(
                target_type=target_type,
                message=message,
                created_by=request.user
            )
            general_notification.save()
            if target_type in ['ALL', 'STAFF', 'BOTH']:
                staff_members = Staff.objects.all()
                for staff_profile in staff_members:
                    Staff_Notification.objects.create(
                        staff_id=staff_profile,
                        message=message
                    )
            if target_type in ['ALL', 'STUDENT', 'BOTH']:
                student_profiles = Student.objects.all()
                for student_profile in student_profiles:
                    Student_Notification.objects.create(
                        student_id=student_profile,
                        message=message
                    )
            messages.success(request, f'Notification Successfully Sent to {target_type}')
            return redirect('general_notification')
        except Exception as e:
            messages.error(request, f"Error sending notification: {str(e)}")
            return redirect('general_notification')
    return redirect('general_notification')

@login_required(login_url='/')
def VIEW_ATTENDANCE(request):
    subjects = Subject.objects.all()
    session_years = Session_Year.objects.all()
    action = request.GET.get('action')
    get_subject = None
    get_session_year = None
    start_date_str = request.POST.get('start_date') if request.method == "POST" else request.GET.get('start_date')
    end_date_str = request.POST.get('end_date') if request.method == "POST" else request.GET.get('end_date')
    attendance_reports = Attendance_Report.objects.select_related(
        'student_id__admin',
        'attendance_id__subject_id',
        'attendance_id__session_year_id'
    ).order_by('-attendance_id__attendance_data', 'student_id__admin__first_name')
    if action == 'filter_attendance':
        subject_id = request.POST.get('subject_id') if request.method == "POST" else request.GET.get('subject_id')
        session_year_id = request.POST.get('session_year_id') if request.method == "POST" else request.GET.get('session_year_id')
        try:
            if subject_id and subject_id.isdigit():
                get_subject = Subject.objects.get(id=int(subject_id))
                attendance_reports = attendance_reports.filter(attendance_id__subject_id=get_subject)
            if session_year_id and session_year_id.isdigit():
                get_session_year = Session_Year.objects.get(id=int(session_year_id))
                attendance_reports = attendance_reports.filter(attendance_id__session_year_id=get_session_year)
            if start_date_str and end_date_str:
                attendance_reports = attendance_reports.filter(
                    attendance_id__attendance_data__range=[start_date_str, end_date_str]
                )
            elif start_date_str:
                attendance_reports = attendance_reports.filter(attendance_id__attendance_data__gte=start_date_str)
            elif end_date_str:
                attendance_reports = attendance_reports.filter(attendance_id__attendance_data__lte=end_date_str)
        except Subject.DoesNotExist:
            messages.error(request, "Selected subject does not exist.")
        except Session_Year.DoesNotExist:
            messages.error(request, "Selected session year does not exist.")
    if action == 'download_csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Student', 'Subject', 'Session Year', 'Date', 'Status'])
        for report in attendance_reports:
            writer.writerow([
                f"{report.student_id.admin.first_name} {report.student_id.admin.last_name}",
                report.attendance_id.subject_id.name,
                f"{report.attendance_id.session_year_id.session_start} - {report.attendance_id.session_year_id.session_end}",
                report.attendance_id.attendance_data.strftime('%Y-%m-%d'),
                'Present' if report.status else 'Absent'
            ])
        return response
    context = {
        'subjects': subjects,
        'session_years': session_years,
        'action': action,
        'get_subject': get_subject,
        'get_session_year': get_session_year,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'attendance_reports': attendance_reports,
    }
    return render(request, 'Hod/view_attendance.html', context)

@login_required(login_url='/')
def get_subjects_by_course(request):
    course_id = request.GET.get('course_id')
    if course_id:
        try:
            course_id_int = int(course_id)
            subjects = Subject.objects.filter(course_id=course_id_int).values('id', 'name')
            return JsonResponse({'subjects': list(subjects)})
        except ValueError:
            return JsonResponse({'subjects': [], 'error': 'Invalid course ID format'}, status=400)
    return JsonResponse({'subjects': []})

@login_required(login_url='/')
def BULK_ADD_STUDENT(request):
    course = Course.objects.all()
    session_year = Session_Year.objects.all()
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'Please upload a CSV file')
            return redirect('bulk_add_student')
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file')
            return redirect('bulk_add_student')
        course_id = request.POST.get('course_id')
        session_year_id = request.POST.get('session_year_id')
        if not course_id or not session_year_id:
            messages.error(request, "Course and Session Year are required.")
            return redirect('bulk_add_student')
        try:
            file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
            csv_reader = csv.DictReader(file_data)
            course_obj = Course.objects.get(id=course_id)
            session_year_obj = Session_Year.objects.get(id=session_year_id)
            required_fields = ['full_name', 'username', 'email', 'password', 'address', 'gender', 'enrollment_no']
            if not all(field in csv_reader.fieldnames for field in required_fields):
                missing = [field for field in required_fields if field not in csv_reader.fieldnames]
                messages.error(request, f"CSV is missing required columns: {', '.join(missing)}")
                return redirect('bulk_add_student')
            students_added_count = 0
            for row in csv_reader:
                if not all(row.get(field) for field in required_fields):
                    messages.warning(request, f"Skipping row due to missing data: {row.get('enrollment_no', 'Unknown Enrollment')}")
                    continue
                if CustomUser.objects.filter(email=row['email']).exists():
                    messages.warning(request, f"Email {row['email']} already exists. Skipping.")
                    continue
                if CustomUser.objects.filter(username=row['username']).exists():
                    messages.warning(request, f"Username {row['username']} already exists. Skipping.")
                    continue
                if Student.objects.filter(enrollment_no=row['enrollment_no']).exists():
                    messages.warning(request, f"Enrollment no {row['enrollment_no']} already exists. Skipping.")
                    continue
                user = CustomUser(
                    first_name=row['full_name'],
                    username=row['username'],
                    email=row['email'],
                    user_type=3
                )
                user.set_password(row['password'])
                user.save()
                student = Student(
                    admin=user,
                    address=row['address'],
                    session_year_id=session_year_obj,
                    course_id=course_obj,
                    gender=row['gender'],
                    enrollment_no=row['enrollment_no'],
                    semester=row.get('semester')
                )
                student.save()
                students_added_count += 1
            if students_added_count > 0:
                messages.success(request, f"{students_added_count} students added successfully!")
            else:
                messages.info(request, "No new students were added.")
            return redirect('bulk_add_student')
        except Course.DoesNotExist:
            messages.error(request, "Selected Course does not exist.")
        except Session_Year.DoesNotExist:
            messages.error(request, "Selected Session Year does not exist.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
        return redirect('bulk_add_student')
    context = {
        'course': course,
        'session_year': session_year,
    }
    return render(request, 'Hod/bulk_add_student.html', context)

@login_required(login_url='/')
def BULK_ADD_STAFF(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'Please upload a CSV file')
            return redirect('bulk_add_staff')
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file')
            return redirect('bulk_add_staff')
        try:
            file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
            csv_reader = csv.DictReader(file_data)
            required_fields = ['full_name', 'username', 'email', 'password', 'address', 'gender']
            if not all(field in csv_reader.fieldnames for field in required_fields):
                missing = [field for field in required_fields if field not in csv_reader.fieldnames]
                messages.error(request, f"CSV is missing required columns: {', '.join(missing)}")
                return redirect('bulk_add_staff')
            staff_added_count = 0
            for row in csv_reader:
                if not all(row.get(field) for field in required_fields):
                    messages.warning(request, f"Skipping row due to missing data: {row.get('username', 'Unknown Username')}")
                    continue
                if CustomUser.objects.filter(email=row['email']).exists():
                    messages.warning(request, f"Email {row['email']} already exists. Skipping.")
                    continue
                if CustomUser.objects.filter(username=row['username']).exists():
                    messages.warning(request, f"Username {row['username']} already exists. Skipping.")
                    continue
                user = CustomUser(
                    first_name=row['full_name'],
                    username=row['username'],
                    email=row['email'],
                    user_type=2
                )
                user.set_password(row['password'])
                user.save()
                staff = Staff(
                    admin=user,
                    address=row['address'],
                    gender=row['gender']
                )
                staff.save()
                staff_added_count += 1
            if staff_added_count > 0:
                messages.success(request, f"{staff_added_count} staff members added successfully!")
            else:
                messages.info(request, "No new staff members were added.")
            return redirect('bulk_add_staff')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('bulk_add_staff')
    return render(request, 'Hod/bulk_add_staff.html')

@login_required(login_url='/')
def STUDENT_DETAILS(request, id):
    try:
        student = Student.objects.select_related('admin', 'course_id', 'session_year_id').get(id=id)
        context = {
            'student': student,
        }
        return render(request, 'Hod/student_details.html', context)
    except Student.DoesNotExist:
        messages.error(request, "Student details not found.")
        return redirect('view_student')