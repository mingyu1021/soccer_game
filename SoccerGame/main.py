import pygame
import sys
import os
import math
import random

# Pygame 초기화
pygame.init()
pygame.mixer.init()  # 사운드 시스템 초기화

# 게임 상수 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_DURATION = 90  # 90초 경기

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

class Player:
    def __init__(self, x, y, color, controls, is_ai=False):
        self.x = x
        self.y = y
        self.color = color
        self.controls = controls
        self.speed = 5
        self.size = 15
        self.is_ai = is_ai
        self.ai_target_x = x
        self.ai_target_y = y
        
        # 선수 이미지 생성
        self.surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, color, (15, 15), self.size)
        
    def move(self, keys, ball=None):
        """키보드 입력에 따라 선수를 움직입니다."""
        if self.is_ai and ball:
            self.ai_move(ball)
        else:
            if keys[self.controls['up']]:
                self.y = max(self.size, self.y - self.speed)
            if keys[self.controls['down']]:
                self.y = min(SCREEN_HEIGHT - self.size, self.y + self.speed)
            if keys[self.controls['left']]:
                self.x = max(self.size, self.x - self.speed)
            if keys[self.controls['right']]:
                self.x = min(SCREEN_WIDTH - self.size, self.x + self.speed)
                
    def ai_move(self, ball):
        """AI 플레이어의 움직임을 제어합니다."""
        # 공과의 거리 계산
        dx = ball.x - self.x
        dy = ball.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # 공이 가까우면 공을 향해 움직임
        if distance > 20:
            if dx > 0:
                self.x = min(SCREEN_WIDTH - self.size, self.x + self.speed)
            elif dx < 0:
                self.x = max(self.size, self.x - self.speed)
                
            if dy > 0:
                self.y = min(SCREEN_HEIGHT - self.size, self.y + self.speed)
            elif dy < 0:
                self.y = max(self.size, self.y - self.speed)
        else:
            # 공이 가까우면 공을 차려고 시도
            if random.random() < 0.1:  # 10% 확률로 공을 찹니다
                return True
        return False
            
    def draw(self, screen):
        """선수를 화면에 그립니다."""
        screen.blit(self.surface, (self.x - self.size, self.y - self.size))
        
    def get_rect(self):
        """선수의 충돌 영역을 반환합니다."""
        return pygame.Rect(self.x - self.size, self.y - self.size, 30, 30)

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.size = 10
        self.friction = 0.98  # 마찰력
        
        # 공 이미지 생성
        self.surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, WHITE, (10, 10), self.size)
        
    def update(self):
        """공의 물리적 움직임을 업데이트합니다."""
        self.x += self.vx
        self.y += self.vy
        
        # 마찰력 적용
        self.vx *= self.friction
        self.vy *= self.friction
        
        # 벽과의 충돌 처리
        if self.x <= self.size or self.x >= SCREEN_WIDTH - self.size:
            self.vx *= -0.8
            self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
            
        if self.y <= self.size or self.y >= SCREEN_HEIGHT - self.size:
            self.vy *= -0.8
            self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))
            
    def draw(self, screen):
        """공을 화면에 그립니다."""
        screen.blit(self.surface, (self.x - self.size, self.y - self.size))
        
    def get_rect(self):
        """공의 충돌 영역을 반환합니다."""
        return pygame.Rect(self.x - self.size, self.y - self.size, 20, 20)
        
    def kick(self, player_x, player_y, power=10):
        """선수가 공을 찹니다."""
        dx = self.x - player_x
        dy = self.y - player_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 50:  # 충돌 범위 내에 있을 때
            if distance > 0:
                self.vx += (dx / distance) * power
                self.vy += (dy / distance) * power
                return True  # 공을 찼음을 알림
        return False

class Goal:
    def __init__(self, x, y, width, height, side):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.side = side  # 'left' 또는 'right'
        
    def draw(self, screen):
        """골대를 화면에 그립니다."""
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 3)
        
    def check_goal(self, ball):
        """공이 골대 안에 들어갔는지 확인합니다."""
        return (self.x < ball.x < self.x + self.width and 
                self.y < ball.y < self.y + self.height)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
        
    def load_sounds(self):
        """사운드 파일들을 로드합니다."""
        try:
            # 실제 사운드 파일이 없으므로 임시로 빈 사운드 생성
            self.sounds['kick'] = pygame.mixer.Sound(pygame.sndarray.make_sound(
                pygame.surfarray.pixels3d(pygame.Surface((1, 1)))))
            self.sounds['goal'] = pygame.mixer.Sound(pygame.sndarray.make_sound(
                pygame.surfarray.pixels3d(pygame.Surface((1, 1)))))
        except:
            # 사운드 로드 실패시 빈 사운드로 대체
            self.sounds['kick'] = None
            self.sounds['goal'] = None
            
    def play_sound(self, sound_name):
        """사운드를 재생합니다."""
        if self.sounds.get(sound_name):
            try:
                self.sounds[sound_name].play()
            except:
                pass

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("축구 게임")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 게임 상태
        self.score_player1 = 0
        self.score_player2 = 0
        self.game_time = 0  # 초 단위
        self.game_state = "playing"  # "playing", "paused", "game_over"
        
        # 에셋 로드
        self.load_assets()
        
        # 게임 객체 생성
        self.create_game_objects()
        
        # 사운드 매니저
        self.sound_manager = SoundManager()
        
    def load_assets(self):
        """게임 에셋들을 로드합니다."""
        self.assets_path = os.path.join(os.path.dirname(__file__), "assets")
        
        # 이미지 로드 (기본 색상으로 대체)
        self.field_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.field_surface.fill(GREEN)
        
    def create_game_objects(self):
        """게임 객체들을 생성합니다."""
        # 선수 생성 (플레이어2는 AI)
        self.player1 = Player(100, SCREEN_HEIGHT // 2, RED, {
            'up': pygame.K_w,
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d
        })
        
        self.player2 = Player(SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2, BLUE, {
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT
        }, is_ai=True)
        
        # 공 생성
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # 골대 생성
        goal_width = 20
        goal_height = 100
        self.goal1 = Goal(0, SCREEN_HEIGHT // 2 - goal_height // 2, goal_width, goal_height, 'left')
        self.goal2 = Goal(SCREEN_WIDTH - goal_width, SCREEN_HEIGHT // 2 - goal_height // 2, goal_width, goal_height, 'right')
        
    def handle_events(self):
        """이벤트 처리를 담당합니다."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.game_state == "playing":
                        # 스페이스바로 공 차기
                        if self.ball.kick(self.player1.x, self.player1.y):
                            self.sound_manager.play_sound('kick')
                elif event.key == pygame.K_r:
                    if self.game_state == "game_over":
                        self.restart_game()
                        
    def update(self):
        """게임 상태를 업데이트합니다."""
        if self.game_state != "playing":
            return
            
        # 게임 시간 업데이트
        self.game_time += 1 / FPS
        
        # 경기 시간 체크
        if self.game_time >= GAME_DURATION:
            self.game_state = "game_over"
            return
        
        # 키보드 입력 처리
        keys = pygame.key.get_pressed()
        self.player1.move(keys)
        self.player2.move(keys, self.ball)
        
        # AI가 공을 차려고 시도
        if self.player2.ai_move(self.ball):
            if self.ball.kick(self.player2.x, self.player2.y, 6):
                self.sound_manager.play_sound('kick')
        
        # 공 업데이트
        self.ball.update()
        
        # 선수와 공의 충돌 처리
        if self.player1.get_rect().colliderect(self.ball.get_rect()):
            if self.ball.kick(self.player1.x, self.player1.y, 8):
                self.sound_manager.play_sound('kick')
            
        if self.player2.get_rect().colliderect(self.ball.get_rect()):
            if self.ball.kick(self.player2.x, self.player2.y, 8):
                self.sound_manager.play_sound('kick')
            
        # 골 판정
        if self.goal1.check_goal(self.ball):
            self.score_player2 += 1
            self.sound_manager.play_sound('goal')
            self.reset_ball()
        elif self.goal2.check_goal(self.ball):
            self.score_player1 += 1
            self.sound_manager.play_sound('goal')
            self.reset_ball()
            
    def reset_ball(self):
        """공을 중앙으로 리셋합니다."""
        self.ball.x = SCREEN_WIDTH // 2
        self.ball.y = SCREEN_HEIGHT // 2
        self.ball.vx = 0
        self.ball.vy = 0
        
    def restart_game(self):
        """게임을 재시작합니다."""
        self.score_player1 = 0
        self.score_player2 = 0
        self.game_time = 0
        self.game_state = "playing"
        self.reset_ball()
        self.player1.x, self.player1.y = 100, SCREEN_HEIGHT // 2
        self.player2.x, self.player2.y = SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2
        
    def get_winner(self):
        """승자를 결정합니다."""
        if self.score_player1 > self.score_player2:
            return "플레이어 1 승리!"
        elif self.score_player2 > self.score_player1:
            return "플레이어 2 (AI) 승리!"
        else:
            return "무승부!"
        
    def draw(self):
        """화면에 모든 요소를 그립니다."""
        # 배경 그리기
        self.screen.blit(self.field_surface, (0, 0))
        
        # 중앙선 그리기
        pygame.draw.line(self.screen, WHITE, (SCREEN_WIDTH // 2, 0), 
                        (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 3)
        
        # 중앙원 그리기
        pygame.draw.circle(self.screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 50, 3)
        
        # 골대 그리기
        self.goal1.draw(self.screen)
        self.goal2.draw(self.screen)
        
        # 선수 그리기
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        
        # 공 그리기
        self.ball.draw(self.screen)
        
        # 점수 표시
        font = pygame.font.Font(None, 36)
        score_text = f"{self.score_player1} - {self.score_player2}"
        score_surface = font.render(score_text, True, WHITE)
        self.screen.blit(score_surface, (SCREEN_WIDTH // 2 - 50, 20))
        
        # 시간 표시
        remaining_time = max(0, GAME_DURATION - self.game_time)
        time_text = f"남은 시간: {int(remaining_time)}초"
        time_surface = font.render(time_text, True, WHITE)
        self.screen.blit(time_surface, (20, 20))
        
        # 조작법 안내
        if self.game_state == "playing":
            controls_text = "WASD: 플레이어1, 스페이스: 공차기, ESC: 종료"
            controls_surface = font.render(controls_text, True, YELLOW)
            self.screen.blit(controls_surface, (20, SCREEN_HEIGHT - 40))
        elif self.game_state == "game_over":
            # 게임 오버 화면
            winner_text = self.get_winner()
            winner_surface = font.render(winner_text, True, ORANGE)
            self.screen.blit(winner_surface, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            
            restart_text = "R키를 눌러 재시작"
            restart_surface = font.render(restart_text, True, YELLOW)
            self.screen.blit(restart_surface, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2))
        
        pygame.display.flip()
        
    def run(self):
        """메인 게임 루프를 실행합니다."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
