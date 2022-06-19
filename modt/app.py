from flask import Flask, render_template, url_for, redirect, request,flash, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from models import check_login, create_account
import cv2,os
from moving_object_tracker import tracker_run
app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'static/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif','mp4'])

app.secret_key = "secret---key"
def allowed_file(filename):
    	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def home():
	return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
	if request.method == 'GET':
		pass
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')

		if not username == '' and not password == '':
			verdict = check_login(username, password)

			if verdict:
				return render_template('success.html')
			else:
				return render_template('failure.html')
	return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'GET':
		pass

	if request.method == 'POST':
		email = request.form.get('email')
		username = request.form.get('username')
		password = request.form.get('password')

		if not email == '' and not username == '' and not password == '':
			create_account(email, username, password)

			return render_template('success.html')

	return render_template('signup.html')


def gen_frames(vid):  # generate frame by frame from camera
    pat = "C:/Users/DELL/Desktop/modt/static/uploads/"+str(vid)
    camera = cv2.VideoCapture(pat)
    i=0
    while True:
        i+=1
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            print("===========>ERROR<============")
            break
        else:
            if i%3==0:
                frame = tracker_run(frame,i)
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
    # pat = "D:/PythonEnv/test/modt/data/video/"+str(vid)
    # tracker_run(pat)

@app.route('/success', methods=['POST'])
def upload_video():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	else:
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		# stream_video(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
		#print('upload_video filename: ' + filename)
		flash('Video successfully uploaded and displayed below')
		return render_template('success.html', filename=filename)


@app.route('/video_feed/<filename>')
def video_feed(filename):
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(filename), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
	app.run(debug=True)