import carb
import omni.ext
import omni.ui as ui
from .ww_omniverse_utils import *
import os
import shutil



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
        self._menu_path = f"Tileset/Export All Components"
        self._window = None
        self._menu = omni.kit.ui.get_editor_menu().add_item(self._menu_path, self._export_components, True)
        return super().on_startup(ext_id) 

    def on_stage_opened(self, event: carb.events.IEvent):
       
    
        return super().on_stage_opened(event)  
    
    def _export_components(self):
        filepath:str = self._stage.GetRootLayer().realPath
        if filepath is None:
            print("Could not find root layer path "+filepath)
            return;
        materialsPath:str = os.path.join(os.path.dirname(filepath),".materials")
        if not os.path.exists(materialsPath):
            print("Could not find materials file "+materialsPath)
            return;
        get_directory("/",lambda path: self._export_components_callback(
                                        path,materialsPath))

    def _export_components_callback(self,outRoot:str, materialsPath:str): 
        #copy materials to output root
        shutil.copytree(materialsPath,os.path.join(outRoot,".materials"))
        root:Usd.Prim = self._stage.GetPseudoRoot()
        self._recurse_export_components(root,outRoot)    

    def _recurse_export_components(self,prim:Usd.Prim, outRoot:str):
            if (prim.GetTypeName()=="Component"):
                self._export_component(prim,outRoot)
            else: #maake a directory
                dirname:str = os.path.join(outRoot,prim.GetName())
                shutil.mkdir(dirname)
                for child in prim.GetChildren():
                    self._recurse_export_components(child,dirname)

    def _export_component(self,prim:Usd.Prim, outDir:str):
           
    def export_prim(self, path):
        prim:Usd.Prim = self._stage.GetPrimAtPath(path)
        
        
