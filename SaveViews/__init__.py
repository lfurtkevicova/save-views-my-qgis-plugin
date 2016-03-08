# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaveViews
                                 A QGIS plugin
 This plugin saves map image for every feature in attribute table of vector layer.
                             -------------------
        begin                : 2016-03-06
        copyright            : (C) 2016 by GISMentos
        email                : info@gismentors.eu
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SaveViews class from file SaveViews.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .save_views import SaveViews
    return SaveViews(iface)
