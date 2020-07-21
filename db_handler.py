from key_derivation import derive_key
from cryptography.fernet import Fernet
import json
import os
from gui import launch_thread, set_db_handler, launch_psw_thread
import sqlite3


class Credential:
    def __init__(self, name, user, psw):
        self.name = name
        self.user = user
        self.psw = psw


class DBHandler:
    #credentials list
    credentials = []

    def __init__(self,conn):
        self.connection = conn
        self.cursor = self.connection.cursor()

    def set_psw(self,psw):
        self.psw = psw

    def change_psw(self,psw):
        self.credentials = []
        
        #load credentials from db
        self.load_credentials()

        #clear table
        self.cursor.execute('DELETE FROM credentials')
        self.connection.commit()

        key = derive_key(psw)
        fernet = Fernet(key)

        print(self.credentials)

        #save credentials encoded with the new key
        for cred in self.credentials:
            sql = 'INSERT INTO credentials(id,encoded) VALUES(?,?)'        
            db_json = {}
            db_json["user"] = cred["user"]
            db_json["psw"] = cred["psw"]
            encrypted = fernet.encrypt(json.dumps(db_json).encode())
            data = (cred["name"],encrypted)                
            self.cursor.execute(sql,data)
            self.connection.commit()

        self.set_psw(psw)

    def add_credential(self,cred):
        #derive crypto key from password
        key = derive_key(self.psw)
        fernet = Fernet(key)

        #check if id already exists
        sql_1 = 'SELECT * FROM credentials WHERE id = ?'
        self.cursor.execute(sql_1,[cred["name"]])
        entry = self.cursor.fetchone()
        
        if entry is None:
            #insert new credential in db
            sql_2 = 'INSERT INTO credentials(id,encoded) VALUES(?,?)'
            
            db_json = {}
            db_json["user"] = cred["user"]
            db_json["psw"] = cred["psw"]
            encrypted = fernet.encrypt(json.dumps(db_json).encode())
            data = (cred["name"],encrypted)
                
            self.cursor.execute(sql_2,data)
            self.connection.commit()

            #append new credential to list
            self.credentials.append(cred)
            return True
        else:
            return False        
    
    def remove_credential(self,name):
        for y in self.credentials:
            if y["name"] == name:
                #remove selected credential
                self.credentials.remove(y)
                #save changes on db
                sql = 'DELETE from credentials where id = ?'
                data = []
                data.append(name)
                self.cursor.execute(sql,data)
                self.connection.commit()               
                return           
    
    def edit_credential(self,cred):
        is_present = False

        #derive crypto key from password
        key = derive_key(self.psw)

        #decrypt credentials
        fernet = Fernet(key)
        
        #edit credential data
        for j in self.credentials:
            if cred["name"] == j["name"]:
                j["user"] = cred["user"]
                j["psw"] = cred["psw"]
                is_present = True
                break
            
        #save changes on db
        if is_present:      
            sql = 'UPDATE credentials SET encoded = ? WHERE id = ?'
            db_json = {}
            db_json["user"] = cred["user"]
            db_json["psw"] = cred["psw"]
            encrypted = fernet.encrypt(json.dumps(db_json).encode())
            data = (encrypted,cred["name"])
            self.cursor.execute(sql,data)
            self.connection.commit()
            
    def load_credentials(self):
        #derive crypto key from password
        key = derive_key(self.psw)

        #decrypt credentials
        fernet = Fernet(key)

        self.cursor.execute("SELECT * FROM credentials")
        rows = self.cursor.fetchall()
        for row in rows:
            decrypted = fernet.decrypt(row[1])
            json_credential = json.loads(decrypted.decode())
            json_credential["name"] = row[0]
            self.credentials.append(json_credential)

        return self.credentials           


############################################# PROGRAM STARTING POINT

#read configuration params
db_path = ''

try:
    with open('config.txt') as json_file:
        config = json.load(json_file)
        db_path = config["db_path"]
        if not ('.db' in db_path):
            raise ValueError('invalid db path')
except Exception as e:
    db_path = 'storage.db'
    with open('config.txt', 'wb') as f:
        obj = {}
        obj["db_path"] = db_path        
        f.write(json.dumps(obj,indent=4,sort_keys=True).encode())

#open db connection
conn = sqlite3.connect(db_path)
sql_create_table = """ CREATE TABLE IF NOT EXISTS credentials (
                                        id text PRIMARY KEY,
                                        encoded text NOT NULL
                                    ); """
conn.execute(sql_create_table)

handler = DBHandler(conn)

#start gui
set_db_handler(handler)
launch_psw_thread()
launch_thread()
