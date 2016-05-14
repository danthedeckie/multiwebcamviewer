#!/usr/bin/env python
'''
    A Simple multi-image display script that pulls in fresh images from webcams.

    All operations are run in separate threads, so are non-blocking,
    and hopefully failure resistant.

    ------------------
    (C) 2016 Daniel Fairhead <daniel.fairhead@om.org>
    MultiWebCamViewer is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    MultiWebCamViewer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MultiWebCamViewer.  If not, see <http://www.gnu.org/licenses/>.

'''

from signal import pause
from threading import Thread, Event
from time import sleep, time
from StringIO import StringIO

from requests import Session
import pygame
import pygame.camera

# Immutable (I wish) globals:

AUTH = ('admin', '')
SCREENSIZE = (1280, 720)

IMG_SIZE = (SCREENSIZE[0]/3, SCREENSIZE[1]/3)

# Thread globals (hurrah for GIL):

image_data = {}
current_time = ''
TIME = time()
PAUSE_EVENT = Event()

#####

def get_forever(url):
    '''
    Keep on getting an image from a URL, shoving it in the image_data
    dictionary as a pygame image, and wait for the ticker to wake me up.
    '''
    s = Session()
    print 'get {} thread started.'.format(url)
    while True:
        try:
            req = s.get(url, auth=AUTH, params={'t':TIME})
            img = pygame.image.load(StringIO(req.content), 'i.jpg')
            image_data[url] = pygame.transform.scale(img, IMG_SIZE)
        except Exception as e:
            print e
            sleep(5)
            PAUSE_EVENT.wait()

####

def update_time(frequency=.08):
    ''' background thread that wakes up all paused threads every frequency. '''
    while True:
        TIME = time()
        sleep(frequency)
        PAUSE_EVENT.set()
        PAUSE_EVENT.clear()


#############################

def main():
    '''
    Main Initialisation and Event Loop
    '''

    t = Thread(target=update_time)
    t.daemon = True
    t.start()

    images = ['http://192.168.0.{}/image.jpg'.format(x) for x in
                ['201','202','203','204','205']]

    for r in images:
        t = Thread(target=get_forever, args=(r,))
        t.daemon=True
        t.start()

    pygame.init()
    screen = pygame.display.set_mode(SCREENSIZE, pygame.FULLSCREEN)
    ticker = pygame.time.Clock()

    sleep(1)

    print 'starting event loop'

    while True:
        x = 0
        y = 0
        for r in images:
            try:
                w, h = image_data[r].get_size()
                if x + w > SCREENSIZE[0]:
                    y += h
                    x = 0
                screen.blit(image_data[r],(x,y))
                x += w
            except KeyError:
                print '{} not there.'.format(r)
        pygame.display.flip()
        ticker.tick(30)

if __name__ == '__main__':
    main()
