import random
import time
import cv2
from keras.models import load_model
import numpy as np
model = load_model('keras_model.h5')
cap = cv2.VideoCapture(0)
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

def compare_choice(prediction, player_score, computer_score):
    options = ['Rock', 'Paper', 'Scissors', 'Nothing']
    
    if prediction[0][0] > 0.5:
        player_choice = options[0]
    elif prediction[0][1] > 0.5:
        player_choice = options[1]
    elif prediction[0][2] > 0.5:
        player_choice = options[2]
    else:
        player_choice = options[3]

    computer_choice = random.choice(options)
    message = ""

    if computer_choice == 'Rock':
        if player_choice == 'Rock':
            message = "You and the computer both chose rock! It's a draw!"
        elif player_choice == 'Paper':
            message = "You chose paper and the computer chose rock! You win!"
            player_score = True
        elif player_choice == 'Scissors':
            message = "You chose scissors and the computer chose rock! You lose!"
            computer_score = True
        else:
            message = "Please choose either rock, paper or scissors."
    elif computer_choice == 'Paper':
        if player_choice == 'Rock':
            message = "You chose rock and the computer chose paper! You lose!"
            computer_score = True
        elif player_choice == 'Paper':
            message = "You and the computer both chose paper! It's a draw!"
        elif player_choice == 'Scissors':
            message = "You chose scissors and the computer chose paper! You win!"
            player_score = True
        else:
            message = "Please choose either rock, paper or scissors."
    elif computer_choice == 'Scissors':
        if player_choice == 'Rock':
            message = "You chose rock and the computer chose scissors! You win!"
            player_score = True
        elif player_choice == 'Paper':
            message = "You chose paper and the computer chose scissors! You lose!"
            computer_score = True
        elif player_choice == 'Scissors':
            message = "You and the computer both chose scissors! It's a draw!"
        else:
            message = "Please choose either rock, paper or scissors."
    else:
        message = "Please choose either rock, paper or scissors."
    return message, player_score, computer_score

camera_started = False
first_game = True
press_p = False
time_since_P = 0
elapsed = 0
p_score = 0
c_score = 0

while True:
    ret, frame = cap.read()
    resized_frame = cv2.resize(frame, (224, 224), interpolation = cv2.INTER_AREA)
    image_np = np.array(resized_frame)
    normalized_image = (image_np.astype(np.float32) / 127.0) - 1 # Normalize the image
    data[0] = normalized_image
    prediction = model.predict(data)

    if camera_started == False:
        camera_started = True
        message = "Press P to play"
    if cv2.waitKey(1) == ord("p") and camera_started == True and first_game == True and press_p == False:
        first_game = False
        press_p = True
        time_since_P = time.time()

    elapsed = time.time() - time_since_P

    if camera_started == True and first_game == False and press_p == True and elapsed < 5:
        message = f"Make your choice in {5 - int(elapsed)} seconds"

    elif camera_started == True and first_game == False and press_p == True and elapsed > 5:
        x = compare_choice(prediction, player_score=False, computer_score=False)
        if x[1] == True:
            p_score += 1
        if x[2] == True:
            c_score += 1
        message = f"{x[0]} {p_score} - {c_score}"
        press_p = False
    elif camera_started == True and first_game == False and press_p == False and elapsed > 10:
        message = "Press X to play again"
    if cv2.waitKey(1) == ord("x") and camera_started == True and first_game == False and press_p == False:
        message = "Make your choice"
        press_p = True
        time_since_P = time.time()
    if p_score == 3:
        camera_started = False
        message = "You won! Please press q to close this window and restart."
    if c_score == 3:
        camera_started = False
        message = "The computer won! Please press q to close this window and restart."

    cv2.putText(frame, message, (50,50), cv2.FONT_HERSHEY_DUPLEX, 0.475, (0, 0, 255), 1)
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
cap.release()
# Destroy all the windows
cv2.destroyAllWindows()