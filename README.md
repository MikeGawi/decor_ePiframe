<img align="right" src="https://github.com/MikeGawi/decor_ePiframe/blob/master/assets/bord.gif" width="400">

# Decor_ePiframe

Displays decorative borders with quotes on [ePiframe](https://github.com/MikeGawi/ePiframe)

This plugin has been created with [ePiframe_plugin](https://github.com/MikeGawi/ePiframe_plugin) template.

Uses free images from [rawpixel](https://www.rawpixel.com/) and [Google Fonts](https://fonts.google.com/) font.

## Requirements

* [ePiframe](https://github.com/MikeGawi/ePiframe) 2.0 or newer (Plugin API v2). For ePiframe 1.x use the version
  of this plugin from before ePiframe 2.0.

## How it works

* The border is drawn over the photo converted for the display, with an optional random quote (semicolon separated list in `quotes`).
* Set `random_border=0` and pick `border` to always use the same one.

## Installation

On working ePiframe:

* Clone to ePiframe plugins path:
	```
	cd <ePiframe path>/plugins
	git clone https://github.com/MikeGawi/decor_ePiframe decor_ePiframe
	```

OR

* Download and extract:
	```
	cd <ePiframe path>/plugins
	wget -q https://github.com/MikeGawi/decor_ePiframe/archive/master.zip -O decor_ePiframe.zip
	unzip decor_ePiframe.zip
	mv decor_ePiframe-master decor_ePiframe
	rm decor_ePiframe.zip
	```

## Configuration

* Configure with the file [*config.cfg*](https://github.com/MikeGawi/decor_ePiframe/blob/master/config.cfg) inside *ePiframe_path/plugins/decor_ePiframe*

OR

* In ePiframe WebUI (if enabled) under *Plugins - Decor*

Check the configuration with `./ePiframe.py check-config` (in the ePiframe folder).

The plugin folder name must stay a valid Python name (letters, digits, `_`), e.g. `decor_ePiframe`: ePiframe
skips plugins in folders with dashes or dots.
