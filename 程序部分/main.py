"""
Strinona Theme Desktop Clock
卡拉彼丘桌面时钟

Copyright (C) 2024 Debeko
版权所有 (C) 2024 Debeko

	This program is free software: you can redistribute it and modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
This program is distributed in the hope that it will be useful , but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the GNU General Public License for more details.
	You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
	本程序为自由软件：你可以根据自由软件基金会发布的GNU通用公共许可协议第三版或更新版本的规定对本程序进行再分发和修改。我们希望分发的这款程序对你有所帮助，但是我们不提供任何保证；也不提供任何对可销售性和适用于特定目的的默示保证。详情请查阅GNU通用公共许可协议。
	你应已随同本程序收到一份GNU通用公共许可协议的副本，如未收到，请查阅 http://www.gnu.org/licenses/

"""

from machine import SPI, Pin
from lcd12864 import SPI_LCD12864
from DS1302 import DS1302
import time
import urandom

# 图像与文字显示数据
from image import Michele, Kokona, Alarm_Weekday, Alarm_Weekend, Alarm_OFF, L_0, L_1, L_2, L_3, L_4, L_5, L_6, L_7, L_8, L_9, L_Separorat, S_0, S_1, S_2, S_3, S_4, S_5, S_6, S_7, S_8, S_9, S_Separator, Meow, Emoticon_01, Emoticon_02, Emoticon_03, Emoticon_04, Emoticon_05, Emoticon_06, Emoticon_07, Emoticon_08, Emoticon_09, Emoticon_10, Emoticon_11

# LCD12864屏幕
spi = SPI(1, baudrate=1_000_000, polarity=1, phase=1)
cs = Pin(9, Pin.OUT, value=0)
lcd = SPI_LCD12864(spi=spi, cs=cs)

# DS1302时钟
ds1302 = DS1302(21, 20, 19)

# 按钮
button_add = Pin(2, Pin.IN, Pin.PULL_UP)
button_sub = Pin(3, Pin.IN, Pin.PULL_UP)
button_m = Pin(4, Pin.IN, Pin.PULL_UP)
button_c = Pin(5, Pin.IN, Pin.PULL_UP)

# 背光（GP12）、音频控制（GP16~GP18）
gp12 = Pin(12, Pin.OUT)
gp16 = Pin(16, Pin.OUT)
gp17 = Pin(17, Pin.OUT)
gp18 = Pin(18, Pin.IN, Pin.PULL_DOWN)

# 按钮状态
last_state_add = button_add.value()
last_state_sub = button_sub.value()
last_state_m = button_m.value()
last_state_c = button_c.value()

# 功能状态
STATE_MAIN = 'main'
STATE_COUNTDOWN = 'countdown'

# 初始状态为时钟与闹钟模式
current_state = STATE_MAIN

# 配置文件（读）
def read_config():
    config = {}
    with open('config.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            if '=' in line:
                key, value = line.strip().split('=')
                config[key] = value
    return config

# 配置文件（写）
def write_config(config):
    with open('config.txt', 'w') as file:
        for key, value in config.items():
            file.write(f"{key}={value}\n")

# 屏幕显示内容
def draw_icon(lcd, icon, x, y):
    for row_idx, row in enumerate(icon):
        for col_idx, pixel in enumerate(row):
            if pixel:
                lcd.pixel(x + col_idx, y + row_idx, 1)

# 时间部分
def update_display(config, colon_on):
    date_time = ds1302.Now()
    lcd.clear()
    
    year, month, day, hour, minute, second, weekday = map(int, date_time)
    
    # 上下午图片切换：上午心夏、下午米雪儿
    if hour < 12:
        draw_icon(lcd, Kokona, 0, 0)
    else:
        draw_icon(lcd, Michele, 0, 0)
    
    # 时间
    display_time(hour, minute, 65, 26, lcd, colon_on)
    
    # 日期
    display_date(day, month, year, 56, 43, lcd)
    
    # 闹钟状态
    alarm_status = config['AlarmStatus']
    if alarm_status == 'Weekday':
        draw_icon(lcd, Alarm_Weekday, 80, 9)
    elif alarm_status == 'Weekend':
        draw_icon(lcd, Alarm_Weekend, 80, 9)
    else:
        draw_icon(lcd, Alarm_OFF, 80, 9)
    
    # 刷新屏幕显示
    lcd.update()

# 显示时间
def display_time(hour, minute, x, y, lcd, colon_on):
    tens_hour = hour // 10
    units_hour = hour % 10
    tens_minute = minute // 10
    units_minute = minute % 10
    
    # 小时
    draw_icon(lcd, L_0 if tens_hour == 0 else globals()[f"L_{tens_hour}"], x, y)
    draw_icon(lcd, L_0 if units_hour == 0 else globals()[f"L_{units_hour}"], x + 10, y)
    
    # 冒号
    if colon_on:
        draw_icon(lcd, L_Separorat, x + 20, y)
    
    # 分钟
    draw_icon(lcd, L_0 if tens_minute == 0 else globals()[f"L_{tens_minute}"], x + 30, y)
    draw_icon(lcd, L_0 if units_minute == 0 else globals()[f"L_{units_minute}"], x + 40, y)

# 显示日期
def display_date(day, month, year, x, y, lcd):

    year_last_two_digits = year % 100
    
    # 年
    tens_year = year_last_two_digits // 10
    units_year = year_last_two_digits % 10
    draw_icon(lcd, S_0 if tens_year == 0 else globals()[f"S_{tens_year}"], x, y)
    draw_icon(lcd, S_0 if units_year == 0 else globals()[f"S_{units_year}"], x + 9, y)
    
    # 月
    tens_month = month // 10
    units_month = month % 10
    draw_icon(lcd, S_0 if tens_month == 0 else globals()[f"S_{tens_month}"], x + 27, y)
    draw_icon(lcd, S_0 if units_month == 0 else globals()[f"S_{units_month}"], x + 36, y)
    
    # 日
    tens_day = day // 10
    units_day = day % 10
    draw_icon(lcd, S_0 if tens_day == 0 else globals()[f"S_{tens_day}"], x + 54, y)
    draw_icon(lcd, S_0 if units_day == 0 else globals()[f"S_{units_day}"], x + 63, y)
    
    # 分隔短杠
    draw_icon(lcd, S_Separator, x + 18, y)
    draw_icon(lcd, S_Separator, x + 45, y)

# 按钮操作
def check_buttons(config, total_minutes, total_seconds, paused):
    global last_state_add, last_state_sub, last_state_m, last_state_c
    
    if not button_add.value() and button_add.value() != last_state_add:
        print("Add")
        if current_state == STATE_MAIN:
            # 修改闹钟状态（关、工作日时间、休息日时间）
            states = ['OFF', 'Weekday', 'Weekend']
            current_index = states.index(config['AlarmStatus'])
            config['AlarmStatus'] = states[(current_index + 1) % len(states)]
            write_config(config)
            # 按下亮屏
            gp12.value(1)
            update_display(config, True)
            time.sleep(5)
            gp12.value(0)
        elif current_state == STATE_COUNTDOWN:
            # 分钟加
            if total_minutes < 59:
                total_minutes += 1
                total_seconds = total_minutes * 60
                # 按下亮屏（有点bug，建议注释掉）
                gp12.value(1)
                time.sleep(1)
                gp12.value(0)
    
    if not button_sub.value() and button_sub.value() != last_state_sub:
        print("Sub")
        if current_state == STATE_MAIN:
            # 修改背光状态
            config['Backlight'] = 'off' if config['Backlight'] == 'on' else 'on'
            write_config(config)
        elif current_state == STATE_COUNTDOWN:
            # 分钟减
            if total_minutes > 1:
                total_minutes -= 1
                total_seconds = total_minutes * 60
                 # 按下亮屏（有点bug，建议注释掉）
                gp12.value(1)
                time.sleep(1)
                gp12.value(0)
    
    if not button_m.value() and button_m.value() != last_state_m:
        print("M")
        if current_state == STATE_MAIN:
            # 切换模式：倒计时和时钟
            change_state(STATE_COUNTDOWN)
        elif current_state == STATE_COUNTDOWN:
            # 暂停倒计时
            paused = not paused
            # 按下亮屏
            gp12.value(1)
            time.sleep(1)
            gp12.value(0)
    
    if not button_c.value() and button_c.value() != last_state_c:
        print("C")
        # 停止响铃（增加BUSY电平检测以防止按下后开启响铃）
        if gp18.value() == 1:
            gp16.value(1)
            time.sleep_ms(100)
            gp16.value(0)
        if current_state == STATE_COUNTDOWN:
            change_state(STATE_MAIN)
            # 重置倒计时
            total_minutes = int(config['CountdownRemainingTime'])
            total_seconds = total_minutes * 60
            paused = False
        # 按下亮屏
        gp12.value(1)
        update_display(config, True)
        time.sleep(5)
        gp12.value(0)
        
    # 更新按钮状态
    last_state_add = button_add.value()
    last_state_sub = button_sub.value()
    last_state_m = button_m.value()
    last_state_c = button_c.value()
    
    return total_minutes, total_seconds, paused

# 背光开关（基于config.txt）
def control_backlight(config):
    if config['Backlight'] == 'on':
        gp12.value(1)
    else:
        gp12.value(0)

# 闹钟功能
def control_alarm(config):
    date_time = ds1302.Now()
    hour = int(date_time[3])
    minute = int(date_time[4])
    second = int(date_time[5])
    
    # 闹钟小时在配置文件改，分钟在这里改
    # 本来想直接在配置txt文件一条龙搞定的，但不知道为什么在测试时会莫名报错，奇怪！所以把分钟调整挪到这里来
    if config['AlarmStatus'] == 'Weekday' and hour == int(config['WeekdayAlarmTime']) and minute == 0 and second == 1:
        gp17.value(1)
        time.sleep_ms(100)
        gp17.value(0)
        # 闹钟时间到亮屏5秒
        gp12.value(1)
        time.sleep(5)
        gp12.value(0)
    elif config['AlarmStatus'] == 'Weekend' and hour == int(config['WeekendAlarmTime']) and minute == 0 and second == 1:
        gp17.value(1)
        time.sleep_ms(100)
        gp17.value(0)
         # 闹钟时间到亮屏5秒
        gp12.value(1)
        time.sleep(5)
        gp12.value(0)

# 倒计时数字显示
def display_digit(lcd, digit, x, y):
    draw_icon(lcd, globals()[f"L_{digit}"], x, y)

# 倒计时时间
def display_countdown_time(minutes, seconds, lcd):
    minutes_str = f"{minutes:02d}"
    seconds_str = f"{seconds:02d}"
    
    # 分钟
    display_digit(lcd, int(minutes_str[0]), 14, 43)  
    display_digit(lcd, int(minutes_str[1]), 27, 43)  
    
    # 秒钟
    display_digit(lcd, int(seconds_str[0]), 90, 43)  
    display_digit(lcd, int(seconds_str[1]), 104, 43)  

# 每次开启倒计时挑一张喵喵卫士表情
def select_random_emoticon():
    emoticons = [Emoticon_01, Emoticon_02, Emoticon_03, Emoticon_04, Emoticon_05, Emoticon_06, Emoticon_07, Emoticon_08, Emoticon_09, Emoticon_10, Emoticon_11]
    return emoticons[urandom.randint(0, len(emoticons) - 1)]

# 显示表情和喵喵卫士
def display_fixed_icons(lcd, emoticon):
    draw_icon(lcd, Meow, 49, 35)
    draw_icon(lcd, emoticon, 29, 6)

# 更改状态
def change_state(new_state):
    global current_state
    current_state = new_state

# 主循环
def main():
    config = read_config()
    colon_on = True
    total_minutes = int(config['CountdownRemainingTime'])
    total_seconds = total_minutes * 60
    paused = False
    emoticon = select_random_emoticon()

    while True:
        if current_state == STATE_MAIN:
            update_display(config, colon_on)
            check_buttons(config, total_minutes, total_seconds, paused)
            control_backlight(config)
            control_alarm(config)
            
            # 时间冒号闪烁
            time.sleep(1)  # 显示1秒
            colon_on = not colon_on
            time.sleep(1)  # 隐藏1秒
        
        elif current_state == STATE_COUNTDOWN:
            if total_seconds > 0 and not paused:
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                
                lcd.clear()
                
                display_fixed_icons(lcd, emoticon)
                
                display_countdown_time(minutes, seconds, lcd)

                lcd.update()

                time.sleep(1)

                total_seconds -= 1
            elif total_seconds <= 0:
                # 倒计时结束时显示
                lcd.clear()
                display_fixed_icons(lcd, emoticon) 
                display_countdown_time(0, 0, lcd)
                lcd.update()
                
                # 倒计时结束，GP17通电100ms开启响铃
                gp17.value(1)
                time.sleep_ms(100)
                gp17.value(0)
                
                while True:
                    total_minutes, total_seconds, paused = check_buttons(config, total_minutes, total_seconds, paused)
                    if total_seconds > 0:  
                        break
            else:
                time.sleep(0.1) 
            
            total_minutes, total_seconds, paused = check_buttons(config, total_minutes, total_seconds, paused)
            
            control_backlight(config)

if __name__ == "__main__":
    main()