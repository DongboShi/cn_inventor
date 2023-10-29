#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import geocode
import eviltransform

def connection():
    conn = MySQLdb.Connect(
        host = "202.120.15.230",
        port = 3306,
        user = "danxiwang",
        passwd = "Wdx19930909",
        db = "business",
        charset = "utf8"
    )
    return conn


def get_address_list():
    conn = connection()
    cur = conn.cursor()
    sql = """
    SELECT
      id,
      if(left(address, length(suoshuquyu) / 3) != corp.suoshuquyu, concat(suoshuquyu, address), address) AS address
    FROM corp
    WHERE address != '????';
    """
    cur.execute(sql)
    data = cur.fethcall()
    cur.close()
    conn.close()
    return data



