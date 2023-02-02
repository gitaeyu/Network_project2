import random
import os
import threading
import time
import pygame
import sys

class monster:
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self.x = 800                    # x축 800 맵 크기에서 시작
        self.y = 400-height             # y축 400 맵 크기에서 이미지 높이 뺀 만큼
        self.address = 'imeage/{0}.png'.format(self.name)





def main2():
    a0 = monster("치코리", 69, 60)
    a1 = monster("피카츄", 57, 60)
    a2 = monster("꼬부기", 59, 60)
    a3 = monster("버터플", 65, 60)
    a4 = monster("독충이", 60, 60)

    pygame.init()
    pygame.display.set_caption('Jumping dino')
    MAX_WIDTH = 800  # 스크린 가로 크기
    MAX_HEIGHT = 400  # 스크린 세로 크기

    monster_list = [a0.address, a1.address, a2.address, a3.address, a4.address]

    Small_font = pygame.font.SysFont(None, 40)
    # set screen, fps
    screen = pygame.display.set_mode((MAX_WIDTH, MAX_HEIGHT))
    # 게임이 실행될 창을 생성 (가로 800 X 세로 400)
    # 이렇게 생성된 창에 데이터를 추가하는 식으로 제작할 것
    fps = pygame.time.Clock()
    # 프레임을 조정하기 위한 변수를 생성
    # 화면을 초당 몇 번을 출력하는지


    # dino
    imgDino1 = pygame.image.load('imeage/dino1.png')
    imgDino2 = pygame.image.load('imeage/dino2.png')
    dino_height = imgDino1.get_size()[1]
    dino_bottom = MAX_HEIGHT - dino_height
    dino_x = 50                 # 공룡의 X축 위치
    dino_y = dino_bottom        # 공룡의 Y축 위치
    jump_top = 200              # 점프시 최고점
    leg_swap = True             # 공룡 사진 변경을 위한 변수
    is_bottom = True            # 달리고 있는지 알려주는 변수
    is_go_up = False            # 공룡 위로 올라가고 있는지 알려주는 변수

    # tree######################
    imgTree = pygame.image.load(monster_list[random.randrange(5)])              # 나무 사진 불러오기
    tree_height = imgTree.get_size()[1]                 # 나무 세로 길이
    tree_x = MAX_WIDTH                                  # 나무 X축 위치 설정
    tree_y = MAX_HEIGHT - tree_height                   # 나무 Y축 위치 설정



    # 화면 표시
    score = 1
    hurdle = 0
    life = 3
    # message_score = Small_font.render("Score : {0}".format(score), True, (0, 0, 0))  # 스코어
    # message_life = Small_font.render("LIFE : {0}".format(life), True, (0, 0, 0))  # life

    while True:
        imgTree = pygame.image.load(monster_list[random.randrange(5)])
        screen.fill((255, 255, 255))                    # 스크린 채울 색깔 설정 RGB # 흰색 화면 출력
        message_score = Small_font.render("Score: {}".format(score), True, (0, 0, 0))  # 스코어
        message_life = Small_font.render("LIFE : {}".format(life), True, (0, 0, 0))  # dino_y
        screen.blit(message_score, (630, 30))  # 화면상에 스코어 표시
        screen.blit(message_life, (100, 30))  # 화면상에 life 표시

        score += 1

        # event check
        for event in pygame.event.get():                # 사용자가 무언가를 했다면(마우스, 키보드 클릭 등)
            if event.type == pygame.QUIT:               # X 버튼을 눌렀다면
                pygame.quit()                           # 게임 멈추기
                sys.exit()                              # 프로그램 종료
            elif event.type == pygame.KEYDOWN:          # 키보드를 클릭 했다면
                if is_bottom:                           # 맨아래, 즉 달리는 중이라면?
                    is_go_up = True                     # 올라가고 있는 상태 변수를 참으로 변경
                    is_bottom = False                   # 달리는 상태 변수를 거짓으로 변경

        # dino move
        if is_go_up:                                    # 올라가고 있다면
            dino_y -= 10                                # 공룡이 위쪽으로 10만큼 올라간다
        elif not is_go_up and not is_bottom:            # 내려가고 있다면
            dino_y += 10                                # 공룡이 아래쪽으로 10만큼 내려간다

        # dino top and bottom check
        if is_go_up and dino_y <= jump_top:             # 공룡이 최대 높이 이하에 위치한다면
            is_go_up = False                            # 내려가는 상태 변수가 참이 된다

        if not is_bottom and dino_y >= dino_bottom:     # 공룡이 최저 높이 이상에 위치한다면
            is_bottom = True                            # 달리고 있는 상태 변수가 참이 된다.
            dino_y = dino_bottom                        # 공룡의 y축 중심은 최저 높이로 변경 된다.

        # tree move
        tree_x -= 10.0                                  # 나무가 왼쪽으로 10만큼 이동한다.
        if tree_x <= 0:                                 # 나무가 창 왼쪽으로 나갔다면
            tree_x = MAX_WIDTH                          # 창 오른쪽으로 보낸다.

        if dino_x - tree_x >= 10 and dino_y < 257:
            hurdle += 1

        if dino_x - tree_x == 0 and dino_y > 257:
            life -= 1

        if life == 0:
            pygame.init()
            pygame.quit()
            return score

        # draw tree
        screen.blit(imgTree, (tree_x, tree_y))          # 스크린에 나무를 띄운다.

        # draw dino
        if leg_swap:                                    # 2번 사진이라면
            screen.blit(imgDino1, (dino_x, dino_y))     # 1번 사진으로 바꾼다
            leg_swap = False                            # 1번 사진이 나오고 있는 상태임을 표시한다
        else:
            screen.blit(imgDino2, (dino_x, dino_y))     # 2번 사진으로 바꾼다
            leg_swap = True                             # 1번 사진이 나오고 있는 상태임을 표시한다

        # update
        pygame.display.update()                         # 앞선 기작으로 변한 상태가 스크린에 보이도록 업데이트를 해주는 코드
        fps.tick(60)                                    # 화면 업데이트가 초당 30번 실행

# print(main2())