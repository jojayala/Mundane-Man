# Sprites and background from Spasman's Boring Man OTSC
# Sounds from http://soundbible.com/1953-Neck-Snap.html and https://www.youtube.com/watch?v=z0aOffHrTac&list=PLX5fBCkxJmm1fPSqgn9gyR3qih8yYLvMj&index=7
# Music from https://www.royaltyfree-music.com/free-music-download
# Framework from https://github.com/LBPeraza/Pygame-Asteroids/blob/master/Asteroids/pygamegame.py


import pygame, random
from math import degrees, pi, atan2, cos, radians, sin


# From https://www.youtube.com/watch?v=5q7tmIlXROg&list=PLX5fBCkxJmm1fPSqgn9gyR3qih8yYLvMj&index=5
def load_map(path):
    f = open(path + '.txt','r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data: game_map.append(list(row))
    return game_map

game_map = load_map('map')
scroll = [0,0]
pygame.mixer.pre_init(44100, -16, 2, 512)
level2 = False


class Tiles(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Tiles, self).__init__()
        self.loc = [x, y]
        self.rect = pygame.Rect(self.loc[0], self.loc[1], 128, 128)


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Spike, self).__init__()
        self.loc = [x, y]
        self.rect = pygame.Rect(self.loc[0], self.loc[1]+24*4, 32*4, 16.4*2)      
    

class Target(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Target, self).__init__()
        self.loc = [x, y]
        self.rect = pygame.Rect(self.loc[0],self.loc[1],128,128)


class PygameGame(object):

    def init(self):
        self.explosionCountWidth = 0
        self.explosionCountHeight = 0
        self.leftSlope = pygame.image.load('images\city_rampB.png').convert()
        self.rightSlope = pygame.image.load('images\city_rampA.png').convert()
        self.leftSlope.set_colorkey((255,255,255))
        self.rightSlope.set_colorkey((255,255,255))
        self.explosionImage = SpriteSheet('images\explosion.png')
        pygame.mixer.set_num_channels(512)
        pygame.mixer.music.load('Musway Studio - 035-2 - Inspiring Epic.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.hitSound = pygame.mixer.Sound('snd_hit_body.ogg')
        self.shootSound = pygame.mixer.Sound('40_smith_wesson_single-mike-koenig.wav')
        self.shootSound.set_volume(0.25)
        self.deathSound = pygame.mixer.Sound('neck_snap-Vladimir-719669812.wav')
        self.jumpSound = pygame.mixer.Sound('Bounce-SoundBible.com-12678623.wav')
        self.jumpSound.set_volume(0.5)
        self.doubleJumpSound = pygame.mixer.Sound('spin_jump-Brandino480-2020916281.wav')
        self.doubleJumpSound.set_volume(0.5)
        self.rollSound = pygame.mixer.Sound('bullet_whizzing_by-Mike_Koenig-2005433595.wav')
        self.rollSound.set_volume(0.2)
        self.walkSounds = [pygame.mixer.Sound('grass_0.wav'),pygame.mixer.Sound('grass_1.wav')]
        self.walkSounds[0].set_volume(0.4)
        self.walkSounds[1].set_volume(0.4)
        self.walkSoundTimer = 0
        self.reloadSound = pygame.mixer.Sound('Eject Clip And Re-Load-SoundBible.com-423238371.wav')
        self.reloadSound.set_volume(0.8)
        self.emptySound = pygame.mixer.Sound('Dry Fire Gun-SoundBible.com-2053652037.wav')
        self.emptySound.set_volume(0.7)
        self.droneSound = pygame.mixer.Sound('Wasp-SoundBible.com-863699866.wav')
        self.droneSound.set_volume(0.08)
        self.player = Player(self.width, self.height)
        self.playerGroup = pygame.sprite.GroupSingle(self.player)
        self.background = pygame.image.load("images\dackground3.png").convert_alpha()
        self.background = pygame.transform.scale(self.background, (800*6, 415*6))
        self.spikeGroup = pygame.sprite.Group()
        self.roll = False
        self.score = 0
        self.rolling = False
        self.gameRect = pygame.Rect(scroll[0], scroll[1], self.width, self.height)
        self.rollRight, self.rollLeft = False, False
        self.reticle = pygame.image.load('images\deticle.png').convert()
        self.reticle.set_colorkey((255,255,255))
        self.blockImg = pygame.image.load('images\city_block.png').convert()
        self.mouseX, self.mouseY = 0, 0
        self.bulletGroup = pygame.sprite.Group()
        self.bullet = Bullet(0,0,0)
        self.enemyBullet = Bullet(0,0,0)
        self.revolver = pygame.image.load('images\spr_weap_revolver.png').convert()
        self.revolver.set_colorkey((255,255,255))
        self.revolverFlip = pygame.transform.flip(self.revolver, False, True)
        self.rotatedRevolver = self.revolver
        self.revolver2 = pygame.image.load('images\spr_weap_revolver.png').convert()
        self.revolver2.set_colorkey((255,255,255))
        self.revolverFlip2 = pygame.transform.flip(self.revolver2, False, True)
        self.rotatedRevolver = self.revolver2
        self.drone = pygame.image.load('images\drone.png').convert()
        self.drone.set_colorkey((255,255,255))
        self.drone = pygame.transform.scale(self.drone, (37*3, 26*3))
        self.targetImg = pygame.image.load('images\spr_emoji_blue_flag.png').convert()
        self.targetImg.set_colorkey((255,255,255))
        self.sword = pygame.image.load('images\sword.png').convert()
        self.sword.set_colorkey((255,255,255))
        self.swordFlip = pygame.transform.flip(self.sword, True, False)
        self.spikeImg = pygame.image.load('images\spikes.png').convert()
        self.spikeImg.set_colorkey((255,255,255))
        self.enemyImg = pygame.image.load('images\dorture.png').convert()
        self.enemyImg.set_colorkey((255,255,255))
        self.enemyGroup = pygame.sprite.Group()
        self.timeLast = 0
        self.enemyRespawn = -1
        self.restartTime = -1
        self.upArrow = pygame.image.load('images\climbarrowUp.png').convert()
        self.rightArrow = pygame.image.load('images\climbarrowRight.png').convert()
        self.upLeftArrow = pygame.image.load('images\climbarrowUpperLeft.png').convert()
        self.leftArrow = pygame.image.load('images\climbarrowLeft.png').convert()
        self.upArrow.set_colorkey((0,0,0))
        self.rightArrow.set_colorkey((0,0,0))
        self.upLeftArrow.set_colorkey((0,0,0))
        self.leftArrow.set_colorkey((0,0,0))
        self.finalScore = 0
        self.firstExplosion = 0
        self.bulletsShot = 0
        self.lastReload = -2600
        self.lastDeath = 0
        self.invulnerability = 2600
        self.healImage = pygame.image.load('images\spr_healing.png').convert()
        self.healImage.set_colorkey((0,0,0))
        self.reloadCooldown = 2600
        self.bulletFont = pygame.font.SysFont('Herald', 75)
        self.ammoImage = pygame.image.load('images\spr_ammoget.png').convert()
        self.enemyBulletGroup = pygame.sprite.Group()
        self.lastEnemyBullet = 0
        self.explosion = self.explosionImage.get_image(0,0,320/5,320/5)
        global level2
        if level2 == True:
            self.zombieLimit = 20
            self.zombieProb = 0.02
            self.droneGroup = pygame.sprite.Group()
            self.droneLimit = 5
        else:
            self.zombieLimit = 10
            self.zombieProb = 0.01

    def mousePressed(self, x, y):
        # shoots player bullet
        bulletCooldown = 200
        timeNow = pygame.time.get_ticks()
        if timeNow - self.timeLast >= bulletCooldown and self.bulletsShot <= 15 and self.score - self.lastReload >= self.reloadCooldown:
            self.firstExplosion = timeNow
            self.shootSound.play()
            self.timeLast = timeNow
            self.bullet = Bullet(self.player.rect.x, self.player.rect.y, self.angle)
            self.bulletGroup.add(self.bullet)
            self.now = pygame.time.get_ticks()
            self.bulletsShot +=1
        elif self.bulletsShot > 15: self.emptySound.play()

    def mouseReleased(self, x, y):
        pass

    def mouseMotion(self, x, y):
        # determines mouse reticle position and player gun angle
        self.mouseX, self.mouseY = x-43, y-45
        self.reticleLocation = [self.mouseX, self.mouseY]
        self.mouseDx, self.mouseDy = self.mouseX - (self.player.rectCopy.x), self.mouseY - (self.player.rectCopy.y)
        rads = atan2(self.mouseDy, self.mouseDx)
        rads %= 2*pi
        self.angle = degrees(rads)
        if self.mouseX > self.player.rectCopy.x: self.rotatedRevolver = pygame.transform.rotate(self.revolver, -self.angle)
        else: self.rotatedRevolver = pygame.transform.rotate(self.revolverFlip, -self.angle)

    def mouseDrag(self, x, y):
        pass

    def keyPressed(self, keyCode, modifier, collisions):
        # For player jumping, rolling, and reloading
        if keyCode == pygame.K_w and self.player.jumpPossible == True:
            if self.player.jumpsRemaining == 2:
                self.jumpSound.play()
                self.player.singleJump = True
                self.player.yVel = -12
                self.player.dy = self.player.yVel
            elif self.player.jumpsRemaining == 1:
                self.doubleJumpSound.play()
                self.player.doubleJump = True
                self.player.singleJump = False
                self.player.yVel = -12
                self.player.dy = self.player.yVel
                self.player.jumpPossible = False
            self.player.jumpsRemaining -= 1
            if collisions['left'] == True and self.isKeyPressed(pygame.K_a): self.player.xVel += 24
            elif collisions['right'] == True and self.isKeyPressed(pygame.K_d): self.player.xVel -= 24
        elif (self.isKeyPressed(pygame.K_a) or self.isKeyPressed(pygame.K_d)) and keyCode == pygame.K_s and self.roll == False:
            self.player.lastRoll = pygame.time.get_ticks()
            self.roll = True
            if self.isKeyPressed(pygame.K_a): self.rollLeft = True
            elif self.isKeyPressed(pygame.K_d): self.rollRight = True
        elif keyCode == pygame.K_r:
            self.reloadSound.play()
            self.lastReload = pygame.time.get_ticks()
        elif keyCode == pygame.K_0: self.player.rect = pygame.Rect(0, 0, self.player.imageWidth-166, self.player.imageHeight-32)

    def keyReleased(self, keyCode, modifier):
        pass

    def timerFired(self, dt, mapScreen, tile_rects, leftRamps, rightRamps):

        if self.reloadCooldown - 50 <= self.score - self.lastReload < self.reloadCooldown: self.bulletsShot = 0
        # Spawns enemies randomly
        spawnBool = self.decision(self.zombieProb)
        if spawnBool == True and len(self.enemyGroup) < self.zombieLimit: 
            enemy = Enemy(self.width,self.height,random.randint(129,4735),random.randint(129,2431))
            if pygame.sprite.spritecollideany(enemy, tile_rects) == None and pygame.sprite.spritecollideany(enemy, leftRamps) == None and pygame.sprite.spritecollideany(enemy, rightRamps) == None: 
                self.enemyGroup.add(enemy)
            else: enemy.kill()
        spawnDrone = self.decision(0.01)
        global level2
        if level2 == True and spawnDrone == True and len(self.droneGroup) < self.droneLimit:
            drone = Drone(random.randint(129,4735),random.randint(129,2431))
            if pygame.sprite.spritecollideany(drone, tile_rects) == None and pygame.sprite.spritecollideany(drone, leftRamps) == None and pygame.sprite.spritecollideany(drone, rightRamps) == None: 
                self.droneGroup.add(drone)
            else: drone.kill()

        # updates and draws enemies and bullets
        self.enemyGroup.update(self.width,self.height,self,mapScreen, self.player, tile_rects,leftRamps,rightRamps)
        if level2 == True: self.droneGroup.update(self.player, self, tile_rects, leftRamps, rightRamps, mapScreen)
        self.bulletGroup.update(mapScreen)
        self.enemyBulletGroup.update(mapScreen)
        # For player deaths
        if self.score - self.lastDeath >= self.invulnerability and ((level2 == True and pygame.sprite.groupcollide(self.playerGroup, self.droneGroup, True, False) or pygame.sprite.groupcollide(self.enemyBulletGroup, self.playerGroup, True, True)) or pygame.sprite.groupcollide(self.playerGroup, self.spikeGroup, True, False) or pygame.sprite.groupcollide(self.playerGroup, self.enemyGroup, True, False)):
            self.deathSound.play()
            self.player = Player(self.width, self.height)
            self.playerGroup.add(self.player)
            self.lastDeath = pygame.time.get_ticks()
            self.bulletsShot = 0
        # For player bullets
        self.numBullets = 15 - self.bulletsShot
        self.bulletText = self.bulletFont.render(f'{self.numBullets+1}/16', False, (0,0,0))
        if pygame.sprite.groupcollide(self.bulletGroup, self.enemyGroup, True, True):
            self.hitSound.play()

        if level2 == True and pygame.sprite.groupcollide(self.bulletGroup, self.droneGroup, True, True):
            self.hitSound.play()
        # For getting to the end flag
        if pygame.sprite.groupcollide(self.targetGroup, self.playerGroup, True, False):
            self.targetGroup.remove(self.target)
            self.finalScore = self.score/1000
            self.restartTime = 100
        # For starting Impossible Mode
        if self.restartTime > 0:
            font = pygame.font.SysFont('Comic Sans MS', 144)
            extraFont = pygame.font.SysFont('Comic Sans MS', 30)
            pygame.draw.rect(mapScreen, (255,255,0),(0,self.height/2-150,self.width,256))
            text = font.render('Climb Complete!', False, (0,0,0))
            extraText = extraFont.render('Impossible Mode Will Now Start', False, (0,255,0))
            scoreText = extraFont.render(f'[Your Time Was {self.finalScore} Seconds!]', False, (255,0,0))
            mapScreen.blit(text, (self.width/2-500,self.height/2-150))
            mapScreen.blit(extraText, (self.width/2-260,self.height/2+30))
            mapScreen.blit(scoreText, (self.width/2-260, self.height/2+60)) 
            self.restartTime -=1
            pygame.time.wait(25)

        elif self.restartTime == 0:
            level2 = True 
            self.run()
        # Kill player if they fall off map
        if self.player.airTime == 400:
            self.player.kill()
            self.deathSound.play()
            self.player = Player(self.width, self.height)
            self.playerGroup.add(self.player)
        

        
    def redrawAll(self, screen, mapScreen): 
        explosionLength = 300
        mapScreen.blit(self.rightArrow, (1000-scroll[0], 2200-scroll[1]))
        mapScreen.blit(self.upLeftArrow, (3000-scroll[0], 1800-scroll[1]))
        mapScreen.blit(self.rightArrow, (3200-scroll[0], 1000-scroll[1]))
        mapScreen.blit(self.upArrow, (2000-scroll[0], 1600-scroll[1]))
        mapScreen.blit(self.upArrow, (4450-scroll[0], 1000-scroll[1]))
        mapScreen.blit(self.leftArrow, (3600-scroll[0], 400-scroll[1]))
        mapScreen.blit(self.upLeftArrow, (2000-scroll[0], 400-scroll[1]))
        mapScreen.blit(self.upArrow, (400-scroll[0], 600-scroll[1]))
        mapScreen.blit(self.player.sprite, (self.player.spriteRect.x-scroll[0],self.player.spriteRect.y-scroll[1]))
        
        if self.mouseX > self.player.rectCopy.x: mapScreen.blit(self.player.head, self.player.headLocation)
        else: mapScreen.blit(self.player.headFlip, self.player.headLocation)
        mapScreen.blit(self.reticle, self.reticleLocation)
        
        if self.mouseX > self.player.rectCopy.x: mapScreen.blit(self.rotatedRevolver, (self.player.rectCopy.x-32,self.player.rectCopy.y-32))
        else: mapScreen.blit(self.rotatedRevolver, (self.player.rectCopy.x-54,self.player.rectCopy.y-32))
        if self.score - self.firstExplosion < explosionLength:
            self.explosionCountWidth =(self.explosionCountWidth+1) % 5
            if self.explosionCountWidth == 4: self.explosionCountHeight = (self.explosionCountHeight+1) % 5
            self.explosion = self.explosionImage.get_image(self.explosionCountWidth*(320/5),self.explosionCountHeight*(320/5),320/5,320/5)
            if self.mouseX > self.player.rectCopy.x and self.mouseY > self.player.rectCopy.y: mapScreen.blit(self.explosion, (self.player.rectCopy.x+24,self.player.rectCopy.y-12))
            elif self.mouseX > self.player.rectCopy.x and self.mouseY < self.player.rectCopy.y: mapScreen.blit(self.explosion, (self.player.rectCopy.x+24,self.player.rectCopy.y-62))
            elif self.mouseX < self.player.rectCopy.x and self.mouseY > self.player.rectCopy.y: mapScreen.blit(self.explosion, (self.player.rectCopy.x-94,self.player.rectCopy.y-12))
            else: mapScreen.blit(self.explosion, (self.player.rectCopy.x-94,self.player.rectCopy.y-62))
        if self.score - self.lastDeath < self.invulnerability: mapScreen.blit(self.healImage, (self.player.rectCopy.x-20,self.player.rectCopy.y-74))
        pygame.draw.rect(mapScreen, (0, 255, 0), (self.width-256,self.height-96, 256, 96))
        mapScreen.blit(self.bulletText, (self.width-250,self.height-64))
        mapScreen.blit(self.ammoImage, (self.width-100,self.height-75))
        screen.blit(mapScreen,(0,0))

    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def __init__(self, width=1600, height=900, fps=144, title="Mundane Man"):

        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.bgColor = (0, 51, 102)
        # stores all the keys currently being held down
        self._keys = dict()
        pygame.init()

    # From https://stackoverflow.com/questions/5886987/true-or-false-output-based-on-a-probability
    def decision(self, probability):

        return random.random() < probability

    def run(self):
        
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        
        # set the title of the window
        pygame.display.set_caption(self.title)
        pygame.font.init()
        
        # call game-specific initialization
        self.init()
        
        self.collisionsEnemy = {'top':False,'bottom':False,'right':False,'left':False}
        self.droneCollisions = {'top':False,'bottom':False,'right':False,'left':False}
        playing = True
        # Load map data
        # Modified from https://www.youtube.com/watch?v=HCWI2f7tQnY&list=PLX5fBCkxJmm1fPSqgn9gyR3qih8yYLvMj&index=3
        tile_rects = pygame.sprite.Group()
        leftRamps = pygame.sprite.Group()
        rightRamps = pygame.sprite.Group()
        y = 0
        for layer in game_map:
            x = 0
            for tile in layer:
                if tile == '1': tile_rects.add(Tiles(x*128,y*128))
                elif tile == '2':
                    self.spike = Spike(x*128,y*128)
                    self.spikeGroup.add(self.spike)
                elif tile == '3':
                    self.target = Target(x*128,y*128)
                    self.targetGroup = pygame.sprite.GroupSingle(self.target)
                elif tile == '4': leftRamps.add(Tiles(x*128,y*128))
                elif tile == '5': rightRamps.add(Tiles(x*128,y*128))
                x += 1
            y += 1

        while playing:
            
            self.score = pygame.time.get_ticks()
            if self.walkSoundTimer > 0: self.walkSoundTimer -= 1
            self.gameRect = pygame.Rect(scroll[0], scroll[1], self.width, self.height)
            # Render map
            mapScreen = pygame.Surface((self.width, self.height))
            mapScreen.fill(self.bgColor)
            mapScreen.blit(self.background, (-self.gameRect.x, -self.gameRect.y))

            # Modified from https://www.youtube.com/watch?v=HCWI2f7tQnY&list=PLX5fBCkxJmm1fPSqgn9gyR3qih8yYLvMj&index=3
            y = 0
            for layer in game_map:
                x = 0
                for tile in layer:
                    if (x)*128 <= self.width+scroll[0] and (y)*128 <= self.height+scroll[1]:
                        if tile == '1' : mapScreen.blit(self.blockImg,(x*128-scroll[0],y*128-scroll[1]))
                        elif tile == '2': mapScreen.blit(self.spikeImg,(x*128-scroll[0],y*128-scroll[1]))
                        elif tile == '3': mapScreen.blit(self.targetImg,(x*128-scroll[0],y*128-scroll[1]))
                        elif tile == '4': mapScreen.blit(self.leftSlope,(x*128-scroll[0],y*128-scroll[1]))
                        elif tile == '5': mapScreen.blit(self.rightSlope,(x*128-scroll[0],y*128-scroll[1]))
                    x += 1
                y += 1
            
            time = clock.tick(self.fps)
            self.timerFired(time, mapScreen, tile_rects, leftRamps, rightRamps)
            # For player inputs
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDrag(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod, collisions)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    level2 = False
                    playing = False
            
            # player updates
            self.player.update(self.width, self.height, self, mapScreen)
            self.player.rect,collisions, self.player.dy = move(self.player.rect,self.player.location,tile_rects,self.player,self.playerGroup,leftRamps,rightRamps, self)
            
            for bullet in self.bulletGroup:
                bulletWallCollide = bulletWallCollision(tile_rects, mapScreen,self.bulletGroup)
                if bulletWallCollide == True:
                    bullet.kill()

            for bullet in self.enemyBulletGroup:
                bulletWall = bulletWallCollision(tile_rects, mapScreen,self.enemyBulletGroup)
                if bulletWall == True:
                    bullet.kill()
            
            self.player.spriteRect = pygame.Rect(self.player.rect.x-82,self.player.rect.y-30,self.player.imageWidth,self.player.imageHeight)
            if self.roll == True and self.player.airTime == 0: self.player.headLocation = [self.player.rect.x-6-scroll[0], self.player.rect.y+27-scroll[1]]
            elif self.isKeyPressed(pygame.K_s): self.player.headLocation = [self.player.rect.x-20-scroll[0], self.player.rect.y-scroll[1]]
            else: self.player.headLocation = [self.player.rect.x-20-scroll[0], self.player.rect.y-22-scroll[1]]         

            # player collisions
            if collisions['top'] == True:
                self.player.yVel += 6
                self.player.dy = self.player.yVel
            
            elif collisions['bottom'] == True:
                self.player.jumpPossible = True
                self.player.jumpsRemaining = 2
                self.player.yVel = 0
                self.player.dy = 0
                self.player.singleJump = False
                self.player.doubleJump = False
                self.player.airTime = 0
                # Slightly modified from https://www.youtube.com/watch?v=z0aOffHrTac
                if self.player.location[0] != 0 and self.walkSoundTimer == 0:
                    self.walkSoundTimer = 30
                    random.choice(self.walkSounds).play()

            elif collisions['left'] == True:
                if self.player.yVel > 3:
                    self.player.yVel = 3
                    self.player.dy = self.player.yVel
                self.player.jumpPossible = True
                self.player.jumpsRemaining = 2
                self.player.airTime = 0
                self.player.sprite = self.player.imageDrag

            elif collisions['right'] == True:
                if self.player.yVel > 3:
                    self.player.yVel = 3
                    self.player.dy = self.player.yVel
                self.player.jumpPossible = True
                self.player.jumpsRemaining = 2
                self.player.airTime = 0
                self.player.sprite = pygame.transform.flip(self.player.imageDrag, True, False)
            
            self.redrawAll(screen, mapScreen)
            # Idea for the added slight delay of the scrolling from https://www.youtube.com/watch?v=5q7tmIlXROg&list=PLX5fBCkxJmm1fPSqgn9gyR3qih8yYLvMj&index=5
            scroll[0] += ((self.player.rect.x+self.mouseX)-scroll[0]-self.width+self.player.imageWidth-140)/20
            scroll[1] += ((self.player.rect.y+self.mouseY)-scroll[1]-self.height+self.player.imageHeight+20)/20
            # For blitting other sprites that can't be affected by scroll
            self.player.rectCopy = pygame.Rect.copy(self.player.rect)
            self.player.rectCopy.x -= scroll[0] - 20
            self.player.rectCopy.y -= scroll[1] - 33
            pygame.display.flip()
        pygame.quit()


# From https://www.reddit.com/r/pygame/comments/23u11o/how_do_i_break_up_a_sprite_sheet/
class SpriteSheet(pygame.sprite.Sprite):
    """ Class used to grab images out of a sprite sheet. """
    # This points to our sprite sheet image
    sprite_sheet = None
 
    def __init__(self, file_name):
        super(SpriteSheet, self).__init__()
        """ Constructor. Pass in the file name of the sprite sheet. """
        self.background = (255, 255, 255)
        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load(file_name).convert()
    
 
    def get_image(self, x, y, width, height):
        """ Grab a single image out of a larger spritesheet
            Pass in the x, y location of the sprite
            and the width and height of the sprite. """
 
        # Create a new blank image
        image = pygame.Surface([width, height]).convert()
 
        # Copy the sprite from the large sheet onto the smaller image
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
 
        # Assuming background works as the transparent color
        image.set_colorkey(self.background)
        
        # Return the image
        return image



class Player(pygame.sprite.Sprite):
    
    def __init__(self, winWidth, winHeight):

        super(Player, self).__init__()
        self.image = SpriteSheet('images\spr_player_move.png')
        self.imageStand = SpriteSheet('images\playerStand.png')
        self.imageJump = SpriteSheet('images\spr_playerJump.png')
        self.imageCrouch = SpriteSheet('images\playerCrouch.png')
        self.imageRoll = SpriteSheet('images\playerRoll.png')
        self.imageDoubleJump = SpriteSheet('images\playerDoubleJump.png')
        self.imageDrag = pygame.image.load('images\playerDrag.png').convert()
        self.imageDrag.set_colorkey((255,255,255))
        self.imageHeight = 128
        self.imageWidth = 196
        self.walkCount = 0
        self.location = [0, 0]
        self.yVel, self.xVel =  0, 0
        self.jumpPossible = False
        self.jumpsRemaining = 2
        self.head = pygame.image.load('images\spr_playerHead.png').convert()
        self.head.set_colorkey((255,255,255))
        self.headFlip = pygame.transform.flip(self.head, True, False)
        self.rect = pygame.Rect(150, winHeight+900, self.imageWidth-166, self.imageHeight-32)
        self.last = pygame.time.get_ticks()
        self.lastRoll = pygame.time.get_ticks()
        self.sprite = self.image.get_image(0,0,self.imageWidth,self.imageHeight)
        self.spriteRect = pygame.Rect(self.rect.x-82,self.rect.y-30,self.imageWidth,self.imageHeight)
        self.doubleJump = False
        self.singleJump = False
        self.dx, self.dy = 0, 0
        self.cooldown = 50
        self.standCount = 0
        self.count = 0
        self.rollCooldown = 500
        self.airTime = 0
        self.rectCopy = pygame.Rect.copy(self.rect)

    def update(self, winWidth, winHeight, game, mapScreen):
        # Standing animation
        self.headLocation = [self.rect.x-20, self.rect.y-22]
        if not game.isKeyPressed(pygame.K_a) and not game.isKeyPressed(pygame.K_d) and not game.isKeyPressed(pygame.K_s) and not game.isKeyPressed(pygame.K_w) and game.roll == False and self.singleJump == False and self.doubleJump == False:
            self.now = pygame.time.get_ticks()
            if self.now - self.last >= self.cooldown:
                self.last = self.now
                self.standCount =(self.standCount +1) % 3
                if game.mouseX > self.rectCopy.x: self.sprite = self.imageStand.get_image(self.standCount*(self.imageWidth),0,self.imageWidth,self.imageHeight)
                else: self.sprite = pygame.transform.flip(self.imageStand.get_image(self.standCount*(self.imageWidth),0,self.imageWidth,self.imageHeight), True, False)
        
        self.spriteRect = pygame.Rect(self.rect.x-82,self.rect.y-30,self.imageWidth,self.imageHeight)
        self.location = [0,0]
        # Rolling
        if game.roll == True and self.airTime == 0:
            self.now = pygame.time.get_ticks()
            if self.now - self.last >= self.cooldown:
                game.rollSound.play()
                self.last = self.now
                self.walkCount = (self.walkCount + 1) % 7
                if game.rollRight == True: 
                    self.sprite = self.imageRoll.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight)
                    self.xVel = 8
                elif game.rollLeft == True: 
                    self.sprite = pygame.transform.flip(self.imageRoll.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight), True, False)
                    self.xVel = -8
                if self.now - self.lastRoll >= self.rollCooldown:
                    self.lastRoll = self.now
                    game.roll = False
                    game.rollRight = False
                    game.rollLeft = False  
                    self.xVel = 0
        # Single Jump
        if self.singleJump == True:
            self.airTime += 1
            self.now = pygame.time.get_ticks()
            self.jumpcooldown = 100
            if self.now - self.last >= self.jumpcooldown:
                self.last = self.now
                self.walkCount = (self.walkCount + 1) % 3
                if game.mouseX > self.rectCopy.x: self.sprite = self.imageJump.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight)
                else: self.sprite = pygame.transform.flip(self.imageJump.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight), True, False)
        # Double Jump
        elif self.doubleJump == True:
            self.airTime += 1
            self.now = pygame.time.get_ticks()
            if self.now - self.last >= self.cooldown:
                self.last = self.now
                self.walkCount = (self.walkCount + 1) % 3
                if game.mouseX > self.rectCopy.x:
                    self.sprite = self.imageDoubleJump.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight)
                else:
                    self.sprite = pygame.transform.flip(self.imageDoubleJump.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight), True, False)  
        # Move left, if in air a little faster
        if game.isKeyPressed(pygame.K_a):
            if not game.isKeyPressed(pygame.K_s) and self.singleJump == False:
                self.now = pygame.time.get_ticks()
                if self.now - self.last >= self.cooldown:
                    self.last = self.now
                    self.walkCount = (self.walkCount + 1) % 7
                    self.sprite = pygame.transform.flip(self.image.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight), True, False)
            if self.airTime > 0: 
                self.dx = -8
                self.location[0] -= 8
            else:
                self.dx = -6
                self.location[0] -= 6
        # Move right, if in air a little faster
        if game.isKeyPressed(pygame.K_d):
            if not game.isKeyPressed(pygame.K_s) and self.singleJump == False:
                self.now = pygame.time.get_ticks()
                if self.now - self.last >= self.cooldown:
                    self.last = self.now
                    self.walkCount = (self.walkCount + 1) % 7
                    self.sprite = self.image.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight)
            if self.airTime > 0: 
                self.dx = 8
                self.location[0] += 8
            else:
                self.dx = 6
                self.location[0] += 6
        self.location[0] += self.xVel
        if self.xVel > 0: self.xVel -= 1
        elif self.xVel < 0: self.xVel += 1
        # Gravity effect
        # A little inspiration from https://www.youtube.com/watch?v=HCWI2f7tQnY&list=PLX5fBCkxJmm1fPSqgn9gyR3qih8yYLvMj&index=3
        self.location[1] += self.yVel
        self.yVel += 0.6
        self.dy = self.yVel
        # Crouch and crouch walking
        if game.roll == False and game.isKeyPressed(pygame.K_s):
            if (game.isKeyPressed(pygame.K_a) or game.isKeyPressed(pygame.K_d)):
                if game.isKeyPressed(pygame.K_a):
                    self.dx += 3
                    self.location[0] += 3
                if game.isKeyPressed(pygame.K_d):
                    self.dx -= 3
                    self.location[0] -= 3
                self.now = pygame.time.get_ticks()
                if self.now - self.last >= self.cooldown:
                    self.last = self.now
                    self.walkCount = (self.walkCount + 1) % 4
                    if game.mouseX > self.rectCopy.x: self.sprite = self.imageCrouch.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight)
                    else: self.sprite = pygame.transform.flip(self.imageCrouch.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight), True, False)
            else: 
                if game.mouseX > self.rectCopy.x: self.sprite = self.imageCrouch.get_image(0,0,self.imageWidth,self.imageHeight)
                else: self.sprite = pygame.transform.flip(self.imageCrouch.get_image(0,0,self.imageWidth,self.imageHeight), True, False)
            # Fast fall
            self.yVel += 0.9
            self.dy = self.yVel
            if self.yVel > 16: 
                self.yVel = 16
                self.dy = self.yVel
        elif self.yVel > 12: 
            self.yVel = 12
            self.dy = self.yVel

class Drone(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super(Drone, self).__init__()
        self.rect = pygame.Rect(x, y, 37*3, 26*3)
        self.location = [0,0]
        self.dx, self.dy = 0, 0
        self.xVel, self.yVel = 0, 0
        self.last = pygame.time.get_ticks()
        self.explosionLength = 300
        self.firstExplosion = 0

    def update(self, player, game, tile_rects, leftRamps, rightRamps, mapScreen):
        self.location[0] += self.xVel
        self.location[1] += self.yVel
        self.location = [0,0]
        # Drone collisions and movement
        if game.droneCollisions['left'] == False and player.rect.x < self.rect.x - 500:
            self.dx = -3
            self.location[0] -= 3
        elif game.droneCollisions['right'] == False and player.rect.x > self.rect.x + 500:
            self.dx = 3
            self.location[0] += 3

        if game.droneCollisions['top'] == False and player.rect.y < self.rect.y - 500:
            self.dy = -3
            self.location[1] -= 3
        elif game.droneCollisions['bottom'] == False and player.rect.y > self.rect.y + 500:
            self.dy = 3
            self.location[1] += 3

        self.rect,game.droneCollisions,self.dy = move(self.rect,self.location,tile_rects,self,game.enemyGroup,leftRamps,rightRamps, game)
           
        if game.droneCollisions['top'] == True:
            self.yVel += 24
            self.dy = self.yVel
                
        elif game.droneCollisions['bottom'] == True:
            self.yVel -= 24
            self.dy = self.yVel
                
        elif game.droneCollisions['left'] == True:
            self.xVel += 24
            self.dx = self.xVel
                    
        elif game.droneCollisions['right'] == True:
            self.xVel -= 24
            self.dx = self.xVel
        
        if self.xVel > 0: self.xVel -= 1
        elif self.xVel < 0: self.xVel += 1
        if self.yVel > 0: self.yVel -= 1
        elif self.yVel < 0: self.yVel += 1
        # drone gun angle
        droneDx, droneDy = player.rect.x - (self.rect.x), player.rect.y - (self.rect.y)
        rads = atan2(droneDy, droneDx)
        rads %= 2*pi
        angle = degrees(rads)
        if player.rect.x > self.rect.x: game.rotatedRevolver2 = pygame.transform.rotate(game.revolver2, -angle)
        else: game.rotatedRevolver2 = pygame.transform.rotate(game.revolverFlip2, -angle)
        # drone render
        if game.gameRect.colliderect(self.rect):
            now = pygame.time.get_ticks()
            if now - self.last >= 2000:
                self.last = now
                game.droneSound.play()
            mapScreen.blit(game.drone, (self.rect.x-scroll[0],self.rect.y-scroll[1]))
            if player.rect.x > self.rect.x: mapScreen.blit(game.rotatedRevolver2,(self.rect.x+50-scroll[0],self.rect.y+30-scroll[1]))
            else: mapScreen.blit(game.rotatedRevolver2,(self.rect.x+15-scroll[0],self.rect.y+30-scroll[1]))
            # Drone shoot bullets
            bulletCooldown = 1000
            timeNow = pygame.time.get_ticks()
            if timeNow - game.lastEnemyBullet >= bulletCooldown:
                randomAngle = game.decision(0.5)
                game.shootSound.play()
                game.lastEnemyBullet = timeNow
                self.firstExplosion = timeNow
                if randomAngle == True: game.enemyBullet = Bullet(self.rect.x, self.rect.y, angle+10)
                else: game.enemyBullet = Bullet(self.rect.x, self.rect.y, angle-20)
                game.enemyBulletGroup.add(game.enemyBullet)
            if game.score - self.firstExplosion < self.explosionLength:
                game.explosionCountWidth =(game.explosionCountWidth+1) % 5
                if game.explosionCountWidth == 4: game.explosionCountHeight = (game.explosionCountHeight+1) % 5
                game.explosion = game.explosionImage.get_image(game.explosionCountWidth*(320/5),game.explosionCountHeight*(320/5),320/5,320/5)
                if player.rect.x > self.rect.x and player.rect.y > self.rect.y: mapScreen.blit(game.explosion, (self.rect.x+80-scroll[0],self.rect.y+60-scroll[1]))
                elif player.rect.x > self.rect.x and player.rect.y < self.rect.y: mapScreen.blit(game.explosion, (self.rect.x+80-scroll[0],self.rect.y+20-scroll[1]))
                elif player.rect.x < self.rect.x and player.rect.y > self.rect.y: mapScreen.blit(game.explosion, (self.rect.x-36-scroll[0],self.rect.y+60-scroll[1]))
                else: mapScreen.blit(game.explosion, (self.rect.x-36-scroll[0],self.rect.y+20-scroll[1]))
                

class Enemy(Player):

    def __init__(self, winWidth, winHeight,x,y):

        super().__init__(winWidth,winHeight)
        self.image = SpriteSheet('images\enemyMove.png')
        self.imageStand = SpriteSheet('images\enemyStand.png')
        self.imageJump = SpriteSheet('images\enemyJump.png')
        self.imageDoubleJump = SpriteSheet('images\enemyDoubleJump.png')
        self.imageDrag = pygame.image.load('images\enemyDrag.png').convert()
        self.imageDrag.set_colorkey((255,255,255))
        self.rect = pygame.Rect(x, y, self.imageWidth-166, self.imageHeight-32)
        self.spriteRect = pygame.Rect(self.rect.x-82,self.rect.y-8,self.imageWidth,self.imageHeight)
        self.walking = False
        self.lastJumpTime = 0
        self.jumpTime = 0

    def jump(self, player, game):
        # enemy jumping
            if self.jumpPossible == True and player.rect.y < self.rect.y:
                if self.jumpsRemaining == 2:
                    if game.gameRect.colliderect(self.rect): game.jumpSound.play()
                    self.singleJump = True
                    self.yVel = -12
                    self.dy = self.yVel
                    self.jumpTime = pygame.time.get_ticks()
                    self.jumpsRemaining -=1
                elif self.jumpsRemaining == 1 and self.lastJumpTime - self.jumpTime >=400:
                    if game.gameRect.colliderect(self.rect): game.doubleJumpSound.play()
                    self.lastJumpTime = self.jumpTime
                    self.doubleJump = True
                    self.singleJump = False
                    self.yVel = -12
                    self.dy = self.yVel
                    self.jumpPossible = False
                    self.jumpsRemaining -= 1
                self.lastJumpTime = pygame.time.get_ticks()

    def update(self, winWidth, winHeight, game, mapScreen, player, tile_rects,leftRamps,rightRamps):
        # kill enemy if falls off map
        if self.airTime == 400: self.kill()
        self.location = [0,0]
        # enemy standing animation
        if self.walking == False and self.singleJump == False and self.doubleJump == False:
            self.now = pygame.time.get_ticks()
            if self.now - self.last >= self.cooldown:
                self.last = self.now
                self.standCount =(self.standCount +1) % 3
                if game.mouseX > self.rectCopy.x: self.sprite = self.imageStand.get_image(self.standCount*(self.imageWidth),0,self.imageWidth,self.imageHeight)
                else: self.sprite = pygame.transform.flip(self.imageStand.get_image(self.standCount*(self.imageWidth),0,self.imageWidth,self.imageHeight), True, False)
        
        self.spriteRect = pygame.Rect(self.rect.x-82,self.rect.y-30,self.imageWidth,self.imageHeight)
        # enemy single jump
        if self.singleJump == True:
            self.airTime += 1
            self.now = pygame.time.get_ticks()
            self.jumpcooldown = 100
            if self.now - self.last >= self.jumpcooldown:
                self.last = self.now
                self.walkCount = (self.walkCount + 1) % 3
                if player.rect.x > self.rect.x: self.sprite = self.imageJump.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight)
                else: self.sprite = pygame.transform.flip(self.imageJump.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight), True, False)
        # enemy double jump
        elif self.doubleJump == True:
            self.airTime += 1
            self.now = pygame.time.get_ticks()
            if self.now - self.last >= self.cooldown:
                self.last = self.now
                self.walkCount = (self.walkCount + 1) % 3
                if player.rect.x > self.rect.x: self.sprite = self.imageDoubleJump.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight)
                else: self.sprite = pygame.transform.flip(self.imageDoubleJump.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight), True, False)
        # player to left of enemy
        if player.rect.x < self.rect.x + 5:
            self.walking = True
            if self.singleJump == False:
                self.now = pygame.time.get_ticks()
                if self.now - self.last >= self.cooldown:
                    self.last = self.now
                    self.walkCount = (self.walkCount + 1) % 7
                    self.sprite = pygame.transform.flip(self.image.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight), True, False)
            if self.airTime > 0: 
                self.dx = -5
                self.location[0] -= 5
            else:
                self.dx = -4
                self.location[0] -= 4
        # player to right of enemy
        elif player.rect.x > self.rect.x - 5:
            self.walking = True
            if self.singleJump == False:
                self.now = pygame.time.get_ticks()
                if self.now - self.last >= self.cooldown:
                    self.last = self.now
                    self.walkCount = (self.walkCount + 1) % 7
                    self.sprite = self.image.get_image(self.walkCount*(self.imageWidth), 0, self.imageWidth, self.imageHeight)
            if self.airTime > 0: 
                self.dx = 5
                self.location[0] += 5
            else:
                self.dx = 4
                self.location[0] += 4

        else: self.walking = False
        self.jump(player, game)
        self.location[0] += self.xVel
        if self.xVel > 0: self.xVel -= 1
        elif self.xVel < 0: self.xVel += 1
        self.location[1] += self.yVel
        self.yVel += 0.6
        self.dy = self.yVel
        if self.yVel > 12: 
            self.yVel = 12
            self.dy = self.yVel
        # enemy collisions
        self.rect,game.collisionsEnemy,self.dy = move(self.rect,self.location,tile_rects,self,game.enemyGroup,leftRamps,rightRamps, game)
        self.spriteRect = pygame.Rect(self.rect.x-82,self.rect.y-30,self.imageWidth,self.imageHeight)    
        if game.collisionsEnemy['top'] == True:
            self.yVel += 6
            self.dy = self.yVel
                
        elif game.collisionsEnemy['bottom'] == True:
            self.jumpPossible = True
            self.jumpsRemaining = 2
            self.yVel = 0
            self.dy = 0
            self.singleJump = False
            self.doubleJump = False
            self.airTime = 0
            if self.location[0] != 0 and game.walkSoundTimer == 0 and game.gameRect.colliderect(self.rect):
                game.walkSoundTimer = 30
                random.choice(game.walkSounds).play()
                
        elif game.collisionsEnemy['left'] == True:
            if self.yVel > 3:
                self.yVel = 3
                self.dy = self.yVel
                self.jumpPossible = True
                self.jumpsRemaining = 2
                self.airTime = 0
                self.sprite = self.imageDrag
                self.xVel += 24
                    
        elif game.collisionsEnemy['right'] == True:
            if self.yVel > 3:
                self.yVel = 3
                self.dy = self.yVel
                self.jumpPossible = True
                self.jumpsRemaining = 2
                self.airTime = 0
                self.sprite = pygame.transform.flip(self.imageDrag, True, False)
                self.xVel -= 24
        # enemy render
        if game.gameRect.colliderect(self.rect):
            mapScreen.blit(self.sprite, (self.spriteRect.x-scroll[0],self.spriteRect.y-scroll[1]))
            if player.rect.x > self.rect.x: mapScreen.blit(game.sword,(self.spriteRect.x+50-scroll[0],self.spriteRect.y-scroll[1]))
            else: mapScreen.blit(game.swordFlip,(self.spriteRect.x+15-scroll[0],self.spriteRect.y-scroll[1]))
        
# Modified from http://blog.lukasperaza.com/getting-started-with-pygame/
class Bullet(pygame.sprite.Sprite):

    time = 50 * 3
    speed = 40
    size = 10

    def __init__(self, x, y, angle):

        super(Bullet, self).__init__()
        size = Bullet.size
        self.image = pygame.image.load('images\spr_proj_musket.png').convert()
        self.image.set_colorkey((255,255,255))
        self.x, self.y = x+32, y+32
        self.rect = pygame.Rect(self.x, self.y, size, size)
        vx = Bullet.speed * cos(radians(angle))
        vy = Bullet.speed * sin(radians(angle))
        self.velocity = vx, vy
        self.grav = 0
        self.timeOnScreen = 0

    def update(self, mapScreen):
        vx, vy = self.velocity
        self.grav += 0.8
        self.x += vx
        self.y += (vy+self.grav)
        self.rect = pygame.Rect(self.x, self.y, Bullet.size, Bullet.size)
        self.timeOnScreen += 1
        if self.timeOnScreen > Bullet.time: self.kill()
        mapScreen.blit(self.image, (self.rect.x-scroll[0],self.rect.y-scroll[1]))
        

# Modified from https://www.youtube.com/watch?v=HCWI2f7tQnY&list=PLX5fBCkxJmm1fPSqgn9gyR3qih8yYLvMj&index=3 and https://www.youtube.com/watch?v=EHfqrAEmVyg&list=PLX5fBCkxJmm1fPSqgn9gyR3qih8yYLvMj&index=14
def move(rect,movement,tiles, player, playerGroup, leftRamps, rightRamps, game):
    # full block collision
    collision_types = {'top':False,'bottom':False,'right':False,'left':False}
    rect.x += movement[0]
    hit_list = pygame.sprite.spritecollide(player, tiles, False)
    for tile in hit_list:
        if player.dx >= 4:
            rect.right = tile.rect.left
            collision_types['right'] = True
        elif player.dx <= -4:
            rect.left = tile.rect.right
            collision_types['left'] = True

    rect.y += movement[1]
    hit_list = pygame.sprite.spritecollide(player, tiles, False)
    for tile in hit_list:
        if player.dy >= 0.6:
            rect.bottom = tile.rect.top
            collision_types['bottom'] = True
        elif player.dy < 0:
            rect.top = tile.rect.bottom
            collision_types['top'] = True
    # ramp collision
    for ramp in pygame.sprite.spritecollide(player, leftRamps, False):
        offsetX = rect.x - ramp.rect.x
        offsetY = max(min(128 - offsetX, 128),0)
        nextY = ramp.rect.y + 128 - offsetY
        if rect.bottom > nextY:
            rect.bottom = nextY
            player.location[1] = rect.y
            collision_types['bottom'] = True
    for ramp in pygame.sprite.spritecollide(player, rightRamps, False):
        offsetX = rect.x - ramp.rect.x
        offsetY = max(min(offsetX + rect.width, 128),0)
        nextY = ramp.rect.y + 128 - offsetY
        if rect.bottom > nextY:
            rect.bottom = nextY
            player.location[1] = rect.y
            collision_types['bottom'] = True
            
    return rect, collision_types, player.dy


def bulletWallCollision(tiles,screen,bulletGroup):

    collision = False
    hit_list = pygame.sprite.groupcollide(tiles, bulletGroup, False, False)
    for tile in hit_list: collision = True
    return collision


def main():

    game = PygameGame()
    game.run()


if __name__ == '__main__': main()