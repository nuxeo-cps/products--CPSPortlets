/*
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziadé <tz@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id:$

javascript layer for tree views
the treeview editor knows how to load nodes dynamically

*/

var CPSTreeViewEditor = Class.create();

CPSTreeViewEditor.prototype = {

  initialize: function(nodeloader_class, node_getter, show_icons) {
    this.hooked = false;
    this.enabled = false;
    this.node_getter = node_getter;
    this.nodeloader_class = nodeloader_class;
    this.show_icons = show_icons;
    this.hookElements();
  },

  reloadNodes: function() {
    this.unHookElements();
    this.hookElements();
  },

  unHookElements: function() {
    if (!this.hooked)
      return;

    // hooking elements
    var onEnterNodeLs = this.onEnterNodeLoader.bindAsEventListener(this);
    var onLeaveNodeLs = this.onLeaveNodeLoader.bindAsEventListener(this);
    var onClickNodeLs = this.onClickNodeLoader.bindAsEventListener(this);

    for (var i = 0; i < this.nodeloaders.length; i++) {
      var nodeloader = this.nodeloaders[i];
      Event.stopObserving(nodeloader, 'mouseover', onEnterNodeLs);
      Event.stopObserving(nodeloader, 'mouseout', onLeaveNodeLs);
      Event.stopObserving(nodeloader, 'click', onClickNodeLs);
    }
    this.hooked = false;
    this.enabled = false;
  },

  hookElements: function() {
    if (this.hooked)
      return;

    this.nodeloaders = document.getElementsByClassName(this.nodeloader_class);
    if (this.nodeloaders.length==0) {
      // nothing to drag
      return;
    }

    // hooking loader elements
    var onEnterNodeLs = this.onEnterNodeLoader.bindAsEventListener(this);
    var onLeaveNodeLs = this.onLeaveNodeLoader.bindAsEventListener(this);
    var onClickNodeLs = this.onClickNodeLoader.bindAsEventListener(this);
    var onClickNodeFlippingLs = this.onClickNodeFlipping.bindAsEventListener(this);


    for (var i = 0; i < this.nodeloaders.length; i++) {
      var nodeloader = this.nodeloaders[i];
      area_id = nodeloader.id.replace('load-caller-', 'load-area-');
      area_node = $(area_id);
      if (area_node) {
        Event.observe(nodeloader, 'mouseover', onEnterNodeLs);
        Event.observe(nodeloader, 'mouseout', onLeaveNodeLs);
        // XXX weak test
        if (area_node.innerHTML.indexOf('<') == -1) {
          Event.observe(nodeloader, 'click', onClickNodeLs);
        }
        else {
          Event.observe(nodeloader, 'click', onClickNodeFlippingLs);
        }
      }
    }
    this.hooked = true;
    this.enabled = true;
  },

  unHookElements: function() {
    if (!this.hooked)
      return;

    // unhooking elements
    for (var i = 0; i < this.nodeloaders.length; i++) {
      var nodeloader = this.nodeloaders[i];
      for (var y = 0; y < Event.observers.length; y++) {
        var element = Event.observers[y][0];
        if (element==nodeloader) {
          Event.stopObserving.apply(nodeloader, Event.observers[y]);
          Event.observers[y][0] = null;
        }
      }
    }
    this.hooked = false;
    this.enabled = false;
  },

  onEnterNodeLoader: function(event) {
    setCursor(event.target, 'hand');
  },

  onLeaveNodeLoader: function(event) {
    setCursor(event.target, 'cursor');
  },

  onClickNodeFlipping: function(event) {
    // xxx weak, need a regexp here

    droppable_id = event.target.id.replace('load-caller-', 'load-area-');

    if ($(droppable_id)) {
      current_style = $(droppable_id).style;

      if (current_style.display) {
        if (current_style.display == 'none')
          current_style.display = '';
        else
          current_style.display = 'none';
      }
      else {
        current_style.display = 'none';
      }
      trigger_node = event.target;

      if (trigger_node.src.indexOf('minus')!=-1)
        trigger_node.src = trigger_node.src.replace('minus', 'plus');
      else
        trigger_node.src = trigger_node.src.replace('plus', 'minus');
    }
  },

  onClickNodeLoader: function(event) {
    var target_id = event.target.id;
    var classes = event.target.className.split(' ');
    var url = '';

    for (var i = 0; i < classes.length; i++) {
      var class_ = classes[i];
      if (class_.indexOf('url:') == 0) {
        url = class_.substring(4);
        url = url + '.' + this.node_getter;
        while (url.indexOf('.')!=-1) {
          url = url.replace('\.', '/');
        }
        break;
      }
    }

    if (url!='') {
      area_id = target_id.replace('load-caller-', 'load-area-');
      this.current_target_id = target_id;
      this.loadNode(area_id, url);
    }
  },

  loadNode: function(area_id, url) {
    if (!$(area_id))
      return;
    // let's do it !
    Effect.Appear($(area_id), {duration:0.5, queue:'end'});
    var loadNodeResultBn = this.loadNodeResult.bind(this);
    params = 'show_icons=' + this.show_icons;
    var options = {parameters: params, onComplete: loadNodeResultBn};
    this.current_area = $(area_id);
    var sender = new Ajax.Request(url, options);
  },

  loadNodeResult: function(originalRequest) {
    // let's load the content
    result = originalRequest.responseText;
    trigger_node = $(this.current_target_id);
    trigger_node.src = trigger_node.src.replace('plus', 'minus');

    this.current_area.innerHTML = result;
    // reloading nodes that where added
    this.reloadNodes();
  }
}


/* helpers */

function setCursor(obj, cursor)
{
  if (!cursor || cursor=="hand" || cursor=="pointer") {
    if (navigator.appName == "Microsoft Internet Explorer")
      isIE = true;
    else
      isIE = false;
    cursor = isIE ? "hand" : "pointer";
  }

  obj.style.cursor = cursor;
}
