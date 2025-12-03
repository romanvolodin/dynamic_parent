# Dynamic Parent

__English__ | [Русский](README-ru.md)

__Dynamic Parent__ is an add-on for Blender.

The add-on allows you to quickly enable/disable parent-child relationships between objects. This is done through the animated `Child Of` constraint. When disabled the child's position relative to the parent is preserved.

## Requirements

The add-on requires Blender 5.0 or newer.

For previous versions of Blender, use Dynamic Parent v2.0.2 or earlier.

## Installation

- [Download the latest version](https://github.com/romanvolodin/dynamic_parent/releases/latest) of the add-on. You do not need to unpack the archive.
- Launch Blender, go to `Edit` → `Preferences...`
- In the column on the left, click the `Add-ons` button. Then click the `Install...` button at the top.
- In the opened window, select the downloaded archive.
- Tick the checkbox to activate the add-on.

## Usage

Select two objects, child should be selected last.

Click `Create` to create constants and animation keys. Move to another frame. Click `Disable` to disable the constraints for the selected objects.

The `Clear` menu:

- `Clear` removes all created DP constraints and its keyframes. So you can start from scratch.
- `Bake and Clear` bakes object/bone animation and then remove DP constraints.

## FAQ

- __Is it possible to re-enable the child constraint?__

  No, it’s not possible. When you disable DP, Blender calculates constraint's transform matrix for the child object. Since a constraint can have only one matrix, we have to create a new constraint each time.
