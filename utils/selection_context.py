from . import objects

class SelectionContext():
    ''' Utility class to revert selection to previous state '''
    selected_objects = None
    active_object = None

    def __enter__(self):
        ''' Save current selection '''
        self.selected_objects = objects.get_selected()
        self.active_object = objects.get_active()
        return self

    def __exit__(self, type, value, traceback):
        ''' Revert selection to original '''
        objects.deselect()
        for obj in self.selected_objects:
            objects.add_to_selection(obj)
        if self.active_object:
            objects.set_active(self.active_object)