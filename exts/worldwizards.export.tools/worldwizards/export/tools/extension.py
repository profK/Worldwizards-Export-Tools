from asyncio import Future, Task
import carb
import omni.ext
import omni.ui as ui
from .ww_omniverse_utils import *
import os
import shutil
from pxr import Usd,UsdShade



# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[worldwizards.export.tools] some_public_function was called with x: ", x)
    return x ** x

def recurse_list_components(prim:Usd.Prim, components:list):
    if (prim.GetTypeName()=="Component"):
        components.append(prim.GetPath())
    else:
        for child in prim.GetChildren():
            recurse_list_components(child,components)

def recurse_list_material_paths(prim:Usd.Prim, materials:list):
   if (prim.GetTypeName()=="Mesh"):
            material:UsdShade.MaterialBindingAPI = \
                UsdShade.MaterialBindingAPI(prim)
            if material.HasMaterialPath():
                materials.append(material.GetMaterialPath())             

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
     
    def _export_components(self, event, *args):
        print("INFO:Export components called")
        task:Task = \
            asyncio.create_task(self._export_components_async(event, *args))

  
    async def _export_components_async(self, event, *args):
        filepath:str = get_current_stage().GetRootLayer().realPath
        if filepath is None:
            print("Could not find root layer path "+filepath)
            return;
        materials_path:str = os.path.join(os.path.dirname(filepath),"Materials")
        if not os.path.exists(materials_path):
            print("Could not find materials file "+materials_path)
            return; 
        #copy materials to output root
        new_root = await get_directory_async("/")
        if new_root is None:
            print("User canceled output ")
            return;
        shutil.copytree(materials_path,os.path.join(new_root,"Materials"))
        root:Usd.Prim = get_current_stage().GetPseudoRoot()
        components:list = []
        recurse_list_components(root,components) 
        for component in components:
            self.export_component(component,new_root)
        print("Exported "+str(len(components))+" components to "+new_root)
    
    def export_component(self,prim:Usd.Prim, outDir:str):
        if (prim.GetTypeName()!="Component"):
            print("Not a component "+prim.GetPath())
            return
        #localize materials
        materail_paths_list = []
        recurse_list_material_paths(prim,materail_paths_list)
        for material_path in materail_paths_list:
            self._localize_material(prim,material_path)
        #create directory
        componentPath:str = prim.GetPath()
        componentDir:str = os.path.join(outDir,componentPath)
        os.makedirs(componentDir)
        '''#export prim
        self.export_prim(componentPath)
        #export materials
        self.export_materials(componentPath,componentDir)
        #export textures
        self.export_textures(componentPath,componentDir)
        #export meshes
        self.export_meshes(componentPath,componentDir)
        '''

    def _localize_material(self,prim:Usd.Prim, material_path:str):
        material:UsdShade.Material = UsdShade.Material(prim.GetStage().GetPrimAtPath(material_path))
        material_name:str = material.GetName()
        prim_path:str = prim.GetPath()
        new_material_path: str = prim_path +"/"+material_name
        if not material_path == new_material_path:
            Usd.Prim.duplicate(material_path,new_material_path)
            materialApi:UsdShade.MaterialBindingAPI = \
                    UsdShade.MaterialBindingAPI(prim)
            materialApi.Bind(new_material_path)

    def export_prim(self, path):
        prim:Usd.Prim = get_current_stage().GetPrimAtPath(path)
        
        
