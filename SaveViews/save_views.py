# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaveViews
                                 A QGIS plugin
 This plugin saves map image for every feature in attribute table of vector layer.
                              -------------------
        begin                : 2016-03-06
        git sha              : $Format:%H$
        copyright            : (C) 2016 by GISMentos
        email                : info@gismentors.eu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QColor, QPixmap
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from save_views_dialog import SaveViewsDialog
import os.path
from qgis.core import *


class SaveViews:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SaveViews_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = SaveViewsDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Save Views')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SaveViews')
        self.toolbar.setObjectName(u'SaveViews')
        
        # clear the previously loaded text (if any) in the line edit widget
        self.dlg.lineEdit.clear()
        # connect the select_output_file method to the clicked signal of the tool button widget
        self.dlg.toolButton.clicked.connect(self.select_output_dir)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SaveViews', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SaveViews/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Save Views'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Save Views'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_output_dir(self):
        self.dirname = QFileDialog.getExistingDirectory(self.dlg, "Select directory ","/home")
        self.dlg.lineEdit.setText(self.dirname)

    def run(self,qgis):
        """Run method that performs all the real work"""
        # populate the Combo Box with the layers loaded in QGIS
        self.dlg.comboBox.clear()
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())
        self.dlg.comboBox.addItems(layer_list)
            
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # save graphical output for every row in attribute table
            selectedLayerIndex = self.dlg.comboBox.currentIndex()
            selectedLayerName = self.dlg.comboBox.currentText()
            selectedLayer = layers[selectedLayerIndex]
            frame_count = 0

            for feature in selectedLayer.getFeatures():
                if frame_count < selectedLayer.dataProvider().featureCount():
                    frame_count = selectedLayer.dataProvider().featureCount()
    
            if frame_count <= 1:
                print "Layer must have more than one feature!"
            else:                
                for feature in range(int(frame_count)):
                    selection = [int(feature)]
                    selectedLayer.setSelectedFeatures(selection)
                    self.iface.mapCanvas().setSelectionColor(QColor("transparent"));
                    box = selectedLayer.boundingBoxOfSelected()
                    self.iface.mapCanvas().setExtent(box)
                    pixmap = QPixmap(self.iface.mapCanvas().mapSettings().outputSize().width(),
                                     self.iface.mapCanvas().mapSettings().outputSize().height())
                    mapfile = self.dirname + "/" + selectedLayerName + "_" + format(feature, "03d") + ".png"
                    self.iface.mapCanvas().saveAsImage(mapfile, pixmap)
                    selectedLayer.removeSelection()
                
                # save also full extend of vector layer                       
                canvas = self.iface.mapCanvas()
                canvas.setExtent(selectedLayer.extent())
                pixmap = QPixmap(self.iface.mapCanvas().mapSettings().outputSize().width(),
                                     self.iface.mapCanvas().mapSettings().outputSize().height())
                mapfile = self.dirname + "/" + selectedLayerName + "_full" + ".png"
                self.iface.mapCanvas().saveAsImage(mapfile, pixmap)
