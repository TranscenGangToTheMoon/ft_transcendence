# Textual imports
from textual.geometry   import Offset
from textual.widget     import Widget

# Local imports
from classes.utils.config   import Config

class Ball(Widget):
    def __init__(self):
        super().__init__()
        self.styles.layer = "3"
        self.styles.width = Config.Ball.width
        self.styles.height = Config.Ball.height
        self.styles.background = "white"
        self.speed = Config.Ball.speed
        self.offset = Offset(Config.Playground.width / 2 - 1, Config.Playground.height / 2 - 1)


    def render(self):
        # return "▄▄\n▀▀"
        return ""
####
    # def handle_wall_bounce(self):
    #     ball_pos_y = self.ball.position.y
    #     if ball_pos_y <= 0:
    #         self.ball.position.y = - ball_pos_y
    #         self.ball.speed_y = - self.ball.speed_y
    #         print('bouncing up', flush=True)
    #     elif ball_pos_y + self.ball.size >= self.canvas.y:
    #         self.ball.position.y -= (ball_pos_y + self.ball.size) - self.canvas.y
    #         self.ball.speed_y = - self.ball.speed_y
    #         print('bouncing down', flush=True)
    #
    # def handle_goal(self):
    #     if self.ball.position.x + self.ball.size < 0:
    #         self.score(self.match.teams[1])
    #     elif self.ball.position.x > self.canvas.x:
    #         self.score(self.match.teams[0])
    #
    # def calculateImpactPosition(self, ballY, paddleY, paddleHeight):
    #     relativeY = (paddleY + paddleHeight / 2) - ballY
    #     return relativeY / (paddleHeight / 2)
    #
    # def calculateNewBallDirection(self, paddleY):
    #     impactPosition = self.calculateImpactPosition(self.ball.position.y + self.ball.size / 2, paddleY, Racket.height)
    #     bounceAngle = impactPosition * self.max_bounce_angle
    #
    #     speed = self.ball.speed
    #     xNewSpeed = speed * math.cos(bounceAngle)
    #     yNewSpeed = speed * -math.sin(bounceAngle)
    #     self.ball.speed_x = -xNewSpeed if self.ball.speed_x < 0 else xNewSpeed
    #     self.ball.speed_y = yNewSpeed
    #
    # def handle_racket_bounce(self, racket):
    #     if (racket.blockGlide):
    #         self.ball.speed_y = -self.ball.speed_y
    #         self.ball.direction_y = -self.ball.direction_y
    #         if (abs(self.ball.position.y - (racket.position.y + racket.height)) <
    #                 abs(self.ball.position.y - (racket.position.y))):
    #             self.ball.position.y = racket.position.y + racket.height
    #         else:
    #             self.ball.position.y = racket.position.y - self.ball.size
    #     else:
    #         self.ball.speed_x = -self.ball.speed_x
    #         self.ball.direction_x = -self.ball.direction_x
    #         self.ball.increment_speed(self.max_ball_speed, self.speed_increment)
    #         self.calculateNewBallDirection(racket.position.y)
    #
    # def handle_racket_collision(self, racket):
    #     ball_is_right_from_racket = self.ball.position.x < racket.position.x + racket.width and self.ball.position.x > racket.position.x
    #     ball_is_left_from_racket = self.ball.position.x + self.ball.size > racket.position.x and self.ball.position.x + self.ball.size < racket.position.x + racket.width
    #     is_ball_y_in_paddle_range = self.ball.position.y + self.ball.size > racket.position.y and self.ball.position.y < racket.position.y + racket.height
    #
    #     if (ball_is_left_from_racket == True or ball_is_right_from_racket == True) and is_ball_y_in_paddle_range == True:
    #         self.handle_racket_bounce(racket)
    #         self.ball.last_racket_touched = racket.player
    #         if racket.player.team == self.match.teams[0]:
    #             self.last_racket_touched_team_a = racket.player
    #         else:
    #             self.last_racket_touched_team_b = racket.player
    #         if (not racket.blockGlide):
    #             if (self.ball.position.x + self.ball.size > racket.position.x and
    #                     self.ball.position.x + self.ball.size < racket.position.x + racket.width
    #             ):
    #                 self.ball.position.x = racket.position.x - self.ball.size;
    #             else:
    #                 self.ball.position.x = racket.position.x + racket.width;
    #     else:
    #         is_ball_x_in_racket_range = self.ball.position.x < racket.position.x + racket.width and self.ball.position.x + self.ball.size > racket.position.x
    #         if (is_ball_x_in_racket_range):
    #             racket.blockGlide = True
    #         else:
    #             racket.blockGlide = False
    #
    # def update(self):
    #     if (self.last_update == 0):
    #         self.last_update = time.perf_counter()
    #     time_delta = time.perf_counter() - self.last_update
    #     self.last_update = time.perf_counter()
    #     for racket in self.rackets:
    #         racket.update(self.ball.size, self.canvas.y, time_delta)
    #     self.ball.position.x += self.ball.speed_x * time_delta
    #     self.ball.position.y += self.ball.speed_y * time_delta
    #     self.handle_wall_bounce()
    #     for racket in self.rackets:
    #         self.handle_racket_collision(racket)
    #     self.send_game_state()
    #     self.handle_goal()