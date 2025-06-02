import asyncio
import pygame
import random
import math
import os
from assets.imageload import imageloadfunc, imagelist, imagenum
pygame.init()
from pygame import mixer
mixer.init()

text_font = pygame.font.Font(None, 30)

screen_info = pygame.display.Info()
screen_width = 1440 #screen_info.current_w
screen_height = 1080 #screen_info.current_h
screen = pygame.display.set_mode((screen_width, screen_height))

#base_surface = pygame.Surface((screen_width, screen_height))
#screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

pygame.display.set_caption("Gemo")
clock = pygame.time.Clock()

def listen_for_quit():
  running = True
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
      running = False
  return running

def draw_text(text, font, text_col, x, y, size = 32):
  font = pygame.font.SysFont(None, size)
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

def listen_for_play():
  gamestart = "NO"
  for event in pygame.event.get():
    if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
      gamestart = "PLAY"
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
      gamestart = "SETTING"
  return gamestart

def damage_block(xpos, ypos, xsize, ysize, loselife, player, progression, danger_color):
  if progression >= xpos-2500 and progression <= xpos+5000:
    DamageBlock = pygame.Rect(xpos - progression, ypos, xsize, ysize)
    pygame.draw.rect(screen, (danger_color), DamageBlock)
    if player.colliderect(DamageBlock):
      loselife = True
  return loselife

def checkpoint(xpos, ypos, xsize, ysize, Player1_Checkpoint, player, progression, yellow_color):
  if progression >= xpos-2500 and progression <= xpos+5000:
    DamageBlock = pygame.Rect(xpos - progression, ypos, xsize, ysize)
    pygame.draw.rect(screen, (yellow_color), DamageBlock)
    if player.colliderect(DamageBlock):
      Player1_Checkpoint = progression - 50
  return Player1_Checkpoint

def blue_block(xpos, ypos, xsize, ysize, loselife, player, progression, Player1_IsMoving, blue_color):
  if progression >= xpos-2500 and progression <= xpos+5000:
    DamageBlock = pygame.Rect(xpos - progression, ypos, xsize, ysize)
    pygame.draw.rect(screen, (blue_color), DamageBlock)
    if player.colliderect(DamageBlock) and Player1_IsMoving:
      loselife = True
  return loselife

def booster_block(xpos, ypos, xsize, ysize, AirResistance, FallSpeed, player, progression, green_color):
  if progression >= xpos-2500 and progression <= xpos+5000:
    DamageBlock = pygame.Rect(xpos - progression, ypos, xsize, ysize)
    pygame.draw.rect(screen, (green_color), DamageBlock)
    if player.colliderect(DamageBlock):
      soundplay('Sounds/regbounce.ogg')
      AirResistance = True
      FallSpeed = -30
  return AirResistance, FallSpeed

def temp_booster_block(xpos, ypos, xsize, ysize, AirResistance, FallSpeed, last_temp, player, temp_appear, progression, green_color2):
  if progression >= xpos-2500 and progression <= xpos+5000 and not temp_appear in last_temp:
    DamageBlock = pygame.Rect(xpos - progression, ypos, xsize, ysize)
    pygame.draw.rect(screen, (green_color2), DamageBlock)
    if player.colliderect(DamageBlock):
      soundplay('Sounds/bounce.ogg')
      last_temp.append(temp_appear)
      AirResistance = True
      FallSpeed = -30
  return AirResistance, FallSpeed, last_temp

def rush_block(xpos, ypos, xsize, ysize, Player1_MoveBy, player, progression, cyan_color, rush_appear, last_rush):
  if progression >= xpos-2500 and progression <= xpos+5000 and not rush_appear in last_rush:
    DamageBlock = pygame.Rect(xpos - progression, ypos, xsize, ysize)
    pygame.draw.rect(screen, (cyan_color), DamageBlock)
    if player.colliderect(DamageBlock):
      soundplay('Sounds/regbounce.ogg')
      last_rush.append(rush_appear)
      Player1_MoveBy = 10
  return Player1_MoveBy, last_rush

def victory_block(xpos, ypos, xsize, ysize, levelnum, layout, backlayout, player, progression, purple_color, victory, nextbool):
  if progression >= xpos-2500 and progression <= xpos+5000:
    DamageBlock = pygame.Rect(xpos - progression, ypos, xsize, ysize)
    pygame.draw.rect(screen, (purple_color), DamageBlock)
    if player.colliderect(DamageBlock):
      try:
        layout, levelnum, backlayout = nextlevel(levelnum)
        nextbool = True
      except:
        victory = True
  return layout, levelnum, nextbool, backlayout, victory

def background_block(xpos, ypos, xsize, ysize, color, closeness, progression):
  if progression >= xpos-2500*closeness and progression <= xpos+5000*closeness:
    DamageBlock = pygame.Rect(xpos - progression/closeness, ypos, xsize, ysize)
    pygame.draw.rect(screen, (color), DamageBlock)

def menu_block(xpos, ypos, xsize, ysize, color):
  DamageBlock = pygame.Rect(xpos, ypos, xsize, ysize)
  pygame.draw.rect(screen, (color), DamageBlock)
  return DamageBlock

def speedReverse(Speed):
  Speed = -Speed
  return Speed

def healthbar(xpos, ypos, xsize, ysize, health, backblock_color2, danger_color, green_color):
  backbar = pygame.Rect(xpos-3, ypos- 4, xsize*1.03, ysize*1.15)
  redbar = pygame.Rect(xpos, ypos, xsize, ysize)
  greenbar = pygame.Rect(xpos, ypos, health*2, ysize)
  pygame.draw.rect(screen, (backblock_color2), backbar)
  pygame.draw.rect(screen, (danger_color), redbar)
  pygame.draw.rect(screen, (green_color), greenbar)

def Ground_block(xpos, ypos, xsize, ysize, touchingGround, progression, Player1_MoveBy, FallSpeed, AirResistance, player, Player1_y1, Player1_SpeedCap, tilesize, block1_color):
  #Ground Blocks that you can stand on similar to floor. Some even have horizontal collison to not let player walk thorugh blocks
  if progression >= xpos-2500 and progression <= xpos+5000:
    GroundBlock = pygame.Rect(xpos - progression, ypos, xsize, ysize)
    pygame.draw.rect(screen, (block1_color), GroundBlock)
    if player.colliderect(GroundBlock):
      if Player1_y1 > ypos+ysize-20:
        FallSpeed = 0.1
      else:
        if AirResistance > -1 and not AirResistance:
          touchingGround = True
        locator = xpos-progression-375+xsize
        #detect if player is at y level and moving against block horizontally left or right
        #bouncing from floor
        if FallSpeed > 10:
          touchingGround = False
          AirResistance = True
          FallSpeed = speedReverse(FallSpeed) / 1.5
        #bouncing off walls
        elif math.ceil(Player1_y1) + tilesize - 10 >= ypos and locator > 100:
          #print(f"Left: {locator}")
          progression -= Player1_SpeedCap*2
          Player1_MoveBy = speedReverse(Player1_MoveBy)
        elif math.ceil(Player1_y1) + tilesize - 10 >= ypos and locator > 0:
          #print(f"Right: {locator}")
          progression += Player1_SpeedCap*2
          Player1_MoveBy = speedReverse(Player1_MoveBy)
  return touchingGround, progression, Player1_MoveBy, FallSpeed, AirResistance

def Moveby(Player1_MoveBy, Player1_IsMoving, Player1_SpeedCap, Player1_Speed):
  if Player1_MoveBy < Player1_SpeedCap:
    Player1_MoveBy += Player1_Speed
  elif Player1_MoveBy > Player1_SpeedCap:
    Player1_MoveBy = Player1_SpeedCap
  Player1_MoveBy += Player1_Speed
  Player1_IsMoving = True
  return Player1_MoveBy, Player1_IsMoving

def movement(PlayerDirection, Player1_MoveBy, progression, Player1_IsMoving, Player1_SpeedCap, Player1_Speed):
  #horizontal movement with momentium
  keys_down = pygame.key.get_pressed()
  if keys_down[pygame.K_RIGHT] and Player1_MoveBy <= Player1_SpeedCap+1:
    if PlayerDirection == "Left":
      Player1_MoveBy = 0
    PlayerDirection = "Right"
    Player1_MoveBy, Player1_IsMoving = Moveby(Player1_MoveBy, Player1_IsMoving, Player1_SpeedCap, Player1_Speed)
    
  elif keys_down[pygame.K_LEFT] and Player1_MoveBy <= Player1_SpeedCap+1:
    if PlayerDirection == "Right":
      Player1_MoveBy = 0
    PlayerDirection = "Left"
    Player1_MoveBy, Player1_IsMoving = Moveby(Player1_MoveBy, Player1_IsMoving, Player1_SpeedCap, Player1_Speed)
    
  elif Player1_MoveBy > 0:
    Player1_MoveBy -= Player1_Speed*2
    if Player1_MoveBy < 0:
      Player1_MoveBy = 0
  if Player1_MoveBy < 0:
    Player1_MoveBy *= 0.96
  if PlayerDirection == "Right":
    progression += Player1_MoveBy
    progression += Player1_MoveBy
  elif PlayerDirection == "Left":
    progression -= Player1_MoveBy
    progression -= Player1_MoveBy
  if Player1_MoveBy > Player1_SpeedCap:
    Player1_MoveBy -= 0.01
  return PlayerDirection, Player1_MoveBy, progression

def jump(FallSpeed, AirResistance, Player1_y1, BlockPath, BlockPathDir, JumpHeight, touchingGround):
  keys_down = pygame.key.get_pressed()
  if keys_down[pygame.K_SPACE] and touchingGround == True:
    soundplay('Sounds/whoosh.ogg')
    FallSpeed = -JumpHeight
    AirResistance = True
    Player1_y1 -= 10
  elif touchingGround == False:
    Player1_y1 += FallSpeed
    if AirResistance == True:
      Player1_IsMoving = True
      FallSpeed *= 0.9
      if FallSpeed >= -0.5:
        AirResistance = False
        FallSpeed = 0.1
    elif AirResistance == False:
      FallSpeed = FallSpeed * 1.08
  elif touchingGround == True:
    FallSpeed = 0.1

  if BlockPath >= 0:
    BlockPathDir = "DOWN"
  elif BlockPath <= -250:
    BlockPathDir = "UP"
  if BlockPathDir == "DOWN":
    BlockPath -= 1
  elif BlockPathDir == "UP":
    BlockPath += 1
  return FallSpeed, AirResistance, Player1_y1, BlockPath, BlockPathDir

def player_face(facemove, facemoveY, Player1_x1, Player1_y1, PlayerDirection, FallSpeed):
  face_X = Player1_x1+facemove
  face_Y = Player1_y1+facemoveY
  Player1_Face = "0_0"
  if PlayerDirection == "Left":
    if facemove > 0:
      facemove -= 1
  elif PlayerDirection == "Right":
    if facemove < 18:
      facemove += 1

  if FallSpeed < 0:
    if facemoveY < 30:
      facemoveY += 1
  elif FallSpeed > 1:
    if facemoveY > 0:
      facemoveY -= 1
      Player1_Face = ">_<"

  return Player1_Face, face_X, face_Y, facemove, facemoveY

def damage(loselife, Player1_y1, progression, PlayerLives, canbehit, last_temp, Player1_Checkpoint, Deaths, last_rush, FallSpeed, Player1_MoveBy):
  #remove health on touch of damage block
  if loselife and canbehit:
    soundplay('Sounds/hit1.ogg')
    PlayerLives -= 1
    loselife = False
    canbehit = False
  if PlayerLives <= 0:
    PlayerLives = 5
    Player1_y1 = 500
    FallSpeed = 0.1
    Player1_MoveBy = 0.05
    progression = Player1_Checkpoint
    Deaths += 1
    last_temp = []
    last_rush = []
  return loselife, Player1_y1, progression, PlayerLives, canbehit, last_temp, Deaths, last_rush, FallSpeed, Player1_MoveBy

def hitrestore(canbehit = False, counter = 0, block1_color = (255, 255, 255)):
  if canbehit == False:
    block1_color = (205, 205, 205)
    counter += 1
    if counter > 120:
      canbehit = True
      counter = 0
      block1_color = (255, 255, 255)
  return canbehit, counter, block1_color

def fallback(Player1_y1, PlayerLives, FallSpeed, AirResistance, canbehit = True):
  #bring player back after falling out of world
  if Player1_y1 >= 800:
    soundplay('Sounds/hit2.ogg')
    Player1_y1 = 800
    PlayerLives -= 2
    FallSpeed = -60
    AirResistance = True
    canbehit = False
  return Player1_y1, PlayerLives, FallSpeed, AirResistance, canbehit

def commands(progression, Falling, FallSpeed, AirResistance, Player1_y1, touchingGround, levelnum, cheats = True):
  #commands for testing and stuff
  if cheats:
    keys_down = pygame.key.get_pressed()
    if keys_down[pygame.K_c] and keys_down[pygame.K_e]:
      progression = int(input("What Progression?: "))

    elif keys_down[pygame.K_c] and keys_down[pygame.K_t]:
      levelnum = int(input("What Level?: "))

    elif keys_down[pygame.K_c] and keys_down[pygame.K_r]:
      if Falling == True:
        Falling = False
      elif Falling == False:
        Falling = True

    elif keys_down[pygame.K_c] and keys_down[pygame.K_f]:
      print(f"FallSpeed: {FallSpeed}")
      print(f"Air Resistance{AirResistance}")
      print(f"Player Y{Player1_y1}")

    if Falling == False or touchingGround == True and AirResistance == False:
      FallSpeed = 0.1

  return progression, Falling, levelinfo(levelnum)

def timer2(GameTimeUp, GameTime):
  #time variable
  GameTimeUp += 1
  if GameTimeUp >= 45:
    GameTimeUp = 0
    GameTime += 1
  return GameTimeUp, GameTime

def levelinfo(level = 1):
  try:
    with open(f"Levels/Level{level}.txt", 'r') as levellayout:
      return levellayout.readlines()
  except:
    print("failed")

def nextlevel(levelnum = 1, backlayout = []):
  levelnum += 1
  musicchose(levelnum)
  layout = levelinfo(levelnum)
  for i in layout:
    backlayout.append(random.randint(1,15))
  return layout, levelnum, backlayout

def musicchose(lvl = 1):
  with open('assets/MusicLvl', 'r') as f:
    f = f.readlines()
    for i in f:
      i = i.split()
      if int(i[0]) == lvl:
        musicloop(str(i[1]))

def startingstats():
  PlayerLives = 5
  Player1_x1 = 400
  Player1_y1 = 500
  Player1_Speed = 0.05
  Player1_SpeedCap = 3
  Player1_MoveBy = 0
  Player1_Checkpoint = 0
  PlayerDirection = "None"
  JumpHeight = 10
  progression = 0
  return PlayerLives, Player1_x1, Player1_y1, Player1_Speed, Player1_SpeedCap, Player1_MoveBy, Player1_Checkpoint, PlayerDirection, JumpHeight, progression

songc = ''
def musicloop(music = 'Music/Build.mp3'):
  global songc
  if not music == songc:
    stop_music()
    songc = music
    mixer.music.load(music)
    mixer.music.play(loops=-1)

def stop_music():
    mixer.music.stop()

def soundplay(sound):
  s = mixer.Sound(sound)
  s.play()
  pass

def filechildstealer(parent):
  #steals all children under folder or file to take to caller
  children = [f for f in os.listdir(parent)] #if os.path.isfile(os.path.join(parent, f))
  return children

def dialogue(dial, name, img, color, images):
  try:
    num = imagenum(img)
    imp = images[num]
    imp = pygame.transform.scale(imp, (160, 160))
    screen.blit(imp, (75, 870))
  finally:
    draw_text((dial), text_font, (color), 300, 900, 50)

def activatedialogue(levelnum, dialoguelist, progression, block1_color, dialoguepos, images):
  #find which dialogue to use
  for i in dialoguepos:
    i = i.split()
    try:
      if levelnum == int(i[0]): 
        if progression > int(i[1]) and progression < int(i[2]):
          dialogue(dialoguelist[int(i[3])], 'Shia', str(i[4]), block1_color, images)
    except:
      i=i

def Homepage(page, block1_color, backblock_color2):
  if page == "Home":
    start_button = menu_block(500, 500, 440, 100, block1_color)
    draw_text(("Play"), text_font, (backblock_color2), 620, 500, 140)
    return start_button
  else:
    pass

def Levelpage(page, block1_color, backblock_color2):
  if page == "Levels":
    back_button = menu_block(500, 300, 440, 100, block1_color)
    draw_text(("Back"), text_font, (backblock_color2), 620, 300, 140)

    LevelList = (filechildstealer("Levels"))
    LevelListBlocks = []
    LevelNum = 1
    X_in = 200
    Y_in = 500
    for i in LevelList:
      LevelListBlocks.append(menu_block(X_in, Y_in, 100, 50, block1_color))
      draw_text((str(LevelNum)), text_font, (backblock_color2), X_in+40, Y_in+10, 50)
      X_in += 150
      LevelNum += 1
      Y_in = 500 + 100*(int(LevelNum/7.1))
      if X_in > 1100:
        X_in = 200
    return LevelListBlocks, back_button
  else:
    return None, None

def menubuttoncheck(page, levelnum, menu, level_buttons, running, start_button, back_button):
  #mouce inputs
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    elif event.type == pygame.MOUSEBUTTONDOWN:
      if page == "Home":
        if start_button.collidepoint(event.pos):
          page = "Levels"
      elif page == "Levels":
        if back_button.collidepoint(event.pos):
          page = "Home"

        LevelnumChoice = 1
        for i in level_buttons:
          if i.collidepoint(event.pos):
            menu = False
            levelnum = int(LevelnumChoice)
          LevelnumChoice += 1
  return page, levelnum, menu, running


async def main():
  images = imagelist()

  keys_down = pygame.key.get_pressed()
  line_color = (255, 255, 255)
  block1_color = (255, 255, 255)
  backblock_color = (128, 128, 128)
  backblock_color2 = (98, 98, 98)
  danger_color = (255, 0, 0)
  blue_color = (0, 0, 255)
  yellow_color = (255, 255, 0)
  green_color = (0, 255, 0)
  green_color2 = (60, 205, 60)
  purple_color = (255, 0, 255)
  cyan_color = (60, 60, 155)
  text_col = (255, 255, 255)
  back_color = (0, 0, 0)

  levelnum = 1 #level to start at
  running = True
  #MENU SCREEN
  menu = True
  page = "Home"
  while running == True and menu == True:
    #running = listen_for_quit()
    screen.fill(back_color)
    #pages
    start_button = Homepage(page, block1_color, backblock_color2)
    level_buttons, level_back_button = Levelpage(page, block1_color, backblock_color2)
    page, levelnum, menu, running = menubuttoncheck(page, levelnum, menu, level_buttons, running, start_button, level_back_button)
    
    musicloop('Music/Drunk.mp3')
    pygame.display.flip()
    clock.tick(60)
    await asyncio.sleep(0)


  tilesize = 50
  progression = 0
  AirResistance = False
  Falling = True
  Player1_IsMoving = False
  touchingGround = True
  BlockPath = 0
  BlockPathDir = "UP"
  facemove = 0
  facemoveY = 0
  FallSpeed = 0.1
  GameTime = 0
  GameTimeUp = 0

  PlayerLives, Player1_x1, Player1_y1, Player1_Speed, Player1_SpeedCap, Player1_MoveBy, Player1_Checkpoint, PlayerDirection, JumpHeight, progression = startingstats()
  last_temp = []
  last_rush = []

  with open("Dialogue/Main.txt", 'r') as f:
    dialoguelist = f.readlines()

  with open("Dialogue/Pos.txt", 'r') as f:
    dialoguepos = f.readlines()

  layout, levelnum, backlayout = nextlevel(levelnum-1)
  #layout = levelinfo(levelnum)
  #musicloop()
  canbehit = True
  canbehitcounter = 0
  Player1_IsMoving = False
  Deaths = 0
  victory = False
  starting_level = levelnum

  #Start Game
  while running == True:
    
    running = listen_for_quit()
    screen.fill(back_color)

    
    if touchingGround == True:
      touchingGround = False

    loselife = False
    temp_appear = 0
    rush_appear = 0

    #player info
    player = pygame.Rect(Player1_x1, Player1_y1, tilesize, tilesize)

    #dialogue boxes
    pygame.draw.rect(screen, (backblock_color), pygame.Rect(40, 855, 220, 195))
    pygame.draw.rect(screen, ((0,0,0)), pygame.Rect(50, 865, 200, 175))
    pygame.draw.rect(screen, (backblock_color2), pygame.Rect(270, 855, 1150, 195))
    
    if victory == False:
      #load background
      blockplaceX = 0
      for i in backlayout:
        blockplaceY = 800
        if i == 1:
          background_block(blockplaceX, blockplaceY-750, tilesize*8, tilesize*16, (50, 50, 50), 4, progression)
        elif i == 2:
          background_block(blockplaceX, blockplaceY-250, tilesize*4, tilesize*6, backblock_color, 1.5, progression)
        elif i == 3:
          background_block(blockplaceX, blockplaceY-450, tilesize*7, tilesize*10, backblock_color2, 2, progression)
        blockplaceX += tilesize

      #load level
      blockplaceX = 0
      for i in layout:
        blockplaceY = 800
        for l in i:
          #regular blocks load
          if str(l) == '1':
            touchingGround, progression, Player1_MoveBy, FallSpeed, AirResistance = Ground_block(blockplaceX, blockplaceY, tilesize, tilesize, touchingGround, progression, Player1_MoveBy, FallSpeed, AirResistance, player, Player1_y1, Player1_SpeedCap, tilesize, block1_color)
          elif str(l) == '2':
            loselife = damage_block(blockplaceX, blockplaceY, tilesize, tilesize, loselife, player, progression, danger_color)
          elif str(l) == '3':
            Player1_Checkpoint = checkpoint(blockplaceX, blockplaceY, tilesize, tilesize, Player1_Checkpoint, player, progression, yellow_color)
          elif str(l) == '4':
            layout, levelnum, nextbool, backlayout, victory = victory_block(blockplaceX, blockplaceY, tilesize, tilesize, levelnum, layout, backlayout, player, progression, purple_color, victory, False)
            if nextbool:
              PlayerLives, Player1_x1, Player1_y1, Player1_Speed, Player1_SpeedCap, Player1_MoveBy, Player1_Checkpoint, PlayerDirection, JumpHeight, progression = startingstats()
              last_temp = []
              last_rush = []
          elif str(l) == '5':
            AirResistance, FallSpeed = booster_block(blockplaceX, blockplaceY, tilesize, tilesize, AirResistance, FallSpeed, player, progression, green_color)
          elif str(l) == '6':
            temp_appear += 1
            AirResistance, FallSpeed, last_temp = temp_booster_block(blockplaceX, blockplaceY, tilesize, tilesize, AirResistance, FallSpeed, last_temp, player, temp_appear, progression, green_color2)
          elif str(l) == '7':
            rush_appear += 1
            Player1_MoveBy, last_rush = rush_block(blockplaceX, blockplaceY, tilesize, tilesize, Player1_MoveBy, player, progression, cyan_color, rush_appear, last_rush)

          #text loads
          elif str(l) == 'a':
            draw_text(("Red Blocks harm you"), text_font, (danger_color), blockplaceX-progression, blockplaceY)
          elif str(l) == 'b':
            draw_text(("Yellow are checkpoints"), text_font, (yellow_color), blockplaceX-progression, blockplaceY)
          elif str(l) == 'c':
            draw_text(("You can jump on walls"), text_font, (block1_color), blockplaceX-progression, blockplaceY)
          elif str(l) == 'd':
            draw_text(("Green launches you upwards"), text_font, (green_color), blockplaceX-progression, blockplaceY)
          elif str(l) == 'e':
            draw_text(("The End"), text_font, (block1_color), blockplaceX-progression, blockplaceY)
          blockplaceY -= tilesize
        blockplaceX += tilesize
        

      activatedialogue(levelnum, dialoguelist, progression, block1_color, dialoguepos, images)

      #Player model square
      pygame.draw.rect(screen, (block1_color), player)
      Player1_Face, face_X, face_Y, facemove, facemoveY = player_face(facemove, facemoveY, Player1_x1, Player1_y1, PlayerDirection, FallSpeed)
      draw_text((Player1_Face), text_font, (purple_color), face_X, face_Y)
      
      #labels and displayed variables
      healthbar(20, 20, 200, 50, PlayerLives*20, backblock_color2, danger_color, green_color)
      draw_text((f"Health: {PlayerLives} / 5"), text_font, (text_col), 40, 40)
      draw_text((f"Progression: {round(progression)}"), text_font, (text_col), 20, 80)
      draw_text((f"Time: {GameTime}"), text_font, (text_col), 20, 100)
      draw_text((f"Deaths: {Deaths}"), text_font, (text_col), 20, 120)
      #draw_text((f"Fallspeed: {FallSpeed}"), text_font, (text_col), 400, 20)
      #draw_text((f"Player Y1: {Player1_y1}"), text_font, (text_col), 400, 40)
      #draw_text((f"Speed: {round(Player1_MoveBy)}"), text_font, (text_col), 20, 140)

      #controls
      PlayerDirection, Player1_MoveBy, progression = movement(PlayerDirection, Player1_MoveBy, progression, Player1_IsMoving, Player1_SpeedCap, Player1_Speed)
      FallSpeed, AirResistance, Player1_y1, BlockPath, BlockPathDir = jump(FallSpeed, AirResistance, Player1_y1, BlockPath, BlockPathDir, JumpHeight, touchingGround)

      #game mechanics
      loselife, Player1_y1, progression, PlayerLives, canbehit, last_temp, Deaths, last_rush, FallSpeed, Player1_MoveBy = damage(loselife, Player1_y1, progression, PlayerLives, canbehit, last_temp, Player1_Checkpoint, Deaths, last_rush, FallSpeed, Player1_MoveBy)
      Player1_y1, PlayerLives, FallSpeed, AirResistance, canbehit = fallback(Player1_y1, PlayerLives, FallSpeed, AirResistance, canbehit)
      canbehit, canbehitcounter, block1_color = hitrestore(canbehit, canbehitcounter, block1_color)
      #progression, Falling, layout = commands(progression, Falling, FallSpeed, AirResistance, Player1_y1, touchingGround, levelnum)
      GameTimeUp, GameTime = timer2(GameTimeUp, GameTime)

    else:
      draw_text(("Victory"), text_font, (text_col), 20, 100, 178)
      draw_text((f"Deaths: {Deaths}"), text_font, (text_col), 20, 300, 58)
      draw_text((f"Time: {GameTime}"), text_font, (text_col), 20, 400, 58)
      draw_text((f"Starting Level: {starting_level}"), text_font, (text_col), 20, 500, 58)
    
    pygame.display.flip()
    clock.tick(60)
    await asyncio.sleep(0)

  #end game on victory or esc quit
  if running == False:
    pygame.display.quit()


asyncio.run(main())