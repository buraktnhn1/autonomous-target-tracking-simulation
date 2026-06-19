import cv2
import numpy as np
import random

width = 1280
height = 720
fps = 30
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('simulation.mp4', fourcc, fps, (width, height))

def load_car_image(image_path, target_size = (40, 65)):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        return np.zeros((target_size[1], target_size[0], 4), dtype = np.uint8)
    
    return cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)

car_images = {
    'blue' : load_car_image('car_blue.png'),
    'yellow' : load_car_image('car_yellow.png'),
    'white' : load_car_image('car_white.png'),
    'red' : load_car_image('car_red.png')
}

vehicles = [
    {'pos': [300, 200], 'vel': [4, 3], 'color': 'blue'},
    {'pos': [600, 200], 'vel': [-3, 5], 'color': 'yellow'}, # Hedefimiz
    {'pos': [400, 500], 'vel': [-4, -4], 'color': 'red'},
    {'pos': [700, 500], 'vel': [3, -3], 'color': 'white'}
]

trees = [[random.randint(50, width - 50), random.randint(0, height), random.randint(20, 45)] for _ in range(45)]
road_y = height // 2

def draw_car(frame, v):
    x, y = int(v['pos'][0]), int(v['pos'][1])
    img = car_images[v['color']]
    h, w = img.shape[:2]

    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(width, x + w), min(height, y + h)
    
    if x1 >= x2 or y1 >= y2: 
        return

    img_x1, img_y1 = x1 - x, y1 - y
    img_x2, img_y2 = img_x1 + (x2 - x1), img_y1 + (y2 - y1)

    car_bgr = img[:, :, :3]

    lower_white = np.array([200, 200, 200], dtype=np.uint8)
    upper_white = np.array([255, 255, 255], dtype=np.uint8)
    
    white_mask = cv2.inRange(car_bgr, lower_white, upper_white)
    
    car_mask = cv2.bitwise_not(white_mask)
    
    car_cropped = car_bgr[img_y1:img_y2, img_x1:img_x2]
    mask_cropped = car_mask[img_y1:img_y2, img_x1:img_x2]
    
    roi = frame[y1:y2, x1:x2]
    
    bg_bg = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(mask_cropped))
    car_fg = cv2.bitwise_and(car_cropped, car_cropped, mask=mask_cropped)
    
    frame[y1:y2, x1:x2] = cv2.add(bg_bg, car_fg)

def getFrame():
    global road_y
    
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (60, 160, 60)
    
    for t in trees:
        t[1] += 2 
        
        if t[1] > height + 50:
            t[1], t[0] = -20, random.randint(50, width-50)
        cv2.circle(frame, (t[0], t[1]), t[2], (40, 110, 40), -1)

    road_y += 2
    if road_y > height + 40: 
        road_y = -40
 
    cv2.rectangle(frame, (0, road_y - 40), (width, road_y + 40), (120, 120, 120), -1)
    cv2.line(frame, (0, road_y), (width, road_y), (200, 200, 200), 4, cv2.LINE_AA)
 
    cv2.rectangle(frame, (width // 3 - 40, 0), (width // 3 + 40, height), (120, 120, 120), -1)
    cv2.line(frame, (width // 3, 0), (width // 3, height), (200, 200, 200), 4, cv2.LINE_AA)
    
    for v in vehicles:
        v['pos'][0] += v['vel'][0]
        v['pos'][1] += v['vel'][1]
        
        img_h, img_w = car_images[v['color']].shape[:2]
        
        if v['pos'][0] <= 0:
            v['pos'][0] = 1
            v['vel'][0] *= -1
        elif v['pos'][0] >= width - img_w:
            v['pos'][0] = width - img_w - 1
            v['vel'][0] *= -1
            
        if v['pos'][1] <= 0:
            v['pos'][1] = 1
            v['vel'][1] *= -1
        elif v['pos'][1] >= height - img_h:
            v['pos'][1] = height - img_h - 1
            v['vel'][1] *= -1
        
        draw_car(frame, v)

    y_car = vehicles[1]
    img_h, img_w = car_images['yellow'].shape[:2]
    target_x = int(y_car['pos'][0] + img_w // 2)
    target_y = int(y_car['pos'][1] + img_h // 2)
    
    cv2.circle(frame, (target_x, target_y), 5, (0, 255, 255), -1)

    cx, cy = width // 2, height // 2
    cv2.line(frame, (cx - 30, cy), (cx + 30, cy), (0, 255, 255), 2)
    cv2.line(frame, (cx, cy - 30), (cx, cy + 30), (0, 255, 255), 2)
    cv2.circle(frame, (cx, cy), 250, (255, 255, 255), 2, cv2.LINE_AA)
    
    return frame

while True:
    frame = getFrame()
    out.write(frame)
    cv2.imshow('Simulation', frame)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

out.release()
cv2.destroyAllWindows()    






