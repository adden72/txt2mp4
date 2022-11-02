from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import datetime
import subprocess

adjust_frame = 29

# Base 디렉토리
base_dir='E:/projects/2022/prisma/txt2mp4'
base_dir='/root/dc22/server/cv2'

# def img2mp4(paths, pathOut , fps =10 ) :
#     import cv2
#     frame_array = []
#     for idx , path in enumerate(paths) :
#         img = cv2.imread(path)
#         height, width, layers = img.shape
#         size = (width,height)
#         frame_array.append(img)
#     out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
#     for i in range(len(frame_array)):
#         # writing to a image array
#         out.write(frame_array[i])
#     out.release()
#
#
def imgsTOmp4(cnt_clips, fps=10):
    frames_img=[]
    h = 0
    w = 0

    for idx in range(cnt_clips):
        image_file = f'{base_dir}/images/image_text_{idx+1}.jpg'
        print(f'loading image {image_file}...')
        img = cv2.imread(image_file)
        h, w, layers = img.shape
        frames_img.append(img)

    mp4_file = f'{base_dir}/image_text_{idx + 1}.mp4'

    mp4_fp = cv2.VideoWriter(mp4_file, cv2.VideoWriter_fourcc(*'X264'), 20, (w, h))
    for i in range(len(frames_img)):
        print(f'write image {i} -- {mp4_file}')
        mp4_fp.write(frames_img[i])
    mp4_fp.release()



def get_images(draw_text, font_size, font_id=0, font_dir='/root/dc22/server/font'):
    rtn_images = []

    list_font = ['1_Font1_Arial.ttf', '2_Font2_SUIT Regular.ttf', '3_Font3_IBM Plex Sans KR.ttf', '4_Font4_Gulim.ttf',
                 '5_Font5_MGungJeong.ttf', '6_HYwulM.ttf']
    font = ImageFont.truetype(f'{font_dir}/{list_font[font_id]}', font_size)
    w, h = font.getsize(draw_text)

    canvas = Image.new('RGB', (w, h), 'white')

    draw = ImageDraw.Draw(canvas)
    draw.text((0, 0), draw_text, 'black', font)

    canvas.save(f'{font_dir}/test.png', 'PNG')

    band_y = 200
    band_height=40
    band_end =1920
    band_start = 0
    band_speed = 4
    idx = 0
    for i in range(0, w, band_speed):
        img_band = Image.new('RGB', (1920, 1080))
        draw = ImageDraw.Draw(img_band)

        draw.rectangle(((0, band_y),(band_end, band_y+band_height )), fill=(255,255,255), outline=(0,255, 0))
        text_band_start_x = band_start- 1920 if band_start > 1920  else 0
        text_band_end_x = text_band_start_x + 1920

        test_band_paste_x = 0 if band_start > 1920 else 1920 - band_start

        # 폰트로 그린 이미지중에 앞(x:0)에서부터 작게 뜯어 내다가 점점 크게 뜯고, band_start가 1920보다 커지면 앞x값이 band_start-1920이 되며 뜯어낸다
        img_text=canvas.crop((text_band_start_x, 0, text_band_end_x ,font_size))

        # 백그라운드 띠위에 폰트로 그린 이미지를 x값이 1920부터 앞으로 이동 하여 0에 수렴하여 계속 그림
        img_band.paste(img_text, (test_band_paste_x, band_y))

        band_start += band_speed
        idx += 1

        print(f'{idx}, {i} = {band_start}/{w}')

        img_band.save(f'{font_dir}/images/image_text_{idx}.jpg', 'JPEG')

        rtn_images.append(img_band)



    # idx =0
    # str_cmd ='C:\"Program Files (x86)"\SWFTools\jpeg2swf.exe -o test.swf '
    # for i in range(0, w, band_speed):
    #     idx += 1
    #     str_cmd += f'image_text_{idx}.jpg '
    #
    # print(str_cmd)
    return rtn_images, idx

_CODEC = 'MJPG'

def cvt_font4div(draw_text, font_size, font_id=0, font_dir='/root/dc22/server/font'):

    now_start = datetime.datetime.now()
    rtn_images = []

    list_font = ['1_Font1_Arial.ttf', '2_Font2_SUIT Regular.ttf', '3_Font3_IBM Plex Sans KR.ttf', '4_Font4_Gulim.ttf',
                 '5_Font5_MGungJeong.ttf', '6_HYwulM.ttf']

    #사용할 폰드 로딩
    font = ImageFont.truetype(f'{font_dir}/{list_font[font_id]}', font_size)
    w_font, h_font = font.getsize(draw_text)

    #사용할 로고이미지로딩
    #img_logo = Image.open(f'{font_dir}/ci_skylife_v2_40.png').convert("RGBA")   # 투명이 검정으로 변함
    img_logo = Image.open(f'{font_dir}/ci_skylife_v2_40.jpg')

    #투명이 검정배경이 되는 처리로직
    ## 반대처리 였군.....(흰색을 투명으로)
    # img_datas = img_logo.getdata()
    # img_datas_tmp = []
    # cutOff = 255
    # for item in img_datas:
    #     tmp_val = (255, 255, 255, 0) if item[0] >= cutOff and item[1]>= cutOff and item[2]>=cutOff else item
    #     img_datas_tmp.append(tmp_val)
    #
    # img_datas.putdata(img_datas_tmp)


    w_logo=img_logo.width
    h_logo=img_logo.height

    print(f'** Font image create....{w_font}*{h_font}')
    # 로그 + 폰트 이미지사이즈의 이미지 생성
    canvas_font_src = Image.new('RGB', (w_font+(w_logo*2), h_font), 'white')
    w_font_log, h_font_logo = canvas_font_src.size
    draw_font_src = ImageDraw.Draw(canvas_font_src)

    # 로고 이미지를 배치
    canvas_font_src.paste(img_logo, (0, 7))
    canvas_font_src.paste(img_logo, (w_font+w_logo, 7))

    # 폰트이미지를 배치한다.
    draw_font_src.text((w_logo, 0), draw_text, 'black', font)

    # canvas_font_src.save(f'{font_dir}/test.png', 'PNG')



    band_y = 1000
    band_height=50
    band_end =1920
    band_start = 0
    band_speed = 4
    mp4_file = f'{font_dir}/cvt_font4{_CODEC}.mp4'
    mp4_fp = cv2.VideoWriter(mp4_file, cv2.VideoWriter_fourcc(*_CODEC), 30, (band_end, 1080))
    idx = 0
    img_band_src = Image.new('RGB', (1920, 1080), (51, 102, 0))
    draw_src = ImageDraw.Draw(img_band_src)
    draw_src.rectangle(((0, band_y), (1920, band_y + band_height)), fill=(255, 255, 255))

    for i in range(0, w_font_log, band_speed):
        img_band = img_band_src.copy()

        #font이미지에서 뜯어낼
        text_band_start_x = band_start- 1920 if band_start > 1920  else 0
        text_band_end_x = text_band_start_x + 1920

        test_band_paste_x = 0 if band_start > 1920 else 1920 - band_start

        # 폰트로 그린 이미지중에 앞(x:0)에서부터 작게 뜯어 내다가 점점 크게 뜯고, band_start가 1920보다 커지면 앞x값이 band_start-1920이 되며 뜯어낸다
        img_text=canvas_font_src.crop((text_band_start_x, 0, text_band_end_x ,h_font))

        # 백그라운드 띠위에 폰트로 그린 이미지를 x값이 1920부터 앞으로 이동 하여 0에 수렴하여 계속 그림
        img_band.paste(img_text, (test_band_paste_x, band_y))

        band_start += band_speed
        idx += 1

        # print(f'{idx}, {i} = {band_start}/{w_font_log}')

        numpy_image=np.array(img_band)

        cv2_image=cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

        #특수효과 <블러, 가우시안블러효과>
        # cv2_image=cv2.GaussianBlur(cv2_image, ksize = (9, 9),sigmaX = 0)
        # cv2_image, color_tmp = cv2.pencilSketch(cv2_image, sigma_s=60, sigma_r=0.05, shade_factor=0.015)

        mp4_fp.write(cv2_image)

    now_end1 = datetime.datetime.now()
    now_gap = now_end1 - now_start
    print(f'** images --> mp4 pass1<{idx}> time: {now_gap}')

    # 여기서부터는 폰트이미지 끝이 오른쪽 화면 바깥에서 안쪽으로 들어오는 이미지를 처리한다.
    text_band_end_x = w_font_log
    while((band_start-1920) < w_font_log):
        img_band = img_band_src.copy()
        text_band_start_x = band_start - 1920

        # print(f'{idx}= {text_band_start_x}/{w_font_log}')

        img_text = canvas_font_src.crop((text_band_start_x, 0, text_band_end_x, h_font))


        img_band.paste(img_text, (0, band_y))
        numpy_image = np.array(img_band)
        cv2_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
        mp4_fp.write(cv2_image)

        band_start += band_speed
        idx += 1

    mp4_fp.release()

    now_end2 = datetime.datetime.now()
    now_gap = now_end2 - now_end1
    now_gap_pass = now_end2 - now_start

    print(f'** images --> mp4 pass2<{idx}> time: {now_gap}')
    print(f'** images --> mp4 pass time: {now_gap_pass}')

    subprocess.call(f'{base_dir}/ffmpeg.sh {base_dir}/cvt_font4div.mp4 {base_dir}/0018_001.swf', shell=True)

    now_end3 = datetime.datetime.now()
    now_gap_pass = now_end3 - now_start
    print(f'** images --> mp4 ffmpeg time: {now_end3 - now_end2}')
    print(f'** images --> mp4 total time: {now_gap_pass}')




#
# rtn, cnt_clips= get_images('본 채널은 스카이라이프 백석센터에서 송출되고 있는 테스트 채널입니다.  방송 상태가 고르지 못할 경우 미디어운용팀으로 연락 주시기 바랍니다. 미디어운용팀 MCR 031-950-8754   - skylife -'
#            , 40, 0, font_dir=base_dir)


cvt_font4div(' 본 채널은 스카이라이프 백석센터에서 송출되고 있는 테스트 채널입니다.  방송 상태가 고르지 못할 경우 미디어운용팀으로 연락 주시기 바랍니다. 미디어운용팀 MCR 031-950-8754 '
           , 40, 0, font_dir=base_dir)


# imgsTOmp4(cnt_clips, '')
# from img2swf import writeSwf
#
# writeSwf(f'{font_dir}/image_swf.swf', rtn)


