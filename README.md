# World Transform Display and Edit Addon (for Blender 3.6.9+)

This addon provides an intuitive way to **display, copy, paste, and edit world transforms** for objects and bones in Blender. It allows precise control over transformations with features like **axis locking** and **undo functionality**, making it ideal for animators and riggers.

---

## Features

- **Display World Transforms**:
  - View location, rotation, and scale in world space.
  - Show or hide detailed transform properties with a toggle.
- **Edit World Transforms**:
  - Manually edit location, rotation, and scale in world space.
  - Lock specific axes for location, rotation, and scale while editing.
- **Copy and Paste Transforms**:
  - Copy world transforms to the clipboard in JSON format.
  - Paste transforms from the clipboard to objects or bones.
- **Apply and Undo Transforms**:
  - Apply the current world transform to selected objects or bones.
  - Undo the last applied transform for easy adjustments.
- **Axis Locking**:
  - Lock or unlock individual axes for location, rotation, and scale.

---

## Installation

1. **Download**  
   Download the `world_transform_display_edit.py` file from this repository.

2. **Install in Blender**  
   - Open Blender.  
   - Go to `Edit > Preferences > Add-ons`.  
   - Click `Install...`, select the `world_transform_display_edit.py` file, and enable it.

3. **Access the Addon**  
   - The addon will now be available in the **3D Viewport Sidebar** under `Item > World Transform`.

---

## Usage Instructions

1. Select an object or pose bone in the 3D Viewport.
2. Open the **World Transform** panel in the Sidebar under `Item`.
3. Perform the following operations:
   - **Display Transforms**: View location, rotation, and scale in world space.
   - **Edit Transforms**: Adjust location, rotation, and scale values directly.
   - **Copy Transforms**: Click "Copy" to copy the current world transform to the clipboard in JSON format.
   - **Paste Transforms**: Click "Paste" to apply the transform stored in the clipboard to the selected object or bone.
   - **Apply Transforms**: Apply the current world transform to selected objects or bones.
   - **Undo Transforms**: Revert the last applied transform for precise adjustments.

---

## Requirements

- **Blender Version**: 3.6.9 or later

---

## Known Limitations

- Pasting transforms requires valid JSON clipboard data; ensure the copied data is compatible.
- Undo functionality relies on having a previously applied transform in memory.

---

## Contribution

This addon was developed with the assistance of AI tools, such as ChatGPT, to accelerate development and improve code quality. Contributions are welcome! If you’d like to suggest improvements, report bugs, or add new features:

1. Fork this repository.
2. Create a new branch for your changes.
3. Submit a pull request.

---

## License

This addon is licensed under the **GNU General Public License v3**.
