from werkzeug import exceptions
from flask import render_template, request
from flask import current_app as app

from application.data_helper import save_data
from application.data_helper import teachers, goals, days_of_week
from application.data_helper import random_limit, grouped_by_hours


@app.route('/')
def main():
    random_teachers = random_limit(teachers, 6)
    return render_template('index.html', teachers=random_teachers,
                           goals=goals)


@app.route('/all/')
def get_all_teachers():
    return render_template('index.html', teachers=teachers.items(),
                           goals=goals)


@app.route('/goals/<goal_code>/')
def get_goal(goal_code):
    goal = goals[goal_code]
    filtered = {
        teacher_id: teacher for teacher_id, teacher in teachers.items()
        if goal_code in teacher['goals']
    }
    sorted_teachers = sorted(filtered.items(),
                             key=lambda x: x[1]['rating'], reverse=True)
    return render_template('goal.html', goal=goal, teachers=sorted_teachers)


@app.route('/profiles/<int:teacher_id>/')
def get_profile(teacher_id):
    teacher = teachers.get(teacher_id)
    grouped_days = grouped_by_hours(teacher['free'])
    goals_by_codes = [goal['desc'] for code, goal in goals.items()
                      if code in teacher['goals']]
    profile = {
        'teacher': teacher,
        'goals': goals_by_codes,
        'hours': grouped_days
    }
    return render_template('profile.html', profile=profile,
                           days_of_week=days_of_week)


@app.route('/request/')
def get_request():
    return render_template('request.html', goals=goals)


@app.route('/request_done/', methods=['POST'])
def send_request():
    client_name = request.form.get("clientName")
    client_phone = request.form.get("clientPhone")
    goal_code = request.form.get("goal")
    goal = goals[goal_code]
    time = request.form.get("time")
    request_data = {
        'client_name': client_name,
        'client_phone': client_phone,
        'goal_desc': goal['desc'],
        'time': time
    }
    save_data(app.config.get('REQUEST_FILE'), request_data)
    return render_template('request_done.html', request_data=request_data)


@app.route('/booking/<int:teacher_id>/')
def get_booking(teacher_id):
    teacher = teachers.get(teacher_id)
    booking_day = days_of_week[request.args.get('day')]
    booking_hour = request.args.get('hour')
    booking_data = {
        'teacher': teacher,
        'day': booking_day['full_ver'],
        'hour': booking_hour
    }
    return render_template('booking.html', booking_data=booking_data)


@app.route('/booking_done/', methods=['POST'])
def send_booking():
    client_name = request.form.get("clientName")
    client_phone = request.form.get("clientPhone")
    booking_day = request.form.get("bookingDay")
    booking_hour = request.form.get("bookingHour")
    booking_teacher = request.form.get("bookingTeacher")
    booking_data = {
        'client_name': client_name,
        'client_phone': client_phone,
        'booking_day': booking_day,
        'booking_hour': booking_hour,
        'booking_teacher': booking_teacher
    }
    save_data(app.config.get('BOOKING_FILE'), booking_data)
    return render_template('booking_done.html', booking_data=booking_data)


@app.errorhandler(exceptions.NotFound)
def not_found(e):
    return render_template("404.html"), e.code


@app.errorhandler(exceptions.InternalServerError)
def server_error(e):
    return render_template("500.html"), e.code