from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
app.config['UPLOAD_FOLDER_VIDEO'] = 'static/videos'
app.config['UPLOAD_FOLDER_THUMBNAIL'] = 'static/thumbnail'
db = SQLAlchemy(app)

# Ensure upload folders exist
os.makedirs(app.config['UPLOAD_FOLDER_VIDEO'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER_THUMBNAIL'], exist_ok=True)

# Database Model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    video_path = db.Column(db.String(200), nullable=False)
    thumbnail_path = db.Column(db.String(200), nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

# ✅ Upload Course API
@app.route('/upload-course', methods=['POST'])
def upload_course():
    title = request.form['title']
    description = request.form['description']
    price = request.form['price']
    
    # File Upload Handling
    video = request.files['video']
    thumbnail = request.files['thumbnail']

    # Save Files
    video_path = os.path.join(app.config['UPLOAD_FOLDER_VIDEO'], video.filename)
    thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER_THUMBNAIL'], thumbnail.filename)
    video.save(video_path)
    thumbnail.save(thumbnail_path)

    # Save Course to Database
    new_course = Course(
        title=title,
        description=description,
        price=float(price),
        video_path=video_path,
        thumbnail_path=thumbnail_path
    )
    db.session.add(new_course)
    db.session.commit()

    return jsonify({"message": "Course uploaded successfully!"})

# ✅ Get All Courses API
@app.route('/get-courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    output = []

    for course in courses:
        output.append({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'price': course.price,
            'video': course.video_path,
            'thumbnail': course.thumbnail_path
        })
    
    return jsonify(output)

# ✅ Delete Course API
@app.route('/delete-course/<int:id>', methods=['DELETE'])
def delete_course(id):
    course = Course.query.get(id)

    if not course:
        return jsonify({"error": "Course not found"}), 404

    # Delete Files from Server
    os.remove(course.video_path)
    os.remove(course.thumbnail_path)

    # Delete Course from Database
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Course deleted successfully!"})

# ✅ Run Server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
