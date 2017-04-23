# Hex3d

This is an attempt to make 3d interactive hex maps using vanilla pygame.  
For a map of arround 30x30 hex tiles this program works quite well, but I was a bit dissapointed I couldn't get more performance out of it with larger maps.  It also suffers from a slight rendering issue from pygame not playing nicely with floating point coordinates for drawing.

[Demonstration](https://media.giphy.com/media/LeRejUoi238xq/giphy.gif)

### Requirements
* numpy
* opensimplex
* pygame

### Mouse Controls
* Hold right mouse button and drag horizontally to rotate
* Hold right mouse button and drag vertically to change elevation angle
* Scroll wheel to zoom

### Keyboard Controls
* Left and right to rotate 60 degrees
* Up and down to change elevation angle
* Plus and Minus to zoom in and out
