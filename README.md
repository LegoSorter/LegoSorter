# LegoSorter

## How to run


### LINUX
```
export LEGO_HOME=<set your lego home directory>
bash start.sh

// example of generating images
blender --background --addons importldraw --python render.py -- --width 400 --height 400 --output_dir "$LEGO_HOME/output" --part "$LEGO_HOME/dataset/ldraw/parts/1.dat" --scene "$LEGO_HOME/dataset/scenes/simple.blend" --ldraw "$LEGO_HOME/dataset/ldraw" --samples 6
```

### WINDOWS (PLEASE INSTALL MANUALLY BEFORE)
```
set LEGO_HOME=<set your lego home directory>

// example of generating images
blender --background --addons importldraw --python render.py -- --width 400 --height 400 --output_dir "%LEGO_HOME%/output" --part "%LEGO_HOME%/dataset/ldraw/parts/1.dat" --scene "%LEGO_HOME%/dataset/scenes/simple.blend" --ldraw "%LEGO_HOME%/dataset/ldraw" --samples 6
```