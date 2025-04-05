import cv2
from ultralytics import YOLO
from get_edge import edge
frame_number = 0
def maketxt(result,f_num):
    try:
        id = result[0].boxes.id.tolist()
        conf = result[0].boxes.conf.tolist()
        xyxy = result[0].boxes.xyxy.tolist()
        f = open("text_files/text"+str(f_num)+".txt","w")
        for i in range(len(id)):
            t = str(i) +"/ "+ str(xyxy[int(i-1)]) +"/ "+ str(conf[int(i-1)])+"\n"
            f.write(t)
        f.close()
    except AttributeError:
        f = open("text_files/text"+str(f_num)+".txt","w")
        t = "No_detected"
        f.write(t)
        f.close()
    #print("id:",id)
    #print("conf:",conf)
    #print("xyxy:",xyxy)
def plot(cap,results,total):
    ids_areas = []
    index_num = 0
    size = cap.shape[:2]
    """ cv2.line(cap,
            (int(size[1] / 2), 0),
            (int(size[1] / 2) ,size[0]),
            (0,255,0),
            2) """
    for cls in results[0].boxes.cls:

        if cls != 0:
            index_num += 1
            break
        else:
            if cls is None:break
            try:
                id = results[0].boxes.id[index_num].tolist()
                conf = results[0].boxes.conf[index_num].tolist()
                xyxy = results[0].boxes.xyxy[index_num].tolist()
            except TypeError:break
            
            font = cv2.FONT_HERSHEY_DUPLEX
            font_scale = 1
            font_thickness = 2
            if (xyxy[0] + xyxy[2]) / 2 <= size[1] / 2:
                color = (255,0,0)
                area = 1
            else:
                color = (0,0,255)
                area = 0
            cv2.rectangle(cap,
                        (round(xyxy[0]),round(xyxy[1])),
                        (round(xyxy[2]),round(xyxy[3])),
                        color,
                        3)
            text = "id:"+str(int(id))+" "+"area:"+str(area)+" "+str(round(conf*100)/100)
            (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, font_thickness)
            cv2.rectangle(cap,
                        (round(xyxy[0]),round(xyxy[1])),
                        (round(xyxy[0])+text_width,round(xyxy[1])-text_height),
                        color,
                        -1)
            cv2.putText(cap, text, (round(xyxy[0]),round(xyxy[1])), font, font_scale, (255,255,255),font_thickness)
            ids_areas.append([id,area])
            index_num += 1
    return cap, ids_areas
id_record = []
area_record = {}
p_id_rec = []
p_id_rec1 = []
p_id_rec2 = []
p_id_rec3 = []
p_id_rec4 = []
all_id = []
all_id1 = []
all_id2 = []
all_id3 = []
all_id4 = []
def trucking(ids_areas):
    count = 0
    global all_id,all_id1,all_id2,all_id3,all_id4,p_id_rec
    now_ids = []
    
    if ids_areas is None:pass
    else:
        for id ,area in ids_areas:
            id = int(id)
            all_id.append(id)
            if id in id_record:#idが既出の場合。
                #いっこ前の周にはあったけど今回はなくなったidの最後のareaが1か0かで判別。
                now_ids.append(int(id))
                if area_record[str(id)] != "out":
                    area_record[str(id)] = area
            else:
                id_record.append(int(id))
                if area == 0:
                    area_record[str(id)] = area
                else:
                    area_record[str(id)] = "out"
        all_id4 = all_id3[:]
        all_id3 = all_id2[:]
        all_id2 = all_id1[:]
        all_id1 = all_id[:]
        
        p_id_rec4 = p_id_rec3[:]
        p_id_rec3 = p_id_rec2[:]
        p_id_rec2 = p_id_rec1[:]
        p_id_rec1 = p_id_rec[:]
        
        dumy = p_id_rec4[:]
        if now_ids is not None:
            for i in p_id_rec3:
                try:
                    dumy.remove(i)
                except ValueError:dumy = []
        print("dumy",dumy)
        print("pre",p_id_rec)
        print("now",now_ids)
        print("area",area_record)
        print("---------------------")
        if dumy == []:pass
        else:
            for k in dumy:
                if k in all_id or k in all_id1 or k in all_id2:pass
                else:
                    if area_record[str(k)] == 1:
                        count+=1
                    area_record.pop(str(k))
                    id_record.remove(k)
                """ area_record_key = list(area_record)
                for j in area_record_key:
                    if int(j) not in now_ids:
                        area_record.pop(str(j)) """
        p_id_rec = now_ids
        return count


model = YOLO('best.pt')
cap = cv2.VideoCapture(0)
FPS = 24
cap.set(cv2.CAP_PROP_FPS, FPS)
people_num = 0
total = 0
frame_num = 0
while cap.isOpened():
    # １フレーム読み込む
    success, frame = cap.read()
    if success:
        #frame = edge(frame)
        # YOLOv8でトラッキング
        size = frame.shape[:2]
        print("size:",size)
        results = model.track(frame, persist=True, verbose=False)
        maketxt(results,frame_num)
        #print(frame_num)
        # 結果を描画する関数
        frame_annotated ,ids_areas = plot(frame,results,total)
        people_num = trucking(ids_areas)
        total += people_num
        #print(total)
        cv2.putText(frame_annotated, str(total), (0,30), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255),2)
        # OpenCVで表示＆キー入力チェック
        cv2.imshow("YOLOv8 Tracking", frame_annotated)
        frame_num += 1
        key = cv2.waitKey(1)
        if key != -1:
            print("STOP PLAY")
            break
    else:break