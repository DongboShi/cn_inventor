#!/usr/bin/env python
# -*- coding: utf-8 -*-
import eviltransform
import db_util
import geocode
import poi_search
import multiprocessing.dummy
import sys
reload(sys)
sys.setdefaultencoding("utf8")



KEYS = [
    "6809f51ea24cd02694e4639bb85260ea",
    "f4a7973d38dad930c86b91fb0cbdc09b",
    "aff09a5f226f723091806d5c22215db1"
]
COUNT = 0

def get_task_list():
    conn = db_util.connection()
    cur = conn.cursor()
    # cur.execute("select id, address, suoshuquyu from geo_info where is_completed = 0 limit 0, 9000000;")
    cur.execute("SELECT rid, DZ from geo_info where is_completed = 0;")
    task_list = cur.fetchall()
    cur.close()
    conn.close()
    return task_list


def fetch_one(task):
    # rid, address, province = task
    rid, addr_for_search = task
    print rid
    # if address == u"暂无" or address is None:
    #     return None
    # else:
    #     if address.startswith(province):
    #         addr_for_search = address
    #     else:
    #         addr_for_search = province + address
    key_index = rid % 3
    global KEYS
    geocoder = geocode.AmapGecoder(KEYS[key_index])
    while True:
        try:
            result = geocoder.geocode(addr_for_search)
            global COUNT
            COUNT += 1
            break
        except (geocode.requests.ConnectionError, geocode.requests.exceptions.ReadTimeout):
            continue
    if result["status"] == "1":
        if result["geocodes"]:
            geocoding_info = result["geocodes"][0]
            cols = ["province","city","citycode","district","level","adcode","location","formatted_address"]
            insert_data = {k: v for k, v in geocoding_info.iteritems() if k in cols and v and type(v) is not list}
            location = insert_data["location"]
            lng_gcj02, lat_gcj02 = tuple(location.split(","))
            lat_wgs84, lng_wgs84 = eviltransform.gcj2wgs_exact(float(lat_gcj02), float(lng_gcj02))
            insert_data.update({"lat": str(lat_wgs84), "lng": str(lng_wgs84), "is_completed": "1"})
            sql = db_util.make_update_sql("geo_info", insert_data, {"rid": str(rid)})
            # sql = db_util.make_insert_sql("geo_info", insert_data)
            conn = db_util.connection()
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
        else:
            return None
    return True

# def fetch_one(task):
#     print task
#     global COUNT
#     COUNT += 1
#     global KEYS
#     searcher = poi_search.POISearcher(KEYS[COUNT % len(KEYS)])
#     page = 1
#     while True:
#         data = searcher.search(task, page=page)
#         if data["pois"]:
#             conn = db_util.connection()
#             cur = conn.cursor()
#             for poi in data["pois"]:
#                 item = {}
#                 item["id"] = poi["id"]
#                 item["name"] = poi["name"]
#                 item["type"] = poi["type"]
#                 item["typecode"] = poi["typecode"]
#                 item["address"] = poi["address"]
#                 item["location"] = poi["location"]
#                 item["pname"] = poi["pname"]
#                 item["cityname"] = poi["cityname"]
#                 item["adname"] = poi["adname"]
#                 item["keyword"] = task
#                 lng_gcj02, lat_gcj02 = tuple(item["location"].split(","))
#                 lat_wgs84, lng_wgs84 = eviltransform.gcj2wgs_exact(float(lat_gcj02), float(lng_gcj02))
#                 item["lat"] = lat_wgs84
#                 item["lng"] = lng_wgs84
#                 sql = db_util.make_insert_sql("poi_info", item)
#                 cur.execute(sql)
#                 conn.commit()
#             cur.close()
#             conn.close()
#             if len(data["pois"]) < 20:
#                 break
#             else:
#                 page += 1
#         else:
#             break


# def get_task_list():
#     conn = db_util.connection()
#     cur = conn.cursor()
#     cur.execute("select name_chn from edu_ins;")
#     tasks = [i for i, in cur.fetchall()]
#     cur.close()
#     conn.close()
#     return tasks


def main():
    tasks = get_task_list()
    print len(tasks)
    # pool = multiprocessing.dummy.Pool(6)
    # pool.map(fetch_one, tasks)
    # pool.close()
    # pool.join()
    for i in tasks:
       fetch_one(i)


if __name__ == "__main__":
    main()
