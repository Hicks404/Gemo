import os
import pygame

def filechildstealer(parent):
  #steals all children under folder or file to take to caller
  children = [f for f in os.listdir(parent)] #if os.path.isfile(os.path.join(parent, f))
  return children

def imageloadfunc(img):
    img_path = os.path.join("assets", img)
    image = pygame.image.load(img_path).convert_alpha()
    #image = pygame.image.load('Colo1.png').convert_alpha()
    return image

def imagelist():
    fi = open('assets/preload.txt', 'r')
    fi = fi.readlines()
    imageList = []
    for i in fi:
       i = i.strip()
       image = pygame.image.load(f"assets/PNG/{i}")
       imageList.append(image)
       #print(i)
    return imageList

def imagenum(image):
  image = image.replace('PNG','png')
  f = open('assets/preload.txt', 'r')
  f = f.readlines()
  f = [item.strip() for item in f]
  num = 0
  found = False
  while found == False:
    if f[num].lower() == image.lower():
        found = True
    else:
        num += 1
  return num
   
#print(imagenum('Shia16.PNG'))
#print(imagelist())