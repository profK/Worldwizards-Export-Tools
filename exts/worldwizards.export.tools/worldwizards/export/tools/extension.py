import carb
import omni.ext
import omni.ui as ui
from .ww_omniverse_utils import *



# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[worldwizards.export.tools] some_public_function was called with x: ", x)
    return x ** x


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class WorldwizardsExportToolsExtension(ExtensionFramework):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
         # add to menu
        self._menu_path = f"Tileset/Export Selected Tiles"
        self._window = None
        self._menu = omni.kit.ui.get_editor_menu().add_item(self._menu_path, self._group_export, True)
        return super().on_startup(ext_id) 

    def on_stage_opened(self, event: carb.events.IEvent):
       
    
        return super().on_stage_opened(event)  
    
    def _group_export():
        pass
