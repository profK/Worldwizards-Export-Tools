from asyncio import Future, Task
import traceback
import carb
import omni.ext
import omni.ui as ui
from .ww_omniverse_utils import *
import os
import shutil
from omni import usd
from pxr import Usd,UsdShade



# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[worldwizards.export.tools] some_public_function was called with x: ", x)
    return x ** x

def get_kind(prim:Usd.Prim):
    kindAPI = Usd.ModelAPI(prim)
    return kindAPI.GetKind()

def recurse_list_components(prim:Usd.Prim, components:list):

    if (get_kind(prim)=="component"):
        print("Found component "+str(prim.GetPath()))
        components.append(prim.GetPath())
    else:
        for child in prim.GetChildren():
            recurse_list_components(child,components)

def recurse_list_material_paths(prim:Usd.Prim, materials:list):
    print("recurse_list_material_paths "+str(prim.GetPath())+
            " type "+prim.GetTypeName())
    if (prim.GetTypeName()=="Mesh"):
            materialAPI:UsdShade.MaterialBindingAPI = \
                UsdShade.MaterialBindingAPI(prim)
            material: UsdShade.Material = materialAPI.ComputeBoundMaterial()[0]
            if not material is None:
                #print("material "+str(material.GetPath()))
                materials.append(material)
    for child in prim.GetChildren():
        recurse_list_material_paths(child,materials)                       

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
        try:
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
            new_materials_path = os.path.join(new_root,"Materials")
            if os.path.exists(new_materials_path):
                shutil.rmtree(new_materials_path)
            shutil.copytree(materials_path,new_materials_path)
            root:Usd.Prim = get_current_stage().GetPseudoRoot()
            component_paths:list = []
            recurse_list_components(root,component_paths) 
            print("INFO: Components in tree:"+str(component_paths))
            for path in component_paths:
                component:Usd.Prim = get_current_stage().GetPrimAtPath(path)

                self.export_component(component,new_root)
            print("INFO: Exported "+str(len(component_paths))+" components to "+new_root)
        except Exception:
            print(traceback.format_exc())
            return

    def export_component(self,prim:Usd.Prim, outDir:str):
        print("INFO: Exporting component "+str(prim.GetPath()))
        if not (get_kind(prim)=="component"):
            print("Not a component "+str(prim.GetPath()))
            return
        #localize materials
        material_list = []
        recurse_list_material_paths(prim,material_list)
        print(str(prim.GetPath())+" has materials "+str(material_list))
        for material_prim in material_list:
            self._localize_material(prim,material_prim)
        #create directory
        componentPath:str = prim.GetPath()
        componentDir:str = os.path.join(outDir,str(componentPath))
        print("component dir "+componentDir)
        if not os.path.exists(componentDir):
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

    def _localize_material(self,prim:Usd.Prim, material_prim:UsdShade.Material):
        material_path:str = str(material_prim.GetPath())
        prim_path:str = str(prim.GetPath())
        print("copying material from"+prim_path+" to "+material_path)
        material_name:str = material_path.split("/")[-1]
        
        new_material_path: str = prim_path +"/Looks/"+material_name
        if not material_path == new_material_path:
            stage = get_current_stage()
            usd.duplicate_prim(stage,material_path,
                               new_material_path)
            new_material_prim:UsdShade.Material = \
                UsdShade.Material(stage.GetPrimAtPath(new_material_path))
            materialApi:UsdShade.MaterialBindingAPI = \
                    UsdShade.MaterialBindingAPI(prim)
            materialApi.Bind(new_material_prim)

    def export_prim(self, path):
        prim:Usd.Prim = get_current_stage().GetPrimAtPath(path)
        
        
