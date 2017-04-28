# Data Representation
We want to use some unusal approach to represent our data.
Since there are high correlations between spatial properties and delay propagation we decided to use some image representation.
To get to this representation we used a compact representation as it can be found on the offical website of Stuttgart's transportation authority.

![vvsplan](https://github.com/jhertfe/vvs-delay/blob/dev/get_coordinates/snet.png)

We then used a small HTML/JavaScript page to capture click positions according to the stations on the map.
A click would also bring up some prompt to the user which requires the station name to be typed in. 
The retrieved coordinates are translated back into an image representation i.e. a numpy array.
The array get's scaled down by width and height as long as every pixel representates at most one station.
Empty columns and empty rows get removed as well.
## Input example
This results in an 86 times 16 pixel image.

![input](https://github.com/jhertfe/vvs-delay/blob/dev/get_coordinates/input.png)

In this example every station got the value 255. The real input will contain delays in minutes.
The spatial relations is still there!

## Mappings
To map stations to their representating pixel and vice versa mappings are created as dictionaries.

1. [stations2pixel.json] takes the station's name as a key and will output a tuple (x, y) coordinate
2. [pixel2stationsjson] takes as first key x and as second key y and will output the station's name


[stations2pixel.json]: https://github.com/jhertfe/vvs-delay/blob/dev/get_coordinates/station2pixel.json
[pixel2stationsjson]: https://github.com/jhertfe/vvs-delay/blob/dev/get_coordinates/pixel2station.json
