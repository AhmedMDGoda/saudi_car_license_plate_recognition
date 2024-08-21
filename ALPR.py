#import cv2
import numpy as np
from ultralytics import YOLO
from brisque import BRISQUE
import arabic_reshaper
from bidi.algorithm import get_display

#check on the image resolution using BRISQUE
def check_image(image):
    brisque = BRISQUE()
    brisque_score = brisque.score(image)
    check = False
    if brisque_score > 70 or brisque_score < 0:
        check = True
    print(brisque_score)
    return check

#License plate detection using LP_Detection model 
def detection_model(image):
    license_plate_detector = YOLO('LP_Detection.pt')
    license_plates = license_plate_detector(image)[0]
    
    #In case no detections
    if not license_plates:
        print("There is no plate in this image...!")
        return np.array([])
    
    licenses = []
    for license_plate in license_plates.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = license_plate
        license_plate_crop = image[int(y1):int(y2), int(x1): int(x2), :]
        licenses.append(license_plate_crop)
        #print(score)
        #break
    
    
    return licenses



#Character recognition using LP_Recognition model
def character_recognition(image):
    model = YOLO('LP_Recogntion.pt')
    predictions = model(image)[0]
    boxes_with_labels = []
    for result in predictions.boxes.data.tolist():
        x1, y1, x2, y2, confidence, class_id = result
        class_name = predictions.names[class_id]
        boxes_with_labels.append((x1, class_name))
    sorted_boxes = sorted(boxes_with_labels)
    text = ''
    for box in sorted_boxes:
        text += box[1]    
    print(text)
    
    #error in recognition
    if len(text)<4 or len(text)>7:
        return ''
    
    character_count = sum(1 for char in text if char.isalpha())
    if character_count != 3:
        return ''
    
    return text


#Character mapping using dictionary
ENGLISH_TO_ARABIC = {
    'A': 'ا',
    'B': 'ب',
    'J': 'ح',
    'D': 'د',

    'R': 'ر',
    'S': 'س',
    'X': 'ص',
    'T': 'ط',

    'E': 'ع',
    'G': 'ق',
    'K': 'ك',
    'L': 'ل',

    'Z': 'م',
    'N': 'ن',
    'H': 'ه',
    'U': 'و',
    'V': 'ي',

    '0': '٠',
    '1': '۱',
    '2': '۲',
    '3': '۳',
    '4': '٤',
    '5': '۵',
    '6': '٦',
    '7': '٧',
    '8': '٨',
    '9': '٩',
    
    
}


#Convert english characters to arabic characters using mapping
def replace_english_to_arabic(text):
    for  english,arabic in ENGLISH_TO_ARABIC.items():
        text = text.replace(english,arabic+' ')
    reshaped_text = arabic_reshaper.reshape(text)
    final_text = get_display(reshaped_text)
    return final_text

#split between character by spaces
def split_characters(text):
    result = ''
    for ch in text:
        result = result + ch + ' '
    return result

#class to send the final text to api
class result:
    def __init__(self,filename,arabic_text,english_text):
        self.filename = filename
        self.arabic_text = arabic_text
        self.english_text = english_text
    
        


#main function
def car_plate(image,filename):
    try:
        #step 1: check on the image quality
        check = check_image(image)
        if check == True:
            return  {"Error Message in {}".format(filename):"This image has low quality...!"}
        
        #step 2: license plate detection
        licenses = detection_model(image)
        
        if not licenses:
            return  {"Error Message in {}".format(filename):"There is no license plate in this image...!"}
        
        #cv2.imshow("plate detection", license_plate )
        #cv2.waitKey(0)
        
        #step 3: license plate recognition
        responses = []
        num = 0
        for license_plate in licenses:
            text = character_recognition(license_plate)
            num += 1
            if not text:
                responses.append({"Error Message in {}".format(filename):"The license plate number {} is not readable...!".format(num)})  
            else:
                
                #step 4: character mapping
                english_text = split_characters(text)
                arabic_text = replace_english_to_arabic(english_text)
                response = result(filename +" -- license plate number {} --".format(num),arabic_text,english_text)
                responses.append(response)
            
            #print("plate number:")
            #print(arabic_text)
            #print(text)
        return responses
    except:
        return  {"Error Message":"Please enter another image ...!"}

