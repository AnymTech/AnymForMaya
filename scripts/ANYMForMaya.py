import os, sys
import re
import json
import webbrowser
import math
import maya.cmds as cmds
import maya.api.OpenMaya as om
import inspect

def get_plugin_root():
	return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

PLUGIN_ROOT = get_plugin_root()
ICONS_DIR = os.path.join(PLUGIN_ROOT, '..', 'res', 'icons')
MODEL_PATH = os.path.join(PLUGIN_ROOT, '..', 'res', 'model', 'AnymModel.fbx')
DATA_DIR = os.path.join(os.path.expanduser('~'), '.AnymForMaya')
DEPENDENCIES_DIR = os.path.join(PLUGIN_ROOT, '..', 'dependencies')

if not os.path.exists(DATA_DIR):
	os.makedirs(DATA_DIR)

if DEPENDENCIES_DIR not in sys.path:
	sys.path.insert(0, DEPENDENCIES_DIR)

import requests

start_poses = {
	"--select armature--": None,
	'tpose': '0.0 0.0 0.91 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0',
	'standing': '0.0 0.0 0.915556 -2.686633 -2.507240 -3.725996 8.863924 -0.977226 1.382313 0.000000 0.113183 10.036398 2.418233 -4.287297 -4.288259 0.000000 0.000000 -0.000001 0.968358 5.593504 0.122170 0.435359 -0.016123 8.599061 -5.051244 -1.822243 -5.085787 0.000000 0.000000 -0.000001 0.807181 4.508004 -1.114769 -3.923263 -1.782650 11.946513 -2.286621 0.419885 -1.593431 5.200063 -3.178905 -5.355329 -1.712830 1.747785 16.304016 -1.668256 9.644320 4.197483 -3.659436 71.470565 5.343645 -32.365001 -8.193753 17.004270 -8.932759 7.274603 17.997885 4.799549 -14.141005 0.980003 14.342044 -67.479631 0.540239 24.710453 10.176975 12.695284 5.134529 -5.652613 22.329369\n',
	'walking': '0.0 0.0 0.869634 -5.156413 -1.214391 -5.410411 -1.709857 2.046793 -20.518447 -0.194409 2.821928 9.639633 22.674375 2.022817 7.065949 0.319114 -0.242817 -0.046777 -0.485952 -0.883780 21.276853 12.540215 -1.923606 17.813456 -12.848437 -5.769769 -8.659176 -0.403757 0.317752 -0.080174 4.731687 0.752432 14.091849 -1.918952 0.502233 1.095741 1.762074 0.605030 1.362915 -1.460636 4.213001 -19.982780 -0.953491 -5.442693 5.160420 5.932315 5.130612 1.747537 18.007731 72.350556 25.328865 -31.373172 -5.726233 -2.154197 2.176981 19.996316 -18.105757 1.457258 -5.002118 -1.150550 23.709883 -64.830696 -12.471515 41.735666 7.170822 -5.860969 -0.917491 -16.211826 -11.683631\n',
	'running': '0.0 0.0 0.944308 12.812485 -3.764145 -3.449099 6.162934 -2.591651 21.884037 -16.779459 5.769927 1.611377 12.924832 2.332486 2.128104 0.000000 0.000000 -0.000001 2.281804 7.332328 -16.747847 -10.971671 -0.227808 8.013506 -23.763674 -7.757531 -2.377268 0.000000 0.000000 -0.000001 -10.430504 6.608937 6.446684 -10.014379 -4.599386 6.985147 -10.106457 -0.428153 2.249650 8.424983 -2.053782 -10.427315 2.427841 1.754064 0.686918 -6.744412 -1.306699 4.014442 -37.160491 65.066568 -17.400981 -107.616498 0.533386 23.300145 -20.239555 -7.541115 -2.493251 -8.147590 2.082604 4.206349 -35.837155 -62.851323 58.385568 113.784891 1.138298 20.943669 23.422029 -4.067571 -27.872150\n',
	'crouched': '0.0 0.0 0.792000 -7.587353 -3.244431 -5.244226 10.449458 -2.692427 1.237742 8.725213 8.053955 59.866197 28.034230 4.273684 -27.513477 -0.000001 -0.000000 0.000000 -12.310561 4.514536 -49.888928 -24.246104 5.546499 49.671887 -30.678573 9.327886 5.286487 0.000001 0.000000 0.000000 -8.409343 1.527181 46.302820 -4.850420 0.085146 10.987337 -3.818213 -0.937031 2.779952 15.485148 4.624125 9.982532 6.171311 -0.166689 -33.296183 -22.539460 -6.687543 -7.196572 -42.859961 27.952473 -40.464302 -95.768290 -24.000663 9.008869 -17.402181 -4.216924 19.540276 20.828827 7.671515 -3.644733 22.885188 -70.705963 -26.571569 73.503613 7.590814 9.765324 12.214401 -0.851391 0.037118\n',
	'fighting': '0.0 0.0 0.929197 1.998556 0.365758 -2.714235 11.078149 -15.233524 -13.417147 15.345969 0.333671 13.138032 12.556353 10.035754 18.094387 0.000000 0.000000 -0.000001 -7.943415 11.946518 7.718570 -9.117149 -5.011846 5.266846 -16.635733 -4.257653 0.560239 0.000000 0.000000 -0.000001 0.645713 -0.742055 11.902913 3.841259 2.161500 -1.203929 0.955819 0.166722 -0.892026 12.257349 -0.606808 2.459871 15.515777 3.088477 13.207125 -10.436967 -19.768036 -9.090913 -52.863180 56.077539 -40.028783 -112.513607 -29.267658 25.987605 -6.362055 -16.723496 -3.005818 13.895320 20.171606 -7.156372 83.480282 -55.718614 -57.387083 110.505613 0.414810 22.901932 13.447608 21.708462 -25.038953\n',
}

def get_api_key():
	filepath = os.path.join(DATA_DIR, 'settings.json')
	if not os.path.exists(filepath):
		default_key = {'api_key': '123456789'}
		with open(filepath, 'w') as f:
			json.dump(default_key, f)
	with open(filepath, 'r') as f:
		api_key = json.load(f).get('api_key', '123456789')
	return api_key.strip()

def store_api_key(key):
	filepath = os.path.join(DATA_DIR, 'settings.json')
	with open(filepath, 'w') as json_file:
		json.dump({'api_key': key}, json_file)

def remove_nr(s):
	head = s.rstrip('0123456789')
	tail = s[len(head):]
	return head, tail

def duplicate_and_rename_full_skeleton(root, suffix):
	duplicates = cmds.duplicate(root, renameChildren=True)
	_, pose_nr = remove_nr(root)

	if not duplicates:
		cmds.error(f"Could not duplicate skeleton from: {root}")
	new_root = duplicates[0]

	dup_joints = cmds.listRelatives(new_root, ad=True, type='joint') or []
	spine_counter = 2

	for jnt in dup_joints:
		short_name, _ = remove_nr(jnt.split("|")[-1])
		if "Spine" in short_name:
			short_name = short_name[:5] + str(spine_counter) if spine_counter > 0 else short_name[:5]
			spine_counter -= 1
		if len(pose_nr) > 0:
			short_name += '_' + pose_nr
		short_name += suffix
		cmds.rename(jnt, short_name)

	cmds.rename(new_root, root + suffix)
	return root + suffix

def get_all_joints(root):
	all_joints_ = cmds.listRelatives(root, ad=True, type='joint') or []
	all_joints_.append(root)
	all_joints_ = cmds.ls(all_joints_, l=True)
	all_joints = []
	for jnt in all_joints_:
		if root in jnt:
			all_joints.append(jnt)
	return all_joints

def create_limb_ik_handles(ik_root, box_scale=0.05, model=False):
	limb_chains = [
		("LeftArm_IK",  "LeftHand_IK",  f"{ik_root}_LeftArm_IKHandle"),
		("RightArm_IK", "RightHand_IK", f"{ik_root}_RightArm_IKHandle"),
		("LeftHip_IK",  "LeftFoot_IK",  f"{ik_root}_LeftLeg_IKHandle"),
		("RightHip_IK", "RightFoot_IK", f"{ik_root}_RightLeg_IKHandle"),
	]

	ik_handles = []
	ik_ctrls = []

	for start_jnt, end_jnt, handle_name in limb_chains:
		start_full = find_joint_in_dup(ik_root, start_jnt)
		end_full   = find_joint_in_dup(ik_root, end_jnt)
		if not start_full or not end_full:
			continue

		ik_handle, effector = cmds.ikHandle(
			startJoint=start_full,
			endEffector=end_full,
			solver='ikRPsolver',
			name=handle_name
		)
		cmds.setAttr(f"{handle_name}.displayLocalAxis", 0)
		cmds.setAttr(f"{handle_name}.displayHandle", 0)

		ctrl_name = handle_name.replace("IKHandle", "IKCtrl")
		if 'leg' in ctrl_name.lower():
			mp = 3.5
			if model:
				box_scale = .05
				box_points = [
					(-box_scale, -mp*box_scale, -box_scale),
					(-box_scale,  2*box_scale, -box_scale),
					(-box_scale,  2*box_scale,  box_scale),
					(-box_scale, -.5*box_scale,box_scale),
					(-box_scale, -mp*box_scale, -box_scale),
					( box_scale, -mp*box_scale, -box_scale),
					( box_scale,  2*box_scale, -box_scale),
					(-box_scale,  2*box_scale, -box_scale),
					( box_scale,  2*box_scale, -box_scale),
					( box_scale,  2*box_scale,  box_scale),
					(-box_scale,  2*box_scale,  box_scale),
					( box_scale,  2*box_scale,  box_scale),
					( box_scale, -.5*box_scale,box_scale),
					(-box_scale, -.5*box_scale,box_scale),
					( box_scale, -.5*box_scale,box_scale),
					( box_scale, -mp*box_scale, -box_scale),
				]
			else:
				box_points = [
					(-box_scale, -mp*box_scale, -box_scale),
					(-box_scale,  box_scale, -box_scale),
					(-box_scale,  box_scale,  box_scale),
					(-box_scale, -box_scale,box_scale),
					(-box_scale, -mp*box_scale, -box_scale),
					( box_scale, -mp*box_scale, -box_scale),
					( box_scale,  box_scale, -box_scale),
					(-box_scale,  box_scale, -box_scale),
					( box_scale,  box_scale, -box_scale),
					( box_scale,  box_scale,  box_scale),
					(-box_scale,  box_scale,  box_scale),
					( box_scale,  box_scale,  box_scale),
					( box_scale, -box_scale,box_scale),
					(-box_scale, -box_scale,box_scale),
					( box_scale, -box_scale,box_scale),
					( box_scale, -mp*box_scale, -box_scale),
				]
		elif 'left' in ctrl_name.lower():
			if model:
				box_scale = .07
			box_points = [
				(-box_scale, -box_scale, -.5*box_scale),
				(-box_scale, box_scale, -.5*box_scale),
				(-box_scale, box_scale, .5*box_scale),
				(-box_scale, -box_scale, .5*box_scale),
				(-box_scale, -box_scale, -.5*box_scale),
				(box_scale, -.5*box_scale, -.5*box_scale),
				(box_scale, .5*box_scale, -.5*box_scale),
				(-box_scale, box_scale, -.5*box_scale),
				(box_scale, .5*box_scale, -.5*box_scale),
				(box_scale, .5*box_scale, .5*box_scale),
				(-box_scale, box_scale, .5*box_scale),
				(box_scale, .5*box_scale, .5*box_scale),
				(box_scale, -.5*box_scale, .5*box_scale),
				(-box_scale, -box_scale, .5*box_scale),
				(box_scale, -.5*box_scale, .5*box_scale),
				(box_scale, -.5*box_scale, -.5*box_scale),
			]
		else:
			if model:
				box_scale = .07
			box_points = [
				(-box_scale, -.5*box_scale, -.5*box_scale),
				(-box_scale, .5*box_scale, -.5*box_scale),
				(-box_scale, .5*box_scale, .5*box_scale),
				(-box_scale, -.5*box_scale, .5*box_scale),
				(-box_scale, -.5*box_scale, -.5*box_scale),
				(box_scale, -box_scale, -.5*box_scale),
				(box_scale, box_scale, -.5*box_scale),
				(-box_scale, .5*box_scale, -.5*box_scale),
				(box_scale, box_scale, -.5*box_scale),
				(box_scale, box_scale, .5*box_scale),
				(-box_scale, .5*box_scale, .5*box_scale),
				(box_scale, box_scale, .5*box_scale),
				(box_scale, -box_scale, .5*box_scale),
				(-box_scale, -.5*box_scale, .5*box_scale),
				(box_scale, -box_scale, .5*box_scale),
				(box_scale, -box_scale, -.5*box_scale),
			]

		ik_ctrl = cmds.curve(name=ctrl_name, degree=1, point=box_points)
		cmds.setAttr(ik_ctrl + ".overrideEnabled", 1)
		cmds.setAttr(ik_ctrl + ".overrideColor", 12)
		offset_grp = cmds.group(ik_ctrl, name=ctrl_name + "_offset")

		cmds.delete(cmds.parentConstraint(end_full, offset_grp, mo=False))

		cmds.pointConstraint(ik_ctrl, ik_handle, mo=False)
		cmds.orientConstraint(ik_ctrl, end_full, mo=True, name=ctrl_name.replace("Ctrl","_Orient"))

		if 'leg' in ctrl_name.lower():
			cmds.xform(
				ik_ctrl, 
				ws=True, 
				t = cmds.xform(find_joint_in_dup(ik_root.split('_')[0], end_jnt.split('_')[0]), q=True, ws=True, t=True)
			)

		for attr in ('sx', 'sy', 'sz'):
			cmds.setAttr(f"{ik_ctrl}.{attr}", lock=True, keyable=False)

		ik_handles.append(ik_handle)
		ik_ctrls.append(offset_grp)

	return ik_handles, ik_ctrls

def create_master_control(root, total_root, scale=0.15):
	rig_master_grp = f"{root}_FullBodyRig_Grp"
	
	master_ctrl = cmds.circle(name=f"{root}_Master_Ctrl", normal=[0, 1, 0], radius=scale*2, sections=16)[0]
	master_offset = total_root
	
	root_pos = cmds.xform(root, query=True, worldSpace=True, translation=True)
	cmds.xform(master_offset, worldSpace=True, translation=[root_pos[0], 0, root_pos[2]])
	
	if cmds.objExists(rig_master_grp):
		current_parent = cmds.listRelatives(rig_master_grp, parent=True)
		if current_parent and current_parent[0] == root:
			cmds.parent(rig_master_grp, world=True)
	
	cmds.parent(root, master_ctrl)
	cmds.parent(master_ctrl, master_offset)
	
	if cmds.objExists(rig_master_grp):
		cmds.parent(rig_master_grp, master_ctrl)
		
	for attr in ['sx', 'sy', 'sz']:
		cmds.setAttr(f"{master_ctrl}.{attr}", lock=True, keyable=False)
	
	return master_ctrl

def create_fk_controls(fk_root, radius=0.025, model=False):
	rig_tag = fk_root.split("|")[-1].replace("_FK", "")
	ik_terminal_names = {
		'LeftArm', 'LeftForearm', 'LeftHand',
		'RightArm', 'RightForearm', 'RightHand',
		'LeftHip', 'LeftKnee', 'LeftFoot', 'LeftToe',
		'RightHip', 'RightKnee', 'RightFoot', 'RightToe'
	}
	radii = {
		'Spine': .125,
		'Spine1': .15,
		'Spine2': .18,
		'LeftShoulder': .08,
		'RightShoulder': .08,
		'LeftArm': .09,
		'RightArm': .09,
		'LeftHand': .04,
		'RightHand': .04,
		'Neck': .08,
		'Head': .1,
		'LeftKnee': .08,
		'RightKnee': .08,
	}

	s = 0.2 if model else 0.1 
	h = 0.8660254037844386 * s
	hex_pts = [
		( s,     0.0, 0.0),
		( 0.5*s,  h,  0.0),
		(-0.5*s,  h,  0.0),
		(-s,     0.0, 0.0),
		(-0.5*s, -h,  0.0),
		( 0.5*s, -h,  0.0),
		( s,     0.0, 0.0),
	]

	fk_joints = get_all_joints(fk_root) 
	offset_grps = []
	ctrl_dict = {} 
	temp_container = cmds.group(em=True, n=f"{rig_tag}_FKCtrls_TMP_GRP")

	for jnt in fk_joints:
		if "_tip" in jnt or jnt.endswith(fk_root):
			continue

		leaf = jnt.split("|")[-1]      
		basename = leaf[:-3] if leaf.endswith("_FK") else leaf 

		if any(k in leaf for k in ("Spine", "Neck", "Head", "Hip", "Knee")):
			normal = [0, 0, 1]
		elif "Foot" in leaf or "Toe" in leaf:
			normal = [0, 1, 0]
		else:
			normal = [1, 0, 0]

		if "Hips" in leaf:
			ctrl_name   = f"{rig_tag}_Hips_Ctrl"
			offset_name = f"{ctrl_name}_offset"
			ctrl = cmds.curve(name=ctrl_name, degree=1, point=hex_pts)
			lock_attrs = ('sx','sy','sz')
			color = 14
		else:
			if model:
				radius = radii.get(jnt.split('|')[-1][:-3], .06)
			ctrl_name   = f"{rig_tag}_{basename}_FKCtrl"
			offset_name = f"{ctrl_name}_offset"
			ctrl = cmds.circle(name=ctrl_name, normal=normal, radius=radius)[0]
			lock_attrs = ('tx','ty','tz','sx','sy','sz')
			color = 18

		offset_grp = cmds.group(ctrl, name=offset_name)
		cmds.parent(offset_grp, temp_container)

		cmds.delete(cmds.parentConstraint(jnt, offset_grp))

		ctrl_long   = cmds.ls(ctrl, l=True)[0]
		offset_long = cmds.ls(offset_grp, l=True)[0]

		cmds.orientConstraint(ctrl_long, jnt, maintainOffset=True)
		
		jnt_pos = cmds.xform(jnt, query=True, worldSpace=True, translation=True)
		jnt_name = jnt.split('|')[-1]
		if 'Head' in jnt_name:
			cmds.xform(ctrl, r=True, os=True, t=[0.,-.03,.15])
		elif 'Neck' in jnt_name:
			cmds.xform(ctrl, r=True, os=True, t=[0.,-.03,.02])
		elif 'Spine' in jnt_name:
			cmds.xform(ctrl, r=True, os=True, t=[0.,-.03,0.])
		elif 'Arm' in jnt_name:
			cmds.xform(ctrl, r=True, os=True, t=[0.,0.,-.03])
		elif 'Hand' in jnt_name:
			cmds.xform(ctrl, r=True, os=True, t=[0.,0.,-.02])
		elif 'Foot' in jnt_name or 'Toe' in jnt_name:
			cmds.xform(ctrl, r=True, os=True, t=[0.,0.,-.02])
	
		cmds.setAttr(ctrl + ".overrideEnabled", 1)
		cmds.setAttr(ctrl + ".overrideColor", color)
		for attr in lock_attrs:
			cmds.setAttr(f"{ctrl}.{attr}", lock=True, keyable=False)

		if "Hips" in leaf:
			cmds.pointConstraint(ctrl_long, jnt, mo=False)

			base_root = fk_root.replace("_FK", "") 
			base_hips = find_joint_in_dup(base_root, basename)
			if base_hips:
				cmds.pointConstraint(ctrl_long, base_hips, mo=False)

			ik_root = f"{base_root}_IK"  
			ik_hips = find_joint_in_dup(ik_root, basename + "_IK")
			if ik_hips:
				cmds.pointConstraint(ctrl_long, ik_hips, mo=False)

		else:
			if basename not in ik_terminal_names:
				base_root = fk_root.replace("_FK", "")
				ik_root = f"{base_root}_IK"
				ik_jnt = find_joint_in_dup(ik_root, basename + "_IK")
				if ik_jnt:
					cmds.delete(cmds.parentConstraint(ik_jnt, offset_long))
					cmds.orientConstraint(ctrl_long, ik_jnt, maintainOffset=True)

		ctrl_dict[jnt] = {'ctrl': ctrl_long, 'offset': offset_long}
		offset_grps.append(offset_long)

	for jnt in fk_joints:
		if "_tip" in jnt:
			continue
		parent_joint = cmds.listRelatives(jnt, parent=True, fullPath=True)
		if parent_joint and parent_joint[0] in ctrl_dict and jnt in ctrl_dict:
			parent_ctrl   = ctrl_dict[parent_joint[0]]['ctrl']
			current_offset = ctrl_dict[jnt]['offset']
			cmds.parent(current_offset, parent_ctrl)

	top_offset = offset_grps[-1]
	cmds.parent(top_offset, fk_root)
	cmds.delete(temp_container)

	return fk_root + '|' + top_offset.split('|')[-1]

def find_joint_in_dup(dup_root, joint_name):
	all_joints = cmds.listRelatives(dup_root, ad=True, type='joint') or []
	all_joints.append(dup_root)
	all_joints = cmds.ls(all_joints, l=True)
	for jnt_path in all_joints:
		name = jnt_path.split("|")[-1].split("_")[0]
		if joint_name.split("_")[0] == name and 'tip' not in jnt_path:
			return jnt_path
	return None

def _wire_ik_fk_visibility(root, switch_ctrl, switch_attr, ik_nodes, fk_nodes, threshold=0.5):
	fk_cond = cmds.shadingNode("condition", asUtility=True, name=f"{root}_FK_Vis_COND")
	cmds.setAttr(f"{fk_cond}.operation", 4)
	cmds.setAttr(f"{fk_cond}.secondTerm", 0.99)
	cmds.setAttr(f"{fk_cond}.colorIfTrueR", 1)
	cmds.setAttr(f"{fk_cond}.colorIfFalseR", 0)
	cmds.connectAttr(f"{switch_ctrl}.{switch_attr}", f"{fk_cond}.firstTerm", f=True)

	ik_cond = cmds.shadingNode("condition", asUtility=True, name=f"{root}_IK_Vis_COND")
	cmds.setAttr(f"{ik_cond}.operation", 2)
	cmds.setAttr(f"{ik_cond}.secondTerm", 0.01)
	cmds.setAttr(f"{ik_cond}.colorIfTrueR", 1)
	cmds.setAttr(f"{ik_cond}.colorIfFalseR", 0)
	cmds.connectAttr(f"{switch_ctrl}.{switch_attr}", f"{ik_cond}.firstTerm", f=True)

	invisible_fk_names = ['LeftArm_FKCtrl_offset', 'RightArm_FKCtrl_offset', 'LeftHip_FKCtrl_offset', 'RightHip_FKCtrl_offset']
	for n_ in invisible_fk_names:
		n = find_in_group(root.split('_')[0], root + '_' + n_)
		if cmds.objExists(n):
			cmds.connectAttr(f"{fk_cond}.outColorR", f"{n}.visibility", f=True)
	for n_ in ik_nodes:
		n = find_in_group(root.split('_')[0], n_)
		if cmds.objExists(n):
			cmds.connectAttr(f"{ik_cond}.outColorR", f"{n}.visibility", f=True)

def create_ik_fk_switch(base_root, ik_root, fk_root, switch_name="IK_FK_Switch", scale=0.05):
	base_joints = get_all_joints(base_root)
	ik_joints   = get_all_joints(ik_root)
	fk_joints   = get_all_joints(fk_root)
	for joint in base_joints + ik_joints + fk_joints:
		if not "_tip" in joint and not joint.endswith(base_root):
			for attr in ['t', 's']:
				cmds.setAttr(f"{joint}.{attr}x", lock=True, keyable=False)
				cmds.setAttr(f"{joint}.{attr}y", lock=True, keyable=False)
				cmds.setAttr(f"{joint}.{attr}z", lock=True, keyable=False)

	base_dict = { jnt.split("|")[-1]: jnt for jnt in base_joints }
	ik_dict   = { jnt.split("|")[-1]: jnt for jnt in ik_joints }
	fk_dict   = { jnt.split("|")[-1]: jnt for jnt in fk_joints }

	switch_ctrl = cmds.curve(name=f"{base_root}_IKFK_Switch_Ctrl", degree=1, point=[
		(-scale, scale, scale), (scale, scale, scale), (scale, -scale, scale), (-scale, -scale, scale), 
		(-scale, scale, scale), (-scale, scale, -scale), (scale, scale, -scale), (scale, scale, scale), 
		(scale, scale, -scale), (scale, -scale, -scale), (scale, -scale, scale), (scale, -scale, -scale), 
		(-scale, -scale, -scale), (-scale, -scale, scale), (-scale, -scale, -scale), (-scale, scale, -scale)
	])
	
	switch_offset = cmds.group(switch_ctrl, name=f"{switch_ctrl}_offset")
	
	cmds.xform(switch_offset, ws=True, t=[.4, .6, 0])
	
	cmds.addAttr(switch_ctrl, longName=switch_name, attributeType="double",
				 min=0, max=1, defaultValue=1., keyable=True)

	for short_name, base_path in base_dict.items():
		_, pose_nr = remove_nr(base_root)
		if len(pose_nr) == 0:
			ik_path = ik_dict.get(short_name + "_IK", None)
			fk_path = fk_dict.get(short_name + "_FK", None)
		else:
			ik_path = ik_dict.get(short_name + f"_{pose_nr}" + "_IK", None)
			fk_path = fk_dict.get(short_name + f"_{pose_nr}" + "_FK", None)
			base_strs = base_path.split("|")
			base_path = "|".join(base_strs)
			
		if ik_path and fk_path:
			bc_node = cmds.shadingNode("blendColors", asUtility=True, 
									   name=f"{short_name}_BC")
			cmds.connectAttr(f"{ik_path}.rotate", f"{bc_node}.color1", force=True)
			cmds.connectAttr(f"{fk_path}.rotate", f"{bc_node}.color2", force=True)
			cmds.connectAttr(f"{bc_node}.output", f"{base_path}.rotate", force=True)

			cmds.connectAttr(f"{switch_ctrl}.{switch_name}", 
							 f"{bc_node}.blender", force=True)
			
	return switch_ctrl, switch_offset

def create_pole_vector_controls(ik_root, ik_handles, parent_group):
	handle_start_joint = {
		f"{ik_root}_LeftArm_IKHandle":  "LeftShoulder_IK",
		f"{ik_root}_RightArm_IKHandle": "RightShoulder_IK",
		f"{ik_root}_LeftLeg_IKHandle":  "LeftHip_IK",
		f"{ik_root}_RightLeg_IKHandle": "RightHip_IK"
	}
	handle_mid_joint = {
		f"{ik_root}_LeftArm_IKHandle":  "LeftForearm",
		f"{ik_root}_RightArm_IKHandle": "RightForearm",
		f"{ik_root}_LeftLeg_IKHandle":  "LeftKnee",
		f"{ik_root}_RightLeg_IKHandle": "RightKnee"
	}
	handle_end_joint = {
		f"{ik_root}_LeftArm_IKHandle":  "LeftHand_IK",
		f"{ik_root}_RightArm_IKHandle": "RightHand_IK",
		f"{ik_root}_LeftLeg_IKHandle":  "LeftFoot_IK",
		f"{ik_root}_RightLeg_IKHandle": "RightFoot_IK"
	}
	for ik_handle in ik_handles:
		start_joint_path = find_joint_in_dup(ik_root, handle_start_joint.get(ik_handle, None))
		mid_joint_path = find_joint_in_dup(ik_root.split('_')[0], handle_mid_joint.get(ik_handle, None))
		end_joint_path = find_joint_in_dup(ik_root, handle_end_joint.get(ik_handle, None))
		pv_locator = cmds.spaceLocator(name=f"{ik_handle}_PV")[0]
		for axis in ("X","Y","Z"):
			cmds.setAttr(f"{ik_handle}_PV.localScale{axis}", 0.1)
		
		A = om.MVector(cmds.xform(start_joint_path, q=True, ws=True, t=True))
		B = om.MVector(cmds.xform(mid_joint_path, q=True, ws=True, t=True))
		C = om.MVector(cmds.xform(end_joint_path, q=True, ws=True, t=True))
		
		diff = C - A
		halfway_point = A + diff/2
		if (B - halfway_point).length() > .07:
			direction = (B - halfway_point).normalize()
			pv_position = B + direction * .2
		else:
			if 'arm' in ik_handle.lower():
				pv_position = B + om.MVector(0,0,-.15)
			else:
				pv_position = B + om.MVector(0,0,.15)
		
		cmds.xform(pv_locator, ws=True, t=pv_position)
		cmds.poleVectorConstraint(pv_locator, ik_handle)		
		cmds.parent(pv_locator, parent_group)

def setup_full_body_ik_fk(root, total_root, model=False):
	
	ik_root = duplicate_and_rename_full_skeleton(root, "_IK")
	ik_root_long = cmds.ls(ik_root, l=True)[0]
	ik_grp = cmds.group(ik_root_long, name=f"{root}_IK_Skel_Grp")

	fk_root = duplicate_and_rename_full_skeleton(root, "_FK")
	fk_root_long = cmds.ls(fk_root, l=True)[0]
	fk_grp = cmds.group(fk_root_long, name=f"{root}_FK_Skel_Grp")

	ik_handles, ik_ctrls = create_limb_ik_handles(ik_grp, model=model)
	if ik_handles:
		ik_handles_grp = cmds.group(ik_handles + ik_ctrls, name=f"{root}_IK_Handles_Grp")
		cmds.parent(ik_handles_grp, ik_grp)

	offset_grp_fk = create_fk_controls(fk_root, model=model)
	cmds.parent(offset_grp_fk, fk_grp)

	create_pole_vector_controls(ik_grp, ik_handles, ik_grp)

	controls_grp, offset_grp = create_ik_fk_switch(root, ik_grp, fk_grp, switch_name=f"{root}_IK_FK_Switch")
	cmds.parent(controls_grp, root)
	cmds.parent(offset_grp, root)

	rig_master_grp = f"{root}_FullBodyRig_Grp"
	if not cmds.objExists(rig_master_grp):
		rig_master_grp = cmds.group(empty=True, name=rig_master_grp)
	cmds.parent(ik_grp, fk_grp, rig_master_grp)
	cmds.parent(rig_master_grp, root)

	mc = create_master_control(root, total_root)

	ik_vis_nodes = []
	if ik_handles_grp and cmds.objExists(ik_handles_grp):
		ik_vis_nodes.append(ik_handles_grp) 
	fk_vis_nodes = [offset_grp_fk] 


	_wire_ik_fk_visibility(
		root,
		controls_grp,
		f"{root}_IK_FK_Switch", 
		ik_vis_nodes,
		fk_vis_nodes,
		threshold=0.5
	)

	cmds.select(clear=True)
	
def find_anym_armatures(bones=["Hips", "Hand_L_tip"]):
		all_objects = cmds.ls()
		unique_groups = set()

		for obj in all_objects:
			if cmds.nodeType(obj) == 'transform':
				if (any(cmds.ls(obj + '|' + bone, long=True) for bone in bones)):

					group_name = obj.split('|', 1)[0]

					if len(get_joint_hierarchy(group_name)) == 28 and 'ANYM_output' not in group_name:
						unique_groups.add(group_name)

		return list(unique_groups)

def format_pose(pose_data) -> None:
	header = """HIERARCHY
ROOT Hips
{
	OFFSET 0.000000 0.000000 0.000000
	CHANNELS 6 Xposition Yposition Zposition Zrotation Yrotation Xrotation
	JOINT LeftHip
	{
		OFFSET 0.080781 0.005359 -0.054022
		CHANNELS 3 Zrotation Yrotation Xrotation
		JOINT LeftKnee
		{
			OFFSET 0.000000 -0.010000 -0.417793
			CHANNELS 3 Zrotation Yrotation Xrotation
			JOINT LeftFoot
			{
				OFFSET 0.000000 0.000000 -0.401472
				CHANNELS 3 Zrotation Yrotation Xrotation
				JOINT LeftToe
				{
					OFFSET 0.011334 -0.104165 -0.041164
					CHANNELS 3 Zrotation Yrotation Xrotation
					End Site
					{
						OFFSET 0.000000 -0.150000 0.000000
					}
				}
			}
		}
	}
	JOINT RightHip
	{
		OFFSET -0.080781 0.005359 -0.054025
		CHANNELS 3 Zrotation Yrotation Xrotation
		JOINT RightKnee
		{
			OFFSET 0.000000 -0.010000 -0.417793
			CHANNELS 3 Zrotation Yrotation Xrotation
			JOINT RightFoot
			{
				OFFSET 0.000000 0.000000 -0.401472
				CHANNELS 3 Zrotation Yrotation Xrotation
				JOINT RightToe
				{
					OFFSET  -0.011334 -0.104165 -0.041168
					CHANNELS 3 Zrotation Yrotation Xrotation
					End Site
					{
						OFFSET 0.000000 -0.150000 0.000000
					}
				}
			}
		}
	}
	JOINT Spine
	{
		OFFSET 0.000000 0.011802 0.097172
		CHANNELS 3 Zrotation Yrotation Xrotation
		JOINT Spine1
		{
			OFFSET 0.000000 0.013769 0.113368
			CHANNELS 3 Zrotation Yrotation Xrotation
			JOINT Spine2
			{
				OFFSET 0.000000 0.015737 0.129563
				CHANNELS 3 Zrotation Yrotation Xrotation
				JOINT Neck
				{
					OFFSET 0.000000 0.017704 0.145760
					CHANNELS 3 Zrotation Yrotation Xrotation
					JOINT Head
					{
						OFFSET  0.000000 -0.019722 0.067202
						CHANNELS 3 Zrotation Yrotation Xrotation
						End Site
						{
							OFFSET 0.000000 0.000000 0.200000
						}
					}
				}
				JOINT LeftShoulder
				{
					OFFSET 0.061401 0.017995 0.098779
					CHANNELS 3 Zrotation Yrotation Xrotation
					JOINT LeftArm
					{
						OFFSET 0.115589 0.000581 0.000000
						CHANNELS 3 Zrotation Yrotation Xrotation
						JOINT LeftForearm
						{
							OFFSET 0.255608 0.010000 0.000000
							CHANNELS 3 Zrotation Yrotation Xrotation
							JOINT LeftHand
							{
								OFFSET 0.234041 -0.010000 0.00000
								CHANNELS 3 Zrotation Yrotation Xrotation
								End Site
								{
									OFFSET 0.200000 0.000000 0.000000
								}
							}
						}
					}
				}
				JOINT RightShoulder
				{
					OFFSET -0.061401 0.017414 0.098778
					CHANNELS 3 Zrotation Yrotation Xrotation
					JOINT RightArm
					{
						OFFSET -0.115589 -0.000581 0.000000
						CHANNELS 3 Zrotation Yrotation Xrotation
						JOINT RightForearm
						{
							OFFSET -0.255711 0.010000 0.000000
							CHANNELS 3 Zrotation Yrotation Xrotation
							JOINT RightHand
							{
								OFFSET -0.234017 -0.010000 0.000000
								CHANNELS 3 Zrotation Yrotation Xrotation
								End Site
								{
									OFFSET -0.200000 0.000000 0.000000
								}
							}
						}
					}
				}
			}
		}
	}
}
MOTION
"""
	n_lines = len(pose_data.split('\n')) + 1
	data = (
		header +
		f"Frames: {n_lines}" +
		"\nFrame Time: 0.050000 \n" +
		pose_data
	)

	return data

def import_fbx(namespace):
	if not cmds.pluginInfo("fbxmaya", q=True, loaded=True):
		cmds.loadPlugin("fbxmaya")

	if not cmds.namespace(exists=namespace):
		cmds.namespace(add=namespace)

	kwargs = dict(
		i=True,
		type="FBX",
		ignoreVersion=True,
		rnn=True,            
		options="fbx",
		pr=True,
		ns=namespace,
		mergeNamespacesOnClash=False, 
	)

	new_nodes = cmds.file(MODEL_PATH, **kwargs) 
	ch36_list = cmds.ls(f"{namespace}:Ch36", l=True, type="transform") or []
	arm_list  = cmds.ls(f"{namespace}:Armature", l=True, type="transform") or []

	if not ch36_list or not arm_list:
		new_nodes_long = cmds.ls(new_nodes, l=True) or []
		for n in new_nodes_long:
			short = n.split("|")[-1]
			short_no_ns = short.split(":")[-1]
			if short_no_ns == "Ch36" and not ch36_list:
				ch36_list = [n]
			elif short_no_ns == "Armature" and not arm_list:
				arm_list = [n]

	ch36 = ch36_list[0]
	armature = arm_list[0]

	for axis in ("x","y","z"):
		cmds.setAttr(f"{armature}.s{axis}", 0.0095)
	cmds.setAttr(f"{armature}.ry", -90.0)

	hips = find_in_group(armature, "mixamorig1:Hips")
	if hips:
		cmds.setAttr(f"{hips}.tx", 0.0)
		cmds.setAttr(f"{hips}.ty", 0.0)
		cmds.setAttr(f"{hips}.tz", 0.0)

	ch36 = cmds.rename(ch36, f'{namespace}Mesh')
	armature = cmds.rename(armature, f'{namespace}Arm')

	children = cmds.listRelatives(armature, ad=True, type='transform', f=True) or []
	children.sort()
	for child in children:
		cmds.rename(child.split('|')[-1], namespace + '_' + child.split(':')[-1])

	return ch36, armature

def find_in_group(root, name):
	root_paths = cmds.ls(root, l=True) or []
	if not root_paths:
		return None
	root_path = root_paths[0]

	candidates = set()
	for q in (name, "*:"+name):
		hits = cmds.ls(q, l=True) or []
		for h in hits:
			candidates.add(h)

	def under_root(p):
		return p == root_path or p.startswith(root_path + "|")

	matches = [p for p in candidates if under_root(p)]

	if not matches:
		desc = cmds.listRelatives(root_path, ad=True, pa=True) or []
		pool = [root_path] + desc
		matches = [p for p in pool if p.split("|")[-1].split(":")[-1] == name]

	if not matches:
		return None

	matches.sort(key=lambda p: p.count("|"))
	return matches[0]

def constrain_model(source_root, target_armature, maintain_offset=True):
	constraints = []
	bone_mapping = {
		"Hips": f"{source_root[:-5]}_Hips",
		"Spine": f"{source_root[:-5]}_Spine",
		"Spine1": f"{source_root[:-5]}_Spine1",
		"Spine2": f"{source_root[:-5]}_Spine2",
		"Neck": f"{source_root[:-5]}_Neck",
		"Head": f"{source_root[:-5]}_Head",
		"LeftShoulder": f"{source_root[:-5]}_LeftShoulder",
		"LeftArm": f"{source_root[:-5]}_LeftArm",
		"LeftForearm": f"{source_root[:-5]}_LeftForeArm",
		"LeftHand": f"{source_root[:-5]}_LeftHand",
		"RightShoulder": f"{source_root[:-5]}_RightShoulder",
		"RightArm": f"{source_root[:-5]}_RightArm",
		"RightForearm": f"{source_root[:-5]}_RightForeArm",
		"RightHand": f"{source_root[:-5]}_RightHand",
		"LeftHip": f"{source_root[:-5]}_LeftUpLeg",
		"LeftKnee": f"{source_root[:-5]}_LeftLeg",
		"LeftFoot": f"{source_root[:-5]}_LeftFoot",
		"LeftToe": f"{source_root[:-5]}_LeftToeBase",
		"RightHip": f"{source_root[:-5]}_RightUpLeg",
		"RightKnee": f"{source_root[:-5]}_RightLeg",
		"RightFoot": f"{source_root[:-5]}_RightFoot",
		"RightToe": f"{source_root[:-5]}_RightToeBase",
	}

	target_root = target_armature

	for source_bone_name, target_bone_name in bone_mapping.items():
		try:
			source_jnt = find_in_group(source_root, source_bone_name)
			target_jnt = find_in_group(target_root, target_bone_name)
			oc = cmds.orientConstraint(source_jnt, target_jnt, mo=maintain_offset)[0]
		except:
			import pdb; pdb.set_trace()
		constraints.append(oc)

		if source_bone_name == "Hips":
			pc = cmds.pointConstraint(source_jnt, target_jnt, mo=maintain_offset)[0]
			constraints.append(pc)

def lock_trs_on_children(root):
	ik_joints = [
		'LeftShoulder', 'LeftArm', 'LeftForearm',
		'RightShoulder', 'RightArm', 'RightForearm',
		'LeftHip', 'LeftKnee', 'LeftFoot', 
		'RightHip', 'RightKnee', 'RightFoot', 
	]
	descendants = cmds.listRelatives(root, ad=True, type='transform', f=True) or []

	for node in descendants:
		if '_IK' in node:
			name = (node.split('|')[-1]).split('_')[0]
			if name in ik_joints:
				continue

		for prefix in ('t', 'r', 's'):  
			for axis in ('x', 'y', 'z'):
				attr = f"{node}.{prefix}{axis}"
				try:
					cmds.setAttr(attr, lock=True, keyable=False) 
					cmds.setAttr(attr, channelBox=False)
				except Exception:
					pass

def import_animation(data, name, scale=.01, set_ik=False, is_pose=False, import_model=False, keyframe_indices=None) -> None:		

	class ArmatureBone:
		def __init__(self, name, parent=None):
			self.name = name
			self.parent = parent

		@property
		def full_path(self):
			if self.parent:
				return f"{self.parent.full_path}|{self.name}"
			return self.name

	def create_unique_group_name(base_name):
		group_name = base_name
		i = 1
		while cmds.objExists(group_name):
			group_name = f"{base_name}{i:03d}"
			i += 1
		return group_name

	channel_mapping = {
		'Xposition': 'translateX',
		'Yposition': 'translateY',
		'Zposition': 'translateZ',
		'Xrotation': 'rotateX',
		'Yrotation': 'rotateY',
		'Zrotation': 'rotateZ'
	}
	fps_v = {
		'game': 15.0,
		'film': 24.0,
		'pal': 25.0,
		'ntsc': 30.0,
		'show': 48.0,
		'palf': 50.0,
		'ntscf': 60.0
	}
	current_time_unit = cmds.currentUnit(query=True, time=True)
	scene_fps = fps_v.get(current_time_unit, 24.0)

	space_re = re.compile(r'\s+')
	channels = []
	frame = 1
	rot_order = 0 # XYZ
	pose_data = []

	lines = data.splitlines()
	group_name = create_unique_group_name(name)
	if not "ANYM_output" in name:
		group_name += "_Main"

	group = cmds.group(em=True, name=group_name)
	cmds.setAttr(f"{group}.scale", scale, scale, scale)

	current_bone = ArmatureBone(group)
	in_motion_section = False
	expecting_end_site_close = False

	for line in lines:
		line = line.strip().replace("\t", " ")

		if not in_motion_section:

			if line.startswith("ROOT"):
				current_bone = ArmatureBone(line[5:].strip(), current_bone)

			elif "JOINT" in line:
				joint_name = space_re.split(line)[1]
				current_bone = ArmatureBone(joint_name, current_bone)

			elif "End Site" in line:
				expecting_end_site_close = True

			elif "}" in line:
				if expecting_end_site_close:
					expecting_end_site_close = False
				else:
					current_bone = current_bone.parent
					if current_bone:
						cmds.select(current_bone.full_path)

			elif "CHANNELS" in line:
				chan = space_re.split(line)
				for i in range(int(chan[1])):
					channels.append(f"{current_bone.full_path}.{channel_mapping[chan[2 + i]]}")

			elif "OFFSET" in line:
				offset_values = [val * 100 for val in list(map(float, space_re.split(line)[1:4]))]

				joint_name = f"{current_bone.name}_tip" if expecting_end_site_close else current_bone.name

				if current_bone.parent:
					parent_path = current_bone.parent.full_path
					if "_tip" in joint_name:
						parent_path += f"|{current_bone.name}"
					joint = cmds.joint(parent_path, name=joint_name, p=(0, 0, 0))
				else:
					joint = cmds.joint(name=joint_name, p=(0, 0, 0))

				cmds.setAttr(f"{joint}.rotateOrder", rot_order)
				cmds.setAttr(f"{joint}.translate", *offset_values)

				cmds.select(joint)

			elif 'MOTION' in line:
				in_motion_section = True

		else:
			if line.startswith("Frames:"):
				continue
			elif line.startswith("Frame Time:"):
				parts = space_re.split(line)
				if len(parts) >= 3:
					outp_fps = 1 / float(parts[2])
					fps_r = outp_fps / scene_fps
				continue
			else:
				if frame != 0 and (not keyframe_indices or frame in keyframe_indices):
					data = list(map(float, space_re.split(line)))
					data[:3] = [x * 100 for x in data[:3]]
					time_v = int((frame - 1) * fps_r)
					for index, value in enumerate(data):
						if is_pose:
							if import_model:
								pose_data.append((channels, index, value))
							else:
								cmds.setAttr(channels[index], value)
						else:
							cmds.setKeyframe(channels[index], time=time_v, value=value)
				frame += 1
	
	cmds.setAttr(f"{group}.rotateX", -90)
	if is_pose:
		total_group = cmds.group(em=True, name=group_name[:-5])
		cmds.parent(group, total_group)

	if import_model:
		ns = group_name.replace("|", "_").replace("-", "_")
		if ns.endswith("_Main"):
			ns = ns[:-5] 

		ch36, armature = import_fbx(namespace=ns)
		constrain_model(group, armature) 

		cmds.parent(ch36, total_group)
		cmds.parent(armature, total_group)
		cmds.setAttr(f"{armature}.visibility", False, lock=True)
		cmds.setAttr(f"{ch36}.inheritsTransform", False)

		for attr in ['sx','sy','sz','rx','ry','rz','tx','ty','tz']:
			cmds.setAttr(f"{armature}.{attr}", lock=True, keyable=False)
			cmds.setAttr(f"{ch36}.{attr}", lock=True, keyable=False)

		for channels, index, value in pose_data:
			cmds.setAttr(total_group + '|' + channels[index], value)

	if set_ik:
		cmds.refresh(force=True)
		setup_full_body_ik_fk(group, total_group, model=import_model)
		hips_main = find_in_group(find_in_group(total_group, group), 'Hips')
		hips_ik   = find_in_group(total_group, f'{group}_IK')
		hips_fk   = find_in_group(total_group, f'{group}_FK')
		if import_model and hips_main:
			cmds.setAttr(hips_main + '.visibility', False, lock=True)
		if hips_ik:
			cmds.setAttr(hips_ik + '.visibility', False, lock=True)
		if hips_fk:
			cmds.setAttr(hips_fk + '.visibility', False, lock=True)

		lock_trs_on_children(hips_main)
		lock_trs_on_children(hips_ik)
		lock_trs_on_children(hips_fk)

def get_joint_hierarchy(joint):
		children = cmds.listRelatives(joint, type="joint", children=True, fullPath=True) or []
		hierarchy = [joint]
		for child in children:
			hierarchy.extend(get_joint_hierarchy(child))
		return hierarchy

def get_keyframe_indices(armature_name):
	all_keyframes = []
	
	rig_master_grp = f"{armature_name}_FullBodyRig_Grp"
	ik_grp = f"{armature_name}_IK_Skel_Grp"
	fk_grp = f"{armature_name}_FK_Skel_Grp"
	
	all_rig_nodes = []
	all_rig_nodes.extend(get_all_joints(armature_name))
	
	fk_ctrls = cmds.ls(f"{armature_name}*_FKCtrl", type="transform")
	all_rig_nodes.extend(fk_ctrls)
	ik_ctrls = cmds.ls(f"{armature_name}*_IKCtrl", type="transform")
	all_rig_nodes.extend(ik_ctrls)
	ik_handles = cmds.ls(f"{armature_name}*_IKHandle", type="ikHandle")
	all_rig_nodes.extend(ik_handles)
	pv_ctrls = cmds.ls(f"{armature_name}*_PV", type="transform")
	all_rig_nodes.extend(pv_ctrls)
	switch_ctrl = cmds.ls(f"{armature_name}_IKFK_Switch_Ctrl", type="transform")
	all_rig_nodes.extend(switch_ctrl)
	master_ctrl = cmds.ls(f"{armature_name}_Master_Ctrl", type="transform")
	all_rig_nodes.extend(master_ctrl)
	
	for node in all_rig_nodes:
		attrs = cmds.listAttr(node, keyable=True) or []
		
		for attr in attrs:
			connections = cmds.listConnections(f"{node}.{attr}", source=True, destination=False, type="animCurve")
			if connections:
				for connection in connections:
					times = cmds.keyframe(connection, query=True, timeChange=True)
					if times:
						all_keyframes.extend(times)
	
	unique_keyframes = [int(idx) for idx in sorted(list(set(all_keyframes)))]
	
	return unique_keyframes

def get_bone_rotations(armature_name, frame=1):
	joint_hierarchy = get_joint_hierarchy(armature_name)

	rotations = list()

	cmds.currentTime(frame, edit=True)

	for joint in joint_hierarchy:
		joint_name = cmds.ls(joint, shortNames=True)[0]

		if "_tip" not in joint_name and joint_name != armature_name:

			rotation_orig = list(cmds.getAttr(f"{joint}.rotate")[0])
			
			if joint_name.endswith("Hips"):
				
				rotation_main = cmds.getAttr(f"{armature_name[:-5]}.rotate")[0]
				rotation_mc = cmds.getAttr(f"{armature_name}_Master_Ctrl.rotate")[0]
				rotation_orig[2] += rotation_mc[1] + rotation_main[1]
			
			rotation = [rotation_orig[2], rotation_orig[1], rotation_orig[0]]
			rotations.append(rotation)

	return rotations

def get_root_position(armature_name, frame=1):
	cmds.currentTime(frame, edit=True)

	root_joint = armature_name + "|Hips"
	lh_joint = root_joint + "|LeftHip"

	try:
		r_position = list(cmds.xform(root_joint, query=True, worldSpace=True, translation=True))
		lh_position = list(cmds.xform(lh_joint, query=True, worldSpace=True, translation=True))
		diff = [(r_position[i] - lh_position[i])**2 for i in range(3)]
		scale = math.sqrt(sum(diff)) / .09732761852
		rescaled_position = [coor * scale for coor in r_position]
		return rescaled_position
	except:
		raise ValueError(f"Armature '{armature_name}' is not compatible with Anym.")

def format_request(poses, is_looping, solve_ik, n_frames, fps):

	indices = list()
	target_rot = list()
	target_root_pos = list()

	for target in poses:
		pose_name = target.pose_name
		if target.is_static:
			rot = get_bone_rotations(pose_name)
			root_pos = get_root_position(pose_name)
			indices.append(target.frame_idx)
			target_rot.append(rot)
			target_root_pos.append(root_pos)

		else:
			pose_indices = get_keyframe_indices(pose_name)
			for idx in pose_indices:
				rot = get_bone_rotations(pose_name, idx)
				root_pos = get_root_position(pose_name, idx)
				indices.append(1) if idx == 0 else indices.append(idx)
					
				target_rot.append(rot)
				target_root_pos.append(root_pos)

	pose_data = zip(indices, target_rot, target_root_pos)
	pose_data = sorted(pose_data)
	indices, target_rot, target_root_pos = zip(*pose_data)
			
	data = {
		"is_looping": is_looping,
		"solve_ik": solve_ik,
		"n_frames": n_frames,
		"fps": fps,
		"indices": indices,
		"target_rot": target_rot,
		"target_root_pos": target_root_pos,
	}

	return data

def api_request(data, api_key, url):
		
	url = f'{url}/predict/'

	headers = {
		'X-API-KEY': f'{api_key}',
		'X-Plugin-Token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwbHVnaW5fdmVyc2lvbl9pZCI6IjIzNDAxODcyLTE5NWEtNDgxNC05MGI4LTViN2M3ZWYwMjgyMCJ9.ZcE_uIi9S6gXyqaaHXhYmftbDqEEC0soyHMqWDEgVak',
		'Content-Type': 'application/json'
	}

	response = requests.post(url, headers=headers, json=data)

	return response.status_code, response.json()

class AnymTool:
	def __init__(self):
		self.icon_path = ICONS_DIR
		self.url = 'https://app.anym.tech/'
		self.tot_frames = 40
		self.window_name = "AnymToolWindow"
		self.poses = []
		self.create_ui()
		self.create_script_job()

	def create_ui(self):

		if cmds.window(self.window_name, exists=True):
			cmds.deleteUI(self.window_name)

		cmds.window(self.window_name, title="ANYM v1.0", width=340, height=1000)

		main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5, columnAttach=('both', 5))

		cmds.columnLayout(adjustableColumn=True, columnAlign="center")
		form = cmds.formLayout(width=340, height=100)
		if os.path.exists(os.path.join(self.icon_path, 'ANYM.png')):
			logo = cmds.image(image=os.path.join(self.icon_path, 'ANYM.png'), width=180, height=50)
			cmds.formLayout(form, edit=True,
							attachPosition=[(logo, 'left', 0, 28), (logo, 'top', 0, 30)])
		else:
			text_label = cmds.text(label="ANYM v1.0", font="boldLabelFont", height=40, backgroundColor=[0.2, 0.2, 0.2])
			cmds.formLayout(form, edit=True,
							attachForm=[(text_label, 'top', 40), (text_label, 'left', 120)])
		cmds.setParent('..')

		cmds.separator(height=10, style='none')

		cmds.frameLayout(label="Poses", collapsable=False, marginHeight=5, marginWidth=5,
						 backgroundColor=[0.2, 0.2, 0.2])
		cmds.columnLayout(adjustableColumn=True, rowSpacing=5)

		cmds.rowLayout(numberOfColumns=2, columnWidth2=[10, 50], adjustableColumn=1)
		self.selected_pose = cmds.optionMenuGrp(label="Available Pose", columnWidth=[(1, 75), (2, 220)])
		cmds.setParent('..')

		cmds.rowLayout(numberOfColumns=4, adjustableColumn=4, columnWidth4=(100, 50, 100, 50), columnAlign4=('left', 'left', 'right', 'left'))
		cmds.text(label="Create FK/IK   ", align='left')
		self.fkik_checkbox = cmds.checkBox(label="", value=True)

		cmds.text(label="Import Model   ", align='left')
		self.import_model_checkbox = cmds.checkBox(label="", value=True)
		cmds.setParent('..') 

		poses = start_poses.keys()
		for pose in poses:
			cmds.menuItem(label=pose)

		cmds.iconTextButton(
			style='iconAndTextHorizontal',
			image1= os.path.join(self.icon_path, 'file.svg'),
			label='Import Armature',
			command=self.import_armature,
			height=30,
			backgroundColor=[0.3, 0.3, 0.3]
		)
		cmds.iconTextButton(
			style='iconAndTextHorizontal',
			image1=os.path.join(self.icon_path, 'running.svg'),
			label="Add Pose",
			command=self.add_pose,
			height=30,
			backgroundColor=[0.3, 0.3, 0.3]
		)

		self.poses_layout = cmds.scrollLayout(height=130, backgroundColor=[0.25, 0.25, 0.25])
		cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
		cmds.setParent('..') 
		cmds.setParent('..') 

		cmds.separator(height=10, style='none')

		cmds.frameLayout(label="Context", collapsable=False, marginHeight=5, marginWidth=5,
						 backgroundColor=[0.2, 0.2, 0.2])
		cmds.columnLayout(adjustableColumn=True, rowSpacing=5)

		cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(100, 50), columnAlign2=('left', 'left'))
		cmds.text(label="Total Frames", align='left')
		self.tot_frames_inp = cmds.intField(value=self.tot_frames, minValue=1, maxValue=9999, width=20)
		cmds.setParent('..') 

		cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(100, 50), columnAlign2=('left', 'left'))
		cmds.text(label="FPS", align='left')
		self.fps = cmds.intField(value=30, minValue=20, maxValue=240, width=20)
		cmds.setParent('..')

		cmds.rowLayout(numberOfColumns=4, adjustableColumn=4, columnWidth4=(100, 50, 100, 50), columnAlign4=('left', 'left', 'right', 'left'))
		cmds.text(label="Is Looping   ", align='left')
		self.is_looping = cmds.checkBox(label="", value=False)

		cmds.text(label="Apply IK Solver   ", align='left')
		self.solve_ik = cmds.checkBox(label="", value=True)
		cmds.setParent('..') 

		cmds.separator(height=10, style='none')

		button_layout = cmds.rowLayout(numberOfColumns=2, columnWidth2=(40, 290), adjustableColumn=2)

		if os.path.exists(os.path.join(self.icon_path, 'ANYM_logo.png')):
			cmds.image(image=os.path.join(self.icon_path, 'ANYM_logo.png'), width=30, height=30)

		else:
			cmds.text(label="ANYM", font="smallBoldLabelFont", width=30)
		cmds.button(label="Generate Animation", command=self.generate_animation, height=40,
					backgroundColor=[.96, .64, .32])
		
		cmds.setParent('..')

		cmds.separator(height=10, style='none')

		cmds.iconTextButton(
			style='iconAndTextHorizontal',
			image1= os.path.join(self.icon_path, 'fetch.svg'),
			label='Fetch Exported Animation',
			command=self.exported_anim_listener,
			height=30,
			backgroundColor=[0.3, 0.3, 0.3]
		)

		cmds.separator(height=5, style='none')

		stored_api_key = get_api_key()
		self.api_key_field = cmds.textFieldGrp(
			label="API Key",
			tx=stored_api_key,
			columnWidth=[(1, 60), (2, 240)],
			changeCommand=self.on_api_key_change
		)

		cmds.showWindow(self.window_name)
		cmds.window(self.window_name, edit=True, widthHeight=(340, 680))

	def create_script_job(self):
		if hasattr(self, 'create_job'):
			cmds.scriptJob(kill=self.create_job, force=True)
		if hasattr(self, 'delete_job'):
			cmds.scriptJob(kill=self.delete_job, force=True)

		self.create_job = cmds.scriptJob(event=["DagObjectCreated", self.on_object_change])
		self.delete_job = cmds.scriptJob(event=["SelectionChanged", self.on_object_change])

	def on_object_change(self):
		self.populate_pose_menu()

	def on_api_key_change(self, *kwargs):
		api_key = cmds.textFieldGrp(self.api_key_field, query=True, text=True).strip()
		store_api_key(api_key)

	def import_armature(self, *kwargs):
		pose_name = cmds.optionMenuGrp(self.selected_pose, query=True, value=True)
		create_fkik = cmds.checkBox(self.fkik_checkbox, query=True, value=True)
		import_model = cmds.checkBox(self.import_model_checkbox, query=True, value=True)
		pose_data = start_poses[pose_name]
		if pose_name != "--select armature--":
			import_animation(format_pose(pose_data), pose_name, set_ik=create_fkik, is_pose=True, import_model=import_model)

	def set_max_frames(self, *kwargs):
		all_indices = []
		for pose in self.poses:
			if pose.is_static:
				all_indices.append(pose.frame_idx)
			else:
				indices = get_keyframe_indices(pose.pose_name)
				all_indices.extend(indices)

		if len(all_indices) > 0:
			max_frame = max(all_indices)

			if max_frame > cmds.intField(self.tot_frames_inp, query=True, value=True):
				cmds.intField(self.tot_frames_inp, edit=True, value=max_frame)

	def populate_pose_menu(self):
		groups = find_anym_armatures()
		poses_copy = self.poses.copy()

		for pose_setting in poses_copy:
			menu = pose_setting.pose

			if cmds.optionMenu(menu, exists=True):
				if cmds.optionMenu(menu, query=True, numberOfItems=True) > 0:
					current_selection = cmds.optionMenu(menu, query=True, value=True)
				else:
					current_selection = None

				cmds.optionMenu(menu, edit=True, deleteAllItems=True)
				cmds.menuItem(parent=menu, label="--select pose--")

				for group in groups:
					cmds.menuItem(parent=menu, label=group[:-5])

				if current_selection != "--select pose--" and current_selection:
					if current_selection + "_Main" in groups:
						cmds.optionMenu(menu, edit=True, value=current_selection)
				else:
					cmds.optionMenu(menu, edit=True, value="--select pose--")
			else:
				self.poses.remove(pose_setting)

	def add_pose(self, *args):
		pose_setting = PoseSettings()
		self.poses.append(pose_setting)
		pose_layout = cmds.rowLayout(numberOfColumns=6, columnWidth6=(30, 120, 40, 20, 40, 40),
									columnAlign5=('left', 'left', 'center', 'right', 'left'),
									adjustableColumn=6, parent=self.poses_layout)

		cmds.iconTextButton(
			label="",
			command=lambda *args: self.remove_pose(pose_layout, pose_setting),
			width=25,
			height=25,
			image1=os.path.join(self.icon_path, 'remove.svg'),
			style='iconAndTextHorizontal'
		)

		pose_setting.pose = cmds.optionMenu()

		pose_setting.is_static_label = cmds.text(label="Static:", align='right')
		pose_setting.is_static_cb = cmds.checkBox(label="", value=False, 
											changeCommand=lambda *args: self.update_pose_mode(pose_setting))
		
		pose_setting.frame_label = cmds.text(label="Frame:", visible=False)
		pose_setting.n_frames = cmds.intField(value=1, minValue=1, maxValue=9999, width=45, 
												changeCommand=self.set_max_frames, visible=False)

		self.populate_pose_menu()
	
	def update_pose_mode(self, pose_setting):
		is_static = pose_setting.is_static
		
		if is_static:
			cmds.text(pose_setting.frame_label, edit=True, visible=True, label="Frame:")
			cmds.intField(pose_setting.n_frames, edit=True, visible=True)
		else:
			cmds.text(pose_setting.frame_label, edit=True, visible=True, label=" ")
			cmds.intField(pose_setting.n_frames, edit=True, visible=False)

	def remove_pose(self, pose_layout, pose_setting):
		cmds.deleteUI(pose_layout)
		self.poses.remove(pose_setting)

	def valid_request(self):
		if len(self.poses) < 1:
			self.show_error_window("Warning: At least one pose must be selected.")
			return False

		pose_names = [pose.pose_name for pose in self.poses]
		
		if any(pose_name == '--select armature--' for pose_name in pose_names):
			self.show_error_window("Warning: All poses must have an armature selected.")
			return False
		
		frame_indices = []
		for pose in self.poses:
			if pose.is_static:
				frame_indices.append(pose.frame_idx)
			else:
				indices = get_keyframe_indices(pose.pose_name)
				frame_indices.extend(indices)
		frame_indices.sort()
		
		indices_diff = (
			[frame_indices[i + 1] - frame_indices[i] for i in range(len(frame_indices) - 1)] if len(frame_indices) > 1 else frame_indices
		)
		n_frames = cmds.intField(self.tot_frames_inp, query=True, value=True)
		fps = cmds.intField(self.fps, query=True, value=True)

		if len(frame_indices) == 0:
			self.show_error_window(f"Warning: None of the selected poses have keyframe values. If it is to be treated as static, toggle Static and provide a desired frame index.")
			return False

		if n_frames > (fps * 10):
			self.show_error_window(f"Warning: The total duration cannot exceed 10 seconds, currently {n_frames / fps:.1f}.")
			return False

		if len(frame_indices) != len(set(frame_indices)):
			self.show_error_window("Warning: All keyframes need to be assigned to a unique frame index.")
			return False
		
		if max(frame_indices) > n_frames:
			self.show_error_window("Warning: All keyframes need to fall within total animation duration.")
			return False

		if max(indices_diff) > 5 * fps:
			self.show_error_window(f"Warning: Keyframes can be spaced up to 5 seconds apart, currently spaced {max(indices_diff) / fps:.1f} seconds apart.")
			return False

		return True

	def show_error_window(self, message):
		cmds.confirmDialog(
			title="Invalid ANYM request",
			message=message,
			button=["OK"],
			defaultButton="OK",
			icon="warning"
		)

	def generate_animation(self, *args):
		self.set_max_frames()

		if self.valid_request():

			api_key = cmds.textFieldGrp(self.api_key_field, query=True, text=True).strip()
			n_frames = cmds.intField(self.tot_frames_inp, query=True, value=True) - 1
			fps = cmds.intField(self.fps, query=True, value=True)
			is_looping = cmds.checkBox(self.is_looping, query=True, value=True)
			solve_ik = cmds.checkBox(self.solve_ik, query=True, value=True)
			data = format_request(
				self.poses, 
				is_looping, 
				solve_ik, 
				n_frames, 
				fps
			)

			status_code, output = api_request(data, api_key, f'{self.url}api')

			if status_code == 200:
				anim_id = output['data']['animation_id']

				webbrowser.open(
					f'{self.url}preview/{anim_id}/', new=0
				)

			else:
				self.show_error_window(message=f"Error {status_code}: {output['message']}")

	def exported_anim_listener(self):
		try:
			api_key = cmds.textFieldGrp(self.api_key_field, query=True, text=True).strip()

			headers = {
				'X-API-KEY': f'{api_key}',
				'X-Plugin-Token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwbHVnaW5fdmVyc2lvbl9pZCI6IjIzNDAxODcyLTE5NWEtNDgxNC05MGI4LTViN2M3ZWYwMjgyMCJ9.ZcE_uIi9S6gXyqaaHXhYmftbDqEEC0soyHMqWDEgVak',
				'Content-Type': 'application/json'
			}

			response = requests.get(f'{self.url}api/import-animation/', headers=headers)
			
			if response.status_code == 200:
				import_animation(
					data=response.json()['data']['animation'], 
					name="ANYM_output",
					keyframe_indices=response.json()['data']['keyframe_indices']
				)
			elif response.status_code == 404:
				self.show_error_window(message=f"Error {response.status_code}: No fetchable animation found. First click 'Generate Animation', then unlock it in the Anym previewer.")
			else:
				self.show_error_window(message=f"Error {response.status_code}: {response.json()['message']}")
		except:
			self.show_error_window(message=f"Error importing ANYM animation.")

	def __del__(self):
		if hasattr(self, 'create_job'):
			cmds.scriptJob(kill=self.create_job, force=True)
		if hasattr(self, 'delete_job'):
			cmds.scriptJob(kill=self.delete_job, force=True)
		self.timer.stop()
		self.timer = None

class PoseSettings:
	def __init__(self):
		self.pose = None
		self.n_frames = None
		self.is_static_cb = None

	@property
	def pose_name(self):
		return cmds.optionMenu(self.pose, query=True, value=True) + '_Main'

	@property
	def frame_idx(self):
		return cmds.intField(self.n_frames, query=True, value=True)
	
	@property
	def is_static(self):
		return cmds.checkBox(self.is_static_cb, query=True, value=True)

def initializePlugin(mobject):
	global anym_tool_instance
	anym_tool_instance = AnymTool()

	if not cmds.menu('AnymMenu', exists=True):
		cmds.menu('AnymMenu', label='Anym', parent='MayaWindow')
		cmds.menuItem(label='Open Anym Tool', parent='AnymMenu', command=lambda *args: show_anym_tool())

def uninitializePlugin(mobject):
	global anym_tool_instance
	if anym_tool_instance:
		del anym_tool_instance
		anym_tool_instance = None

	if cmds.menu('AnymMenu', exists=True):
		cmds.deleteUI('AnymMenu')

def show_anym_tool(*args):
	global anym_tool_instance
	if not anym_tool_instance or not cmds.window(anym_tool_instance.window_name, exists=True):
		anym_tool_instance = AnymTool()
	else:
		cmds.showWindow(anym_tool_instance.window_name)
