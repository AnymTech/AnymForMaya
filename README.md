# Anym for Maya

This repo contains a Maya plugin for using the Anym engine.

## Getting Started

### API Key

To use this plugin, you'll need an Anym API key. To get one;
- Make an account on [app.anym.tech/signup](https://app.anym.tech/signup/) and verify your e-mail address
- In the dashboard, click on **Create Company**, fill in a name and click the Confirm button
- Scroll to the bottom of the page and click **Create new API Key**
- Next to the new key, click **Copy Key** to copy your key to your clipboard

### Installation

1. **Download** this repository and unzip it to your desired location
2. **Open Maya**
3. Navigate to **Windows → Settings/Preferences → Plug-in Manager**
4. Click **Browse** and select **`AnymForMaya.py`** from the unzipped folder

The plugin will now open, and be available in the top bar of your Maya interface under the **Anym** tab.

## Usage

### Video Tutorial

For a visual guide on using the plugin, check out our [Maya plugin tutorial](https://www.youtube.com/watch?v=CJgg9eiLYN4) which demonstrates the total workflow for obtaining a first animation.

### Step-by-Step Workflow

#### 1. Setup
- **Enter your API key** in the designated field within the plugin interface

#### 2. Import Character
- Select a pose from the **"Available Pose:"** dropdown menu
- Click **"Import Armature"** to bring the character into your scene
- All imported armatures include IK/FK switch setups by default

#### 3. Create Key Poses
- **Pose your character** using the provided IK and FK handles along with the master control
- **Set keyframes** as you normally would in Maya (**S** hotkey)
  - Use the red triangle next to attributes in the coordinate tab to create keyframes
- Create as many key poses as needed for your animation

#### 4. Generate Animation
- Once your key poses are set, click **"Generate Animation"**
- The **browser-based previewer** will open automatically
- On first use, you'll be prompted to enter login credentials

#### 5. Preview and Iterate
- Review the generated animation in the browser previewer
- If not satisfied, return to Maya and:
  - Adjust your poses
  - Add or modify keyframes
  - Click "Generate Animation" again
- **Repeat this process** until you're happy with the motion

#### 6. Export Your Animation
- In the browser previewer, click **"Unlock Animation"**
- **Name your animation** if desired
- Navigate to the **"Unlocked Animations"** tab
- Click **"Export Animation"**

#### 7. Import to Maya
- Return to the Maya plugin
- Click **"Fetch Exported Animation"**
- Your generated animation will be imported into your Maya scene
- The animation can now be **retargeted and processed** just like traditional mocap data


## Support

For technical support, API access, or general questions, contact **hello@anym.tech**.

## Requirements

- Maya (compatible versions)
- Active internet connection
- Valid Anym API key
