"""
Blender UI Panels for CrossRig.

These define the user interface in the 3D Viewport sidebar.
"""

import bpy
from bpy.types import Panel, UIList


class CROSSRIG_UL_ActionList_Edit(UIList):
    """Custom UIList for displaying action items."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "use_action", text="")
            row.label(text=item.action_name, icon='ACTION')

            # Armature badge
            if item.armature_name:
                row.label(text=f"[{item.armature_name}]", icon='ARMATURE_DATA')
                sub = row.row(align=True)
                op = sub.operator("crossrig.select_armature_from_list", text="", icon="RESTRICT_SELECT_OFF", emboss=False)
                op.armature_name = item.armature_name

            # Action length (frames)
            act = bpy.data.actions.get(item.action_name)
            if act:
                row.label(text=f"{int(act.frame_range[1] - act.frame_range[0])} fr", icon='TIME')

            # Repeat Count control
            sub = row.row(align=True)
            sub.prop(item, "repeat_count", text="")
            sub.scale_x = 0.6

            # Angle control
            sub = row.row(align=True)
            sub.prop(item, "angle", text="")
            sub.scale_x = 0.8


class CROSSRIG_UL_BoneMappingList(UIList):
    """Custom UIList for displaying bone mapping items."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)

            # Source bone (read-only)
            row.label(text=item.source_bone, icon='BONE_DATA')

            # Arrow
            row.label(text="→", icon='FORWARD')

            # Target bone (editable via search)
            settings = context.scene.mixamo_unified
            target_arm = settings.bone_mapping_target_armature

            if target_arm and target_arm.type == 'ARMATURE':
                # Use bone search
                row.prop_search(
                    item, "target_bone",
                    target_arm.data, "bones",
                    text="",
                    icon='BONE_DATA'
                )
            else:
                # Fallback to text input if no target armature
                row.prop(item, "target_bone", text="", icon='BONE_DATA')

            # Confidence badge (color-coded)
            if item.confidence >= 1.0:
                # Manual mapping - green
                row.label(text="✓", icon='CHECKMARK')
            elif item.confidence >= 0.8:
                # High confidence auto-map - yellow
                row.label(text=f"{int(item.confidence * 100)}%", icon='INFO')
            elif item.confidence > 0.0:
                # Low confidence auto-map - orange
                row.label(text=f"{int(item.confidence * 100)}%", icon='ERROR')
            else:
                # No mapping - red
                row.label(text="?", icon='QUESTION')


class CROSSRIG_PT_UnifiedPanel(Panel):
    """Main panel for CrossRig."""

    bl_label = "CROSSRIG"
    bl_idname = "CROSSRIG_PT_unified_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CrossRig"

    def draw(self, context):
        layout = self.layout
        prefs = context.scene.crossrig_settings

        # ============================================================
        # PLAY GROUND SECTION
        # ============================================================
        box = layout.box()
        row = box.row(align=True)
        icon = 'TRIA_DOWN' if prefs.show_playground else 'TRIA_RIGHT'
        row.prop(prefs, "show_playground", icon=icon, icon_only=True, emboss=False)
        row.label(text="Play Ground", icon='SCENE')

        if prefs.show_playground:
            # === Load & Organize Animations Subsection ===
            col = box.column(align=True)
            row = col.row(align=True)
            sub_icon = 'TRIA_DOWN' if prefs.show_load_organize else 'TRIA_RIGHT'
            row.prop(prefs, "show_load_organize", icon=sub_icon, icon_only=True, emboss=False)
            row.label(text="Load & Organize Animations", icon='ANIM')

            if prefs.show_load_organize:
                sub_box = col.box()

                # Forward axis setting
                row = sub_box.row()
                row.prop(prefs, "forward_axis", text="Character Forward Axis")

                # Load actions button
                row = sub_box.row()
                row.operator("crossrig.get_actions", text="Load Actions", icon='FILE_REFRESH')

                # Action list with move buttons
                row = sub_box.row()
                row.template_list(
                    "CROSSRIG_UL_ActionList_Edit",
                    "",
                    prefs, "action_collection",
                    prefs, "action_index",
                    rows=5
                )
                col_list = row.column(align=True)
                col_list.operator("crossrig.move_action_up", icon='TRIA_UP', text="")
                col_list.operator("crossrig.move_action_down", icon='TRIA_DOWN', text="")

                # Settings
                inner_box = sub_box.box()
                inner_box.prop(prefs, "root_bone", text="Root Bone")
                inner_box.prop(prefs, "overlap_frames", text="Overlap Frames")
                inner_box.operator("crossrig.confirm_order", text="Confirm Order", icon='CHECKMARK')

            # === Nonlinear Animation Subsection ===
            col.separator()
            row = col.row(align=True)
            sub_icon = 'TRIA_DOWN' if prefs.show_nla else 'TRIA_RIGHT'
            row.prop(prefs, "show_nla", icon=sub_icon, icon_only=True, emboss=False)
            row.label(text="Nonlinear Animation", icon='NLA')

            if prefs.show_nla:
                sub_box = col.box()

                row = sub_box.row(align=True)
                row.operator("crossrig.send_to_timeline", text="Send to NLA", icon='NLA')

                # Bake + Stabilize
                row = sub_box.row(align=True)
                row.operator("crossrig.bake_action", text="Bake Action", icon='RENDER_ANIMATION')
                row.operator("crossrig.stabilize_root", text="Stabilize Root", icon='PINNED')

            # === Export Subsection ===
            col.separator()
            row = col.row(align=True)
            sub_icon = 'TRIA_DOWN' if prefs.show_export else 'TRIA_RIGHT'
            row.prop(prefs, "show_export", icon=sub_icon, icon_only=True, emboss=False)
            row.label(text="Export", icon='EXPORT')

            if prefs.show_export:
                sub_box = col.box()

                row = sub_box.row(align=True)
                row.operator("crossrig.export_fbx", text="Full (Mesh + Armature)", icon='MESH_DATA')

                row = sub_box.row(align=True)
                row.operator("crossrig.export_fbx_armature_only", text="Armature Only", icon='ARMATURE_DATA')

            # === Animation Presets Subsection ===
            col.separator()
            row = col.row(align=True)
            sub_icon = 'TRIA_DOWN' if prefs.show_presets else 'TRIA_RIGHT'
            row.prop(prefs, "show_presets", icon=sub_icon, icon_only=True, emboss=False)
            row.label(text="Animation Presets", icon='FILE')

            if prefs.show_presets:
                sub_box = col.box()

                # Save/Load presets
                row = sub_box.row(align=True)
                row.operator("crossrig.save_preset", text="Save Preset", icon='FILE_NEW')
                row.operator("crossrig.load_preset_menu", text="Load", icon='FILE_FOLDER')

                # Additional preset operations
                row = sub_box.row(align=True)
                row.operator("crossrig.load_preset", text="Browse Presets", icon='FILEBROWSER')
                row.operator("crossrig.delete_preset", text="Delete", icon='TRASH')

                # Folder access
                sub_box.operator("crossrig.open_preset_folder", text="Open Preset Folder", icon='FILE_FOLDER')

        # ============================================================
        # BONE MAPPING SECTION
        # ============================================================
        layout.separator()
        box = layout.box()
        row = box.row(align=True)
        icon = 'TRIA_DOWN' if prefs.show_bone_mapping else 'TRIA_RIGHT'
        row.prop(prefs, "show_bone_mapping", icon=icon, icon_only=True, emboss=False)
        row.label(text="Bone Mapping", icon='CON_ARMATURE')

        if prefs.show_bone_mapping:
            # === Setup Subsection ===
            col = box.column(align=True)
            row = col.row(align=True)
            sub_icon = 'TRIA_DOWN' if prefs.show_bone_mapping_setup else 'TRIA_RIGHT'
            row.prop(prefs, "show_bone_mapping_setup", icon=sub_icon, icon_only=True, emboss=False)
            row.label(text="Setup", icon='SETTINGS')

            if prefs.show_bone_mapping_setup:
                sub_box = col.box()

                # Armature selectors
                row = sub_box.row()
                row.prop(prefs, "bone_mapping_source_armature", text="Source")

                row = sub_box.row()
                row.prop(prefs, "bone_mapping_target_armature", text="Target")

                # Preset name
                row = sub_box.row()
                row.prop(prefs, "bone_mapping_preset_name", text="Preset Name")

                # Create mapping button
                row = sub_box.row()
                row.operator("crossrig.create_bone_mapping", text="Create Bone Mapping", icon='ADD')

                # Auto-map section
                inner_box = sub_box.box()
                inner_box.label(text="Auto-Mapping", icon='AUTO')
                row = inner_box.row()
                row.prop(prefs, "auto_map_threshold", text="Threshold", slider=True)
                row = inner_box.row()
                row.operator("crossrig.auto_map_bones", text="Auto-Map Bones", icon='AUTOMERGE_ON')

            # === Mapping List Subsection ===
            col.separator()
            row = col.row(align=True)
            sub_icon = 'TRIA_DOWN' if prefs.show_bone_mapping_list else 'TRIA_RIGHT'
            row.prop(prefs, "show_bone_mapping_list", icon=sub_icon, icon_only=True, emboss=False)
            row.label(text="Bone Mappings", icon='ALIGN_JUSTIFY')

            if prefs.show_bone_mapping_list:
                sub_box = col.box()

                # Bone mapping list
                row = sub_box.row()
                row.template_list(
                    "CROSSRIG_UL_BoneMappingList",
                    "",
                    prefs, "bone_mappings",
                    prefs, "bone_mapping_index",
                    rows=8
                )
                col_list = row.column(align=True)
                col_list.operator("crossrig.remove_bone_mapping", icon='REMOVE', text="")

                # Clear all button
                row = sub_box.row()
                row.operator("crossrig.clear_bone_mappings", text="Clear All Mappings", icon='X')

            # === Mapping Presets Subsection ===
            col.separator()
            row = col.row(align=True)
            sub_icon = 'TRIA_DOWN' if prefs.show_bone_mapping_presets else 'TRIA_RIGHT'
            row.prop(prefs, "show_bone_mapping_presets", icon=sub_icon, icon_only=True, emboss=False)
            row.label(text="Mapping Presets", icon='FILE')

            if prefs.show_bone_mapping_presets:
                sub_box = col.box()

                # Save/Load presets
                row = sub_box.row(align=True)
                row.operator("crossrig.save_bone_mapping", text="Save Mapping", icon='FILE_NEW')
                row.operator("crossrig.load_bone_mapping_menu", text="Load", icon='FILE_FOLDER')

                # Additional preset operations
                row = sub_box.row(align=True)
                row.operator("crossrig.load_bone_mapping", text="Browse Mappings", icon='FILEBROWSER')
                row.operator("crossrig.delete_bone_mapping", text="Delete", icon='TRASH')

                # Folder access
                sub_box.operator("crossrig.open_bone_mapping_folder", text="Open Mapping Folder", icon='FILE_FOLDER')

            # === Apply Animation Subsection ===
            col.separator()
            row = col.row(align=True)
            sub_icon = 'TRIA_DOWN' if prefs.show_bone_mapping_apply else 'TRIA_RIGHT'
            row.prop(prefs, "show_bone_mapping_apply", icon=sub_icon, icon_only=True, emboss=False)
            row.label(text="Apply Animation", icon='PLAY')

            if prefs.show_bone_mapping_apply:
                sub_box = col.box()

                # Apply animation with mapping
                row = sub_box.row()
                row.operator("crossrig.apply_animation_with_mapping", text="Apply Animation with Mapping", icon='IMPORT')

                # Validate mapping
                row = sub_box.row()
                row.operator("crossrig.validate_bone_mapping", text="Validate Mapping", icon='CHECKMARK')

        # ============================================================
        # ARMATURE MANAGE SECTION
        # ============================================================
        layout.separator()
        box = layout.box()
        row = box.row(align=True)
        icon = 'TRIA_DOWN' if prefs.show_armature_manage else 'TRIA_RIGHT'
        row.prop(prefs, "show_armature_manage", icon=icon, icon_only=True, emboss=False)
        row.label(text="Armature Manage", icon='ARMATURE_DATA')

        if prefs.show_armature_manage:
            col = box.column(align=True)

            # === Smart Rig Subsection ===
            row = col.row(align=True)
            sub_icon = 'TRIA_DOWN' if prefs.show_smart_rig else 'TRIA_RIGHT'
            row.prop(prefs, "show_smart_rig", icon=sub_icon, icon_only=True, emboss=False)
            row.label(text="Smart Rig (Auto-Generate)", icon='MOD_ARMATURE')

            if prefs.show_smart_rig:
                sub_box = col.box()

                if not prefs.smart_rig_active:
                    # Not in smart rig mode - show start button
                    row = sub_box.row()
                    row.prop(prefs, "smart_rig_bone_set", text="Bone Set")

                    row = sub_box.row()
                    row.operator("crossrig.start_smart_rig_mode", text="Start Smart Rig Mode", icon='PLAY')
                    row = sub_box.row()
                    row.label(text="Select mesh and click Start", icon='INFO')
                else:
                    # In smart rig mode - show landmark picking interface
                    row = sub_box.row()
                    row.label(text=f"Target: {prefs.smart_rig_target_mesh.name}", icon='MESH_DATA')

                    # Show bone set and allow changing
                    row = sub_box.row()
                    row.prop(prefs, "smart_rig_bone_set", text="Mode")

                    # Landmark count
                    landmark_count = len(prefs.smart_rig_landmarks)
                    row = sub_box.row()
                    row.label(text=f"Landmarks: {landmark_count}", icon='EMPTY_DATA')

                    # Quick landmark buttons
                    inner_box = sub_box.box()

                    # Show mode-specific instructions
                    if prefs.smart_rig_bone_set == 'SMART':
                        inner_box.label(text="SMART MODE: Pick 6 landmarks", icon='INFO')
                        inner_box.label(text="Click button → Click on mesh surface", icon='HAND')

                        # Show only required landmarks for SMART mode
                        flow = inner_box.grid_flow(row_major=True, columns=1, align=True)

                        op = flow.operator("crossrig.pick_landmark", text="1. Neck (Center)")
                        op.landmark_id = "neck"
                        op.landmark_side = 'CENTER'

                        op = flow.operator("crossrig.pick_landmark", text="2. Chin (Center)")
                        op.landmark_id = "chin"
                        op.landmark_side = 'CENTER'

                        op = flow.operator("crossrig.pick_landmark", text="3. Hip (Center)")
                        op.landmark_id = "spine_bottom"
                        op.landmark_side = 'CENTER'

                        op = flow.operator("crossrig.pick_landmark", text="4. Left Shoulder")
                        op.landmark_id = "shoulder"
                        op.landmark_side = 'LEFT'

                        op = flow.operator("crossrig.pick_landmark", text="5. Left Wrist")
                        op.landmark_id = "wrist"
                        op.landmark_side = 'LEFT'

                        op = flow.operator("crossrig.pick_landmark", text="6. Left Ankle")
                        op.landmark_id = "ankle"
                        op.landmark_side = 'LEFT'

                        # Auto-mirror button
                        row = inner_box.row()
                        row.operator("crossrig.auto_detect_symmetry", text="Auto-Mirror to Right Side", icon='MOD_MIRROR')

                    else:
                        inner_box.label(text="Pick Landmarks (Click button → Click mesh)", icon='HAND')

                    # Head/Neck landmarks
                    flow = inner_box.grid_flow(row_major=True, columns=2, align=True)
                    op = flow.operator("crossrig.pick_landmark", text="Head Top")
                    op.landmark_id = "head_top"
                    op.landmark_side = 'CENTER'

                    op = flow.operator("crossrig.pick_landmark", text="Neck")
                    op.landmark_id = "neck"
                    op.landmark_side = 'CENTER'

                    # Spine landmarks
                    flow = inner_box.grid_flow(row_major=True, columns=3, align=True)
                    op = flow.operator("crossrig.pick_landmark", text="Spine Top")
                    op.landmark_id = "spine_top"
                    op.landmark_side = 'CENTER'

                    op = flow.operator("crossrig.pick_landmark", text="Spine Mid")
                    op.landmark_id = "spine_mid"
                    op.landmark_side = 'CENTER'

                    op = flow.operator("crossrig.pick_landmark", text="Hips")
                    op.landmark_id = "spine_bottom"
                    op.landmark_side = 'CENTER'

                    # Bilateral landmarks - Arms
                    inner_box.label(text="Arms (L/R):", icon='CONSTRAINT_BONE')
                    flow = inner_box.grid_flow(row_major=True, columns=2, align=True)

                    for limb_part in [('shoulder', 'Shoulder'), ('elbow', 'Elbow'), ('wrist', 'Wrist'), ('hand', 'Hand')]:
                        row_lr = flow.row(align=True)
                        op_l = row_lr.operator("crossrig.pick_landmark", text=f"L {limb_part[1]}")
                        op_l.landmark_id = limb_part[0]
                        op_l.landmark_side = 'LEFT'

                        op_r = row_lr.operator("crossrig.pick_landmark", text=f"R {limb_part[1]}")
                        op_r.landmark_id = limb_part[0]
                        op_r.landmark_side = 'RIGHT'

                    # Bilateral landmarks - Legs
                    inner_box.label(text="Legs (L/R):", icon='CONSTRAINT_BONE')
                    flow = inner_box.grid_flow(row_major=True, columns=2, align=True)

                    for limb_part in [('hip', 'Hip'), ('knee', 'Knee'), ('ankle', 'Ankle'), ('foot', 'Foot'), ('toe', 'Toe')]:
                        row_lr = flow.row(align=True)
                        op_l = row_lr.operator("crossrig.pick_landmark", text=f"L {limb_part[1]}")
                        op_l.landmark_id = limb_part[0]
                        op_l.landmark_side = 'LEFT'

                        op_r = row_lr.operator("crossrig.pick_landmark", text=f"R {limb_part[1]}")
                        op_r.landmark_id = limb_part[0]
                        op_r.landmark_side = 'RIGHT'

                    # Symmetry tools
                    row = sub_box.row(align=True)
                    row.operator("crossrig.auto_detect_symmetry", text="Auto-Mirror Landmarks", icon='MOD_MIRROR')

                    # Actions
                    row = sub_box.row(align=True)
                    row.operator("crossrig.generate_smart_rig", text="Generate Rig", icon='ARMATURE_DATA')
                    row.operator("crossrig.clear_all_landmarks", text="Clear All", icon='X')

                    row = sub_box.row()
                    row.operator("crossrig.exit_smart_rig_mode", text="Exit Mode", icon='CANCEL')

            # === Template Management Subsection ===
            col.separator()

            # Save armature structure
            row = col.row()
            row.operator("crossrig.save_armature_template", text="Save Armature Structure", icon='ARMATURE_DATA')

            # Load armature structure
            row = col.row(align=True)
            row.operator("crossrig.load_armature_template_menu", text="Quick Load", icon='FILE_FOLDER')
            row.operator("crossrig.load_armature_template", text="Browse", icon='FILEBROWSER')

            # Load to mesh
            row = col.row(align=True)
            row.operator("crossrig.load_armature_template_to_mesh", text="Load to Mesh", icon='MESH_DATA')
            row.operator("crossrig.delete_armature_template", text="Delete", icon='TRASH')

            # Folder access
            col.operator("crossrig.open_armature_template_folder", text="Open Template Folder", icon='FILE_FOLDER')

        # ============================================================
        # ANIMATION MANAGE SECTION
        # ============================================================
        layout.separator()
        box = layout.box()
        row = box.row(align=True)
        icon = 'TRIA_DOWN' if prefs.show_animation_manage else 'TRIA_RIGHT'
        row.prop(prefs, "show_animation_manage", icon=icon, icon_only=True, emboss=False)
        row.label(text="Animation Manage", icon='ANIM_DATA')

        if prefs.show_animation_manage:
            col = box.column(align=True)

            # Save animation
            row = col.row()
            row.operator("crossrig.save_animation_data", text="Save Animation", icon='EXPORT')

            # Apply animation
            row = col.row(align=True)
            row.operator("crossrig.apply_animation_data_menu", text="Quick Apply", icon='IMPORT')
            row.operator("crossrig.apply_animation_data", text="Browse", icon='FILEBROWSER')

            # Delete and folder
            row = col.row(align=True)
            row.operator("crossrig.delete_animation_data", text="Delete", icon='TRASH')
            row.operator("crossrig.open_animation_data_folder", text="Open Folder", icon='FILE_FOLDER')

        # ============================================================
        # Footer
        # ============================================================
        layout.separator()
        layout.operator(
            "wm.url_open",
            text="Comming soon with new version",
            icon="URL"
        ).url = "https://afzalgates.com/"


# Classes to register
classes = (
    CROSSRIG_UL_ActionList_Edit,
    CROSSRIG_UL_BoneMappingList,
    CROSSRIG_PT_UnifiedPanel,
)


def register():
    """Register UI classes."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister UI classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
