[[ -z "$LEGO_HOME" ]] && { echo "LEGO_HOME is empty" ; exit 1; }

WORKING_DIRECTORY="$LEGO_HOME/dataset"

cd "$WORKING_DIRECTORY" || exit

## install blender
yes | sudo apt-get install snapd xdg-open-snapd
yes | sudo snap install blender --classic

## clone ldraw importer add-on
git clone -b master --single-branch https://github.com/TobyLobster/ImportLDraw.git

## create path to add-on
ADDON_PATH="$WORKING_DIRECTORY/ImportLDraw"

## install add-on
blender --background --python install_addon.py -- "$ADDON_PATH" "importldraw"

## download ldraw parts
wget -nc http://www.ldraw.org/library/updates/complete.zip
unzip complete.zip

## run blender
blender --background --addons importldraw --python test_render.py -- "$WORKING_DIRECTORY/ldraw/parts/1.dat" "$WORKING_DIRECTORY/test_render/1.png" "$WORKING_DIRECTORY/ldraw"
