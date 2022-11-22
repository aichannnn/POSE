import streamlit as st
import pandas as pd
from PIL import Image
import cv2
import numpy as np
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
           angle = 360 - angle

    return angle

# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
# DB Management
import sqlite3
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data


def main():
	"""Simple Login App"""

	st.title("VIRTUAL GYM TRAINER")

	menu = ["Login","SignUp"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Login":
		st.sidebar.subheader("Login Section")
		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password",type='password')
		if st.sidebar.checkbox("Login"):
			# if password == '12345':
			create_usertable()
			hashed_pswd = make_hashes(password)

			result = login_user(username,check_hashes(password,hashed_pswd))

			if result:

				st.success("Logged In as {}".format(username))

				task = st.sidebar.selectbox("Task",["Home","Exercise","About","Admin"])
				if task == "Home":
					st.subheader("> Home")
					imag = Image.open('img.jpeg')
					st.image(imag, width=700)
					into = Image.open('intro.jpg')
					st.image(into, width=750)
					st.title("Important Tips from AI Trainer")
					tip = Image.open('ab.jpg')
					st.image(tip)

				elif task == "Exercise":
					side = st.sidebar.selectbox("Select a exercises",["Introduction", "Left Arm curls", "Right Arm Curls"])

					if side == "Introduction":
						st.subheader("> Introduction")
						st.title("Introduction")
						st.subheader("How to use this ?")
						st.write("1. Insert a camera if you are using Pc")
						st.write("2. Click on select box")
						st.write("3. Choose exercises and select one ")
						st.write("4. Click on Taskbar and Click on Black Icon to see the Window ")
						st.write("5. Press Q for quit the window and then start next exercise ")

					if side == "Left Arm curls":

						cap = cv2.VideoCapture(0)
						# Curl counter variables
						counter = 0
						stage = None

						## Setup mediapipe instance
						with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
							while cap.isOpened():
								ret, frame = cap.read()

								# Recolor image to RGB
								image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
								image.flags.writeable = False

								# Make detection
								results = pose.process(image)

								# Recolor back to BGR
								image.flags.writeable = True
								image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

								# Extract landmarks
								try:
									landmarks = results.pose_landmarks.landmark

									# Get coordinates
									shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
												landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
									elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
											 landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
									wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
											 landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

									# Calculate angle
									angle = calculate_angle(shoulder, elbow, wrist)

									# Visualize angle
									cv2.putText(image, str(angle),
												tuple(np.multiply(elbow, [640, 480]).astype(int)),
												cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
												)

									# Curl counter logic
									if angle > 160:
										stage = "down"
									if angle < 40 and stage == 'down':
										stage = "up"
										counter += 1
										print(counter)

								except:
									pass

								# Render curl counter
								# Setup status box
								cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)

								# Rep data
								cv2.putText(image, 'REPS', (15, 12),
											cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
								cv2.putText(image, str(counter),
											(10, 60),
											cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

								# Stage data
								cv2.putText(image, 'STAGE', (65, 12),
											cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
								cv2.putText(image, stage,
											(60, 60),
											cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

								# Render detections
								mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
														  mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2,
																				 circle_radius=2),
														  mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2,
																				 circle_radius=2)
														  )

								cv2.imshow('LEFT ARM Counter ', image)
								if cv2.waitKey(10) & 0xFF == ord('q'):
									break
							cap.release()
							cv2.destroyAllWindows()
							st.subheader("How to do it?")
							image = Image.open('bb.jpg')
							st.image(image, caption='arm curl ', width=300)
							st.write("1. Stand straight and slowly lift your left hand up and down.")
							st.write("2. You can also do it by using doubles.")
							st.write("It will count your Right hand bicep reps")
							st.write("Press Stop Button to stop action")
							st.write("😊😊 Enjoy your workout 🏋")

					if side == "Right Arm Curls":
						cap = cv2.VideoCapture(0)

						# Curl counter variables
						counter = 0
						stage = None

						## Setup mediapipe instance
						with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
							while cap.isOpened():
								ret, frame = cap.read()

								# Recolor image to RGB
								image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
								image.flags.writeable = False

								# Make detection
								results = pose.process(image)

								# Recolor back to BGR
								image.flags.writeable = True
								image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

								# Extract landmarks
								try:
									landmarks = results.pose_landmarks.landmark

									# Get coordinates
									shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
												landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
									elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
											 landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
									wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
											 landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

									# Calculate angle
									angle = calculate_angle(shoulder, elbow, wrist)

									# Visualize angle
									cv2.putText(image, str(angle),
												tuple(np.multiply(elbow, [640, 480]).astype(int)),
												cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
												)

									# Curl counter logic
									if angle > 160:
										stage = "down"
									if angle < 30 and stage == 'down':
										stage = "up"
										counter += 1
										print(counter)

								except:
									pass

								# Render curl counter
								# Setup status box
								cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)

								# Rep data
								cv2.putText(image, 'REPS', (15, 12),
											cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
								cv2.putText(image, str(counter),
											(10, 60),
											cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

								# Stage data
								cv2.putText(image, 'STAGE', (65, 12),
											cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
								cv2.putText(image, stage,
											(60, 60),
											cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

								# Render detections
								mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
														  mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2,
																				 circle_radius=2),
														  mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2,
																				 circle_radius=2)
														  )

								cv2.imshow('RIGHT ARM COUNTER', image)
								if cv2.waitKey(10) & 0xFF == ord('q'):
									break

						cap.release()
						cv2.destroyAllWindows()
					image = Image.open('bb.jpg')
					st.image(image, caption='arm curl ', width=300)
					st.subheader("How to do it?")
					st.write("1. Stand straight and slowly lift your right hand up and down.")
					st.write("2. You can also do it by using doubles.")
					st.write("It will count your Right hand bicep reps")
					st.write("Press Stop Button to stop action")
					st.write("😊😊 Enjoy your workout 🏋")
				if task == "About":
					st.subheader("> About")
					st.subheader("About AI Virtual Gym trainer.")
					st.write("""
				                Lifting weights is a great way to develop muscles, protect bones, burn calories, and stay fit. Maybe you
				                 don’t know where to start or how to perform the exercises. You may be tempted to just copy the exercises 
				                 your others are doing, but they may be doing things the wrong way. 
				                This is where your personal AI trainer comes in handy. With your personal AI trainer, 
				                you have immediate access to a world of knowledge to help you develop a weight-training routine that’s 
				                safe and effective. Weight training and healthy diet is one of the best ways to get into shape and lead
				                 a healthy lifestyle. With each passing day people are getting conscious about their health. 
				                 Many people today have a busy and hectic life and they cannot manage to go to the gym by using AI based 
				                 virtual gym they workout anytime anywhere without getting injured.It uses computer vision and gives output
				                 by tracing all 33 keypoint of your body.
				    """)
				elif task == "Admin":
					if password == '12345' and username =='admin':
						#st.sidebar("User Activity['User Info']")
						st.subheader("User Profiles")
						user_result = view_all_users()
						clean_db = pd.DataFrame(user_result,columns=["Username","Password"])
						st.dataframe(clean_db)
					else:
						st.write("This page is only for Admin")
			else:
				st.warning("Incorrect Username/Password")





	elif choice == "SignUp":
		st.subheader("Create New Account")
		new_user = st.text_input("Username")
		new_password = st.text_input("Password",type='password')

		if st.button("Signup"):
			create_usertable()
			add_userdata(new_user,make_hashes(new_password))
			st.success("You have successfully created a valid Account")
			st.info("Go to Login Menu to login")




main()