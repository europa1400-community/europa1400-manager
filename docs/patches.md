# Patches

The manager installs patches from their original authors; it does not change them. The current list with download
sources: [All patches](patch-list.md).

## Multiplayer

### Netfix (`netfix`)

For the player who **hosts** a multiplayer game; the others need nothing. Over VPNs (Radmin, Hamachi, ZeroTier) and the
Internet, game messages often arrive in pieces, which the game's server cannot handle: "out of sync" and lost
connections. Netfix makes the server wait for complete messages and answer faster.

Installs the **patch loader** (`e1400patch`) as well. The loader changes no game file: it points the game's
`game.ini` to its own server component, and uninstalling restores the previous setting. Details:
[europa1400-patches](https://github.com/europa1400-community/europa1400-patches/blob/main/patches/netfix/README.md).

Supported: Gold 2.06, German (GOG, Steam). Other versions follow.

### Network Fix (`networkfix`)

An older, independent community fix for multiplayer stability
([europa1400-networkfix](https://github.com/maci0/europa1400-networkfix)). The manager does not install it together
with Netfix.

## Graphics

### DxWrapper (`dxwrapper`)

Runs the game's Direct3D 8 graphics through Direct3D 9 and sets the option that fixes the broken interface textures
(`SetPOW2Caps`) on current Windows versions.

### DXVK (`dxvk`)

Translates Direct3D 9 to Vulkan. The game uses Direct3D 8, so DXVK only works together with DxWrapper, which is
installed with it. Can help with performance or display problems on some systems, mostly on Linux.

### DDrawCompat (`ddraw_compat`)

Compatibility fixes for DirectDraw, used by the classic renderer. A ddraw.dll you put into the game folder yourself is
backed up and restored on uninstall.

!!! tip
    Start with as few patches as possible and add one at a time. If something gets worse, uninstall the last one.
