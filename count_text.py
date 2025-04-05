import glob
id_record = []
area_record = {}
p_id_rec = []
def trucking(ids_areas):
    count = 0
    global p_id_rec
    now_ids = []
    if ids_areas is None:pass
    else:
        for id ,area in ids_areas:
            id = int(id)
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
        print("---------------------")
        if dumy == []:pass
        else:
            for k in dumy:
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


texts = glob.glob("text_files/*.txt")
print(texts)
for txt in texts:
    f = open(txt,"r")
    t = f.read()
    if t == "No_detected":pass
    else:
        ids_areas = []
        lines = t.split("\n")[:-1]
        for a_people in lines:
            data = a_people.split(" ")
            data_index = 0
            for j in data:
                j = j.replace("[","")
                j = j.replace(",","")
                j = j.replace("]","")
                data[data_index] = j
                data_index += 1
            x0 = data[1]
            x1 = data[3]
            center = (x0+x1)/2
            if center <= 320:
                area = 0
            else:area = 1
            ids_areas.append([data[0],area])
        trucking(ids_areas)
