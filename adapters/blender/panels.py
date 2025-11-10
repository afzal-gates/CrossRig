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

                    # Show picked landmarks list with edit/delete options
                    if landmark_count > 0:
                        landmarks_box = sub_box.box()
                        landmarks_box.label(text="Picked Landmarks (Edit Mode):", icon='EDITMODE_HLT')

                        for idx, landmark in enumerate(prefs.smart_rig_landmarks):
                            row = landmarks_box.row(align=True)

                            # Landmark info with color-coded icon
                            if landmark.landmark_side == 'CENTER':
                                icon = 'SPHERE'
                            elif landmark.landmark_side == 'LEFT':
                                icon = 'BACK'
                            else:
                                icon = 'FORWARD'

                            row.label(text=f"{landmark.landmark_id} ({landmark.landmark_side})", icon=icon)

                            # Re-pick button (edit)
                            op = row.operator("crossrig.pick_landmark", text="", icon='GREASEPENCIL', emboss=True)
                            op.landmark_id = landmark.landmark_id
                            op.landmark_side = landmark.landmark_side

                            # Delete button
                            op = row.operator("crossrig.clear_landmark", text="", icon='X', emboss=True)
                            op.index = str(idx)

                    # Quick landmark buttons
                    inner_box = sub_box.box()

                    # Show mode-specific instructions
                    if prefs.smart_rig_bone_set == 'SMART':
                        inner_box.label(text="SMART MODE: Pick 6 landmarks", icon='INFO')
                        inner_box.label(text="Click button → Click on mesh", icon='HAND')
                        inner_box.label(text="Bones placed at center of mass", icon='PIVOT_MEDIAN')

                        # Show only required landmarks for SMART mode
                        flow = inner_box.grid_flow(row_major=True, columns=1, align=True)

                        op = flow.operator("crossrig.pick_landmark", text="1. Neck (Center)")
                        op.landmark_id = "neck"
                        op.landmark_side = 'CENTER'

                        op = flow.operator("crossrig.pick_landmark", text="2. Chin (Center)")
                        op.landmark_id = "chin"
                        op.landmark_side = 'CENTER'

                        op = flow.operator("crossrig.pick_landmark", text="3. Hips (Center)")
                        op.landmark_id = "hips"
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
                    flow = inner_box.grid_flow(row_major=True, columns=3, align=True)
                    op = flow.operator("crossrig.pick_landmark", text="Head Top")
                    op.landmark_id = "head_top"
                    op.landmark_side = 'CENTER'

                    op = flow.operator("crossrig.pick_landmark", text="Head Top End")
                    op.landmark_id = "head_center"
                    op.landmark_side = 'CENTER'

                    op = flow.operator("crossrig.pick_landmark", text="Neck")
                    op.landmark_id = "neck"
                    op.landmark_side = 'CENTER'

                    # Spine landmarks (show all 4 in full modes)
                    spine_box = inner_box.box()
                    spine_box.label(text="Spine Chain (4 bones):", icon='CONSTRAINT_BONE')
                    flow = spine_box.grid_flow(row_major=True, columns=2, align=True)

                    op = flow.operator("crossrig.pick_landmark", text="Hips (Root)")
                    op.landmark_id = "hips"
                    op.landmark_side = 'CENTER'

                    op = flow.operator("crossrig.pick_landmark", text="Spine Bottom")
                    op.landmark_id = "spine_bottom"
                    op.landmark_side = 'CENTER'

                    op = flow.operator("crossrig.pick_landmark", text="Spine Mid")
                    op.landmark_id = "spine_mid"
                    op.landmark_side = 'CENTER'

                    op = flow.operator("crossrig.pick_landmark", text="Spine Top")
                    op.landmark_id = "spine_top"
                    op.landmark_side = 'CENTER'

                    # LEFT SIDE SECTION
                    left_box = inner_box.box()
                    left_box.label(text="━━━ LEFT SIDE ━━━", icon='BACK')

                    # Left Arms
                    arm_header = left_box.row()
                    arm_header.label(text="Arm Bones:", icon='CONSTRAINT_BONE')
                    flow = left_box.grid_flow(row_major=True, columns=2, align=True)

                    for limb_part in [('shoulder', 'Shoulder'), ('elbow', 'Elbow'), ('wrist', 'Wrist'), ('hand', 'Hand')]:
                        op = flow.operator("crossrig.pick_landmark", text=limb_part[1])
                        op.landmark_id = limb_part[0]
                        op.landmark_side = 'LEFT'

                    # Left Fingers (optional - shown when fingers enabled)
                    if prefs.smart_rig_include_fingers:
                        left_box.separator()
                        finger_header = left_box.row()
                        finger_header.label(text="Finger Bones (Optional):", icon='HAND')
                        left_box.label(text="Pick or leave for auto-generation", icon='INFO')

                        # Thumb (4 bones for Mixamo Standard)
                        left_box.label(text="Thumb:", icon='DOT')
                        flow = left_box.grid_flow(row_major=True, columns=4, align=True)
                        for seg in ['01', '02', '03', '04']:
                            op = flow.operator("crossrig.pick_landmark", text=f"Thumb {seg}")
                            op.landmark_id = f"thumb_{seg}"
                            op.landmark_side = 'LEFT'

                        # Index (4 bones for Mixamo Standard)
                        left_box.label(text="Index:", icon='DOT')
                        flow = left_box.grid_flow(row_major=True, columns=4, align=True)
                        for seg in ['01', '02', '03', '04']:
                            op = flow.operator("crossrig.pick_landmark", text=f"Index {seg}")
                            op.landmark_id = f"index_{seg}"
                            op.landmark_side = 'LEFT'

                        # Middle (4 bones for Mixamo Standard)
                        left_box.label(text="Middle:", icon='DOT')
                        flow = left_box.grid_flow(row_major=True, columns=4, align=True)
                        for seg in ['01', '02', '03', '04']:
                            op = flow.operator("crossrig.pick_landmark", text=f"Middle {seg}")
                            op.landmark_id = f"middle_{seg}"
                            op.landmark_side = 'LEFT'

                        # Ring (4 bones for Mixamo Standard)
                        left_box.label(text="Ring:", icon='DOT')
                        flow = left_box.grid_flow(row_major=True, columns=4, align=True)
                        for seg in ['01', '02', '03', '04']:
                            op = flow.operator("crossrig.pick_landmark", text=f"Ring {seg}")
                            op.landmark_id = f"ring_{seg}"
                            op.landmark_side = 'LEFT'

                        # Pinky (4 bones for Mixamo Standard)
                        left_box.label(text="Pinky:", icon='DOT')
                        flow = left_box.grid_flow(row_major=True, columns=4, align=True)
                        for seg in ['01', '02', '03', '04']:
                            op = flow.operator("crossrig.pick_landmark", text=f"Pinky {seg}")
                            op.landmark_id = f"pinky_{seg}"
                            op.landmark_side = 'LEFT'

                    # Left Legs
                    left_box.separator()
                    leg_header = left_box.row()
                    leg_header.label(text="Leg Bones:", icon='CONSTRAINT_BONE')
                    flow = left_box.grid_flow(row_major=True, columns=2, align=True)

                    for limb_part in [('hip', 'Hip'), ('knee', 'Knee'), ('ankle', 'Ankle'), ('foot', 'Foot'), ('toe', 'Toe')]:
                        op = flow.operator("crossrig.pick_landmark", text=limb_part[1])
                        op.landmark_id = limb_part[0]
                        op.landmark_side = 'LEFT'

                    # RIGHT SIDE SECTION
                    right_box = inner_box.box()
                    right_box.label(text="━━━ RIGHT SIDE ━━━", icon='FORWARD')

                    # Right Arms
                    arm_header = right_box.row()
                    arm_header.label(text="Arm Bones:", icon='CONSTRAINT_BONE')
                    flow = right_box.grid_flow(row_major=True, columns=2, align=True)

                    for limb_part in [('shoulder', 'Shoulder'), ('elbow', 'Elbow'), ('wrist', 'Wrist'), ('hand', 'Hand')]:
                        op = flow.operator("crossrig.pick_landmark", text=limb_part[1])
                        op.landmark_id = limb_part[0]
                        op.landmark_side = 'RIGHT'

                    # Right Fingers (optional - shown when fingers enabled)
                    if prefs.smart_rig_include_fingers:
                        right_box.separator()
                        finger_header = right_box.row()
                        finger_header.label(text="Finger Bones (Optional):", icon='HAND')
                        right_box.label(text="Pick or leave for auto-generation", icon='INFO')

                        # Thumb (4 bones for Mixamo Standard)
                        right_box.label(text="Thumb:", icon='DOT')
                        flow = right_box.grid_flow(row_major=True, columns=4, align=True)
                        for seg in ['01', '02', '03', '04']:
                            op = flow.operator("crossrig.pick_landmark", text=f"Thumb {seg}")
                            op.landmark_id = f"thumb_{seg}"
                            op.landmark_side = 'RIGHT'

                        # Index (4 bones for Mixamo Standard)
                        right_box.label(text="Index:", icon='DOT')
                        flow = right_box.grid_flow(row_major=True, columns=4, align=True)
                        for seg in ['01', '02', '03', '04']:
                            op = flow.operator("crossrig.pick_landmark", text=f"Index {seg}")
                            op.landmark_id = f"index_{seg}"
                            op.landmark_side = 'RIGHT'

                        # Middle (4 bones for Mixamo Standard)
                        right_box.label(text="Middle:", icon='DOT')
                        flow = right_box.grid_flow(row_major=True, columns=4, align=True)
                        for seg in ['01', '02', '03', '04']:
                            op = flow.operator("crossrig.pick_landmark", text=f"Middle {seg}")
                            op.landmark_id = f"middle_{seg}"
                            op.landmark_side = 'RIGHT'

                        # Ring (4 bones for Mixamo Standard)
                        right_box.label(text="Ring:", icon='DOT')
                        flow = right_box.grid_flow(row_major=True, columns=4, align=True)
                        for seg in ['01', '02', '03', '04']:
                            op = flow.operator("crossrig.pick_landmark", text=f"Ring {seg}")
                            op.landmark_id = f"ring_{seg}"
                            op.landmark_side = 'RIGHT'

                        # Pinky (4 bones for Mixamo Standard)
                        right_box.label(text="Pinky:", icon='DOT')
                        flow = right_box.grid_flow(row_major=True, columns=4, align=True)
                        for seg in ['01', '02', '03', '04']:
                            op = flow.operator("crossrig.pick_landmark", text=f"Pinky {seg}")
                            op.landmark_id = f"pinky_{seg}"
                            op.landmark_side = 'RIGHT'

                    # Right Legs
                    right_box.separator()
                    leg_header = right_box.row()
                    leg_header.label(text="Leg Bones:", icon='CONSTRAINT_BONE')
                    flow = right_box.grid_flow(row_major=True, columns=2, align=True)

                    for limb_part in [('hip', 'Hip'), ('knee', 'Knee'), ('ankle', 'Ankle'), ('foot', 'Foot'), ('toe', 'Toe')]:
                        op = flow.operator("crossrig.pick_landmark", text=limb_part[1])
                        op.landmark_id = limb_part[0]
                        op.landmark_side = 'RIGHT'

                    # Symmetry tools
                    row = sub_box.row(align=True)
                    row.operator("crossrig.auto_detect_symmetry", text="Auto-Mirror Landmarks", icon='MOD_MIRROR')

                    # Optional bone generation
                    options_box = sub_box.box()
                    options_box.label(text="Optional Bones:", icon='BONE_DATA')

                    # Fingers toggle with info
                    row = options_box.row()
                    row.prop(prefs, "smart_rig_include_fingers", text="Include Finger Bones")

                    # T-Pose toggle
                    row = options_box.row()
                    row.prop(prefs, "smart_rig_auto_tpose", text="Auto T-Pose After Generation")
                    if not prefs.smart_rig_auto_tpose:
                        info_row = options_box.row()
                        info_row.label(text="Disabled: Use 'Apply T-Pose' button after generation", icon='INFO')

                    if prefs.smart_rig_include_fingers:
                        info_box = options_box.box()
                        info_box.label(text="Finger Bones (5 fingers × 4 bones per hand)", icon='INFO')
                        info_box.label(text="Total: 40 finger bones (20 per hand)", icon='BONE_DATA')
                        info_box.label(text="Pick landmarks below in Left/Right sections", icon='HAND')
                        info_box.label(text="Or leave unpicked for auto-generation", icon='AUTO')

                    # Foot details toggle
                    row = options_box.row()
                    row.prop(prefs, "smart_rig_include_foot_details", text="Include Detailed Feet")

                    # Actions
                    row = sub_box.row(align=True)
                    row.operator("crossrig.generate_smart_rig", text="Generate Armature", icon='ARMATURE_DATA')
                    row.operator("crossrig.clear_all_landmarks", text="Clear All", icon='X')

                    # T-Pose button - shown in smart rig mode
                    row = sub_box.row()
                    row.operator("crossrig.apply_tpose", text="Apply T-Pose", icon='OUTLINER_OB_ARMATURE')
                    row.scale_y = 1.2

                    row = sub_box.row()
                    row.operator("crossrig.exit_smart_rig_mode", text="Exit Mode", icon='CANCEL')

                # === Generate Control Rig Section (always show when expanded) ===
                sub_box.separator()
                generate_box = sub_box.box()
                generate_box.label(text="Armature Tools:", icon='OUTLINER_OB_ARMATURE')
                row = generate_box.row()
                row.label(text="Select armature, then choose action:", icon='INFO')

                # T-Pose button
                row = generate_box.row()
                row.operator("crossrig.apply_tpose", text="Apply T-Pose", icon='OUTLINER_OB_ARMATURE')
                row.scale_y = 1.3

                # Control Rig button
                row = generate_box.row()
                row.operator("crossrig.generate_control_rig", text="Generate Rig (Rigify)", icon='CON_ARMATURE')
                row.scale_y = 1.3

            # === Bone Repositioning Subsection ===
            col.separator()
            row = col.row(align=True)
            sub_icon = 'TRIA_DOWN' if prefs.show_bone_reposition else 'TRIA_RIGHT'
            row.prop(prefs, "show_bone_reposition", icon=sub_icon, icon_only=True, emboss=False)
            row.label(text="Bone Repositioning", icon='BONE_DATA')

            if prefs.show_bone_reposition:
                sub_box = col.box()

                if not prefs.bone_reposition_active:
                    # Not in bone reposition mode - show setup
                    row = sub_box.row()
                    row.prop(prefs, "bone_reposition_armature", text="Armature")

                    row = sub_box.row()
                    row.prop(prefs, "bone_reposition_mesh", text="Mesh")

                    row = sub_box.row()
                    row.prop(prefs, "bone_reposition_mirror", text="Mirror Mode (L ↔ R)")

                    # Smart armature-to-mesh mapping (Full body auto-detection)
                    row = sub_box.row()
                    row.label(text="Smart Body Mapping:", icon='ARMATURE_DATA')

                    row = sub_box.row()
                    row.operator("crossrig.smart_map_armature_to_mesh", text="Auto-Detect Body Landmarks", icon='UV_SYNC_SELECT')
                    row.scale_y = 1.5

                    # Smart hand-finger mapping buttons
                    row = sub_box.row()
                    row.label(text="Smart Hand Mapping:", icon='HAND')

                    row = sub_box.row()
                    split = row.split(factor=0.5)
                    left_col = split.column()
                    right_col = split.column()

                    op = left_col.operator("crossrig.smart_map_hand_fingers", text="Map Left Hand", icon='FORWARD')
                    op.side = 'LEFT'

                    op = right_col.operator("crossrig.smart_map_hand_fingers", text="Map Right Hand", icon='BACK')
                    op.side = 'RIGHT'

                    # Finger alignment tool
                    row = sub_box.row()
                    row.label(text="Finger Alignment:", icon='SNAP_ON')

                    row = sub_box.row()
                    row.operator("crossrig.align_finger_to_hand", text="Align Selected Finger to Hand", icon='ORIENTATION_NORMAL')
                    row.scale_y = 1.3

                    row = sub_box.row()
                    row.label(text="In Pose Mode: Select finger tip → Click Align", icon='INFO')

                    # Interactive finger alignment by clicking mesh
                    row = sub_box.row()
                    row.operator("crossrig.align_finger_by_mesh_click", text="Click Finger Tip to Align", icon='HAND')
                    row.scale_y = 1.3

                    row = sub_box.row()
                    row.label(text="In Object Mode: Click on finger tip mesh to auto-align", icon='INFO')

                    row = sub_box.row()
                    row.operator("crossrig.start_bone_reposition_mode", text="Start Repositioning", icon='PLAY')

                    row = sub_box.row()
                    row.label(text="Select armature and mesh, then click Start", icon='INFO')
                else:
                    # In bone reposition mode - show bone list
                    armature_obj = prefs.bone_reposition_armature

                    if armature_obj and armature_obj.type == 'ARMATURE':
                        row = sub_box.row()
                        row.label(text=f"Armature: {armature_obj.name}", icon='ARMATURE_DATA')
                        row = sub_box.row()
                        row.label(text=f"Mesh: {prefs.bone_reposition_mesh.name}", icon='MESH_DATA')

                        # Show bone count
                        bone_count = len(armature_obj.data.bones)
                        row = sub_box.row()
                        row.label(text=f"Bones: {bone_count}", icon='BONE_DATA')

                        # Show mirror mode status
                        if prefs.bone_reposition_mirror:
                            row = sub_box.row()
                            row.label(text="Mirror Mode: ON (L ↔ R)", icon='MOD_MIRROR')

                        # Toggle mirror mode while active
                        row = sub_box.row()
                        row.prop(prefs, "bone_reposition_mirror", text="Mirror Mode")

                        # Import grouping functions
                        from .bone_reposition_operators import group_bones_by_category, get_group_icon

                        # Get all bone names and group them
                        bone_names = [bone.name for bone in armature_obj.data.bones]
                        bone_groups = group_bones_by_category(bone_names)

                        # List bones organized by groups
                        inner_box = sub_box.box()
                        inner_box.label(text="Click bone to reposition:", icon='HAND')

                        # Display each group
                        for group_name, bones in bone_groups.items():
                            if not bones:
                                continue

                            # Group header
                            group_box = inner_box.box()
                            group_icon = get_group_icon(group_name)
                            group_box.label(text=f"{group_name} ({len(bones)})", icon=group_icon)

                            # Special handling for hand groups - show finger subgroups
                            if group_name in ['Left Hand', 'Right Hand']:
                                # Import finger detection function
                                from .bone_reposition_operators import detect_hand_finger_hierarchy

                                # Determine side
                                side = 'LEFT' if 'Left' in group_name else 'RIGHT'

                                # Detect hand and fingers
                                hand_data = detect_hand_finger_hierarchy(armature_obj, side)

                                if hand_data['hand']:
                                    # Show hand bone first
                                    hand_box = group_box.box()
                                    hand_box.label(text="Hand Bone:", icon='BONE_DATA')
                                    op = hand_box.operator("crossrig.reposition_bone", text=hand_data['hand'])
                                    op.bone_name = hand_data['hand']

                                    # Show finger groups with smart align buttons
                                    finger_box = group_box.box()
                                    finger_box.label(text="Smart Finger Alignment:", icon='HAND')

                                    # Create 5-column layout for fingers
                                    finger_grid = finger_box.grid_flow(row_major=False, columns=5, align=True)

                                    for finger_type in ['thumb', 'index', 'middle', 'ring', 'pinky']:
                                        finger_bones = hand_data['fingers'].get(finger_type, [])
                                        if finger_bones:
                                            # Create column for this finger
                                            finger_col = finger_grid.column(align=True)

                                            # Finger icon and name
                                            finger_col.label(text=finger_type.capitalize(), icon='NORMALIZE_FCURVES')

                                            # Smart align button
                                            op = finger_col.operator(
                                                "crossrig.smart_align_finger_to_mesh",
                                                text=f"Align",
                                                icon='SNAP_ON'
                                            )
                                            op.finger_type = finger_type
                                            op.side = side

                                            # Show bone count
                                            finger_col.label(text=f"({len(finger_bones)} bones)")

                                    # Show all finger bones in expandable section
                                    bones_box = group_box.box()
                                    bones_box.label(text="Individual Bones:", icon='BONE_DATA')

                                    # Get repositioned bones history
                                    history = prefs.bone_reposition_history
                                    repositioned_set = set(history.split(',')) if history else set()

                                    flow = bones_box.grid_flow(row_major=True, columns=2, align=True)
                                    for bone_name in bones:
                                        row = flow.row(align=True)

                                        # Show checkmark for repositioned bones
                                        if bone_name in repositioned_set:
                                            row.label(text="", icon='CHECKMARK')

                                        op = row.operator("crossrig.reposition_bone", text=bone_name)
                                        op.bone_name = bone_name
                                else:
                                    # Fallback: show bones normally if hand not detected
                                    # Get repositioned bones history
                                    history = prefs.bone_reposition_history
                                    repositioned_set = set(history.split(',')) if history else set()

                                    flow = group_box.grid_flow(row_major=True, columns=2, align=True)
                                    for bone_name in bones:
                                        row = flow.row(align=True)
                                        if bone_name in repositioned_set:
                                            row.label(text="", icon='CHECKMARK')
                                        op = row.operator("crossrig.reposition_bone", text=bone_name)
                                        op.bone_name = bone_name
                            else:
                                # Display bones in this group (2 columns)
                                # Get repositioned bones history
                                history = prefs.bone_reposition_history
                                repositioned_set = set(history.split(',')) if history else set()

                                flow = group_box.grid_flow(row_major=True, columns=2, align=True)

                                for bone_name in bones:
                                    row = flow.row(align=True)
                                    # Show checkmark for repositioned bones
                                    if bone_name in repositioned_set:
                                        row.label(text="", icon='CHECKMARK')
                                    op = row.operator("crossrig.reposition_bone", text=bone_name)
                                    op.bone_name = bone_name

                    # Show repositioned bones count
                    history = prefs.bone_reposition_history
                    repositioned_count = len([b for b in history.split(',') if b]) if history else 0

                    if repositioned_count > 0:
                        row = sub_box.row()
                        row.label(text=f"Repositioned: {repositioned_count} bones", icon='INFO')

                    # Clear history button
                    if repositioned_count > 0:
                        row = sub_box.row()
                        row.operator("crossrig.clear_bone_reposition_history", text="Clear History", icon='X')

                    # Exit button
                    row = sub_box.row()
                    row.operator("crossrig.exit_bone_reposition_mode", text="Exit Mode", icon='CANCEL')

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
