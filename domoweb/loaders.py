
import os
import json
import zmq

from domoweb.db.models import Session, Widget, SectionIcon, SectionTheme, WidgetOption, WidgetCommand, WidgetSensor, WidgetDevice, DataType, Device, Command, Sensor, CommandParam
from collections import OrderedDict
from domogik.mq.reqrep.client import MQSyncReq
from domogik.mq.message import MQMessage

import logging

logger = logging.getLogger('domoweb')
cli = MQSyncReq(zmq.Context())

class packLoader:
    @classmethod
    def loadWidgets(cls, pack_path):
        session = Session()

        # Load all Widgets
        logger.info("PACKS: Loading widgets")
        widgets_path = os.path.join(pack_path, 'widgets')
        session.query(Widget).delete()
        session.query(WidgetOption).delete()
        session.query(WidgetCommand).delete()
        session.query(WidgetSensor).delete()
        session.query(WidgetDevice).delete()
        if os.path.isdir(widgets_path):
            for file in os.listdir(widgets_path):
                if not file.startswith('.'): # not hidden file
                    info = os.path.join(widgets_path, file, "info.json")
                    if os.path.isfile(info):
                        widgetset_file = open(info, "r")
                        widgetset_json = json.load(widgetset_file, object_pairs_hook=OrderedDict)
                        widgetset_id = widgetset_json["identity"]["id"]
                        widgetset_name = widgetset_json["identity"]["name"]
                        widgetset_version = widgetset_json["identity"]["version"]
                        widgetset_widgets = widgetset_json["widgets"]
                        for wid, widget in widgetset_widgets.items():
                            widget_id = "%s-%s" %(widgetset_id, wid)
                            widget_name = "%s [%s]" % (widget['name'], widgetset_name)
                            w = Widget(id=widget_id, set_id=widgetset_id, set_name=unicode(widgetset_name), version=widgetset_version, name=unicode(widget_name), height=widget['height'], width=widget['width'])
                            session.add(w)

                            # Options
                            for pid, param in widget['options'].items():
                                id = "%s-%s" % (widget_id, pid)
                                p = WidgetOption(id=id, widget_id=widget_id, key=pid, name=unicode(param['name']), description=unicode(param['description']), type=param['type'])
                                if 'default' in param:
                                    p.default = param['default']
                                if 'required' in param:
                                    p.required = param['required']
                                else:
                                    p.required = True
                                options={}
                                if 'min_length' in param:
                                    options['min_length'] = param['min_length']
                                if 'max_length' in param:
                                    options['max_length'] = param['max_length']
                                if 'min_value' in param:
                                    options['min_value'] = param['min_value']
                                if 'multilignes' in param:
                                    options['multilignes'] = param['multilignes']
                                if 'max_value' in param:
                                    options['max_value'] = param['max_value']
                                if 'mask' in param:
                                    options['mask'] = param['mask']
                                if 'choices' in param:
                                    options['choices'] = param['choices']
                                p.options=unicode(json.dumps(options))
                                session.add(p)
                            # Sensors parameters
                            for pid, param in widget['sensors'].items():
                                id = "%s-%s" % (widget_id, pid)
                                p = WidgetSensor(id=id, widget_id=widget_id, key=pid, name=unicode(param['name']), description=unicode(param['description']), types=json.dumps(param['types']))
                                if 'filters' in param:
                                    p.filters = ', '.join(param['filters'])
                                if 'required' in param:
                                    p.required = param['required']
                                else:
                                    p.required = True
                                session.add(p)
                            # Commands parameters
                            for pid, param in widget['commands'].items():
                                id = "%s-%s" % (widget_id, pid)
                                p = WidgetCommand(id=id, widget_id=widget_id, key=pid, name=unicode(param['name']), description=unicode(param['description']), types=json.dumps(param['types']))
                                if 'filters' in param:
                                    p.filters = ', '.join(param['filters'])
                                if 'required' in param:
                                    p.required = param['required']
                                else:
                                    p.required = True
                                session.add(p)
                            # Devices parameters
                            for pid, param in widget['devices'].items():
                                id = "%s-%s" % (widget_id, pid)
                                p = WidgetDevice(id=id, widget_id=widget_id, key=pid, name=unicode(param['name']), description=unicode(param['description']), types=json.dumps(param['types']))
                                if 'required' in param:
                                    p.required = param['required']
                                else:
                                    p.required = True
                                session.add(p)
        session.commit()
        session.close()

    @classmethod
    def loadIconsets(cls, pack_path):
        session = Session()
        # Load all Iconsets
        logger.info("PACKS: Loading iconsets")
        iconsets_path = os.path.join(pack_path, 'iconsets', 'section')
        session.query(SectionIcon).delete()
        if os.path.isdir(iconsets_path):
            for file in os.listdir(iconsets_path):
                if not file.startswith('.'): # not hidden file
                    info = os.path.join(iconsets_path, file, "info.json")
                    if os.path.isfile(info):
                        iconset_file = open(info, "r")
                        iconset_json = json.load(iconset_file)
                        iconset_id = iconset_json["identity"]["id"]
                        iconset_name = unicode(iconset_json["identity"]["name"])
                        for icon in iconset_json["icons"]:
                            id = iconset_id + '-' + icon["id"]
                            i = SectionIcon(id=id, iconset_id=iconset_id, iconset_name=iconset_name, icon_id=icon["id"], label=unicode(icon["label"]))
                            session.add(i)
        session.commit()
        session.close()

    @classmethod
    def loadThemes(cls, pack_path):
        session = Session()
        # Load all Themes
        logger.info("PACKS: Loading themes")
        themes_path = os.path.join(pack_path, 'themes')
        session.query(SectionTheme).delete()
        if os.path.isdir(themes_path):
            for file in os.listdir(themes_path):
                if not file.startswith('.'): # not hidden file
                    info = os.path.join(themes_path, file, "info.json")
                    if os.path.isfile(info):
                        theme_file = open(info, "r")
                        theme_json = json.load(theme_file)
                        theme_id = theme_json["identity"]["id"]
                        theme_name = unicode(theme_json["identity"]["name"])
                        t = SectionTheme(id=theme_id, label=theme_name)
                        session.add(t)
        session.commit()
        session.close()

class mqDataLoader:
    @classmethod
    def loadDatatypes(cls):
        session = Session()

        # get all datatypes
        logger.info("MQ: Loading Datatypes")
        msg = MQMessage()
        msg.set_action('datatype.get')
        res = cli.request('manager', msg.get(), timeout=10)
        if res is not None:
            _data = res.get_data()['datatypes']
        else:
            _data = {}

        session.query(DataType).delete()
        for type, params in _data.iteritems():
            r = DataType(id=type, parameters=json.dumps(params))
            session.add(r)
        session.commit()
        session.flush()

    @classmethod
    def loadDevices(cls):
        logger.info("MQ: Loading Devices info")
        Device.clean()
        msg = MQMessage()
        msg.set_action('client.list.get')
        res = cli.request('manager', msg.get(), timeout=10)
        if res is not None:
            _datac = res.get_data()
        else:
            _datac = {}
        session = Session()
        for client in _datac.itervalues(): 
            # for each plugin client, we request the list of devices
            if client["type"] == "plugin":
                msg = MQMessage()
                msg.set_action('device.get')
                msg.add_data('type', 'plugin')
                msg.add_data('name', client["name"])
                msg.add_data('host', client["host"])
                res = cli.request('dbmgr', msg.get(), timeout=10)
                if res is not None:
                    _datad = res.get_data()
                else:
                    _datad = {}
                if 'devices' in _datad:
                    for device in _datad["devices"]:
                        d = Device(id=device["id"], name=device["name"], type=device["device_type_id"], reference=device["reference"])
                        session.add(d)
                        if "commands" in device:
                            for ref, command  in device["commands"].iteritems():
                                c = Command(id=command["id"], name=command["name"], device_id=device["id"], reference=ref, return_confirmation=command["return_confirmation"])
                                session.add(c)
                                for param in command["parameters"]:
                                    p = CommandParam(command_id=id, key=param["key"], datatype_id=param["data_type"])
                                    session.add(p)
                        if "sensors" in device:
                            for ref, sensor in device["sensors"].iteritems():
                                s = Sensor(id=sensor["id"], name=sensor["name"], device_id=device["id"], reference=ref, datatype_id=sensor["data_type"], last_value=sensor["last_value"], last_received=sensor["last_received"])
                                session.add(s)

        session.commit()
        session.flush()