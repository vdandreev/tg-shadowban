# Why?
I grew a bit annoyed of several users in some of my tg channels.
Other people found these users entertaining in their twisted way though.
I decided that, instead of ruining the day for others,
or complaining, moaning and bitching, I can write myself a tool
to cleanup these channels from obnoxious users and their garbage for myself. 
You know, freedom of speech and all - you can mute shitposters, you 
do not need to cancel them.

Since this is primarily a tool for myself, please do not expect me keeping
it regularly updated, adding. However, if you find this thing useful, 
please clone/contribute/submit MR.

P.S. I really hope TG team will implement this in their clients some day.
See other people asking for similar feature: 
[https://bugs.telegram.org/c/37](https://bugs.telegram.org/c/37)

# Howto
- get yourself python 3.9+
- ```pip install -r requirements.txt```
- Get TG api credentials from [https://my.telegram.org/](https://my.telegram.org/)
- Modify [config.yaml](config.yaml) to your liking
- ```python tg-ignore.py --conf config.yaml```
