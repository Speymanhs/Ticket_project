import os
import platform
import requests
import time
import sys
import jsonspec
HOST = "localhost"
PORT = "1104"
CMD = token = ''


def __api__():
    return "http://" + HOST + ":" + PORT + "/" + CMD


def printTickets(res):
    number = res["tickets"].split('-')
    i = 0
    print("**************************************")
    while i < int(number[1]):
        block=res['block {}'.format(i)]
        print('subject :'+block['subject'])
        print('id :'+str(block['id']))
        print('status :'+block['status'])
        print('body :'+block['body'])
        if block['answer']:
            print('answer :'+block['answer'])
        else:
            print('answer :' + "")
        print('date created :' + block['sendtime'])
        time.sleep(0.2)
        print("**************************************")
        i=i+1

def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def control_panel_function():
    print("""Give an Order:
    1.Logout
    2. Send a Ticket
    3. Get Tickets as a Client
    4. Close Ticket
    5. Get Tickets as an Administrator
    6. Respond to Ticket
    7. Change a Ticket Status
    8. Change Access to Administrator
    9. Exit
    """)

while True:
    clear()
    flag = 0
    print("""WELCOME TO TICKET CLIENT
    Please Choose What You Want To Do :
    1. Login
    2. Signup
    3. Exit
    """)
    status = input()
    if status == 1:
        clear()
        while True:
            if flag == 1:
                break
            print("username : \n")
            username = input()
            print("password : \n")
            password = input()
            CMD = "login"
            r = requests.post(__api__(), data={'username': username, 'password': password}).json()
            print(r['message'] + '\n')
            if r['code'] == '200':
                clear()
                api = r['api']
                time.sleep(2)
            else:
                clear()
                time.sleep(2)
                break
            while True:
                clear()
                control_panel_function()
                order = input()
                if order == 1:
                    clear()
                    CMD = "logout"
                    data = requests.post(__api__(), data={'username': username, 'password': password}).json()
                    print(data['message'] + '\n')
                    time.sleep(0.5)
                    flag = 1
                    break
                if order == 2:
                    clear()
                    CMD = "sendticket"
                    subject = input("Enter Subject: ")
                    body = input("Enter Body: ")
                    data = requests.post(__api__(), data={'api': api, 'body': body, 'subject': subject}).json()
                    print(data['message'] + '\n')
                    time.sleep(0.5)
                if order == 3:
                    clear()
                    CMD = "getticketcli"
                    data = requests.post(__api__(), params={'api': api}).json()
                    if data['code'] == '200':
                        printTickets(data)
                    else:
                        print(data['message']+'\n')
                    time.sleep(0.5)
                if order == 4:
                    clear()
                    my_id = input("Ticket Id : ")
                    CMD = "closeticket"
                    data = requests.post(__api__(), data={'api': api, 'id': my_id}).json()

                    print(data['message']+'\n')
                    time.sleep(0.5)
                if order == 5:
                    clear()
                    CMD = "getticketmod"
                    data = requests.post(__api__(), params={'api': api}).json()

                    if data['code'] == '200':
                        printTickets(data)
                    else:
                        print(data['message'] + '\n')
                    time.sleep(0.5)
                if order == 6:
                    clear()
                    CMD = "restoticketmod"
                    answer = input("Enter Answer: ")
                    my_id = input("Enter Ticket ID:")
                    data = requests.post(__api__(), data={'api': api, 'id': my_id, 'answer': answer}).json()

                    print(data['message']+'\n')
                    time.sleep(0.5)
                if order == 7:
                    clear()
                    CMD = "changestatus"
                    status = input("Status(Please enter open or closed or inprogress: ")
                    my_id = input("Enter Ticket id: ")
                    data = requests.post(__api__(), data={'api': api, 'id': my_id, 'status': status}).json()
                    print(data['message']+'\n')
                    time.sleep(0.5)
                if order == 8:
                    clear()
                    CMD = "changeaccess"
                    dataBaseUser = input("Enter the username of the database to gain admin access: ")
                    dataBasePass = input("Enter the password of the database to gain admin access: ")
                    data = requests.post(__api__(), data={'api': api, 'dataBaseUser': dataBaseUser, 'dataBasePass': dataBasePass}).json()
                    print(data['message']+'\n')
                    time.sleep(0.5)
                if order == 9:
                    sys.exit()
    elif status == 2:
        clear()
        while True:
            CMD = "signup"
            username = input("Enter Username: ")
            password = input("Enter Password: ")
            clear()
            data = requests.post(__api__(), data={'username': username, 'password': password}).json()
            print(data['message']+'\n')
            if str(data['code']) == "200":
                time.sleep(1)
                break
            else:
                time.sleep(2)
                clear()
    elif status == 3:
        sys.exit()
    else:
        print("Please enter a valid number!\n")