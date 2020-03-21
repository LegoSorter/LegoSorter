# LegoSorter

## How to run

```
export LEGO_HOME=<set your lego home directory>
bash start.sh

// example of generating images
blender --background --addons importldraw --python render.py -- --width 200 --height 200 --output_dir "$LEGO_HOME/output" --part "$LEGO_HOME/dataset/ldraw/parts/1.dat" --ldraw "$LEGO_HOME/dataset/ldraw" --samples 10 --delta_z 33.0
```
