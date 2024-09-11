from flask import Flask, render_template, request, redirect
from models import db, Student, Candidate
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voting_system.db'
db.init_app(app)

# Initialize the database and populate candidates if not already there
with app.app_context():
    db.create_all()
    if not Candidate.query.first():
        candidate1 = Candidate(name="Candidate 1")
        candidate2 = Candidate(name="Candidate 2")
        db.session.add(candidate1)
        db.session.add(candidate2)
        db.session.commit()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/vote', methods=['POST'])
def vote():
    student_id = request.form['student_id']

    # Validate student ID
    if not student_id.startswith('19052'):
        return "Invalid student ID. You are not a Dentistry student.", 400

    # Check if student has already voted
    if Student.query.filter_by(student_id=student_id).first():
        return "You have already voted.", 400

    # Get two random candidates
    candidates = Candidate.query.all()
    candidate_1, candidate_2 = random.sample(candidates, 2)

    # Process the vote
    candidate_id = request.form['candidate']
    voted_candidate = Candidate.query.get(candidate_id)
    if voted_candidate:
        voted_candidate.votes += 1
        db.session.commit()

        # Store student and candidate vote
        new_student = Student(student_id=student_id, candidate_id=candidate_id)
        db.session.add(new_student)
        db.session.commit()

    return "Vote cast successfully!"


# Route to display voting results
@app.route('/results')
def results():
    candidates = Candidate.query.all()

    # Calculate total votes cast
    total_votes = sum(candidate.votes for candidate in candidates)

    if total_votes == 0:
        return "No votes have been cast yet."

    # Render the results page with candidates and total votes
    return render_template('results.html', candidates=candidates, total_votes=total_votes)


if __name__ == '__main__':
    app.run(debug=True)
