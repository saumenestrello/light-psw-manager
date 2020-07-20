from key_derivation import derive_key
from cryptography.fernet import Fernet
import json
import os
from gui import launch_thread

def get_filename(type):
    with open('config.txt') as json_file:
        config = json.load(json_file)
    if type == 'enc':
        return config["filename-enc"]
    elif type == 'dec':
        return config["filename"]
    

class Credential:
    def __init__(self, name, user, psw):
        self.name = name
        self.user = user
        self.psw = psw


class FileManager:
    credentials = {}

    def add_credential(self,cred,psw):
        check = self.is_already_present(cred["name"])
        if check == False:
            self.credentials.append(cred)
            self.save_enc_file(json.dumps(self.credentials).encode(),psw)
    
    def remove_credential(self,name,psw):
        for y in self.credentials:
            if y["name"] == name:
                self.credentials.remove(y)
                self.save_enc_file(json.dumps(self.credentials).encode(),psw)
                return
            
    def is_already_present(self,name):
        for y in self.credentials:
            if y["name"] == name:
                return True

        return False
    
    def edit_credential(self,c,psw):
        for j in self.credentials:
            if c["name"] == j["name"]:
                j["user"] = c["user"]
                j["psw"] = c["psw"]
                break

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

        self.credentials = json.loads(decrypted.decode())
        return self.credentials
            
    def handle_choice(self,choice,psw):
        if int(choice) == 1:
        #cipher mode
            
            key = derive_key(psw) #derive crypto key from password
            file_enc = get_filename('enc') #file name
            file_plain = get_filename('dec') #file name

            #read file
            with open(file_plain, 'rb') as f:
                data = f.read()
                f.close()

            #encrypt file
            fernet = Fernet(key)
            encrypted = fernet.encrypt(data)

            #write file
            with open(file_enc, 'wb') as f:
                f.write(encrypted)

            os.unlink(file_plain)

            open_success_window("File cifrato con successo")

        elif int(choice) == 2:
        #decipher mode
            
            key = derive_key(psw) #derive crypto key from password
            file_enc = get_filename('enc') #file name
            file_plain = get_filename('dec') #file name

            #read file
            with open(file_enc, 'rb') as f:
                data = f.read()
                f.close()

            #decrypt file
            fernet = Fernet(key)
            encrypted = fernet.decrypt(data)

            #write file
            with open(file_plain, 'wb') as f:
                f.write(encrypted)

            os.unlink(file_enc)
            
            open_success_window("File decifrato con successo")


#start gui
launch_thread(FileManager())
