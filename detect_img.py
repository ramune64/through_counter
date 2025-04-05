import cv2
from ultralytics import YOLO

model = YOLO('best.pt')
cap = cv2.imread("nichihamu.jpg")

results = model.track(cap, persist=True, verbose=False)
id = results[0].boxes.id.tolist()
conf = results[0].boxes.conf.tolist()
xyxy = results[0].boxes.xyxy.tolist()
print("id:",id)
print("conf:",conf)
print("xyxy:",xyxy)
f = open("text_files/text"+str(0)+".txt","w")
for i in id:
    t = str(i) +" "+ str(xyxy[int(i-1)]) +" "+ str(conf[int(i-1)])+"\n"
    f.write(t)
f.close()
annotated_frame = results[0].plot()
cv2.imwrite("result2.jpg",annotated_frame)