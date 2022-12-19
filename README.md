# micro-radio
A microcontroller radio project using the Adafruit PyBadge and CircuitPython

![](/media/version2.png)


Using the [Adafruit Pybadge](https://www.adafruit.com/product/4200) along with an [Adalogger FeatherWing](https://www.adafruit.com/product/2922), the PyBadge plays a song from an sdcard with a simple button press.

I very much wanted to create a small radio for my 2yo son, so that he could play some tunes without having to use some kind of smart device. This is very much inspired by the [Yoto Mini](https://ca.yotoplay.com/yoto-mini), but I was interested in creating something a bit simpler, and could play wav files directly.

## The Progress So Far
The code in main.py and badgey.py work together to play the listed files from the /sd directory, and it all more or less works as planned! But, more refinements are needed to the 3D printed case. Just a bit more work to do (and document)!

### Licences
Code is provided under the MIT licence
Images in the /media folder provided under the CC-BY 4.0 licence
3D model files in provided under CC-BY 4.0
- radio-body.stl and speaker-face.stl are derived from a [Thermal Camera](https://www.printables.com/model/239602-thermal-camera) pybadge enclosure created by [JohanAR](https://www.printables.com/social/223044-johanar/about)
- this whole project would not have been possible without the guides and code examples provided by [Adafruit](https://learn.adafruit.com/adafruit-pybadge)
