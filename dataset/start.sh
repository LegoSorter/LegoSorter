[[ -z "$LEGO_HOME" ]] && { echo "LEGO_HOME is empty" ; exit 1; }

# shellcheck disable=SC2164
cd "$LEGO_HOME" 

## install blender
yes | sudo apt-get install snapd xdg-open-snapd
yes | sudo snap install blender --classic

## clone ldraw importer add-on
git clone https://github.com/TobyLobster/ImportLDraw.git

## create path to add-on
ADDON_PATH="$LEGO_HOME/ImportLDraw"

## install add-on
blender --background --python install_addon.py -- "$ADDON_PATH" "importldraw"

## download ldraw parts
wget -nc http://www.ldraw.org/library/updates/complete.zip
unzip complete.zip

## run blender
blender --background --addons importldraw --python render.py -- "$LEGO_HOME/ldraw/parts/1.dat" "$LEGO_HOME/test_render/1.png" "$LEGO_HOME/ldraw"