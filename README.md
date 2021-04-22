# Dynamic Parent

__English__ | [Русский](README-ru.md)

__Dynamic Parent__ is an add-on for Blender.

The add-on allows you to quickly enable/disable parent-child relationships between objects. This is done through the animated `Child Of` constraint. When disabled the child's position relative to the parent is preserved.

## Requirements

The add-on requires Blender 2.83 or newer.


## Installation

- [Download the latest version](https://github.com/romanvolodin/dynamic_parent/releases/latest) of the add-on. You do not need to unpack the archive.
- Launch Blender, go to `Edit` →`Preferences...`
- In the column on the left, click the `Add-ons` button. Then click the `Install...` button at the top.
- In the opened window, select the downloaded archive.
- Tick the checkbox to activate the add-on.


## Usage
Select two objects, child should be selected last.

Click `Create` to create constants and animation keys. Move to another frame. Click `Disable` to disable the constraints for the selected objects.

The `Clear` menu will allow you to bake the animation and/or delete all created DP constraints.  
