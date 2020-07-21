import PySimpleGUI as sg
import threading

crypto_psw = ''

def launch_thread(stub):
    #launch thread to open main window
    worker_thread = threading.Thread(target=open_main_window(stub), args=())
    worker_thread.start()

def launch_psw_thread():
    #launch thread to open password dialog
    worker_thread = threading.Thread(target=open_psw_dialog(), args=())
    worker_thread.start()
    worker_thread.join()

def launch_edit_thread(credential,stub):
    #launch thread to open edit dialog
    worker_thread = threading.Thread(target=open_edit_dialog(credential,stub), args=())
    worker_thread.start()
    worker_thread.join()

def launch_add_thread(stub):
    #launch thread to open add dialog
    worker_thread = threading.Thread(target=open_add_dialog(stub), args=())
    worker_thread.start()
    worker_thread.join()

def launch_error_thread(text):
    #launch thread to show error dialog
    worker_thread = threading.Thread(target=open_error_dialog(text), args=())
    worker_thread.start()
    worker_thread.join()

def launch_success_thread(text):
    #launch thread to show success thread
    worker_thread = threading.Thread(target=open_success_window, args=())
    worker_thread.start()


def create_table(json_data):
    #rows list
    data = []
    #table header
    header_list = [] 
    header_list.append('Name')
    header_list.append('User')
    header_list.append('Psw')
    
    for i in range(0, len(json_data)):
        #create rows and append them to the list
        row = []
        row.append(json_data[i]["name"])
        row.append(json_data[i]["user"])
        row.append(json_data[i]["psw"])
        data.append(row)

    table_data = data

    #save table reference into a global variable
    global table
    table = sg.Table(values=table_data,
                        enable_events=True,
                        display_row_numbers=True,
                        font='Helvetica',
                        def_col_width=20,
                        justification='center',
                        bind_return_key=True,
                        headings = header_list,
                        auto_size_columns=False,
                        key='_table_',
                        text_color='red')
                        
    #create layout as an array of rows
    layout = [[table],[sg.Button('Add'),sg.Button('Exit')]]

    #return window with table inside
    return sg.Window('Credentials list',font='Helvetica',resizable=True).Layout(layout)
    

def open_psw_dialog():
    #create layout for the dialog
    layout = [ [sg.Text('Password',size=(10,1)), sg.InputText(size=(25,1),justification='center', password_char='*')],[sg.Button('Submit')] ]
    #get password
    dialog = sg.Window('Insert password', layout)
    #event loop to process "events" and get the "values" of the inputs
    while True:
        event, values = dialog.read()
        if event == 'Submit':
            psw = values[0]
            if psw != '':
                #save psw inside a global variable
                global crypto_psw
                crypto_psw = psw
                break
            else:
                #show error
                open_error_window('Insert password!')
                
    dialog.close()

def open_edit_dialog(cred,stub):
    #create layout for the dialog
    layout = [ [sg.Text('Name',size=(10,1)),sg.InputText(cred["name"],size=(25,1),justification='center',disabled=True)],[sg.Text('User',size=(10,1)), sg.InputText(cred["user"],size=(25,1),justification='center')],
               [sg.Text('Password',size=(10,1)), sg.InputText(cred["psw"],size=(25,1),justification='center')],
               [sg.Button('Edit'),sg.Button('Delete')] ]

    global crypto_psw
    #create window
    dialog = sg.Window('Edit credential', layout)
    #event loop to process "events" and get the "values" of the inputs
    while True:
        event, values = dialog.read()
        if event == 'Edit':
            #create new row with edited data
            new_row = {}
            new_row["name"] = cred["name"]
            new_row["user"] = values[0]
            new_row["psw"] = values[1]
            #save changes on the storage
            stub.edit_credential(new_row,crypto_psw)
            #refresh table data
            refresh_data()
            break
        elif event == 'Delete':
            #check if the credential exists
            check = stub.is_already_present(cred["name"])
            if check == True:
                #remove credential and save changes on the storage
                stub.remove_credential(cred["name"],crypto_psw)
                #refresh table data
                refresh_data()
            break
        elif event == sg.WIN_CLOSED: #if user closes window or clicks cancel
            break              
    dialog.close()

def open_add_dialog(stub):
    #create layout for the dialog
    layout = [ [sg.Text('Name',size=(10,1)),sg.InputText(size=(25,1),justification='center')],[sg.Text('User',size=(10,1)), sg.InputText(size=(25,1),justification='center')],
               [sg.Text('Password',size=(10,1)), sg.InputText(size=(25,1),justification='center')],
               [sg.Button('Add')] ]

    global crypto_psw
    
    #create window
    dialog = sg.Window('Add credential', layout)
    #event loop to process "events" and get the "values" of the inputs
    while True:
        event, values = dialog.read()
        if event == 'Add':
            #create new row
            new_row = {}
            new_row["name"] = values[0]
            new_row["user"] = values[1]
            new_row["psw"] = values[2]
            #add row and save changes on storage
            res = stub.add_credential(new_row,crypto_psw)
            if res == True:
                #refresh table data
                refresh_data()
            else:
                launch_error_thread('credential already present!')
            break
        elif event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            break              
    dialog.close()

def open_main_window(stub):
    #add a touch of color
    #sg.theme('DarkAmber')
    sg.theme('DarkGrey2')

    global crypto_psw
    #open dialog to get password
    launch_psw_thread()

    global file_manager
    #save reference to file manager into a global variable
    file_manager = stub

    #load and decode encrypted storage file
    stub.load_enc_file(crypto_psw)
    #get credentials JSON array
    data = stub.credentials

    if data != '':
        #create table element
        window = create_table(data)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED: #if user closes window or clicks cancel
                break
            elif event == 'Exit': 
                break
            elif event == 'Add':
                #open add credential dialog
                launch_add_thread(stub)
            elif event == '_table_':
                #open edit credential dialog on row selection
                launch_edit_thread(data[values['_table_'][0]],stub)
                
        window.close()

    else:
        #prepare table
        headings = ['Name', 'User', 'Password']
        header =  [[sg.Text('  ')] + [sg.Text(h, size=(14,1)) for h in headings]]

        input_rows = []

def open_error_dialog(text):
    #create layout for the dialog
    layout = [[sg.Text(text)],[sg.Button('Ok')] ]
    #get password
    dialog = sg.Window('Error', layout)
    #event loop to process "events" and get the "values" of the inputs
    while True:
        event, values = dialog.read()
        if event == 'Ok':
            break
                
    dialog.close()

def refresh_data():
    global table
    global file_manager

    data = []
    #get credentials from file manager and refresh table data
    for i in file_manager.credentials:
        row = []
        row.append(i["name"])
        row.append(i["user"])
        row.append(i["psw"])
        data.append(row)
    table.Update(values=data)
