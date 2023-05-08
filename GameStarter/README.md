# How to use it:
1.Make sure HSRStarter.exe's location is same as loader_config.ini's location.

2.Copy 3Dmigoto files to Game's root dictory(where StarRail.exe located).

(what is 3Dmigoto files?it's d3d11.dll,d3dx.ini,...,etc.you know what I mean.)

3.Edit loader_config.ini,set the correct path for StarRail.exe(normally is XXXXX\Star Rail\Game\StarRail.exe).

4.Right click HSRStarter.exe, run as Administrator,your game now can load 3dmigoto correctly.

then you can press any key to continue,it will automatically open the game.

# Stay safe without inject.
This starter do not use any inject or hook method to make sure your account stay safe.

Note: HSRStarter.exe must run as Administrator.
 
Note: don't put HSRStarter.exe in the same location of StarRail.exe,or it cannot work.

Note: don't put HSRStarter.exe in the game's any directory,ACE will lock your HSRStarter.exe's privilige 
so it cannot work,just put it on desktop will be the easiest way.

Note: If you do not use HSRStarter.exe to start your game,ACE will delete your d3d11.dll.


# Troubleshoots
If you missing ucrtbased.dll and vcruntime140d.dll,you need to get them in dll folder,and put them with your HSRStarter.exe

If you still can not run because luck of dll files,you need to check this website and install
the https://aka.ms/vs/17/release/vc_redist.x64.exe correctly,use x86 version if your game is 32-bit
https://aka.ms/vs/17/release/vc_redist.x86.exe	.

More info see this website:
https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170

If you get the error says:
"The application was unable to start correctly(0xc000007b)"

It means you use the wrong version ,there is x86 and x64 version of program,if one of them can not work,try another.

# Install Mods
If you want my mods work,you need to install some basic files in [Mods] folder.
And you need to config 3dmigoto with my version d3dx.ini in [config] folder.

# Virus problem
Windows Defender think it is a virus:
Trojan:Win32/Wacatac.B!ml

it's a wrong alarm, don't use it if you mind.

or compile it yourself,here is the source code:

https://github.com/airdest/HSRStarter

(This tool is not open source anymore, because somebody abuse it to cheat in game since it can bypass ACE.)

