import imutils
import pygame
import cv2
import numpy as np
import pymunk
import pymunk.pygame_util
from pygame.locals import QUIT
import random
from enum import Enum
import time
import database

screen_width, screen_height = 960, 480


class Game:
    def __init__(self, username):
        self.username = username
        ball_sprite = pygame.image.load(
            'sprites/ball.png')  # Добавление спрайта мяча
        ball_size = (40, 40)  # Задаем размер мяча
        self.ball_sprite = pygame.transform.scale(
            ball_sprite, ball_size)

    # Other methods...

    def detect_blue_lines(self, frame, lower_blue, upper_blue, blur_value, threshold_value, dilation_value):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # Определение HSV кода
        # Создание маски на основе
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        kernel = np.ones(
            (dilation_value * 2 + 1, dilation_value * 2 + 1), np.uint8)
        blurred = cv2.GaussianBlur(
            mask, (blur_value * 2 + 1, blur_value * 2 + 1), 0)
        _, thresh = cv2.threshold(
            blurred, threshold_value, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, kernel, iterations=1)

        contours, _ = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Определение конторов
        lines = []
        for contour in contours:
            x1, y1, w, h = cv2.boundingRect(contour)
            x2, y2 = x1 + w, y1 + h
            # Задаем контур каждой отмеченной линии
            lines.append(((x1, y1), (x2, y2)))
        return contours

    class coll_types(Enum):
        BALL = 0
        STATIC = 1
        RING = 2

    def pairwise(self, iterable):
        a = iter(iterable)
        return zip(a, a)

    def create_body_from_lines(self, space, lines, collision_type, is_contour=False):
        if collision_type == self.coll_types.STATIC:
            body_type = pymunk.Body.STATIC
        else:
            body_type = pymunk.Body.KINEMATIC
        body = pymunk.Body(body_type=body_type)
        if is_contour:
            lines = np.squeeze(lines, axis=1)
            new_lines = []
            for p1, p2 in self.pairwise(lines):
                new_lines.append([list(p1), list(p2)])
            lines = new_lines
            body.position = list(lines[0][0])
        else:
            body.position = lines[0][0]

        space.add(body)
        for line in lines:

            shape = pymunk.Segment(body, body.world_to_local(
                line[0]), body.world_to_local(line[1]), 1)
            shape.elasticity = 1  # Эластичность стены
            shape.friction = 0  # Трение стены
            # print(collision_type.value)
            shape.collision_type = collision_type.value
            space.add(shape)
        return body

    def nothing(self, x):
        pass

    def create_ball(self, space, position):  # Физичное создание мяча
        body = pymunk.Body(1, 100, body_type=pymunk.Body.DYNAMIC)
        body.position = random.randint(
            50, screen_width - 50), random.randint(50, screen_height - 50)
        shape = pymunk.Circle(body, 20)
        shape.elasticity = 1
        shape.friction = 0.0
        direction = random.choice([(1, 1), (-1, 1), (1, -1), (-1, -1)])
        speed = 300
        body.velocity = direction[0] * speed, direction[1] * speed
        space.add(body, shape)
        return shape

    def draw_segment_body(self, screen, body, color, width=1):
        for line in body.shapes:
            moved_a = body.position + line.a
            moved_b = body.position + line.b

            p1 = int(moved_a.x), int(screen_height - moved_a.y)
            p2 = int(moved_b.x), int(screen_height - moved_b.y)

            pygame.draw.lines(screen, color, False, [p1, p2], width=width)

    def main(self):
        start = time.time()
        self.score = 0
        pygame.init()
        font = pygame.font.Font(None, 40)

        self.collision_sound = pygame.mixer.Sound(
            'sound/hit_sound.wav')  # Замените 'collision_sound.wav' на ваш звуковой файл
        screen = pygame.display.set_mode((screen_width, screen_height))
        clock = pygame.time.Clock()
        space = pymunk.Space()
        space.gravity = 0, 0

        cv2.namedWindow('Parameter Adjust')
        # ---------ЗНАЧЕНИЯ ПРОЕКТОРА---------
        cv2.createTrackbar('Threshold', 'Parameter Adjust',
                           108, 255, self.nothing)
        cv2.createTrackbar('Blur', 'Parameter Adjust', 3, 10, self.nothing)
        cv2.createTrackbar('Dilation', 'Parameter Adjust', 1, 10, self.nothing)
        cv2.namedWindow('Blue Color Adjust')
        # ---------ЗНАЧЕНИЕ ПРОЕКТОРА---------
        cv2.createTrackbar('Lower Hue', 'Blue Color Adjust',
                           97, 255, self.nothing)
        cv2.createTrackbar('Upper Hue', 'Blue Color Adjust',
                           113, 255, self.nothing)

        cap = cv2.VideoCapture(0)

        border_lines = [
            ((screen_width, screen_height), (0, screen_height)),
            ((screen_width, 0), (screen_width, screen_height)),
            ((0, screen_height), (0, 0)),
            ((0, 0), (screen_width, 0))
        ]

        # Границы игрового окна
        additional_border_lines = [
            ((100, 100), (200, 100)),
            ((200, 100), (200, 200)),
            ((200, 200), (100, 200)),
            ((100, 200), (100, 100))
        ]
        static_lines = []
        static_lines.append(self.create_body_from_lines(
            space, border_lines, self.coll_types.STATIC))

        ball = None

        ring_x = screen_width / 2 - 50  # начальное положение x
        ring_y = 60
        ring_h = 50
        ring_w = 100

        def move(body, dt):
            body.position += body.velocity
            if body.position.x <= 0 or body.position.x + ring_w >= screen_width:
                body.velocity *= -1
                body.position += 2 * body.velocity

        ring_lines = [
            ((ring_x, ring_y - ring_h), (ring_x +
             ring_w, ring_y - ring_h)),  # Нижняя часть
            ((ring_x + ring_w, ring_y - ring_h),
             (ring_x + ring_w, ring_y)),  # Правая часть
            ((ring_x, ring_y), (ring_x, ring_y - ring_h))  # Левая часть
        ]
        ring = self.create_body_from_lines(
            space, ring_lines, self.coll_types.RING)
        ring.velocity = pymunk.Vec2d(5, 0)
        ring.position_func = move

        def ball_window_collision(arbiter, space, data):
            ball_shape, border_shape = arbiter.shapes
            # Получаем текущее направление движения мяча
            velocity = ball_shape.body.velocity
            # Добавляем случайное отклонение к новому направлению
            velocity = (velocity[0] + random.uniform(-50, 50),
                        velocity[1] + random.uniform(-50, 50))
            # Устанавливаем новое направление движения мяча
            ball_shape.body.velocity = velocity
            self.collision_sound.play()  # Воспроизведение звука столкновения
            return True

        def ball_ring_collision(arbiter, space, data):
            ball_shape, ring_shape = arbiter.shapes
            velocity = ball_shape.body.velocity
            velocity = (velocity[0] + random.uniform(-50, 50),
                        velocity[1] + random.uniform(-50, 50))
            ball_shape.body.velocity = velocity
            self.score += 1
            return True

        ring_collision_handler = space.add_collision_handler(
            self.coll_types.BALL.value, self.coll_types.RING.value)
        ring_collision_handler.pre_solve = ball_ring_collision
        collision_handler = space.add_collision_handler(
            self.coll_types.BALL.value, self.coll_types.STATIC.value)
        collision_handler.pre_solve = ball_window_collision

        running = True
        # handler = space.add_collision_handler(0, 0)
        # handler.pre_solve = collision_handler
        while running:

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            lower_blue = np.array(
                [cv2.getTrackbarPos('Lower Hue', 'Blue Color Adjust'), 50, 50])
            upper_blue = np.array(
                [cv2.getTrackbarPos('Upper Hue', 'Blue Color Adjust'), 255, 255])

            ret, frame = cap.read()
            if not ret:
                break
            frame = imutils.resize(frame, width=960, height=480)
            pts1 = np.float32([[115, 278], [172, 654],
                               [880, 634], [896, 244]])
            pts2 = np.float32([[0, 0], [0, 480],
                               [960, 480], [960, 0]])

            # Apply Perspective Transform Algorithm
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            result = cv2.warpPerspective(frame, matrix, (960, 480))
            threshold_value = cv2.getTrackbarPos(
                'Threshold', 'Parameter Adjust')
            blur_value = cv2.getTrackbarPos('Blur', 'Parameter Adjust')
            dilation_value = cv2.getTrackbarPos('Dilation', 'Parameter Adjust')
            result = cv2.flip(result, 0)

            cv2.imshow('Original', frame)  # Initial Capture
            cv2.imshow("Result", result)

            lines = self.detect_blue_lines(result, lower_blue, upper_blue, blur_value, threshold_value,
                                           dilation_value)

            if len(lines) != 0:
                for line in lines:
                    detected_lines = self.create_body_from_lines(
                        space, line, self.coll_types.STATIC, True)
                    static_lines.append(detected_lines)

            if ball is None:
                ball = self.create_ball(space, (100, 100))

            space.step(1 / 60)
            screen.fill((0, 0, 0))
            for body in static_lines:
                self.draw_segment_body(screen, body, (0, 0, 0))

            self.draw_segment_body(screen, ring, (255, 0, 0), 5)

            if ball is not None:
                ball_pos = ball.body.position
                # ball_rect = self.ball_sprite.get_rect(
                #     center=(int(ball_pos.x), int(screen_height - ball_pos.y)))

                rot_angle = (time.time()) * 30 % 360
                print(rot_angle)
                # print(rot_angle)
                rotated_ball = pygame.transform.rotate(
                    self.ball_sprite, rot_angle)
                ball_rect = rotated_ball.get_rect(
                    center=(int(ball_pos.x), int(screen_height - ball_pos.y)))

                screen.blit(rotated_ball, ball_rect)

            clock.tick(60)
            text = font.render("Score: " + str(self.score), 1, (255, 255, 255))
            screen.blit(text, (0, 0))
            pygame.display.flip()

            pygame.display.update()
        database.Login().add_update(
            username=self.username, score=self.score)
        pygame.quit()


if __name__ == "__main__":
    game = Game("Player1")
    game.main()
