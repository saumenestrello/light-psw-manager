import PySimpleGUI as sg
import threading

crypto_psw = ''

def launch_thread(stub):
    worker_thread = threading.Thread(target=open_main_window(stub), args=())
    worker_thread.start()

def launch_psw_thread():
    worker_thread = threading.Thread(target=open_psw_dialog(), args=())
    worker_thread.start()
    worker_thread.join()

def launch_edit_thread(credential,stub):
    worker_thread = threading.Thread(target=open_edit_dialog(credential,stub), args=())
    worker_thread.start()
    worker_thread.join()

def launch_error_thread(text):
    worker_thread = threading.Thread(target=open_error_window, args=())
    worker_thread.start()

def launch_success_thread(text):
    worker_thread = threading.Thread(target=open_success_window, args=())
    worker_thread.start()


def create_table(json_data):

    data = []
    header_list = []
    header_list.append('NOME')
    header_list.append('USER')
    header_list.append('PSW')
    for i in range(0, len(json_data)):
        row = []
        row.append(json_data[i]["name"])
        row.append(json_data[i]["user"])
        row.append(json_data[i]["psw"])
        #row.append(sg.Button('Elimina'))
        #data.append([json_data[i]["name"],json_data[i]["user"],json_data[i]["psw"]])
        data.append(row)

    table_data = data
    global table
    table = sg.Table(values=table_data,
                        enable_events=True,
                        display_row_numbers=True,
                        font='Helvetica',
                        def_col_width=20,
                        justification='center',
                        bind_return_key=True,
                       # row_header_text='Row #',
                        headings = header_list,
                        auto_size_columns=False,
                        key='_table_',
                        text_color='red')
                        

    layout = [[table],[sg.Button('Aggiungi'),sg.Button('Exit')]]

    return sg.Window('Lista credenziali',font='Helvetica',resizable=True).Layout(layout)
    

def open_psw_dialog():
    layout = [ [sg.Text('Password'), sg.InputText()],[sg.Button('Submit')] ]

    #get password
    dialog = sg.Window('Inserisci la password', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = dialog.read()
        if event == 'Submit':
            psw = values[0]
            if psw != '':
                global crypto_psw
                crypto_psw = psw
                break
            else:
                open_error_window('Inserire una password!')
                
    dialog.close()

def open_edit_dialog(cred,stub):
    layout = [ [sg.Text('Nome     '),sg.Text(cred["name"])],[sg.Text('User     '), sg.InputText(cred["user"])],[sg.Text('Password'), sg.InputText(cred["psw"])],
               [sg.Button('Modifica'),sg.Button('Elimina')] ]

    global crypto_psw
    
    #get password
    dialog = sg.Window('Modifica credenziale', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = dialog.read()
        if event == 'Modifica':
            new_row = {}
            new_row["name"] = cred["name"]
            new_row["user"] = values[0]
            new_row["psw"] = values[1]
            stub.edit_credential(new_row,crypto_psw)
            refresh_data()
            break
        elif event == 'Elimina':
            check = stub.is_already_present(cred["name"])
            if check == True:
                stub.remove_credential(cred["name"],crypto_psw)
                refresh_data()
            break
        elif event == sg.WIN_CLOSED:	# if user closes window or clicks cancel
            break              
    dialog.close()

def open_main_window(stub):
    #add a touch of color
    sg.theme('DarkAmber')

    global crypto_psw
    launch_psw_thread()
    #crypto_psw = open_psw_dialog()

    global file_manager
    file_manager = stub
    
    stub.load_enc_file(crypto_psw)
    data = stub.credentials

    if data != '':
        window = create_table(data)

        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:	# if user closes window or clicks cancel
                break
            elif event == 'Exit': #exit button
                break
            elif event == 'Aggiungi':
                break
            elif event == 'Elimina':
                break
            elif event == '_table_':
                launch_edit_thread(data[values['_table_'][0]],stub)
                

        window.close()

    else:
        #prepare table
        headings = ['NOME', 'USER', 'PASSWORD']
        header =  [[sg.Text('  ')] + [sg.Text(h, size=(14,1)) for h in headings]]

        input_rows = []

def refresh_data():
    global table
    global file_manager

    data = []
    for i in file_manager.credentials:
        row = []
        row.append(i["name"])
        row.append(i["user"])
        row.append(i["psw"])
        data.append(row)
    table.Update(values=data)
