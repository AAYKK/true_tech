import requests
import numpy as np
import time
from heapq import *
import logging 
from datetime import datetime
from config import robot_ip, robot_id

# Получаем текущую дату и время для создания уникального имени файла лога
log_filename = f"log_walls_var_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

# Настраиваем логгер
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


headers={
        'content-type': 'application/json',
        }

d_move=150
d_rotate=95

STOP_TIME=1


class Robot:
    def __init__(self, headers:dict):
        self.headers=headers
        self.orient=0
        self.x, self.y = 0, 15
        self.matrix=np.full((16,16), -1)


    def s_2(self):
        
        json_data = {
            'id': robot_id,
            'type':'all'
            }

        response=requests.post(f'http://{robot_ip}/sensor', headers=headers, json=json_data).json()
           
        data = np.round((np.array([response['laser']['4'], response['laser']['5'], response['laser']['1'], response['laser']['2']]))/150)
        time.sleep(0.05)
        
        yaw=response['imu']['yaw']
        
        return data, yaw
    
    def forward(self, d=d_move):
        
        json_data = {
            'id': robot_id,
            'direction': 'forward',
            'len': d
            }

        with requests.put(f'http://{robot_ip}/move', headers=headers, json=json_data):
            #print(self.x, self.y, self.orient)
            
            if self.orient%4==0:
                #print(f"-y")
                self.y-=1
            
            elif self.orient%4==1:
                #print(f"+x")
                self.x+=1
            
            elif self.orient%4==2:
                #print(f"+y")
                self.y+=1
            
            elif self.orient%4==3:
                #print(f"-x")
                self.x-=1
                
            time.sleep(STOP_TIME)
        
    def left(self, d=d_rotate):
        
        json_data = {
            'id': robot_id,
            'direction': 'left',
            'len': d
            }
        
        requests.put(f'http://{robot_ip}/move', headers=headers, json=json_data)
        self.orient=(self.orient-1)%4
        time.sleep(STOP_TIME)
        
    def right(self, d=d_rotate):
        
        json_data = {
            'id': robot_id,
            'direction': 'right',
            'len': d
            }
        
        requests.put(f'http://{robot_ip}/move', headers=headers, json=json_data)
        self.orient=(self.orient+1)%4
        time.sleep(STOP_TIME)
        
    def back(self, d=d_move):
        
        json_data = {
            'id': robot_id,
            'direction': 'backward',
            'len': d
            }
        
        with requests.put(f'http://{robot_ip}/move', headers=headers, json=json_data):
            if self.orient%4==0:
                self.y+=1
            
            elif self.orient%4==1:
                self.x-=1
            
            elif self.orient%4==2:
                self.y-=1
            
            elif self.orient%4==3:
                self.x+=1
                
            time.sleep(STOP_TIME)

    def restart(self):
        self.__init__(self.headers)
        
   
   
robot=Robot(headers=headers)

robot.restart()




# скан карты

robot.restart()

logging.warning(f"Начинаю по левой стенке")
while True:
    
    data,yaw = robot.s_2()
    
    f, r, b, l = data
    
    logging.info(f"{robot.x, robot.y, robot.orient} f: {f}, r: {r}, b: {b}, l: {l}, yaw: {yaw}")

    coords=(robot.x, robot.y)
    
    if coords in [(7,7), (7,8), (8,7), (8,8)]:
        break
    
    if f!=0 and l==0:
        robot.forward()
        
    elif f==0 and l==0:
        robot.right()
        
    elif f==0 and l!=0:
        robot.left()
        robot.forward()

    elif f!=0 and l!=0:
        robot.left()
        robot.forward()

while True:
    inp=input('Введите команду:\n11-начать новую попытку\n12завершить испытание\n')
    
    print(f"Вы ввели: {inp}\n")
    if inp=='11':
        print(f"Начинаю новую попытку")
        break
    
    elif inp=='12':
        raise KeyboardInterrupt
    
    else:
        continue

robot.restart()


logging.warning(f"Начинаю по правой стенке")
while True:
    
    data,yaw = robot.s_2()
    
    f, r, b, l = data
    
    logging.info(f"{robot.x, robot.y, robot.orient} f: {f}, r: {r}, b: {b}, l: {l}, yaw: {yaw}")

    coords=(robot.x, robot.y)
    
    if coords in [(7,7), (7,8), (8,7), (8,8)]:
        break
    
    if f!=0 and r==0:
        robot.forward()
        
    elif f==0 and r==0:
        robot.left()
        
    elif f==0 and r!=0:
        robot.right()
        robot.forward()

    elif f!=0 and r!=0:
        robot.right()
        robot.forward()
        
    
