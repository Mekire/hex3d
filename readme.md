# Hex3d

This is an attempt to make 3d interactive hex maps using vanilla pygame.  
After some optimizations the program behaves respectably with even fairly large mapsizes. It still suffers from a slight rendering issue from pygame not playing nicely with floating point coordinates for drawing.

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
* Spacebar to reset to initial view
