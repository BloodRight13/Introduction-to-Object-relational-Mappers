# Task 1
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from password import my_password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/fitness_center_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.String(100), unique=True, nullable=False)

class WorkoutSession(db.Model):
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    session_date = db.Column(db.DateTime, nullable=False)
    session_time = db.Column(db.Integer, nullable=False)
    activity = db.Column(db.Integer, nullable=False)


# Task 2
class MemberSchema(ma.Schema):
    id = fields.String(required = True)
    name = fields.String(required = True)
    age = fields.String(required = True)

    class Meta:
        feilds = ('id', 'name', 'age')

member_schema = MemberSchema()
members_schema = MemberSchema(many = True)

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_member = Member(
        id = member_data['id'],
        name = member_data['name'],
        age = member_data['age'])

    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message" : "New member added successfully"}), 201

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return members_schema.jsonify(members)

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    member.name = member_data['id']
    member.email = member_data['name']
    member.phone = member_data['age']
    db.session.commit()
    return jsonify({"message" : "Member details updated successfully"}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message" : "Member removed successfully"}), 200


# Task 3

@app.route('/workouts', methods=['POST'])
def add_workout_session():
    data = request.get_json()
    new_session = WorkoutSession(session_id = data['session_id'], 
        session_id = data['session_id'],
        member_id = data['member_id'], 
        session_date = data['session_date'], 
        session_time = data['session_time'],
        activity = data['activity'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'message': 'Workout session scheduled successfully!'}), 201

@app.route('/workouts/<int:id>', methods=['PUT'])
def update_workout_session(session_id):
    data = request.get_json()
    session = WorkoutSession.query.get_or_404(id)
    session.session_date = data['session_date']
    session.session_time = data['session_time']
    session.activity = data['activity']
    db.session.commit()
    return jsonify({'message': 'Workout session updated successfully!'})

@app.route('/members/<int:id>/workouts', methods=['GET'])
def get_workout_sessions(session_id):
    member = Member.query.get_or_404(id)
    return jsonify([{
        'member_id': w.member_id,
        'session_date': w.session_date,
        'session_time': w.session_time,
        'activity': w.activity
    } for w in member.workout_sessions])

