# Introduction

*Pathologic* is a first-person roleplaying survival/action/horror game, developed by the Russian studio *Ice-Pick Lodge* in 2005. Since then, the game has accrued something of a cult following, both with Russian- and English-speaking gamers, the poor English translation of *Pathologic* notwithstanding. Over time, there have sprouted various fan translation projects, although none of them has yet resulted in a complete literary translation. Hopefully, the technical details presented in this document will help the people interested in translating/modding the game to achieve their goals.

You can get a copy of *Pathologic*, in both English and Russian, at [Good Old Games.](http://www.gog.com/game/pathologic)

# Usage

The project supports both Python 2 and Python 3. To extract a `.vfs` file (e.g. `Strings.vfs`), run:

    python vfs_parser.py <path/to/Strings.vfs>

This will create a directory called `Strings` and place the contents of the archive in that directory. To decode `main.dat`, run:

    python decode_keys.py -i Strings/main.dat

This will create an XML file called `main.dat.xml` in the `Strings` directory. You can then change it with any text editor. When done, save it with a `UTF-8` encoding.
To create a new `main.dat` with your changes, run:

    python encode_keys.py -i Strings/main.dat.xml -o Strings/main.dat

You don't need to pack the files back into the `.vfs`; see below for the reason why.

# Directory structure

    +---bin
    |   \---Final
    |           Config.exe
    |           D3D.dll
    |           DbgHelp.dll
    |           Engine.dll
    |           engine.log
    |           FS.dll
    |           Game.exe
    |           goggame.dll
    |           LifeStudioHeadAPIS.dll
    |           nosound.dll
    |           Sound.dll
    |           UI.dll
    |           unicows.dll
    |           UVPupil.dll
    |           VFS.dll
    |
    +---data
    |   |   Actors.vfs
    |   |   config.ini
    |   |   Fonts.vfs
    |   |   Geometries.vfs
    |   |   init.cfg
    |   |   profiles.xml
    |   |   Scenes.vfs
    |   |   Scripts.vfs
    |   |   Strings.vfs
    |   |   Textures.vfs
    |   |   UI.vfs
    |   |   Video.vfs
    |   |   World.vfs
    |   |
    |   +---Sounds
    |   |       <Game sound files, in .ogg format>
    |   |
    |   \---Video
    |           <Game cutscenes, in .wmv format>
    |
    \---Saves

# Game resources (making the game mod-ready)

Going by the GOG.com version, at least, the game resources (except the sounds - presumably for performance reasons) are stored in .vfs packages, in the game's data directory.
To unpack a .vfs, use an unpacker, like the one linked [at the Ice-Pick Lodge forums](http://forum.ice-pick.com/viewtopic.php?f=12&t=4650#p58685), or the `vfs_parser.py` program in this repository.
The game can be coerced to read the resources from either a .vfs file, or directly from the file system. To do the latter, open the data\config.ini file in a text editor, and take a look at the last section. You should see something like

    [FS]
    ActorsType = VFS
    FontsType = VFS
    GeometriesType = VFS
    ScenesType = VFS
    ScriptsType = VFS
    SoundsType = FS
    StringsType = VFS
    TexturesType = VFS
    UIType = VFS
    VideoType = VFS
    WorldType = VFS

Extract a .vfs to an appropriately-named directory (e.g. the contents of `Fonts.vfs` should go into `data\Fonts`), and then change the appropriate line in the `config.ini` to end with `= FS` instead of `= VFS`. From now on, any changes to the extracted files will reflect directly upon the game.

# Strings.vfs

The `Strings.vfs` package contains the files `keys.txt`, `main.dat`, `map.txt`, and `ui.txt`. Out of those, `main.dat` is the most important, as it contains the text spoken by the game's NPCs. (Note: for some reason, the string IDs and dialog trees are slightly different, between the English and Russian versions of the game. If you blindly replace the `main.dat` for the English version with the Russian one, it might break your game later on.)

## The `main.dat` archive

The structure of a `main.dat` file is shown on the following diagram:

    (All numbers are little-endian):

    +--------------------------------+-------------------------------+--------------------+------------------   ...   --------------+----------------------+------- ...
    |     String count (4 bytes)     |          ID (4 bytes)         | Len (1 or 2) bytes | First string (UCS-2) little-endian      |  Len (1 or 2) bytes  |  Second string ...
    +--------------------------------+-------------------------------+--------------------+------------------   ...   --------------+----------------------+------- ...

The string ID serves to identify it in the NPC dialog tree ([as shown here](http://ice-pick.com/translate/PTP/dialogs.php?parentId=20), for example). The dialog tree is presumably baked into the game executable.

The string length is (somewhat weirdly) represented by either 1 or 2 bytes, as follows: if the string length is less than 128 characters, it is represented by 1 byte; if it's greater or equal to 128, it's represented by `(byte1 % 128) + (byte2 << 7)`. See the `decode_keys.py` program for an example of a `main.dat` decoder.
