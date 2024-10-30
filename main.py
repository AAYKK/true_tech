import requests
import numpy as np
import time
from heapq import *
import logging 
from datetime import datetime

# Получаем текущую дату и время для создания уникального имени файла лога
log_filename = f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

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

def get_rect_num(f, r, b, l):
    if f!=0 and r!=0 and l!=0 and b!=0:
        m=0
        
    elif l==0 and f!=0 and r!=0 and b!=0:
        m = 1

    elif l!=0 and f==0 and r!=0 and b!=0:
        m = 2

    elif l!=0 and f!=0 and r==0 and b!=0:
        m = 3

    elif l!=0 and f!=0 and r!=0 and b==0:
        m = 4

    elif l==0 and f!=0 and r!=0 and b==0:
        m = 5

    elif l!=0 and f!=0 and r==0 and b==0:
        m = 6

    elif l!=0 and f==0 and r==0 and b!=0:
        m = 7

    elif l==0 and f==0 and r!=0 and b!=0:
        m = 8

    elif l==0 and f!=0 and r==0 and b!=0:
        m = 9

    elif l!=0 and f==0 and r!=0 and b==0:
        m = 10

    elif l!=0 and f==0 and r==0 and b==0:
        m = 11

    elif l==0 and f==0 and r==0 and b!=0:
        m = 12

    elif l==0 and f==0 and r!=0 and b==0:
        m = 13

    elif l==0 and f!=0 and r==0 and b==0:
        m = 14

    elif l==0 and f==0 and r==0 and b==0:
        m = 15

    return m


robot_ip=''
robot_id=''

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
        return requests.post(f'http://127.0.0.1:8801/api/v1/maze/restart',  headers=headers)
   
   
robot=Robot(headers=headers)

robot.restart()




# скан карты

robot.restart()

logging.warning(f"Начинаю скан карты: ")
while True:
    
    data, yaw = robot.s_2()
    
    f, r, b, l = data
    
    logging.info(f"{robot.x, robot.y, robot.orient} f: {f}, r: {r}, b: {b}, l: {l}, yaw: {yaw}")
    #logging.info(f"")
    
    if robot.matrix[robot.y][robot.x] == -1:
            
        f_, r_, b_, l_ = np.roll([f, r, b, l], robot.orient)
        
        m=get_rect_num(f_, r_, b_, l_)
        robot.matrix[robot.y][robot.x]=m
    
    else:
        progress=256-np.count_nonzero(robot.matrix == -1)
        
        if progress!=256-4: 
            logging.info(f"{progress}/256, new cell")
            
        else:
            break
        
    
    coords=(robot.x, robot.y)
    
    if coords in [(6,7), (6,8)]:
        if robot.orient==0:
            r=0
        
        elif robot.orient==1:
            f=0
        
        elif robot.orient==2:
            l=0
        
        elif robot.orient==3:
            b=0
            
    elif coords in [(7,6), (8,6)]:
        if robot.orient==0:
            b=0
        
        elif robot.orient==1:
            r=0
        
        elif robot.orient==2:
            f=0
        
        elif robot.orient==3:
            l=0
        
    elif coords in [(9,7), (9,8)]:
        if robot.orient==0:
            l=0
        
        elif robot.orient==1:
            b=0
        
        elif robot.orient==2:
            r=0
        
        elif robot.orient==3:
            f=0
        
    elif coords in [(7,9), (8,9)]:
        if robot.orient==0:
            f=0
        
        elif robot.orient==1:
            l=0
        
        elif robot.orient==2:
            b=0
        
        elif robot.orient==3:
            r=0


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
    
logging.warning('Скан карты закончен')

#нахождение целевой клетки
if robot.matrix[7][6] in [0,1,2,4,5,8,10,13]:
    robot.matrix[7][7]=2
    target=(7,7)
    
elif robot.matrix[8][6] in [0,1,2,4,5,8,10,13]:
    robot.matrix[8][7]=4
    target=(7,8)
        
elif robot.matrix[6][7] in [0,1,2,3,7,8,9,12]:
    robot.matrix[7][7]=1
    target=(7,7)
    
elif robot.matrix[6][8] in [0,1,2,3,7,8,9,12]:
    robot.matrix[7][8]=3
    target=(8,7)
    
elif robot.matrix[7][9] in [0,2,3,4,6,7,10,11]:
    robot.matrix[7][8]=2
    target=(8,7)
    
elif robot.matrix[8][9] in [0,2,3,4,6,7,10,11]:
    robot.matrix[8][8]=4
    target=(8,8)
    
elif robot.matrix[9][7] in [0,1,3,4,5,6,9,14]:
    robot.matrix[8][7]=1
    target=(7,8)
    
elif robot.matrix[9][8] in [0,1,3,4,5,6,9,14]:
    robot.matrix[8][8]=3
    target=(8,8)
    
logging.warning(f"target: {target}")


# Матрица смежностей

ls={}
m=robot.matrix

for y in range(len(m)):
    for x in range(len(m)):
        cell=(x,y)
        
        if m[y][x]==0:
            val=[(x-1,y), (x+1,y), (x,y-1), (x,y+1)]
        
        elif m[y][x]==1:
            val=[(x+1,y), (x,y-1), (x,y+1)]
        
        if m[y][x]==2:
            val=[(x-1,y), (x+1,y), (x,y+1)]     
        
        if m[y][x]==3:
            val=[(x-1,y), (x,y-1), (x,y+1)]
    
        if m[y][x]==4:
            val=[(x-1,y), (x+1,y), (x,y-1)]
            
        if m[y][x]==5:
            val=[(x+1,y), (x,y-1)]
            
        if m[y][x]==6:
            val=[(x-1,y), (x,y-1)]
            
        if m[y][x]==7:
            val=[(x-1,y), (x,y+1)]
            
        if m[y][x]==8:
            val=[(x+1,y), (x,y+1)]
        
        if m[y][x]==9:
            val=[(x,y-1), (x,y+1)]
        
        if m[y][x]==10:
            val=[(x-1,y), (x+1,y)]
        
        if m[y][x]==11:
            val=[(x-1,y)]
        
        if m[y][x]==12:
            val=[(x,y+1)]
            
        if m[y][x]==13:
            val=[(x+1,y)]
        
        if m[y][x]==14:
            val=[(x,y-1)]
        
        if m[y][x]==15:
            val=[]
        
        ls[(x,y)]=[(1,coords) for coords in val]


logging.info(f'матрица смежностей:\n{ls}')

#Алгоритм Дикстры
graph = ls

def dijkstra(start, goal, graph):
    queue = []
    heappush(queue, (0, start))
    
    cost_visited = {start: 0}
    visited = {start: None}

    while queue:
        cur_cost, cur_node = heappop(queue)
        
        if cur_node == goal:
            break

        next_nodes = graph[cur_node]
        
        for next_node in next_nodes:
            neigh_cost, neigh_node = next_node
            new_cost = cost_visited[cur_node] + neigh_cost

            if neigh_node not in cost_visited or new_cost < cost_visited[neigh_node]:
                heappush(queue, (new_cost, neigh_node))
                cost_visited[neigh_node] = new_cost
                visited[neigh_node] = cur_node
    return visited

start = (0, 15)
goal = target

visited = dijkstra(start, goal, graph)

cur_node = goal
move_list=[]

while cur_node != start:
    cur_node = visited[cur_node]
    move_list.append(cur_node)

move_list=move_list[::-1]+[target]


#создаем список команд

robot.restart()

command_list=[]

orient=0

def min_rotate_count_analyze(current, target):
    global orient 
    
    c_l, t_l = current, target
    c_r, t_r = current, target
    
    n1=0
    
    while t_l!=c_l:
        t_l=(t_l-1)%4
        
        n1+=1

    
    n2=0  
    while t_r!=c_r:
        t_r=(t_r+1)%4
        
        n2+=1
    
    
    if n1<=n2:
        orient=(orient+n1)%4
        return n1*['right']

    else:
        orient=(orient-n2)%4
        return n2*['left']
    
    
for i in range(len(move_list)):
    orient=orient%4
    x1,y1=move_list[i-1]
    
    x2,y2=move_list[i]
    
    if x1==x2-1 and y1==y2:
        command_list=command_list+min_rotate_count_analyze(orient,1)
        command_list.append('forward')
        
    elif x1==x2+1 and y1==y2:
        command_list=command_list+min_rotate_count_analyze(orient,3)
        command_list.append('forward')
        
    elif x1==x2 and y1==y2-1:
        command_list=command_list+min_rotate_count_analyze(orient,2)
        command_list.append('forward')
        
    elif x1==x2 and y1==y2+1:
        command_list=command_list+min_rotate_count_analyze(orient,0)
        command_list.append('forward')
    
    
logging.info(f'command_line: {command_list}')

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
    
#Исполняем список команд
robot.restart()

logging.info(f"Исполняю команды")
for command in command_list:
    
    logging.info(f"{robot.x} {robot.y} | {robot.orient}")
    if command=='left':
        robot.left()
        
    elif command=='right':
         robot.right()
        
    elif command=='forward':
        robot.forward()
        
    else:
        logging.error('error')

    