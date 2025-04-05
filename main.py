import cv2
from ultralytics import YOLO
import datetime
import csv

print("Hallo World!!")

def plot(cap,results,total):
    ids_areas = []
    index_num = 0
    size = cap.shape[:2]
    cv2.line(cap,
            (int(size[1] / 2-250), 0),
            (int(size[1] / 2-250) ,size[0]),
            (0,255,0),
            2)
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
            position = ((xyxy[0] + xyxy[2]) / 2,(xyxy[1] + xyxy[3]) / 2)
            if (xyxy[0] + xyxy[2]) / 2 <= size[1] / 2-250:
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
            ids_areas.append([id,area,position])
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
history_buffer = {}  # 各IDごとに座標履歴を保存する辞書
buffer_size = 3  # 最大で10フレーム分の履歴を保持
def update_history_buffer(id, area):
    if id not in history_buffer:
        history_buffer[id] = []
    
    # バッファサイズが超えた場合、古いデータを削除
    if len(history_buffer[id]) >= buffer_size:
        history_buffer[id].pop(0)
    
    # 新しい位置データを追加
    history_buffer[id].append(area)
def trucking(ids_areas):
    count = 0
    global p_id_rec,p_id_rec1,p_id_rec2,p_id_rec3,p_id_rec4
    global all_id,all_id1,all_id2,all_id3,all_id4,p_id_rec
    now_ids = []
    if ids_areas is None:pass
    else:
        for id ,area in ids_areas:
            id = int(id)
            update_history_buffer(id,area)
            if id in id_record:#idが既出の場合。
                #いっこ前の周にはあったけど今回はなくなったやつの最後のareaが1か0かで判別。
                now_ids.append(int(id))
                if area_record[str(id)] != "out":
                    area_record[str(id)] = area
            else:
                id_record.append(int(id))
                if area == 0:
                    area_record[str(id)] = area
                else:
                    area_record[str(id)] = "out"
        
        dumy = p_id_rec[:]
        if now_ids is not None:
            for i in now_ids:
                try:
                    dumy.remove(i)
                except ValueError:dumy = []
        print("dumy",dumy)
        print("pre",p_id_rec)
        print("now",now_ids)
        print("area",area_record)
        print("idrecord",id_record)
        print("buffer",history_buffer)
        print("---------------------")
        if dumy == []:pass
        else:
            for k in dumy:
                if area_record[str(k)] == 1:
                    count+=1
                area_record.pop(str(k))#配列の要素kを削除
                id_record.remove(k)
                dumy.remove(k)
                """ area_record_key = list(area_record)
                for j in area_record_key:
                    if int(j) not in now_ids:
                        area_record.pop(str(j)) """
            for l in dumy:
                now_ids.append(l)
        for j in id_record:
            if j in now_ids or j in p_id_rec:pass
            else:
                print("del;",j)
                area_record.pop(str(j))
                id_record.remove(j)
        p_id_rec = now_ids
        return count


# 記録用の辞書
id_last_position = {}  # 各IDの最後に検出された位置 (x, y) を記録
id_last_velocity = {}  # 各IDの最後に計算された速度 (vx, vy)
id_last_frame = {}    # 各IDが最後に登場したフレームを記録
id_last_area = {}     # 各IDが消えた時の領域を記録
id_first_area = {}    # 各IDが初登場した時の領域を記録
disappeared_ids = {}  # 消えたIDとその消失フレームを記録
max_speed = 10         # 一定フレーム間での最大速度（閾値）
max_distance = 50      # IDが変わった場合でも同一人物とみなす許容距離
current_frame = 0     # 現在のフレーム数

# 毎フレーム処理する関数
def process_frame(ids_areas):
    global current_frame
    current_frame += 1
    
    current_ids = set()  # 現在のフレームで検出されたIDのリスト
    new_counts = 0       # このフレームで新たにカウントされた人数
    
    # 1. 各フレームでのIDと領域の記録
    for id, area,position in ids_areas:
        id = int(id)
        current_ids.add(id)
        x, y = position
        if id not in id_first_area:
            # 初登場の領域を記録（初登場が領域0か1か）
            id_first_area[id] = area
        if id in id_last_position:
            prev_x, prev_y = id_last_position[id]
            vx = x - prev_x
            vy = y - prev_y
            id_last_velocity[id] = (vx, vy)

        # 最後の位置とフレームを記録
        id_last_position[id] = (x, y)
        id_last_frame[id] = current_frame
        id_last_area[id] = area
    #print("last_f:",id_last_frame)
    #print("last_a:",id_last_area)
    #print("last_cu:",current_ids)
    # 2. 前フレームで存在していたが、今回登場しないIDを消失と判断
    for id in list(id_last_frame.keys()):
        if id not in current_ids:
            # そのIDが既に消えたと判断されていない場合のみ
            if id not in disappeared_ids:
                print("消えてなーい")
                disappeared_ids[id] = current_frame

    # 3. 消失して10フレーム経過したIDを確認し、再登場していないかをチェック
    for id, disappear_frame in list(disappeared_ids.items()):
        if current_frame - id_last_frame[id] >= 15:
            print("60F経過ー")
            # 初登場が領域0で、最後に消えた領域が1の場合のみカウント
            print("id:",id)
            print("last",id_last_frame[id])
            print("disappear",disappear_frame)
            print("last_area",id_last_area[id])
            print("first_area",id_first_area[id])
            if id_last_area[id] == 1 and id_first_area[id] == 0:
                print(f"ID {id} が領域0で初登場し、右側で消えたのでカウント +1")
                new_counts += 1  # このフレームでカウントされた人数を増やす
            # カウント処理が完了したら、そのIDは記録から削除
            #time.sleep(1)
            del disappeared_ids[id]
            del id_last_frame[id]
            del id_last_area[id]
            del id_first_area[id]
    
    print(current_frame)
    # このフレームでカウントされた人数を返す
    return new_counts


""" annotated_frame = results[0].plot() """
model = YOLO('best3.pt')
#cap = cv2.imread("nichihamu.jpg")
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0)
FPS = 24
cap.set(cv2.CAP_PROP_FPS, FPS)
#fourcc = cv2.VideoWriter_fourcc(*'xvid')
frame_width = 960  # フレームの幅
frame_height = 540  # フレームの高さ
#fps = float(cap.get(cv2.CAP_PROP_FPS))  # FPS
#out = cv2.VideoWriter("result11_best_20F.avi", fourcc, fps, (frame_width, frame_height),True)
#cv2.imwrite("result.jpg",cap)
people_num = 0
total = 0


d_today = str(datetime.date.today())
t_now = str(datetime.datetime.now().time())
date4 = str(d_today+"-"+t_now)
csvname = date4.split(".")[0].replace(":","-")+".csv"
fname = date4.split(".")[0].replace(":","-")+".txt"
f = open(csvname, 'w',newline="")
f.close()
while cap.isOpened():
    # １フレーム読み込む
    success, frame = cap.read()
    if success:
        #frame = edge(frame)
        # YOLOv8でトラッキング
        frame = cv2.resize(frame, (960, 540))
        frame = cv2.flip(frame, 1)
        results = model.track(frame, persist=True, verbose=False)

        # 結果を描画する関数
        frame_annotated ,ids_areas = plot(frame,results,total)
        people_num = process_frame(ids_areas)
        total += people_num
        f = open(fname,"w")
        #f.write(str(time.time())+":"+str(people_num)+"人")
        f.write("total:"+str(total))
        f.close()
        #print(total)
        cv2.putText(frame_annotated, str(total), (0,30), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255),2)
        # OpenCVで表示＆キー入力チェック
        cv2.imshow("YOLOv8 Tracking", frame_annotated)
        #out.write(frame_annotated)
        d_today = str(datetime.date.today())
        t_now = str(datetime.datetime.now().time())
        date4 = str(d_today+"-"+t_now)
        times = date4.split(":")[0]
        rows = []
        with open(csvname,newline="") as f:
            reader = csv.reader(f)
            try:
                rows = list(reader)
                under = rows[-1]
                if under[0] == times:
                    rows[-1][1] = str(int(rows[-1][1]) + people_num)
                    print(rows)
                else:
                    rows.append([times,people_num])
                    print(rows)
            except IndexError:
                rows.append([str(times),str(total)])
                print(rows)

        with open(csvname, 'w',newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

            
        key = cv2.waitKey(1)
        if key != -1:
            print("STOP PLAY")
            cap.release()
            #out.release()
            break
    else:break
cap.release()
#out.release()
