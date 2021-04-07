'''
PING PONG by A. Golovanov
August 2019
'''

import tkinter as tk

# Frame & HUD constants:
FRAMEWIDTH  = 600       
FRAMEHEIGHT = 400       
BGCOLOR     = '#000000' 
HUDCOLOR    = '#444444' 
SCORESIZE   = 100       
HUDSIZE     = 30       
MAXSCORE    = 5         # score needed to win 

# Paddle constants:
PADSECTION  = 6                  # no. of paddle positions on Y
PADINITSECT = 2                  # no. of section when begin
PADWIDTH    = 10
PADXPOS     = PADWIDTH / 2 + 10  # paddle offset from screen edge
PAD0COLOR   = '#ff8800'
PAD1COLOR   = '#0088ff'

# Ball constants:
BALLRADIUS = 8
BALLSPEED  = 14        # next is init position of ball after missed
BALLRESET  = 20 + PADWIDTH + PADXPOS + BALLRADIUS
BALLCOLOR  = '#ffffff'


class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item
    
    def get_position(self):
        return self.canvas.coords(self.item)
    
    def move(self, x, y):
        self.canvas.move(self.item, x, y)
    
    def delete(self):
        self.canvas.delete(self.item)


class Paddle(GameObject):
    def __init__(self, canvas, x, y, color='#ffffff'):
        self.width  = PADWIDTH
        self.section= PADSECTION
        self.height = FRAMEHEIGHT / self.section
        self.vsect  = PADINITSECT
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2, y,
                                       x + self.width / 2, y + self.height,
                                       fill=color)
        super(Paddle, self).__init__(canvas, item)
    
    def set_ball(self, ball):
        self.ball = ball
    
    def move(self, offset):
        if self.vsect + offset >= 0 and self.vsect + offset <= self.section - 1:
            self.vsect += offset
            pos_inc = offset * self.height
            super(Paddle, self).move(0, pos_inc)


class Ball(GameObject):
    def __init__(self, canvas, x, y, dir):
        self.radius = BALLRADIUS
        self.speed  = BALLSPEED
        self.direction = dir
        item = canvas.create_oval(x - self.radius,
                                  y - self.radius,
                                  x + self.radius,
                                  y + self.radius,
                                  fill=BALLCOLOR)
        super(Ball, self).__init__(canvas, item)
        
    def update(self):
        coords = self.get_position()
        width  = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if coords[1] <= 0 or coords[3] >= height:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)
    
    def collide(self, pads):
        coords = self.get_position()
        y = (coords[1] + coords[3]) * 0.5
        pad = pads[0]
        coords = pad.get_position()
        self.direction[0] *= -1


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.width  = FRAMEWIDTH
        self.height = FRAMEHEIGHT
        self.canvas = tk.Canvas(self, bg=BGCOLOR,
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()
        
        self.canvas.create_line(self.width / 2, 0,
                                self.width / 2, self.height,
                                fill=HUDCOLOR)
        
        self.score = [0, 0]
        self.text = []
        self.ball = None
        self.ballpad = None
        self.paddle = [None, None]
        self.paddle[0] = Paddle(self.canvas,
                                PADXPOS, 
                                self.height * PADINITSECT / PADSECTION,
                                color=PAD0COLOR)
        self.paddle[1] = Paddle(self.canvas,
                                self.width - PADXPOS, 
                                self.height * PADINITSECT / PADSECTION,
                                color=PAD1COLOR)
        self.pads = {}
        self.pads[self.paddle[0].item] = self.paddle[0]
        self.pads[self.paddle[1].item] = self.paddle[1]
        self.hud = [self.draw_text(FRAMEWIDTH * 1/4, FRAMEHEIGHT / 2, str(self.score[0])),
                    self.draw_text(FRAMEWIDTH * 3/4, FRAMEHEIGHT / 2, str(self.score[1]))]
        self.begin = True
        self.setup_game()
        self.canvas.focus_set()
        # bind keys for player0 moving in both lower & upper case
        self.canvas.bind(   '<w>', lambda _: self.paddle[0].move(-1))
        self.canvas.bind(   '<s>', lambda _: self.paddle[0].move( 1))
        self.canvas.bind(   '<W>', lambda _: self.paddle[0].move(-1))
        self.canvas.bind(   '<S>', lambda _: self.paddle[0].move( 1))
        # for player1 it's easier
        self.canvas.bind(  '<Up>', lambda _: self.paddle[1].move(-1))
        self.canvas.bind('<Down>', lambda _: self.paddle[1].move( 1))
    
    def setup_game(self):
        self.add_ball(self.ballpad)
        self.text = [
                     self.draw_text(FRAMEWIDTH  * 1/6,
                                    FRAMEHEIGHT * 1/6,
                                    'W', HUDSIZE),
                     self.draw_text(FRAMEWIDTH  * 1/6,
                                    FRAMEHEIGHT * 5/6,
                                    'S', HUDSIZE),
                     self.draw_text(FRAMEWIDTH  * 5/6,
                                    FRAMEHEIGHT * 1/6,
                                    '↑', HUDSIZE),
                     self.draw_text(FRAMEWIDTH  * 5/6,
                                    FRAMEHEIGHT * 5/6,
                                    '↓', HUDSIZE),
                     self.draw_text(FRAMEWIDTH  * 1/2,
                                    FRAMEHEIGHT * 3/4,
                                    'START  [space]', HUDSIZE)
                     ]
        self.canvas.bind('<space>', lambda _: self.start_game())
    
    def add_ball(self, ballpad):
        if self.ball is not None:
            dir = self.ball.direction
            self.ball.delete()
        if ballpad == None:
            ball_x = FRAMEWIDTH / 2
            dir = [1, -1]
        elif ballpad == 0:
            ball_x = BALLRESET
            dir[0] = 1 
        elif ballpad == 1:
            ball_x = FRAMEWIDTH - BALLRESET 
            dir[0] = -1
        ball_y = FRAMEHEIGHT / 2
        self.ball = Ball(self.canvas, ball_x, ball_y, dir)
    
    def draw_text(self, x, y, text, size=SCORESIZE):
        font = ('Courier', size)
        return self.canvas.create_text(x, y, text=text, font=font, fill=HUDCOLOR)
    
    def start_game(self):
        self.canvas.unbind('<space>')
        for x in self.text:
            self.canvas.delete(x)
        self.game_loop()
    
    def score_update(self, pad):
        self.ball.speed = None
        self.score[(pad + 1) % 2] += 1
        
        self.canvas.itemconfig(self.hud[0], text=str(self.score[0]))
        self.canvas.itemconfig(self.hud[1], text=str(self.score[1]))
        
        if max(self.score) >= MAXSCORE:
            right_player_wins = self.score.index(max(self.score))
            winner = 'Right' if right_player_wins else 'Left'
            self.draw_text(FRAMEWIDTH  * 1/2,
                           FRAMEHEIGHT * 1/4,
                           '{} player wins!!!'.format(winner), 
                           HUDSIZE)
        else:    
            self.paddle[pad].ball = self.ball
            self.ballpad = pad
            self.ball.direction[0] = -1 if pad else 1 
            self.after(1000, self.setup_game)
    
    def game_loop(self):
        self.check_collisions()
        
        if self.ball.get_position()[0] <= 0:
            self.score_update(0)
        elif self.ball.get_position()[2] >= self.width:
            self.score_update(1)
        else:
            self.ball.update()
            self.after(25, self.game_loop)
    
    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        pads = [self.pads[x] for x in items if x in self.pads]
        if len(pads) > 0:
            self.ball.collide(pads)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('PING PONG')
    game = Game(root)
    game.mainloop()