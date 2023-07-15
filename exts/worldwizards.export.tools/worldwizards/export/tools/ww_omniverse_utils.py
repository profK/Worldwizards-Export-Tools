from pxr import Usd, Sdf, UsdGeom, Tf
from omni import usd
import os
import omni
import carb
from omni.kit.window.file_exporter import get_file_exporter


def get_ext_root_path(extname:str):
    #print("Get root of ext "+extname)
    manager = omni.kit.app.get_app().get_extension_manager()
    ext_id = manager.get_extension_id_by_module(extname)
    path = manager.get_extension_path(ext_id)
    #print("path is "+path)
    return path

def get_current_stage() -> Usd.Stage:
    return usd.get_context().get_stage()

def add_layer_reference(ref_path:str, file_path:str, visible:bool = True) -> Usd.PrimAllPrimsPredicate:
    stage:Usd.Stage
    stage = get_current_stage()
    # You can use standard python list.insert to add the subLayer to any position in the list
    refPrim:Usd.Prim = stage.DefinePrim(ref_path)
    references: Usd.References = refPrim.GetReferences()
    references.AddReference(
        assetPath=file_path
    )
    #print("visible= "+str(visible))
    set_prim_visibility(refPrim,visible)
    return refPrim

def set_prim_visibility(prim:Usd.Prim,visible:bool = True):
    imageable = UsdGeom.Imageable(prim)
    #print("Setting visibility of "+prim.GetName()+" to "+str(visible))
    if not visible:
        imageable.MakeInvisible()
    else:
        imageable.MakeVisible()

def get_directory(root:str,callback_fn) -> None  :
    file_exporter = get_file_exporter()
    file_exporter.show_window(
        title="Save components to ...",
        export_button_label="Choose",
        # The callback function called after the user has selected an export location.
        export_handler=callback_fn,
        filename_url="root"
    )       

class ExtensionFramework(omni.ext.IExt):

        
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[extension.framework] extension framework startup")
        self._usd_context = omni.usd.get_context()
        self._selection = self._usd_context.get_selection()
        self._events = self._usd_context.get_stage_event_stream()
        self._ext_Id = ext_id 
        self._stage_event_sub = \
        omni.usd.get_context().get_stage_event_stream().create_subscription_to_pop(
            self._on_stage_event, name="WWStageEventSub")
        #register selection listener
        



    def on_shutdown(self):
        print("[extension.framework] extension framework shutdown")

    def _on_stage_event(self, event:carb.events.IEvent):
        #No switch statenment in p3.7 :frown:
        self._stage = get_current_stage()
        if event.type ==  int(omni.usd.StageEventType.OPENED) :
            Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_notice_changed, self._stage)
            self.on_stage_opened(event)
        elif event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_selection_changed()    
        

    def on_stage_opened(self, event:carb.events.IEvent):
        print("Stage opened")    

    def _on_selection_changed(self):
        print("Selection Changed") 
        selections = self._selection.get_selected_prim_paths()
        return self.on_selection_changed(selections)
    
    def on_selection_changed(self,currently_selected: list):
        print("current selections: "+str(currently_selected))

    def _on_notice_changed(self, notice, stage):
        print("Notice changed")