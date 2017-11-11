#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import xml.etree.ElementTree as etree
import sys

from xml_main_menu import Main_menu1
from renderer import Renderer
from viewer import Viewer
import pdb


def confirmed(toplevel, msg):
    """ Dialogo simple para pedir confirmación """
    dlg = Gtk.MessageDialog(
                parent = toplevel,
                text = msg,
                buttons = ("Cancelar", Gtk.ResponseType.CANCEL,
                           "Aceptar", Gtk.ResponseType.ACCEPT),
                message_type = Gtk.MessageType.QUESTION)
    Ok = dlg.run() == Gtk.ResponseType.ACCEPT

    dlg.destroy()
    return Ok


def warning(toplevel, msg):
    """ Dialogo simple para avisar de posibles problemas """
    dlg = Gtk.MessageDialog(
                parent = toplevel,
                text = msg,
                buttons = ("Aceptar", Gtk.ResponseType.ACCEPT),
                message_type = Gtk.MessageType.QUESTION)
    dlg.run()
    dlg.destroy()
    return


class Prop_table():
    """ El siguiente diccionario define las características de cada uno de
        los elementos (luces, camaras y objetos)
        No utilizar la estructura directamente... utilice las rutinas
        para acceder a los diferentes rubros.
    """

    PROPS = {
    #   Categorias
    #   |       Miembros de la categoria
    #   |       |       Características de cada miembro
    #   |       |       |
    #   V       |       |
        "lights": {
            "xlate": "Luces",
            "kinds": {
    #           |       |
    #           V       |
                "point": {
                    "xlate": "Puntual",
                    "params": {
    #                   |
    #                   V
                        "location": {"xlate": "Ubicación", "type": "vector"},
                        "color":    {"xlate": "Color",     "type": "rgb"}}},

                "directional": {
                    "xlate": "Direccional",
                    "params": {
                        "direction": {"xlate": "Dirección", "type": "vector"},
                        "point_at":  {"xlate": "Apunta a",  "type": "vector"},
                        "color":     {"xlate": "Color",     "type": "rgb"}}}
            }
        },

        "cameras": {
            "xlate": "Cámaras",
            "kinds": {
                "perspective": {
                    "xlate": "Perspectiva",
                    "params": {
                        "location": {"xlate": "Ubicación", "type": "vector"},   # vec3
                        "point_at": {"xlate": "Apunta a",  "type": "vector"},   # vec3
                        "up":       {"xlate": "Arriba",    "type": "vector"},   # vec3
                        "fov_y":    {"xlate": "Ángulo Y",  "type": "float"},    # float
                        "width":    {"xlate": "Aspecto",   "type": "integer"},  # integer
                        "height":   {"xlate": "Aspecto",   "type": "integer"},  # integer
                        "begrow":   {"xlate": "Aspecto",   "type": "integer"},  # integer
                        "endrow":   {"xlate": "Aspecto",   "type": "integer"},  # integer
                        "begcol":   {"xlate": "Aspecto",   "type": "integer"},  # integer
                        "endcol":   {"xlate": "Aspecto",   "type": "integer"}}},  # integer

                "parallel": {
                    "xlate": "Paralelo",
                    "params": {
                        "location":  {"xlate": "Ubicación", "type": "vector"},
                        "direction": {"xlate": "Apunta a",  "type": "vector"},
                        "up":        {"xlate": "Arriba",    "type": "vector"},
                        "aspect":    {"xlate": "Aspecto",   "type": "float"}}}
            }
        },

        "objects": {
            "xlate": "Objetos",
            "kinds": {
                "plane": {
                    "xlate": "Plano",
                    "params": {
                        "normal":     {"xlate": "Normal",    "type": "vector"},
                        "distance":   {"xlate": "Distancia", "type": "float"},
                        "diffuse":    {"xlate": "Difusa",    "type": "rgb"},
                        "ambient":    {"xlate": "Ambiente",  "type": "rgb"},
                        "reflection": {"xlate": "Reflexión", "type": "rgb"}}},
                "box": {
                    "xlate": "Caja",
                    "params": {
                        "location":   {"xlate": "Ubicación", "type": "vector"},
                        "side":       {"xlate": "Lado",      "type": "float"},
                        "diffuse":    {"xlate": "Difusa",    "type": "rgb"},
                        "ambient":    {"xlate": "Ambiente",  "type": "rgb"},
                        "reflection": {"xlate": "Reflexión", "type": "rgb"}}},

                "sphere": {
                    "xlate": "Esfera",
                    "params": {
                        "location":   {"xlate": "Ubicación",  "type": "vector"},
                        "radius":     {"xlate": "Radio",      "type": "float"},
                        "diffuse":    {"xlate": "Difusa",     "type": "rgb"},
                        "ambient":    {"xlate": "Ambiente",    "type": "rgb"},
                        "reflection": {"xlate": "Reflexión",  "type": "rgb"}}},

                "cone": {
                    "xlate": "Cono",
                    "params": {
                        "location": {"xlate": "Ubicación", "type": "vector"},
                        "height": {"xlate": "Alto", "type": "float"},
                        "radius": {"xlate": "Radio", "type": "float"},
                        "diffuse": {"xlate": "Difusa", "type": "rgb"},
                        "ambient": {"xlate": "Ambiente", "type": "rgb"},
                        "reflection": {"xlate": "Reflexión", "type": "rgb"}}}
            }
        }
    }

    def category_name(self, cat_name):
        """ Devuelve la traducción de la categoría """
        return self.PROPS[cat_name]["xlate"]


    def categories(self):
        """ Devuelve un generador de los indices de las categorías """
        return self.PROPS.keys()


    def kind_name(self, cat_name, kind):
        """ Devuelve la traducción del miembro de una categoría """
        return self.PROPS[cat_name]["kinds"][kind]["xlate"]


    def kinds(self, cat_name):
        """ Devuelve un generador de miembros de una categoría """
        return self.PROPS[cat_name]["kinds"].keys()


    def field_name(self, cat_name, kind, el):
        """ Devuelve a la traducción de una propiedad """
        return self.PROPS[cat_name]["kinds"][kind]["params"][el]["xlate"]


    def field_type(self, cat_name, kind, el):
        """ Devuelve al tipo de la propiedad """
        return self.PROPS[cat_name]["kinds"][kind]["params"][el]["type"]


    def fields(self, cat_name, kind):
        """ Devuelve un generador con las propiedades """
        return self.PROPS[cat_name]["kinds"][kind]["params"].keys()



class Prop_editor(Gtk.Dialog):
    def __init__(self, toplevel, ptable, category, key):
        super(Prop_editor, self).__init__(
                    parent = toplevel,
                    title = category,
                    buttons = ("Cancel", Gtk.ResponseType.CANCEL,
                               "Accept", Gtk.ResponseType.ACCEPT))

        self.toplevel = toplevel
        self.ptable = ptable
        self.grid = Gtk.Grid(row_spacing = 4, column_spacing = 8, margin = 6)

        # Siempre agregar campo de referencia
        lbl = Gtk.Label("Reference:", xalign = 1.0)
        lbl.xref = 'reference'

        self.grid.attach(lbl, 0, 0, 1, 1)
        wdg = Gtk.Entry()
        self.grid.attach(wdg, 1, 0, 1, 1)

        # Siempre agregar el tipo de elemento (no editable - 
        # fue elegido en el popup)
        lbl = Gtk.Label("Element:", xalign = 1.0)
        lbl.xref = 'element'

        self.grid.attach(lbl, 0, 1, 1, 1)
        self.grid.attach(Gtk.Label(key), 1, 1, 1, 1)

        # Agregar los items variables
        for y, el in enumerate(self.ptable.fields(category, key)):
            lbl_text = self.ptable.field_name(category, key, el) + ':'
            lbl = Gtk.Label(lbl_text, xalign = 1.0)
            lbl.xref = el

            field = self.ptable.field_type(category, key, el)
            self.grid.attach(lbl, 0, y+2, 1, 1)

            if type(field) == tuple:
                wdg = Gtk.ComboBoxText()
                for opt in el[1]:
                    wdg.append(opt, opt)
                wdg.set_active(0)

            elif field in ("vector", "rgb", "float", "string", "integer"):
                wdg = Gtk.Entry()

            else:
                print("Help - unknown data type")

            self.grid.attach(wdg, 1, y+2, 1, 1)

        cont = self.get_content_area()
        cont.add(self.grid)
        self.grid.show_all()


    def pack(self):
        """ Convertir los campos de edición en un diccionario para almacenar
            en el treestore de la escena
        """
        packed = {}
        children = list(self.grid.get_children())
        children.reverse()

        for i in range(0, len(children), 2):
            key = children[i].get_text()
            xref = children[i].xref
            wdg = children[i+1]

            if type(wdg) in (Gtk.Entry, Gtk.Label):
                packed[xref] = wdg.get_text()

            elif type(wdg) == Gtk.ComboBoxText:
                packed[xref] = wdg.get_active_text()

            else:
                print("Campo valor desconocido ({:s})".format(str(type(wdg))))

        return packed



class Scene(Gtk.Frame):
    def __init__(self, toplevel):
        super(Scene, self).__init__(label = "Escena")
        self.set_size_request(120, -1)
        self.toplevel = toplevel
        self.filename = None
        self.ptable = Prop_table()

        # Treestore almacena los datos de la escena
        #               str                 object
        # Categoria:    categoria           etiqueta visible
        # Objeto        referencia          parametros objeto

        self.store = Gtk.TreeStore(str, object, str)

        self.tree = Gtk.TreeView(
                    model = self.store,
                    vexpand = True,
                    margin = 4)

        renderer = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn("Elementos", renderer, text = 0)
        self.tree.append_column(col)
        self.tree.connect("button-press-event", self.treeview_button_pressed)

        self.clear()                            # (re-)Inicializa las categorias

        scroller = Gtk.ScrolledWindow(vexpand = True)
        scroller.add(self.tree)

        vbox = Gtk.VBox()
        vbox.pack_start(scroller, True, True, 0)
        self.add(vbox)

        label = Gtk.Label("Cámara activa: ")
        vbox.pack_start(label, False, False, 0)
        # 1er falso para que expanda en la direccion del box, 2do falso para
        # que se pegue a loscostados o no,
        self.cam_label = Gtk.Label("")
        vbox.pack_start(self.cam_label, False, False, 0)

        start_button = Gtk.Button("Renderizar")
        start_button.connect("clicked", self.on_start_button_clicked)
        vbox.pack_start(start_button, False, False, 0)

        self.toplevel.menu.add_items_to("Archivo", (
                    (None, None),
                    ("Guardar como...", self.save_as),
                    ("Guardar", self.save),
                    ("Abrir", self.load_from)))


    def dump(self):
        for row in self.store:
            print("{:-15s}: {:s}".format(row[0], str(row[1])))


    def treeview_button_pressed(self, wdg, event):
        if event.button == 3:
            # path será None o una tupla que contiene el path a la fila
            path = self.tree.get_path_at_pos(event.x, event.y)
            if path == None:              # Click no fue sobre una categoria
                return

            # 'get_iter' convierte path a iter
            cat_iter = self.store.get_iter(path[0])
            self.show_popup(cat_iter)


    def camera_defined(self):
        active = self.cam_label.get_text()
        if active == "":
            warning(self.toplevel, "Camera no está definida")
            return None

        for row in self.store:
            if row[0] == "cameras":
                for subrow in row.iterchildren():
                    if subrow[0] == active:
                        return subrow[1]

        return None


    def on_start_button_clicked(self, btn):
        cap = btn.get_label()
        if cap == "Renderizar":
            props = self.camera_defined()
            if props == None:
                return

            btn.set_label("Detener")
            render = Renderer(self, props)

        else:
            btn.set_label("Renderizar")


    def show_popup(self, cat_iter):
        """ Construir el popup para seleccionar acciones

                       | row[0]             | row[1]
                       | str                | object
            -----------+--------------------+--------------------
            Categoria  | categoria          | etiqueta visible
            Objeto     | referencia         | parametros objeto
        """
        row = self.store[cat_iter]
        lbl_ref, cat_obj, category = row

        is_category = isinstance(cat_obj, str)

        menu = Gtk.Menu()

        if is_category:
            item = Gtk.MenuItem("Agregar elemento")
            menu.append(item)

            submenu = Gtk.Menu()
            for key in self.ptable.kinds(lbl_ref):
                subitem = Gtk.MenuItem(self.ptable.kind_name(lbl_ref, key))
                subitem.connect("activate", self.popup_add_element, lbl_ref, key)
                submenu.append(subitem)
            item.set_submenu(submenu)

        else:   # es un elemento:
            for action, handler in (
                        ("Remover elemento", self.popup_remove_element),
                        ("Editar elemento",  self.popup_edit_element),
                        ("Activar",          self.popup_activate_element)):
                item = Gtk.MenuItem(action,
                            sensitive = action != "Activar" or category == "cameras")
                item.connect("activate", handler, lbl_ref, cat_iter)
                menu.append(item)

        menu.show_all()
        menu.popup(None, None, None, None, 1, Gtk.get_current_event_time())


    def popup_add_element(self, menuitem, category, key):
        """ Edita las propiedades de un elemento nuevo de tipo <key>
            y, de aceptarse, se agrega a <category>
        """
        prop_edit = Prop_editor(self.toplevel, self.ptable, category, key)
        if prop_edit.run() == Gtk.ResponseType.ACCEPT:
            data = prop_edit.pack()
            self.insert_element(category, data)
        prop_edit.destroy()


    def popup_remove_element(self, menuitem, lbl_ref, cat_iter):
        """ Remueve el elemento con treeiter <cat_iter>
        """
        if confirmed(self.toplevel,
                     "Seguro que quiere remover el elemento '{:s}'".format(lbl_ref)):
            if (lbl_ref == self.cam_label.get_text()):
            	self.cam_label.set_text("")
            self.store.remove(cat_iter)


    def popup_edit_element(self, menuitem, lbl_ref, cat_iter):
        """ Edita las propiedades de un elemento nuevo de tipo <key>
            y, de aceptarse, se agrega a <category>
        """
        pass


    def popup_activate_element(self, menuitem, lbl_ref, cat_iter):
        self.cam_label.set_text(lbl_ref)


    def insert_element(self, category, data):
        """ Inserta un elemento nuevo al miembre <data> de la
            categoría <category>
        """
        for row in self.store:
            if row[0] == category:
                cat_iter = row.iter
                self.store.append(cat_iter, (
                            data["reference"],
                            data,
                            category) )
                break


    def clear(self):
        """ Inicializa la lista de elementos:
                - Vacia completamente al TreeStore
                - Agrega las categorías iniciales
        """
        self.store.clear()
        # Ingresar las categorias principales (encabezados) en la escena
        for cat in self.ptable.categories():
            self.store.append(None, (cat,
                                     self.ptable.category_name(cat),
                                     cat) )


    def save_file(self, filename):
        with open(filename, "w") as xmlf:
            print('<?xml version="1.0"?>', file = xmlf)
            print('<scene>', file = xmlf)

            for row in self.store:
                category = row[0]
                print("  <{:s}>".format(category), file = xmlf)

                for subrow in row.iterchildren():
                    print(str(subrow[1]))
                    el = '    <{:s}'.format(subrow[1]["element"])
                    for key in subrow[1]:
                        el += ' {:s}="{:s}"'.format(key, subrow[1][key])
                    print(el + ' />', file = xmlf)

                print("  </{:s}>".format(category), file = xmlf)
            print('</scene>', file = xmlf)


    def load_file(self, filename):
        tree = etree.parse(filename)
        root = tree.getroot()

        if root.tag != "scene":
            print("Esto no es un archivo con una escena")
            sys.exit(1)

        self.clear()

        for child in root:              # Recorrer las categorias
            for element in child:       # Recorrer los elementos de la categoria
                self.insert_element(child.tag, element.attrib)

        self.tree.expand_all()


    def save(self, menuitem):
        if self.filename == None:       # No tenemos nombre para el archivo
            self.save_as(menuitem)      # todavia: Llamar a "Save as..."
        else:
            self.save_file(self.filename)


    def save_as(self, menuitem):
        fc_dialog = Gtk.FileChooserDialog(
                    parent = self.toplevel,
                    title = "Save scene",
                    do_overwrite_confirmation = True,
                    buttons = ("Cancelar", Gtk.ResponseType.CANCEL,
                               "Guardar", Gtk.ResponseType.ACCEPT),
                    action = Gtk.FileChooserAction.SAVE)

        if fc_dialog.run() != Gtk.ResponseType.ACCEPT:
            return

        fname = fc_dialog.get_filename()
        if fname == "": return

        self.filename = fname
        fc_dialog.destroy()

        self.save_file(self.filename)


    def load_from(self, menuitem):
        fc_dialog = Gtk.FileChooserDialog(
                    parent = self.toplevel,
                    title = "Load scene",
                    buttons = ("Cancelar", Gtk.ResponseType.CANCEL,
                               "Cargar", Gtk.ResponseType.ACCEPT),
                    action = Gtk.FileChooserAction.OPEN)

        if fc_dialog.run() == Gtk.ResponseType.ACCEPT:
            fname = fc_dialog.get_filename()

            if fname != "":
                self.filename = fname
                self.load_file(self.filename)

        fc_dialog.destroy()




class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect('destroy', lambda x: Gtk.main_quit())
        self.set_size_request(400, 400)

        self.menu =  Main_menu1(self)
        self.scene = Scene(self)
        self.viewer = Viewer(self)

        vbox = Gtk.VBox(spacing = 4)
        vbox.pack_start(self.menu, False, False, 0)

        hbox = Gtk.HBox(spacing = 4, margin = 4)
        hbox.pack_start(self.scene, False, False, 0)
        hbox.pack_start(self.viewer, True, True, 0)
        vbox.pack_start(hbox, True, True, 0)

        self.add(vbox)
        self.show_all()


    def run(self):
        Gtk.main()


def main():
    mw = MainWindow()
    mw.run()
    return 0

if __name__ == '__main__':
    main()
