from key_derivation import derive_key
from cryptography.fernet import Fernet
import json
import os
from gui import launch_thread


class Credential:
    def __init__(self, name, user, psw):
        self.name = name
        self.user = user
        self.psw = psw


class FileManager:
    #credentials list
    credentials = {}

    def add_credential(self,cred,psw):
        #check if credential id is already present
        check = self.is_already_present(cred["name"])
        if check == False:
            self.credentials.append(cred)
            #save changes on storage
            self.save_enc_file(json.dumps(self.credentials).encode(),psw)
            return True
        else:
            return False
    
    def remove_credential(self,name,psw):
        for y in self.credentials:
            if y["name"] == name:
                #remove selected credential
                self.credentials.remove(y)
                #save changes on storage
                self.save_enc_file(json.dumps(self.credentials).encode(),psw)
                return
            
    def is_already_present(self,name):
        #check if credential id is already present
        for y in self.credentials:
            if y["name"] == name:
                return True

        return False
    
    def edit_credential(self,c,psw):
        #edit credential data
        for j in self.credentials:
            if c["name"] == j["name"]:
                j["user"] = c["user"]
                j["psw"] = c["psw"]
                break
        #save changes on storage
        self.save_enc_file(json.dumps(self.credentials).encode(),psw)
        
    def save_enc_file(self,data,psw):
        #derive crypto key from password
        key = derive_key(psw) 

        #file name
        file_enc = 'storage.json' 

        #encrypt file
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)

        #write file
        with open(file_enc, 'wb') as f:
            f.write(encrypted)

    def load_enc_file(self,psw):
        #derive crypto key from password
        key = derive_key(psw) 

        #file name
        file_enc = 'storage.json' 
        
        #read file
        with open(file_enc, 'rb') as f:
            data = f.read()
            f.close()

        #if file is empty return
        if data == '':
            return data

        #decrypt file
        fernet = Fernet(key)
        decrypted = fernet.decrypt(data)

        #save credentials list as JSON array
        self.credentials = json.loads(decrypted.decode())
        return self.credentials           


#start gui
launch_thread(FileManager())
